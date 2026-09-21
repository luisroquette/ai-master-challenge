"""C1 fixtures shared with scoring/UI checks; no external network required."""
import csv
import hashlib
import io
import json
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


if __name__ == "__main__":
    unittest.main()
