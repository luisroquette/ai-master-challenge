from pathlib import Path

from streamlit.testing.v1 import AppTest

from app import persist_export, read_synthetic_decision, record_synthetic_decision

ROOT = Path(__file__).parents[1]


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
    assert len(app.get("page_link")) == 2

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
