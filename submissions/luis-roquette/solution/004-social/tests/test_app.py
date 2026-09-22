from __future__ import annotations

import os
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

from streamlit.testing.v1 import AppTest

from tests.helpers import csv_bytes, make_post


APP = Path(__file__).parents[1] / "app.py"


def valid_upload() -> bytes:
    rows: list[dict[str, object]] = []
    for period, start, interactions in (
        ("before", datetime(2025, 1, 1, 12), 4),
        ("current", datetime(2025, 1, 8, 12), 8),
    ):
        for index in range(30):
            rows.append(
                make_post(
                    id=f"{period}-{index}",
                    content_id=f"{period}-content-{index}",
                    creator_id=f"creator-{index % 5}",
                    post_date=(start + timedelta(days=index % 7)).isoformat(),
                    likes=interactions,
                    shares=0,
                    comments_count=0,
                )
            )
    return csv_bytes(rows)


def later_upload() -> bytes:
    start = datetime(2025, 1, 15, 12)
    return csv_bytes(
        [
            make_post(
                id=f"later-{index}",
                content_id=f"later-content-{index}",
                creator_id=f"creator-{index % 5}",
                post_date=(start + timedelta(days=index % 7)).isoformat(),
                likes=9,
                shares=0,
                comments_count=0,
            )
            for index in range(30)
        ]
    )


class AppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.previous = os.environ.get("SOCIAL_COCKPIT_DB_PATH")
        os.environ["SOCIAL_COCKPIT_DB_PATH"] = str(Path(self.directory.name) / "cockpit.sqlite3")

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("SOCIAL_COCKPIT_DB_PATH", None)
        else:
            os.environ["SOCIAL_COCKPIT_DB_PATH"] = self.previous
        self.directory.cleanup()

    def app(self) -> AppTest:
        return AppTest.from_file(str(APP), default_timeout=20).run()

    def test_initial_render_has_title_uploader_source_state_and_history(self) -> None:
        app = self.app()
        self.assertFalse(app.exception)
        self.assertIn("Cockpit de Social Media", app.title[0].value)
        self.assertEqual(app.file_uploader[0].label, "Enviar CSV")
        text = " ".join(item.value for item in (*app.markdown, *app.caption, *app.info))
        self.assertIn("Nenhuma fonte ativa", text)
        self.assertIn("Histórico de decisões", [item.value for item in app.subheader])

    def test_valid_then_invalid_upload_preserves_active_analysis(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        self.assertFalse(app.exception)
        active = next(item.value for item in app.caption if "Fonte ativa" in item.value)
        self.assertIn("60 linhas", active)
        self.assertGreaterEqual(len(app.metric), 3)
        self.assertEqual(len(app.download_button), 2)

        app.file_uploader[0].set_value(("invalid.csv", b"id\n1\n", "text/csv")).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Arquivo rejeitado" in item.value for item in app.error))
        self.assertTrue(any(item.value == active for item in app.caption))
        self.assertGreaterEqual(len(app.metric), 3)

    def test_priority_drilldown_and_decision_survive_new_session(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        labels = [item.label for item in app.number_input]
        self.assertEqual(labels, ["Impacto", "Força", "Atualidade"])
        self.assertTrue(any("Registros de origem" in item.label for item in app.expander))
        app.selectbox(key="decision_status").set_value("accepted")
        app.button(key="save_decision").click().run()
        self.assertTrue(any("Decisão registrada" in item.value for item in app.success))
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            baseline = json.loads(connection.execute("SELECT baseline_json FROM decisions").fetchone()[0])
        self.assertEqual(baseline["n_rate"], 30)
        self.assertEqual(baseline["creators"], 5)
        self.assertEqual(len(baseline["source_row_ids"]), 30)

        reopened = self.app()
        self.assertFalse(reopened.exception)
        self.assertTrue(any("accepted" in item.value for item in reopened.markdown))
        self.assertTrue(any("Reenvie o CSV" in item.value for item in reopened.caption))

    def test_empty_filter_has_explicit_state(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.multiselect(key="platform_filter").set_value([]).run()
        self.assertFalse(app.exception)
        self.assertTrue(any("Filtro vazio" in item.value for item in app.warning))

    def test_partial_period_label_and_posterior_observation(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.selectbox(key="period_mode").set_value("Semana ISO").run()
        self.assertTrue(any("cobertura parcial" in item.value for item in app.caption))
        app.selectbox(key="period_mode").set_value("Últimos 7 dias").run()
        app.button(key="save_decision").click().run()
        self.assertTrue(any("Decisão registrada" in item.value for item in app.success))

        app.file_uploader[0].set_value(("later.csv", later_upload(), "text/csv")).run()
        self.assertTrue(any(item.value == "Observação posterior" for item in app.subheader))
        app.button(key="save_outcome").click().run()
        self.assertTrue(
            any("Observação registrada: observed — comparable_execution_unknown" in item.value for item in app.success)
        )


if __name__ == "__main__":
    unittest.main()
