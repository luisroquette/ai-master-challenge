"""Autocontained sanitized fixtures, never submission metrics or human evidence.

Run from the solution directory, including when collected from the sealed S07 copy.
Only manifest.generated_at is excluded: it records the wall time of publication,
not a scientific result. No other timestamps or numerical tolerances are ignored.
"""

import csv
import hashlib
import io
import json
import runpy
import socket
import sqlite3
from contextlib import closing
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace

import joblib
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import support_copilot.ui as ui
from support_copilot.data import (
    CUSTOMER_COLUMNS,
    CUSTOMER_TAXONOMY,
    IT_TAXONOMY,
    atomic_json,
    content_hash,
)
from support_copilot.decision import base_policy, lock_policy
from support_copilot.modeling import Prediction
from support_copilot.retrieval import RetrievalPolicy, lock_review
from support_copilot.store import list_decisions

ROOT = Path.cwd()  # S07 lives under runtime; never derive the solution from __file__.
REPRODUCE = runpy.run_path(str(ROOT / "scripts/reproduce.py"))["reproduce"]


def sources(root):
    root.mkdir(parents=True)
    words = [chr(97 + i // 26) + chr(97 + i % 26) + "token" for i in range(20)]
    customer = []
    for label, token in zip(CUSTOMER_TAXONOMY, (
            "billing", "cancellation", "product", "refund", "technical"), strict=True):
        for word in words:
            row = dict.fromkeys(CUSTOMER_COLUMNS, "")
            row.update({"Ticket ID": str(len(customer) + 1), "Ticket Type": label,
                        "Ticket Description": f"{token} {token} device {word}",
                        "Ticket Status": "Closed", "Ticket Priority": "Low",
                        "Ticket Channel": "Email", "Resolution": "reset the device",
                        "First Response Time": "2026-01-01T00:00:00Z",
                        "Time to Resolution": "2026-01-01T01:00:00Z"})
            customer.append(row)
    customer_path, it_path = root / "customer.csv", root / "it.csv"
    pd.DataFrame(customer).to_csv(customer_path, index=False)
    pd.DataFrame([{"Document": f"{token} {token} device {word}", "Topic_group": label}
                  for label, token in zip(IT_TAXONOMY, (
                      "access", "admin", "hr", "hardware", "project", "misc", "purchase",
                      "storage"), strict=True) for word in words]).to_csv(it_path, index=False)
    return customer_path, it_path


def canonical_run(root):
    manifest = json.loads((root / "manifest.json").read_text())
    manifest.pop("generated_at")  # The ONE allowed exclusion, justified in module docstring.
    values = {}
    for key, entry in manifest["artifacts"].items():
        if entry["status"] != "ready":
            continue
        path = root / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        if entry["type"] in {"domain-model", "retriever"}:
            value = ui.logical_payload(joblib.load(path))
            # Binary hashes validate their own run, while equivalence uses semantic state.
            entry["sha256"] = entry["logical_sha256"]
        elif path.suffix == ".csv":
            value = json.loads(pd.read_csv(path, keep_default_na=entry["type"] != "review-template")
                               .to_json(orient="records"))
        else:
            value = json.loads(path.read_text())
        assert content_hash(value) == entry["logical_sha256"], key
        values[key] = value
    return json.loads(json.dumps({"manifest": manifest, "values": values}, sort_keys=True))


def test_reproduce_twice_same_inputs(tmp_path):
    customer, it = sources(tmp_path / "sources")
    first, second = tmp_path / "first", tmp_path / "second"
    REPRODUCE(customer, it, first)
    REPRODUCE(customer, it, second)
    assert canonical_run(first) == canonical_run(second)
    assert not (first / "data/customer-test.json").exists()
    assert not (first / "review/retrieval-test-template.csv").exists()
    assert json.loads((first / "models/metrics.json").read_text())["status"] == "sealed"


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    root = tmp_path_factory.mktemp("workflow")
    customer, it = sources(root / "source")
    artifacts = root / "artifacts"
    REPRODUCE(customer, it, artifacts)
    return artifacts, customer, it


@pytest.mark.parametrize("mutation", ["metric", "split", "policy", "logical", "timestamp"])
def test_comparison_rejects_every_other_change(prepared, tmp_path, mutation):
    import shutil
    original = prepared[0]
    changed = tmp_path / "changed"
    shutil.copytree(original, changed)
    baseline = canonical_run(original)
    manifest = json.loads((changed / "manifest.json").read_text())
    if mutation == "split":
        manifest["splits"]["customer"]["partitions"]["train"]["ids"][0] = "customer:changed"
    elif mutation == "logical":
        manifest["artifacts"]["models.customer"]["logical_sha256"] = "a" * 64
    else:
        key = {"metric": "models.metrics", "policy": "policies.customer",
               "timestamp": "review.retrieval-calibration-packet"}[mutation]
        entry = manifest["artifacts"][key]
        path = changed / entry["path"]
        value = json.loads(path.read_text())
        value[{"metric": "status", "policy": "threshold", "timestamp": "created_at"}[
            mutation]] = "changed"
        atomic_json(value, path)
        entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        entry["logical_sha256"] = content_hash(value)
    atomic_json(manifest, changed / "manifest.json")
    try:
        actual = canonical_run(changed)
    except AssertionError:
        return
    assert actual != baseline


def test_comparison_allows_only_manifest_generated_at(prepared, tmp_path):
    import shutil
    changed = tmp_path / "changed"
    shutil.copytree(prepared[0], changed)
    manifest = json.loads((changed / "manifest.json").read_text())
    manifest["generated_at"] = "2030-01-01T00:00:00Z"
    atomic_json(manifest, changed / "manifest.json")
    assert canonical_run(prepared[0]) == canonical_run(changed)


def test_release_only_after_explicit_lock_preserves_runtime(prepared, tmp_path):
    import shutil
    original, customer, it = prepared
    root = tmp_path / "artifacts"
    shutil.copytree(original, root)
    bundle = ui.load_artifacts(root)
    retriever = bundle.get("retrieval.customer").value
    calibration = pd.DataFrame(bundle.get("data.customer.calibration").value)
    lock_review(retriever, calibration, artifacts=root, decision="pending_review")
    sentinel = tmp_path / "decisions.sqlite3"
    sentinel.write_bytes(b"unrelated runtime preserved")
    REPRODUCE(customer, it, root)
    assert (root / "review/retrieval-test-opened.json").exists()
    assert (root / "review/retrieval-test-template.csv").exists()
    assert sentinel.read_bytes() == b"unrelated runtime preserved"
    assert ui.load_artifacts(root).get("queue.customer").status == "ready"
    before = canonical_run(root)
    REPRODUCE(customer, it, root)
    assert canonical_run(root) == before


@pytest.mark.parametrize("kind", ["missing", "corrupt", "schema", "traversal", "symlink"])
def test_invalid_it_artifact_isolated_before_deserialization(prepared, tmp_path, monkeypatch, kind):
    import shutil
    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    entry = manifest["artifacts"]["models.it"]
    path = root / entry["path"]
    if kind == "missing":
        path.unlink()
    elif kind == "corrupt":
        path.write_bytes(b"invalid")
    elif kind == "schema":
        entry["schema_version"] = 99
    elif kind == "traversal":
        entry["path"] = "../outside.joblib"
    else:
        outside = tmp_path / "outside.joblib"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
    atomic_json(manifest, root / "manifest.json")
    loaded, original_load = [], joblib.load
    forbidden = entry["sha256"]
    def spy(path):
        loaded.append(hashlib.sha256(path.getvalue()).hexdigest())
        return original_load(path)
    monkeypatch.setattr(joblib, "load", spy)
    bundle = ui.load_artifacts(root)
    assert bundle.get("models.it").status != "ready"
    assert forbidden not in loaded
    assert bundle.get("analytics.operational_summary").status == "ready"
    assert bundle.get("models.customer").status == "ready"
    assert bundle.get("models.it").correction == "make reproduce"


def fixture_bundle(prepared, *, priority="Low", text=None):
    """A synthetic perfect classifier is adversarial fixture only, never a real artifact."""
    bundle = ui.load_artifacts(prepared[0])
    policy = lock_policy(replace(base_policy("customer", "fixture"), automation_enabled=True,
                                  threshold=0.5, disabled_reason=None))
    probabilities = {label: float(label == "Technical issue") for label in CUSTOMER_TAXONOMY}
    prediction = Prediction("customer", "ok", "Technical issue", 1.0, probabilities,
                            "fixture", False)
    model = SimpleNamespace(predict_one=lambda _: prediction)
    retriever = bundle.get("retrieval.customer").value
    if text is None:
        text = next(row["text"] for row in retriever.records
                    if row["text"].startswith("technical "))
    retrieval = RetrievalPolicy(True, 0.2, "fixture", "fixture", "a" * 64,
                                 "enabled", retriever.index_version)
    states = dict(bundle.features)
    for key, value in {
        "queue.customer": [{"ticket_id": "customer:fixture-a", "text": text,
                            "priority": priority},
                           {"ticket_id": "customer:fixture-b", "text": text,
                            "priority": priority}],
        "models.customer": SimpleNamespace(model=model),
        "policies.customer": asdict(policy), "retrieval.policy": asdict(retrieval),
    }.items():
        states[key] = ui.FeatureState("ready", value, "fixture-only")
    return replace(bundle, features=states)


def app_for(bundle, runtime, monkeypatch):
    monkeypatch.setenv("SUPPORT_COPILOT_RUNTIME", str(runtime))
    monkeypatch.setattr(ui, "load_artifacts", lambda _: bundle)
    monkeypatch.setattr(socket, "create_connection", lambda *args, **kwargs: pytest.fail("network"))
    return AppTest.from_file(str(ROOT / "app.py")).run()


def button(app, label):
    return next(widget for widget in app.button if widget.label == label)


@pytest.mark.parametrize("label,action", [("Aprovar", "approve"),
    ("Editar e aprovar", "edit_approve"), ("Rejeitar", "reject"), ("Escalonar", "escalate")])
def test_four_actions_rerun_restart_export(prepared, tmp_path, monkeypatch, label, action):
    bundle = fixture_bundle(prepared)
    before = canonical_run(prepared[0])
    app = app_for(bundle, tmp_path, monkeypatch)
    assert not app.exception and app.title[0].value == "Fila diária"
    assert not button(app, "Aprovar").disabled
    submission_id = app.session_state["submission_id"]
    app.text_area[0].input("reset device then retry private@example.test")
    app.text_area[1].input("review requested")
    button(app, label).click().run()
    assert not app.exception and "audit_id=1" in app.success[0].value
    app.run()
    assert app.session_state["submission_id"] == submission_id
    with closing(sqlite3.connect(tmp_path / "decisions.sqlite3", isolation_level=None)) as conn:
        rows = list_decisions(conn)
    assert len(rows) == 1 and rows[0].human_action == action
    assert rows[0].ticket_id == "customer:fixture-a"
    if action == "edit_approve":
        assert "[EMAIL]" in rows[0].final_text and rows[0].edit_ratio > 0
    # Fresh app session sees the same real SQLite event and persists exact export bytes.
    fresh = AppTest.from_file(str(ROOT / "app.py")).run()
    fresh.switch_page("pages/evidence.py").run()
    button(fresh, "Persistir export CSV").click().run()
    assert not fresh.exception and fresh.download_button
    export = fresh.session_state["export"]
    assert export.content == export.path.read_bytes()
    exported = list(csv.DictReader(io.StringIO(export.content.decode())))
    assert exported[0]["id"] == "1" and exported[0]["submission_id"] == submission_id
    assert canonical_run(prepared[0]) == before


@pytest.mark.parametrize("changes", [{"priority": "Critical"},
                                    {"text": "technical device refund"},
                                    {"text": "technical device private@example.test"}])
def test_risk_precedes_perfect_confidence_in_pipeline_and_ui(prepared, tmp_path, monkeypatch,
                                                          changes):
    bundle = fixture_bundle(prepared, **changes)
    app = app_for(bundle, tmp_path, monkeypatch)
    assert not app.exception
    assert button(app, "Aprovar").disabled and button(app, "Editar e aprovar").disabled
    assert not button(app, "Escalonar").disabled
    row = bundle.get("queue.customer").value[0]
    assessed = ui.assess_ticket({**row, "domain": "customer", "Ticket Priority": row["priority"]},
                                bundle.get("models.customer").value.model,
                                ui._policy(bundle, "customer"),
                                bundle.get("retrieval.customer").value,
                                RetrievalPolicy(**bundle.get("retrieval.policy").value))
    assert assessed["route"]["action"] == "human_review"
    assert assessed["retrieval"]["draft"] is None
    if changes.get("priority") == "Critical":
        # An exact indexed description is the maximal cosine match, still never a draft.
        assert assessed["prediction"]["confidence"] == 1.0
        assert assessed["retrieval"]["sources"][0]["similarity"] == pytest.approx(1.0)
    if "@" in changes.get("text", ""):
        assert assessed["retrieval"]["sources"] == ()  # Privacy blocks querying altogether.


def test_ticket_change_and_failed_write_preserve_form(prepared, tmp_path, monkeypatch):
    bundle = fixture_bundle(prepared)
    app = app_for(bundle, tmp_path, monkeypatch)
    old_uuid = app.session_state["submission_id"]
    app.text_area[0].input("edited first ticket")
    app.run()
    app.selectbox[2].select("customer:fixture-b").run()
    assert app.text_area[0].value == "reset the device"
    assert app.session_state["submission_id"] != old_uuid
    new_uuid = app.session_state["submission_id"]
    app.text_area[0].input("edited second ticket")
    monkeypatch.setattr(ui, "persist_decision", lambda *_: (_ for _ in ()).throw(
        sqlite3.OperationalError("fixture failure")))
    button(app, "Editar e aprovar").click().run()
    assert app.error and not app.success
    assert app.text_area[0].value == "edited second ticket"
    assert app.session_state["submission_id"] == new_uuid


def test_missing_manifest_default_queue_and_separate_pages(prepared, tmp_path, monkeypatch):
    monkeypatch.setenv("SUPPORT_COPILOT_ARTIFACTS", str(tmp_path))
    monkeypatch.setenv("SUPPORT_COPILOT_RUNTIME", str(tmp_path / "runtime"))
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    assert not app.exception and app.title[0].value == "Fila diária"
    assert "make reproduce" in app.warning[0].value
    monkeypatch.setenv("SUPPORT_COPILOT_ARTIFACTS", str(prepared[0]))
    scorecard = app.switch_page("pages/scorecard.py").run()
    assert not scorecard.exception
    assert [x.value for x in scorecard.subheader] == [
        "Histórico observado", "Desempenho medido", "Cenários projetados"]
    lab = app.switch_page("pages/it_lab.py").run()
    lab.text_area[0].input("hardware device")
    button(lab, "Classificar IT").click().run()
    assert not lab.exception


def test_demo_has_no_install_download_or_training():
    import subprocess
    command = subprocess.check_output(["make", "-n", "demo"], cwd=ROOT, text=True)
    assert "pip install" not in command and "scripts/reproduce.py" not in command
    assert "curl -" not in command and "streamlit" in command


@pytest.mark.parametrize("field", ["lock_sha256", "configuration_sha256", "code_revision"])
def test_stale_environment_never_loads_binary(prepared, tmp_path, monkeypatch, field):
    import shutil
    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    manifest[field] = "changed"
    atomic_json(manifest, root / "manifest.json")
    monkeypatch.setattr(joblib, "load", lambda *_: pytest.fail("stale binary loaded"))
    bundle = ui.load_artifacts(root)
    assert bundle.get("models.customer").status == "stale"


def test_hash_check_is_shared_with_cli(prepared, tmp_path, monkeypatch):
    import shutil

    from support_copilot.retrieval import _artifact

    root = tmp_path / "artifacts"
    shutil.copytree(prepared[0], root)
    manifest = json.loads((root / "manifest.json").read_text())
    (root / manifest["artifacts"]["models.customer"]["path"]).write_bytes(b"corrupt")
    monkeypatch.setattr(joblib, "load", lambda *_: pytest.fail("corrupt binary loaded"))
    with pytest.raises(ValueError, match="hash_mismatch"):
        _artifact(root, manifest, "models.customer")


def test_unsupported_models_create_policies_without_binary(tmp_path):
    customer, it = sources(tmp_path / "source")
    # One sanitized representative per class: taxonomy remains valid, support is insufficient.
    for path, target in ((customer, "Ticket Type"), (it, "Topic_group")):
        pd.read_csv(path).groupby(target).head(1).to_csv(path, index=False)
    manifest = REPRODUCE(customer, it, tmp_path / "artifacts")
    for domain in ("customer", "it"):
        assert manifest["models"][domain]["status"] == "insufficient_support"
        assert manifest["artifacts"][f"models.{domain}"]["status"] == "unavailable"
        assert not (tmp_path / f"artifacts/models/{domain}.joblib").exists()
        assert (tmp_path / f"artifacts/models/{domain}-policy.json").exists()
    assert manifest["retrieval"]["eligible_queries"] == 0


def test_reject_requires_reason_and_readback_failure_never_confirms(prepared, tmp_path,
                                                                  monkeypatch):
    app = app_for(fixture_bundle(prepared), tmp_path, monkeypatch)
    button(app, "Rejeitar").click().run()
    assert app.error and not app.success
    monkeypatch.setattr(ui, "list_decisions", lambda _: [])
    button(app, "Aprovar").click().run()
    assert app.error and not app.success
    with closing(sqlite3.connect(tmp_path / "decisions.sqlite3", isolation_level=None)) as conn:
        assert len(list_decisions(conn)) == 1  # Commit exists; missing readback is NOT success.


def test_pipeline_sanitizer_checks_final_whitespace_normalized_form(tmp_path):
    from support_copilot.data import load_customer_tickets, sanitize_text

    # Synthetic reproduction of the real failure: joining lines must not create
    # a value accepted at ingestion and quarantined by the model's second check.
    with pytest.raises(ValueError, match="suspected_name"):
        sanitize_text("Technical\nIssue")
    assert sanitize_text(sanitize_text("reset\n the device")) == "reset the device"
    customer, _ = sources(tmp_path / "source")
    raw = pd.read_csv(customer, keep_default_na=False)
    raw.loc[0, "Ticket Description"] = "Technical\nIssue"
    raw.to_csv(customer, index=False)
    frame = load_customer_tickets(customer)
    assert frame.attrs["quality"]["excluded"]["privacy_quarantine"] == 1
    assert all(sanitize_text(text) == text for text in frame.text)
