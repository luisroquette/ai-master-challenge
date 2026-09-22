from __future__ import annotations

import os
import atexit
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from streamlit.testing.v1 import AppTest
from streamlit.testing.v1.app_test import TMP_DIR

from tests.helpers import csv_bytes, make_post


APP = Path(__file__).parents[1] / "app.py"
# Streamlit owns this process-wide test directory; close it explicitly before
# Python's finalizer reports implicit cleanup under PYTHONWARNINGS=error.
atexit.register(TMP_DIR.cleanup)


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


def later_upload(start: datetime | None = None) -> bytes:
    start = start or datetime(2025, 1, 15, 12)
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

    def test_priority_renders_engine_evidence_before_source_references(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        text = "\n".join(item.value for item in app.markdown)
        for expected in (
            "Taxa-alvo ERv (%): `8.0`", "Volume-alvo — visualizações / interações: `3000` / `240`",
            "Benchmark — mediana ERv (%): `4.0`", "Benchmark — quartis Q1 / Q3 ERv (%): `4.0` / `4.0`",
            "Delta ERv (p.p.): `4.0`", "Amostra-alvo — posts elegíveis / creators: `30` / `5`",
            "Amostra do benchmark — posts elegíveis / creators: `30` / `5`",
            "Contexto solicitado:", "Contexto efetivo:", "Nível efetivo / fallback: mesmo contexto; período anterior de igual duração",
            "Suficiência: suficiente", "Força da evidência (C): `0.06`", "Referências de origem:",
        ):
            self.assertIn(expected, text)
        self.assertLess(text.index("Taxa-alvo"), text.index("Referências de origem"))
        contexts = [json.loads(item.value) for item in app.json]
        self.assertEqual(contexts[0], contexts[1])
        self.assertEqual(contexts[0]["platform"], "Instagram")

    def test_post_priority_discloses_fallback_and_benchmark_references(self) -> None:
        rows = [make_post(id=f"before-{i}", content_id=f"before-{i}", creator_id=f"creator-{i % 5}", post_date="2024-11-01T12:00:00", audience_location="US", likes=[2, 4, 6, 8, 10, 12][i % 6], shares=0, comments_count=0) for i in range(30)]
        rows.append(make_post(id="target", content_id="target", creator_id="new-creator", likes=30, shares=0, comments_count=0))
        app = self.app()
        app.file_uploader[0].set_value(("post.csv", csv_bytes(rows), "text/csv")).run()
        self.assertFalse(app.exception)
        text = "\n".join(item.value for item in app.markdown)
        for expected in ("Taxa-alvo ERv (%): `30.0`", "Benchmark — mediana ERv (%): `7.0`", "Benchmark — quartis Q1 / Q3 ERv (%): `4.0` / `10.0`", "Delta ERv (p.p.): `23.0`", "Amostra do benchmark — posts elegíveis / creators: `30` / `5`", "core+age+gender/365d"):
            self.assertIn(expected, text)
        contexts = [json.loads(item.value) for item in app.json]
        self.assertEqual(contexts[0]["audience_location"], "BR")
        self.assertNotIn("audience_location", contexts[1])
        self.assertIn("audience_location", contexts[2])
        self.assertEqual(len(app.dataframe[0].value), 31)

    def test_sponsorship_priority_labels_creator_medians_and_post_quartiles(self) -> None:
        rows = [make_post(id=f"{sponsored}-{i}", content_id=f"{sponsored}-{i}", creator_id=f"creator-{i % 5}", is_sponsored=sponsored, likes=8 if sponsored == "TRUE" else 4, shares=0, comments_count=0) for sponsored in ("TRUE", "FALSE") for i in range(30)]
        app = self.app()
        app.file_uploader[0].set_value(("sponsorship.csv", csv_bytes(rows), "text/csv")).run()
        self.assertFalse(app.exception)
        text = "\n".join(item.value for item in (*app.markdown, *app.caption))
        for expected in ("Taxa-alvo ERv (%): `8.0`", "Benchmark — mediana ERv (%): `4.0`", "Delta ERv (p.p.): `4.0`", "medianas das medianas por creator", "quartis descritivos dos posts orgânicos", "núcleo de patrocínio; audiência apenas nos filtros"):
            self.assertIn(expected, text)

    def test_revision_and_original_survive_new_session_without_csv(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.button(key="save_decision").click().run()
        reopened = self.app()
        reopened.selectbox(key="revision_status").set_value("edited")
        reopened.text_area(key="revision_text").set_value("Testar somente um vídeo.")
        reopened.button(key="save_revision").click().run()
        self.assertTrue(any("Revisão registrada" in item.value for item in reopened.success))
        final = self.app()
        self.assertFalse(final.exception)
        with closing(sqlite3.connect(Path(self.directory.name) / "cockpit.sqlite3")) as connection:
            rows = connection.execute("SELECT decision_id, revision_of, status, baseline_json FROM decisions ORDER BY decided_at").fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1][1], rows[0][0])
        self.assertEqual([row[2] for row in rows], ["accepted", "edited"])
        self.assertEqual(rows[0][3], rows[1][3])
        self.assertTrue(any(rows[0][0] in item.value and "Revisão da decisão" in item.value for item in final.caption))
        self.assertTrue(any("Testar somente um vídeo." in item.value for item in final.markdown))

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
        self.assertEqual([item.value for item in app.number_input], [0.0, 0.0, 0.0])
        app.selectbox(key="execution_status").set_value("yes")
        app.date_input(key="execution_date").set_value(date(2025, 1, 14))
        app.button(key="save_outcome").click().run()
        self.assertTrue(
            any("Observação registrada: pending — execution_before_decision" in item.value for item in app.success)
        )
        reopened = self.app()
        self.assertFalse(reopened.exception)
        text = "\n".join(item.value for item in (*reopened.markdown, *reopened.caption))
        for expected in ("Observação pending", "execution_before_decision", "Execução declarada: yes", "2025-01-14", "Janela observada: 2025-01-15 a 2025-01-21", "mediana baseline / observada / delta (p.p.): `8.0` / `9.0` / `1.0`", "Visualizações por dia — baseline / observada:", "Observação não causal"):
            self.assertIn(expected, text)
        self.assertIn("428.57142857142856", text)

    def test_valid_observation_survives_reopen(self) -> None:
        app = self.app()
        app.file_uploader[0].set_value(("social.csv", valid_upload(), "text/csv")).run()
        app.button(key="save_decision").click().run()
        now = datetime.now(timezone.utc)
        synthetic_start = (now + timedelta(days=1)).replace(tzinfo=None)
        app.file_uploader[0].set_value(("synthetic-future.csv", later_upload(synthetic_start), "text/csv")).run()
        app.selectbox(key="execution_status").set_value("yes")
        app.date_input(key="execution_date").set_value(now.date())
        app.button(key="save_outcome").click().run()
        self.assertTrue(any("Observação registrada: observed — comparable_after_declared_execution" in item.value for item in app.success))
        reopened = self.app()
        self.assertFalse(reopened.exception)
        text = "\n".join(item.value for item in (*reopened.markdown, *reopened.caption))
        for expected in ("Observação observed", "comparable_after_declared_execution", synthetic_start.date().isoformat(), "mediana baseline / observada / delta", "Visualizações por dia", "Observação não causal"):
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
