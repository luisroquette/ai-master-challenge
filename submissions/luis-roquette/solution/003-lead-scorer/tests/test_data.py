"""C1 fixtures shared with scoring/UI checks; no external network required."""
import csv
import hashlib
import io
import json
import contextlib
import http.server
import runpy
import stat
import threading
import zipfile
from pathlib import Path
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch

import data


def fixture_tables():
    return {
        "accounts.csv": [{"account": "Acme", "year_established": "1990"}],
        "products.csv": [{"product": "GTX Pro", "series": "GTX", "sales_price": "100"},
                         {"product": "Other", "series": "Other", "sales_price": "10"}],
        "sales_teams.csv": [{"sales_agent": "Ana", "manager": "Luis", "regional_office": "Central"}],
        "sales_pipeline.csv": [
            {"opportunity_id": "001", "sales_agent": "Ana", "product": "GTXPro", "account": "Acme",
             "deal_stage": "Won", "engage_date": "2017-01-01", "close_date": "2017-01-02", "close_value": "90"},
            {"opportunity_id": "002", "sales_agent": "Ana", "product": "Other", "account": "Acme",
             "deal_stage": "Lost", "engage_date": "2017-01-01", "close_date": "2017-02-02", "close_value": "0"},
            {"opportunity_id": "003", "sales_agent": "Ana", "product": "GTX Pro", "account": "Acme",
             "deal_stage": "Engaging", "engage_date": "2017-03-01", "close_date": "", "close_value": ""},
            {"opportunity_id": "004", "sales_agent": "Ana", "product": "GTX Pro", "account": "",
             "deal_stage": "Prospecting", "engage_date": "", "close_date": "", "close_value": ""},
        ],
    }


def fixture_snapshot(tables=None):
    tables = fixture_tables() if tables is None else tables
    files, entries = [], {}
    for name, records in tables.items():
        header = list(records[0]) if records else list(data.SCHEMA[name])
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=header)
        writer.writeheader()
        writer.writerows(records)
        content = out.getvalue().encode()
        files.append((name, content))
        entries[name] = {"headers": header, "sha256": hashlib.sha256(content).hexdigest(),
                         "source_url": "https://example.invalid/fixture", "license": "synthetic",
                         "download_url": "https://example.invalid/fixture/" + name}
    return data.Snapshot(tuple(files), json.dumps({"schema_version": 1, "files": entries}), "fixture-dependency-digest")


def write_fixture(directory, snapshot=None):
    snapshot = snapshot or fixture_snapshot()
    directory = Path(directory)
    raw = directory / "raw"
    raw.mkdir()
    for name, content in snapshot.files:
        (raw / name).write_bytes(content)
    manifest = directory / "manifest.json"
    manifest.write_text(snapshot.manifest_json)
    return raw, manifest


class DataTests(unittest.TestCase):
    def test_TC01_real_provenance(self):
        snapshot = data.read_snapshot(data.ROOT / "data/raw", data.ROOT / "data/manifest.json")
        dataset = data.load_dataset(snapshot)
        self.assertEqual(dataset.counts["sales_pipeline.csv"], 8800)
        self.assertEqual([dataset.counts[n] for n in ("accounts.csv", "products.csv", "sales_teams.csv")], [85, 7, 35])
        for entry in json.loads(snapshot.manifest_json)["files"].values():
            self.assertEqual(entry["license"], "CC0-1.0")
            self.assertIn("datasetVersionNumber=1", entry["download_url"])
        self.assertEqual(len(dataset.opportunities), 8800)

    def test_TC04_file_manifest_and_recovery_guards(self):
        for fault in ("missing", "checksum", "manifest", "manifest_files_list", "manifest_entry_list",
                      "manifest_bad_hash", "marker_before", "marker_after"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                raw, manifest = write_fixture(directory)
                if fault == "missing":
                    (raw / "accounts.csv").unlink()
                elif fault == "checksum":
                    (raw / "accounts.csv").write_bytes(b"tampered")
                elif fault == "manifest":
                    manifest.write_text("{}")
                elif fault.startswith("manifest_"):
                    metadata = json.loads(manifest.read_text())
                    if fault == "manifest_files_list":
                        metadata["files"] = []
                    elif fault == "manifest_entry_list":
                        metadata["files"]["accounts.csv"] = []
                    else:
                        metadata["files"]["accounts.csv"]["sha256"] = "wrong"
                    manifest.write_text(json.dumps(metadata))
                elif fault == "marker_before":
                    (raw.parent / ".recovery.lock").mkdir()
                if fault == "marker_after":
                    original = Path.read_bytes
                    def read(path):
                        content = original(path)
                        if path.name == "sales_teams.csv":
                            (raw.parent / ".recovery.lock").mkdir()
                        return content
                    with patch.object(Path, "read_bytes", read), self.assertRaises(data.DataValidationError):
                        data.read_snapshot(raw, manifest)
                else:
                    with self.assertRaises(data.DataValidationError):
                        data.read_snapshot(raw, manifest)

    def test_TC04_headers_and_primary_keys(self):
        for fault in ("header", "empty_key", "normalized_duplicate", "duplicate_id", "duplicate_alias"):
            with self.subTest(fault=fault):
                tables = fixture_tables()
                if fault == "header":
                    del tables["accounts.csv"][0]["year_established"]
                elif fault == "empty_key":
                    tables["accounts.csv"][0]["account"] = "  "
                elif fault == "normalized_duplicate":
                    tables["accounts.csv"].append({"account": " Acme ", "year_established": "2000"})
                elif fault == "duplicate_alias":
                    tables["products.csv"].append({"product": "GTXPro", "series": "GTX", "sales_price": "100"})
                else:
                    tables["sales_pipeline.csv"][1]["opportunity_id"] = "001"
                with self.assertRaises(data.DataValidationError) as error:
                    data.load_dataset(fixture_snapshot(tables))
                self.assertEqual(error.exception.diagnostics[-1].scope, "global")

    def test_TC04_unreadable_and_irregular_csv(self):
        original = fixture_snapshot()
        for corrupt in (b"\xff", b"account,year_established\nAcme,1990,extra\n", b""):
            with self.subTest(corrupt=repr(corrupt)):
                snapshot = replace(original, files=tuple(
                    (name, corrupt if name == "accounts.csv" else content)
                    for name, content in original.files))
                with self.assertRaises(data.DataValidationError) as error:
                    data.load_dataset(snapshot)
                self.assertEqual(error.exception.diagnostics[-1].code, "unreadable_csv")

    def test_TC04_closed_date_order_and_missing_required_date(self):
        for field, value in (("close_date", "2016-01-01"), ("close_date", ""),
                             ("engage_date", "wrong")):
            with self.subTest(field=field, value=value):
                tables = fixture_tables()
                tables["sales_pipeline.csv"][0][field] = value
                result = data.load_dataset(fixture_snapshot(tables))
                self.assertFalse(result.opportunities.iloc[0].eligible_history)
                self.assertTrue(any(d.field == field for d in result.diagnostics))

    def test_TC04_row_errors_and_fallback(self):
        cases = (("product", "unknown", "unknown_key", False),
                 ("sales_agent", "unknown", "unknown_key", False),
                 ("engage_date", "2017-02-30", "invalid_date", False),
                 ("engage_date", "20170301", "invalid_date", False),
                 ("account", "unknown", "account_fallback", True),
                 ("deal_stage", "unknown", "invalid_stage", False))
        for field, value, code, eligible in cases:
            with self.subTest(field=field, value=value):
                tables = fixture_tables()
                tables["sales_pipeline.csv"][2][field] = value
                result = data.load_dataset(fixture_snapshot(tables))
                row = result.opportunities.set_index("opportunity_id").loc["003"]
                self.assertEqual(bool(row.eligible_active), eligible)
                diagnostic = next(d for d in result.diagnostics if d.opportunity_id == "003" and d.code == code)
                self.assertTrue(diagnostic.field and diagnostic.reason and diagnostic.correction)

    def test_TC04_financial_error_does_not_remove_training_label(self):
        for stage, value in (("Won", ""), ("Won", "-1"), ("Won", "nan"), ("Won", "inf"), ("Lost", "1")):
            with self.subTest(stage=stage, value=value):
                tables = fixture_tables()
                tables["sales_pipeline.csv"][0].update(deal_stage=stage, close_value=value)
                result = data.load_dataset(fixture_snapshot(tables))
                row = result.opportunities.iloc[0]
                self.assertTrue(row.eligible_history)
                self.assertFalse(row.financial_eligible)
                self.assertTrue(any(d.code == "invalid_financial_label" for d in result.diagnostics))

    def test_TC04_blank_optional_dates_remain_supported(self):
        result = data.load_dataset(fixture_snapshot())
        prospect = result.opportunities.set_index("opportunity_id").loc["004"]
        self.assertTrue(prospect.eligible_active)
        self.assertFalse(any(d.code == "invalid_date" and d.opportunity_id == "004"
                             for d in result.diagnostics))

    def test_TC04_account_year_partitions(self):
        for year, route in (("0", "fallback"), ("-1", "fallback"), ("1", "full"),
                            ("1990.5", "fallback"), ("nan", "fallback"), ("bad", "fallback")):
            with self.subTest(year=year):
                tables = fixture_tables()
                tables["accounts.csv"][0]["year_established"] = year
                result = data.load_dataset(fixture_snapshot(tables))
                self.assertEqual(result.opportunities.iloc[0].route, route)
                self.assertTrue(result.opportunities.iloc[0].eligible_history)

    def test_TC05_price_boundaries(self):
        for value, valid in (("-1", False), ("0", False), ("1", True), ("nan", False), ("inf", False), ("bad", False)):
            with self.subTest(value=value):
                tables = fixture_tables()
                tables["products.csv"][0]["sales_price"] = value
                result = data.load_dataset(fixture_snapshot(tables))
                self.assertEqual(bool(result.opportunities.iloc[2].eligible_active), valid)

    def test_TC06_normalization_identity_and_cardinality(self):
        tables = fixture_tables()
        tables["sales_pipeline.csv"][0]["opportunity_id"] = " 001 "
        result = data.load_dataset(fixture_snapshot(tables))
        self.assertEqual(len(result.opportunities), 4)
        row = result.opportunities.iloc[0]
        self.assertEqual(row.opportunity_id, "001")
        self.assertEqual(row["product"], "GTX Pro")
        self.assertEqual(row.sales_price, 100)
        self.assertEqual(row.product_match, "both")

    def test_TC07_accounting_and_no_history(self):
        tables = fixture_tables()
        tables["sales_pipeline.csv"][2]["product"] = "unknown"
        tables["sales_pipeline.csv"].append(dict(tables["sales_pipeline.csv"][1], opportunity_id="005", deal_stage="Invalid"))
        result = data.load_dataset(fixture_snapshot(tables))
        partitions = ("supported_active", "supported_history", "unsupported_active", "excluded_history_or_stage")
        self.assertEqual(sum(result.counts.get(key, 0) for key in partitions), 5)
        self.assertEqual(result.counts["unsupported_active"], 1)
        tables["sales_pipeline.csv"] = tables["sales_pipeline.csv"][2:]
        with self.assertRaises(data.DataValidationError) as error:
            data.load_dataset(fixture_snapshot(tables))
        self.assertEqual(error.exception.diagnostics[-1].code, "no_usable_history")

    def test_TC40_fingerprint_bytes_config_provenance_dependencies(self):
        snapshot = fixture_snapshot()
        original = data.fingerprint(snapshot, {"seed": 42, "version": 1})
        self.assertEqual(original, data.fingerprint(snapshot, {"version": 1, "seed": 42}))
        self.assertNotEqual(original, data.fingerprint(snapshot, {"seed": 43, "version": 1}))
        for changed in (replace(snapshot, files=tuple((n, b + b"\n") for n, b in snapshot.files)),
                        replace(snapshot, dependency_digest="different"),
                        replace(snapshot, manifest_json=snapshot.manifest_json.replace("synthetic", "changed"))):
            self.assertNotEqual(original, data.fingerprint(changed, {"seed": 42, "version": 1}))
        with self.assertRaises(ValueError):
            data.fingerprint(snapshot, {"threshold": float("nan")})

    def test_TC40_read_once_snapshot_survives_filesystem_change(self):
        with tempfile.TemporaryDirectory() as directory:
            raw, manifest = write_fixture(directory)
            snapshot = data.read_snapshot(raw, manifest)
            before = data.fingerprint(snapshot, {})
            (raw / "accounts.csv").write_bytes(b"corrupt")
            self.assertEqual(before, data.fingerprint(snapshot, {}))
            self.assertEqual(len(data.load_dataset(snapshot).opportunities), 4)


@contextlib.contextmanager
def recovery_source(snapshot, archive=False, extra=None):
    """Real loopback transport; no successful external-network stub."""
    payloads = dict(snapshot.files)
    if archive:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zipped:
            for name, content in snapshot.files:
                if extra and isinstance(extra[0], zipfile.ZipInfo) and extra[0].filename == name:
                    continue
                zipped.writestr(name, content)
            if extra:
                zipped.writestr(*extra)
        payloads = {"fixture.zip": buffer.getvalue()}
    requests = []
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            content = payloads.get(self.path.removeprefix("/"))
            self.send_response(200 if content is not None else 404)
            self.end_headers()
            if content is not None:
                self.wfile.write(content)

        def log_message(self, *_):
            pass
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    manifest = json.loads(snapshot.manifest_json)
    for name, entry in manifest["files"].items():
        entry["download_url"] = f"http://127.0.0.1:{server.server_port}/" + ("fixture.zip" if archive else name)
        if archive:
            entry["archive_member"] = name
    try:
        yield replace(snapshot, manifest_json=json.dumps(manifest)), requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class RecoveryTests(unittest.TestCase):
    def test_TC02_direct_and_archive_verified_promotion(self):
        for archive in (False, True):
            with self.subTest(archive=archive), recovery_source(fixture_snapshot(), archive) as (snapshot, requests):
                with tempfile.TemporaryDirectory() as directory:
                    raw, manifest = write_fixture(directory, snapshot)
                    (raw / "accounts.csv").write_bytes(b"damaged original")
                    original = data._directory_digests(raw)
                    result = data.recover_dataset(manifest, raw)
                    self.assertEqual(result["status"], "recovered")
                    self.assertEqual(dict(data.read_snapshot(raw, manifest).files), dict(snapshot.files))
                    self.assertEqual(data._directory_digests(Path(result["backup"])), original)
                    self.assertEqual(len(requests), 1 if archive else 4)
                    self.assertFalse((raw.parent / ".recovery.lock").exists())

    def test_TC03_checksum_and_schema_fail_before_promotion(self):
        for fault in ("checksum", "schema"):
            with self.subTest(fault=fault), recovery_source(fixture_snapshot()) as (snapshot, _):
                with tempfile.TemporaryDirectory() as directory:
                    raw, manifest = write_fixture(directory, snapshot)
                    original = data._directory_digests(raw)
                    metadata = json.loads(manifest.read_text())
                    if fault == "checksum":
                        metadata["files"]["accounts.csv"]["sha256"] = "0" * 64
                    else:
                        metadata["files"]["accounts.csv"]["headers"] = ["wrong"]
                    manifest.write_text(json.dumps(metadata))
                    with self.assertRaises(data.RecoveryError):
                        data.recover_dataset(manifest, raw)
                    self.assertEqual(data._directory_digests(raw), original)
                    self.assertFalse((raw.parent / ".recovery.lock").exists())

    def test_TC03_promotion_and_final_validation_roll_back(self):
        for fault in ("second_rename", "final_validation"):
            with self.subTest(fault=fault), recovery_source(fixture_snapshot()) as (snapshot, _):
                with tempfile.TemporaryDirectory() as directory:
                    raw, manifest = write_fixture(directory, snapshot)
                    (raw / "accounts.csv").write_bytes(b"original needing recovery")
                    original = data._directory_digests(raw)
                    rename, load = Path.rename, data.load_dataset
                    calls = []
                    def fail_rename(path, target):
                        if path.name.endswith("-stage"):
                            raise OSError("injected second rename failure")
                        return rename(path, target)
                    def fail_load(value):
                        calls.append(value)
                        if len(calls) == 2:
                            raise ValueError("injected final validation failure")
                        return load(value)
                    with patch.object(Path, "rename", fail_rename if fault == "second_rename" else rename), \
                            patch.object(data, "load_dataset", fail_load if fault == "final_validation" else load), \
                            self.assertRaises(data.RecoveryError):
                        data.recover_dataset(manifest, raw)
                    self.assertEqual(data._directory_digests(raw), original)
                    self.assertFalse((raw.parent / ".recovery.lock").exists())

    def test_TC03_failed_rollback_preserves_original_and_resume(self):
        with recovery_source(fixture_snapshot()) as (snapshot, _), tempfile.TemporaryDirectory() as directory:
            raw, manifest = write_fixture(directory, snapshot)
            (raw / "accounts.csv").write_bytes(b"original requiring repair")
            original = data._directory_digests(raw)
            rename = Path.rename
            def fail(path, target):
                if path.name.endswith(("-stage", "-backup")):
                    raise OSError("injected promotion/rollback failure")
                return rename(path, target)
            with patch.object(Path, "rename", fail), self.assertRaisesRegex(data.RecoveryError, "--resume"):
                data.recover_dataset(manifest, raw)
            marker = raw.parent / ".recovery.lock"
            record = json.loads((marker / "transaction.json").read_text())
            self.assertEqual(data._directory_digests(raw.parent / record["backup"]), original)
            self.assertFalse(raw.exists())
            with self.assertRaises(data.DataValidationError):
                data.read_snapshot(raw, manifest)
            with self.assertRaises(data.RecoveryError):
                data.recover_dataset(manifest, raw)
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                data.main(["recover", "--resume", "--manifest", str(manifest), "--raw-dir", str(raw)])
            self.assertIn("original_restored", stdout.getvalue())
            self.assertEqual(data._directory_digests(raw), original)
            self.assertFalse(marker.exists())

    def test_TC03_interruption_before_and_after_promotion_resumes_original(self):
        for point in ("staging", "after_first_rename", "after_promotion"):
            with self.subTest(point=point), recovery_source(fixture_snapshot()) as (snapshot, _):
                with tempfile.TemporaryDirectory() as directory:
                    raw, manifest = write_fixture(directory, snapshot)
                    (raw / "accounts.csv").write_bytes(b"original before interrupt")
                    original = data._directory_digests(raw)
                    rename, download = Path.rename, data._download
                    def interrupt_rename(path, target):
                        result = rename(path, target)
                        if ((point == "after_first_rename" and Path(target).name.endswith("-backup")) or
                                (point == "after_promotion" and path.name.endswith("-stage"))):
                            raise KeyboardInterrupt()
                        return result
                    def interrupt_download(url):
                        raise KeyboardInterrupt()
                    with patch.object(Path, "rename", interrupt_rename), \
                            patch.object(data, "_download", interrupt_download if point == "staging" else download), \
                            self.assertRaises(KeyboardInterrupt):
                        data.recover_dataset(manifest, raw)
                    self.assertTrue((raw.parent / ".recovery.lock").exists())
                    result = data.recover_dataset(manifest, raw, resume=True)
                    self.assertEqual(result["status"], "original_restored")
                    self.assertEqual(data._directory_digests(raw), original)

    def test_TC03_zip_rejects_extra_traversal_symlink_duplicate(self):
        symbolic = zipfile.ZipInfo("accounts.csv")
        symbolic.create_system = 3
        symbolic.external_attr = (stat.S_IFLNK | 0o777) << 16
        for extra in (("../escape.csv", b"bad"), ("metadata.csv", b"unlisted"),
                      (symbolic, b"/tmp/outside")):
            with self.subTest(member=str(extra[0])), recovery_source(fixture_snapshot(), True, extra) as (snapshot, _):
                with tempfile.TemporaryDirectory() as directory:
                    raw, manifest = write_fixture(directory, snapshot)
                    original = data._directory_digests(raw)
                    with self.assertRaises(data.RecoveryError):
                        data.recover_dataset(manifest, raw)
                    self.assertEqual(data._directory_digests(raw), original)

    def test_TC03_sources_import_and_cli_are_explicit(self):
        for url in ("http://example.com/file", "file:///etc/passwd", "ftp://example.com/file",
                    "https://name:secret@example.com/file", "http://127.0.0.1.evil/file"):
            with self.subTest(url=url), patch.object(data, "build_opener") as opener:
                with self.assertRaises(data.RecoveryError):
                    data._download(url)
                opener.assert_not_called()
        with self.assertRaises(data.RecoveryError):
            data._SafeRedirect().redirect_request(None, None, 302, "", {}, "http://example.com/file")
        with patch("urllib.request.OpenerDirector.open", side_effect=AssertionError("implicit network")):
            runpy.run_path(str(data.ROOT / "data.py"), run_name="import_check")
            data.load_dataset(fixture_snapshot())
        with contextlib.redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as exit_code:
            data.main(["recover", "--help"])
        self.assertEqual(exit_code.exception.code, 0)
        self.assertIn(".venv/bin/python data.py recover", output.getvalue())
        self.assertIn("--resume", output.getvalue())

    def test_TC03_resume_rejects_tampered_paths_digests_symlinks(self):
        for fault in ("outside", "raw", "digest", "symlink", "oversize", "backup_corrupt"):
            with self.subTest(fault=fault), recovery_source(fixture_snapshot()) as (snapshot, _):
                with tempfile.TemporaryDirectory() as directory:
                    raw, manifest = write_fixture(directory, snapshot)
                    original = data._directory_digests(raw)
                    rename = Path.rename
                    def interrupt(path, target):
                        result = rename(path, target)
                        if Path(target).name.endswith("-backup"):
                            raise KeyboardInterrupt()
                        return result
                    with patch.object(Path, "rename", interrupt), self.assertRaises(KeyboardInterrupt):
                        data.recover_dataset(manifest, raw)
                    marker = raw.parent / ".recovery.lock"
                    record_path = marker / "transaction.json"
                    record = json.loads(record_path.read_text())
                    backup = raw.parent / record["backup"]
                    if fault == "outside":
                        record["backup"] = "../../outside"
                    elif fault == "raw":
                        record["raw"] = "elsewhere"
                    elif fault == "digest":
                        record["original"]["accounts.csv"] = "invalid"
                    elif fault == "symlink":
                        (raw.parent / record["displaced"]).symlink_to(backup, target_is_directory=True)
                    elif fault == "backup_corrupt":
                        (backup / "accounts.csv").write_bytes(b"bad backup")
                    record_path.write_text(" " * 8193 if fault == "oversize" else json.dumps(record))
                    with self.assertRaises(data.RecoveryError):
                        data.recover_dataset(manifest, raw, resume=True)
                    self.assertTrue(marker.exists())
                    self.assertTrue(backup.exists())
                    if fault != "backup_corrupt":
                        self.assertEqual(data._directory_digests(backup), original)

    def test_TC03_active_recovery_excludes_resume_and_readers(self):
        with recovery_source(fixture_snapshot()) as (snapshot, _), tempfile.TemporaryDirectory() as directory:
            raw, manifest = write_fixture(directory, snapshot)
            download = data._download
            def check_during_download(url):
                with self.assertRaises(data.RecoveryError):
                    data.recover_dataset(manifest, raw, resume=True)
                with self.assertRaises(data.DataValidationError):
                    data.read_snapshot(raw, manifest)
                return download(url)
            with patch.object(data, "_download", check_during_download):
                data.recover_dataset(manifest, raw)


if __name__ == "__main__":
    unittest.main()
