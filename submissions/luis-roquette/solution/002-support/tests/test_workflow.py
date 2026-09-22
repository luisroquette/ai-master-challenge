import json
import runpy
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).parents[1]
PROOF = runpy.run_path(ROOT / "app.py")
persist_export = PROOF["persist_export"]
read_synthetic_decision = PROOF["read_synthetic_decision"]
record_synthetic_decision = PROOF["record_synthetic_decision"]


def test_package_imports() -> None:
    import support_copilot

    assert support_copilot.__version__ == "0.1.0"


def test_streamlit_form_persists_edited_response_and_exposes_download(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("SUPPORT_COPILOT_RUNTIME", str(tmp_path))
    app = AppTest.from_file(ROOT / "app.py").run()

    assert not app.exception
    assert app.title[0].value == "Prova mínima do ambiente"

    app.text_area[0].input("Resposta sintética editada")
    app.button[0].click().run()

    assert not app.exception
    assert app.success[0].value == "Prova sintética persistida: id=1"
    assert len(app.download_button) == 1
    assert read_synthetic_decision(tmp_path / "environment-proof.sqlite3", 1) == (
        1,
        "Resposta sintética editada",
        1,
    )

    app.switch_page("pages/limits.py").run()
    assert not app.exception
    assert app.title[0].value == "Limites da prova"


def test_fresh_connection_and_download_match_persisted_file(tmp_path: Path) -> None:
    database = tmp_path / "proof.sqlite3"
    destination = tmp_path / "proof.csv"
    decision_id = record_synthetic_decision(database, "Conteúdo sintético editado")

    assert read_synthetic_decision(database, decision_id) == (
        decision_id,
        "Conteúdo sintético editado",
        1,
    )

    downloaded = persist_export(database, destination)
    assert downloaded == destination.read_bytes()
    assert b"Conte\xc3\xbado sint\xc3\xa9tico editado" in downloaded


def test_diagnostic_scorecard_smoke(tmp_path: Path, monkeypatch) -> None:
    analytics = tmp_path / "analytics"
    analytics.mkdir()
    summary = {
        "schema_version": 1,
        "evidence_kind": "historical_observed",
        "analysis_scope": "sanitized_customer_train_plus_calibration_representatives",
        "data_version": "fixture-v1",
        "source_rows": 100,
        "sanitized_rows": 80,
        "representative_rows": 60,
        "development_rows": 48,
        "valid_intervals": 40,
        "interval_exclusions": {
            "not_closed": 2, "missing": 2, "invalid_timestamp": 2, "negative": 2
        },
        "median_post_response_hours": 1.5,
        "observed_excess_hours": 3.0,
        "supported_waste_groups": 1,
        "satisfaction_status": "no_reliable_signal",
        "satisfaction_sample": 4,
        "limitations": ["fixture"],
    }
    satisfaction = {
        "status": "no_reliable_signal", "valid_ratings": 4, "missing_ratings": 44,
        "baseline_mae": 1.0, "ridge_mae": 1.0,
    }
    (analytics / "operational-summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (analytics / "satisfaction-model.json").write_text(
        json.dumps(satisfaction), encoding="utf-8"
    )
    monkeypatch.setenv("SUPPORT_COPILOT_ARTIFACTS", str(tmp_path))
    app = AppTest.from_file(ROOT / "app.py").run()

    assert not app.exception
    assert app.header[0].value == "Diagnóstico operacional"
    assert [subheader.value for subheader in app.subheader] == [
        "Histórico observado", "Desempenho medido", "Cenários projetados"
    ]
    assert "Fila, modelos, gate, recuperação e auditoria" in app.info[-1].value
