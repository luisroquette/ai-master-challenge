import tomllib
from dataclasses import replace
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from ravenstack_churn.publish import publish_artifacts

SOLUTION_ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_has_three_decision_views(generated_artifacts, monkeypatch) -> None:
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app = AppTest.from_file(SOLUTION_ROOT / "app.py").run(timeout=20)
    assert not app.exception
    assert [tab.label for tab in app.tabs] == [
        "Decisão executiva",
        "Evidências",
        "Fila operacional",
    ]
    assert len(app.get("download_button")) == 1


def test_queue_filter_and_download_match_canonical_artifact(
    generated_artifacts, monkeypatch
) -> None:
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app = AppTest.from_file(SOLUTION_ROOT / "app.py").run(timeout=20)
    selected = app.selectbox(key="finding_filter").select("F-support-escalation").run()
    canonical = pd.read_csv(generated_artifacts / "account_queue.csv")
    expected = canonical.query("finding_id == 'F-support-escalation'")
    assert selected.dataframe[0].value["Conta"].tolist() == expected["account_id"].tolist()
    assert len(selected.download_button) == 1


def test_dashboard_runs_from_repository_root(generated_artifacts, monkeypatch) -> None:
    repo_root = next(
        parent
        for parent in Path(__file__).resolve().parents
        if (parent / "CONTRIBUTING.md").exists()
    )
    monkeypatch.chdir(repo_root)
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app_path = repo_root / "submissions/luis-roquette/solution/001-churn/app.py"
    app = AppTest.from_file(app_path).run(timeout=20)
    assert not app.exception


def test_chronology_filter_changes_the_selected_reading(generated_artifacts, monkeypatch) -> None:
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(generated_artifacts))
    app = AppTest.from_file(SOLUTION_ROOT / "app.py").run(timeout=20)
    observed = app.selectbox(key="chronology_filter").select("observed").run()
    assert not observed.exception
    assert any("observada" in caption.value.lower() for caption in observed.caption)


def test_cloud_requirements_match_runtime_dependencies() -> None:
    project = tomllib.loads((SOLUTION_ROOT / "pyproject.toml").read_text())
    expected = set(project["project"]["dependencies"])
    actual = {
        line for line in (SOLUTION_ROOT / "requirements.txt").read_text().splitlines() if line
    }
    assert actual == expected


def test_empty_queue_uses_bounded_validation_watchlist(
    analysis_result, tmp_path, monkeypatch
) -> None:
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
    )
    publish_artifacts(result, tmp_path)
    monkeypatch.setenv("RAVENSTACK_ARTIFACT_DIR", str(tmp_path))
    app = AppTest.from_file(SOLUTION_ROOT / "app.py").run(timeout=20)
    assert not app.exception
    assert len(app.slider) == 1
    assert app.slider[0].label == "Até a posição"
    assert len(app.warning) == 1
