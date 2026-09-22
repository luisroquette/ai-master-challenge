"""Fixture-first tests for the Streamlit portfolio and session contract."""
from dataclasses import replace
from datetime import datetime, timezone
import math
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scoring as s


def _periods():
    return tuple(s.PeriodEvidence(name, tuple(f"{name}-{i}" for i in range(n)), n // 2,
        n - n // 2, n, ()) for name, n in (("train", 200), ("calibration", 100), ("test", 100)))


def _evaluation(candidate, route):
    periods = _periods()
    return s.CandidateEvaluation(f"fixture-{candidate}-{route}", candidate, route, "passed",
        s.DEFAULT_CONFIG.fingerprint, "split", "features", ("product",), periods,
        "2020-01-01", "2020-02-01", .5, .15, .4, .25, .69,
        (s.BandEvidence("baixa", 50, .2, .2, True, ()),
         s.BandEvidence("media", 0, None, None, False, ("empty_band",)),
         s.BandEvidence("alta", 50, .8, .8, True, ())),
        (s.TopKMetric(.1, 10, .5, .3, None), s.TopKMetric(.2, 20, .5, .5, None)),
        (), (), (), 0, 100)


def _score(oid, stage, seller="Ana", manager="Mara", region="Sul", state="calibrated", **changes):
    base = dict(opportunity_id=oid, stage=stage, sales_agent=seller, manager=manager,
        regional_office=region, product=f"Produto {oid}", account="Conta", state=state,
        potential_revenue=100., fingerprint="fixture", diagnostics=(),
        next_action="Validar a necessidade antes do próximo passo")
    if state == "calibrated":
        base.update(route="full", origin="logistic", band="alta", band_kind="probability",
            probability=.8, expected_revenue=80., evaluation_id="fixture-logistic-full",
            observed_n=50, effective_support=50., evidence_strength="moderada",
            explanation_scale="calibrated_log_odds", base_value=0., factors=(
                s.Factor("product", base["product"], math.log(4), "favoravel", "Referência", True),
                s.Factor("series", "S1", -.2, "desfavoravel", "Referência", True)))
    elif state == "relative":
        base.update(route="prospecting" if stage == "Prospecting" else "fallback",
            origin="historical_evidence", band="media", band_kind="relative", relative_index=.52,
            observed_n=25, prior_strength=20., effective_support=45., evidence_strength="fraca",
            explanation_scale="relative_index", base_value=.5)
    else:
        base.update(diagnostics=(s.diagnostic("unknown_product", "Produto não encontrado",
            "Corrija product no cadastro", field="product", opportunity_id=oid, scope="row"),))
    base.update(changes)
    return s.ScoreResult(**base)


def bundle_fixture(fingerprint="fixture"):
    evaluations = tuple(_evaluation(candidate, route) for candidate in ("logistic", "boosting")
                        for route in ("full", "fallback"))
    scores = (
        _score("E-A", "Engaging"),
        _score("E-A2", "Engaging", state="relative"),
        _score("P-A", "Prospecting", state="relative"),
        _score("P-BAD", "Prospecting", state="insufficient_data"),
        _score("E-B", "Engaging", seller="Beto", region="Norte", probability=.7, expected_revenue=70.),
        _score("E-C", "Engaging", seller="Caio", manager="Nina", region="Leste"),
        _score("UNASSIGNED", "Engaging", seller=None, manager=None, region=None,
               state="insufficient_data"),
    )
    return s.ScoringBundle(fingerprint, s.DEFAULT_CONFIG.version, evaluations,
        tuple(s.select_route(evaluations, route) for route in ("full", "fallback")), scores, (),
        {"revision": "fixture-revision", "source_digest": "fixture-source"})


class PortfolioContractTests(unittest.TestCase):
    def setUp(self):
        import app
        self.app = app
        self.bundle = bundle_fixture()

    def test_TC33_TC34_seller_stage_sections_and_unsupported_visibility(self):
        rows = self.app.portfolio_rows(self.bundle, "Vendedor", "Ana")
        self.assertEqual({row.opportunity_id for row in rows}, {"E-A", "E-A2", "P-A", "P-BAD"})
        sections = self.app.stage_sections(rows, "Prospecting", None)
        self.assertEqual([row.opportunity_id for row in sections["relative"]], ["P-A"])
        self.assertEqual([row.opportunity_id for row in sections["insufficient_data"]], ["P-BAD"])
        bad = self.app.detail_view(sections["insufficient_data"][0])
        self.assertEqual(bad["Estado"], "Dados insuficientes")
        self.assertIn("Corrija product", bad["Correção"])
        self.assertNotIn("Probabilidade", bad)
        self.assertNotIn("Receita esperada", bad)

    def test_TC33_unassigned_rows_stay_in_quality_view_without_a_portfolio_owner(self):
        unassigned = next(row for row in self.bundle.scores if row.opportunity_id == "UNASSIGNED")
        for role, identity in (("Vendedor", "Ana"), ("Gestor", "Mara")):
            self.assertNotIn(unassigned, self.app.portfolio_rows(self.bundle, role, identity))
        self.assertEqual(self.app.detail_view(unassigned)["Estado"], "Dados insuficientes")

    def test_TC35_manager_filters_exact_membership_and_score_invariance(self):
        team = self.app.portfolio_rows(self.bundle, "Gestor", "Mara")
        south = self.app.portfolio_rows(self.bundle, "Gestor", "Mara", "Sul", "Todos da equipe")
        beto = self.app.portfolio_rows(self.bundle, "Gestor", "Mara", "Todas as regiões", "Beto")
        self.assertEqual({r.opportunity_id for r in team}, {"E-A", "E-A2", "P-A", "P-BAD", "E-B"})
        self.assertEqual({r.opportunity_id for r in south}, {"E-A", "E-A2", "P-A", "P-BAD"})
        self.assertEqual([r.opportunity_id for r in beto], ["E-B"])
        original = {r.opportunity_id: r.to_dict() for r in self.bundle.scores}
        self.assertEqual(original, {r.opportunity_id: r.to_dict() for r in self.bundle.scores})

    def test_TC36_details_factors_origin_support_action_and_no_stale_selection(self):
        detail = self.app.detail_view(next(r for r in self.bundle.scores if r.opportunity_id == "E-A"))
        self.assertEqual(detail["Origem"], "logistic")
        self.assertEqual(detail["Evidência"], "moderada")
        self.assertEqual(len(detail["Fatores favoráveis"]), 1)
        self.assertEqual(len(detail["Fatores desfavoráveis"]), 1)
        self.assertIn("Validar", detail["Próxima ação"])
        state = {}
        self.app.ensure_session(state, "fixture")
        state["selection_by_stage"]["Engaging"] = {"context": "old", "id": "E-A"}
        self.assertIsNone(self.app.resolve_selection(state, "Engaging", "new", ["E-B"], []))
        self.assertNotIn("Engaging", state["selection_by_stage"])

    def test_TC37_TC38_manager_only_pin_preserves_score_and_attribution(self):
        state = {}
        self.app.ensure_session(state, "fixture")
        before = next(r for r in self.bundle.scores if r.opportunity_id == "E-B").to_dict()
        now = datetime(2026, 9, 22, 15, 30, tzinfo=timezone.utc)
        with self.assertRaises(PermissionError):
            self.app.set_temporary_priority(state, "Vendedor", "Engaging", "E-B", "Mara", {"E-B"}, "fixture", now)
        pin = self.app.set_temporary_priority(state, "Gestor", "Engaging", "E-B", "Mara", {"E-B"}, "fixture", now)
        sections = self.app.stage_sections(self.app.portfolio_rows(self.bundle, "Gestor", "Mara"), "Engaging", pin)
        self.assertEqual([r.opportunity_id for r in sections["pinned"]], ["E-B"])
        self.assertEqual(pin.manager, "Mara")
        self.assertEqual(pin.created_at_utc, now)
        self.assertEqual(before, next(r for r in self.bundle.scores if r.opportunity_id == "E-B").to_dict())

    def test_TC39_pin_lifetime_filter_retention_and_resets(self):
        state = {}
        self.app.ensure_session(state, "fixture")
        self.app.set_temporary_priority(state, "Gestor", "Engaging", "E-B", "Mara", {"E-B"}, "fixture")
        self.assertIn("Engaging", state["pins_by_stage"])
        self.assertEqual(self.app.visible_pin(state, "Engaging", {"E-A"}), None)
        self.assertIn("Engaging", state["pins_by_stage"])
        self.app.recalculate(state)
        self.assertEqual(state["pins_by_stage"], {})
        self.assertEqual(state["calculation_generation"], 1)
        self.app.ensure_session(state, "changed")
        self.assertEqual(state["pins_by_stage"], {})
        self.assertEqual(state["calculation_generation"], 0)

    def test_TC40_cache_identity_changes_for_data_config_and_source(self):
        from data import Snapshot
        one = Snapshot((("x.csv", b"one"),), "{}", "deps")
        two = Snapshot((("x.csv", b"two"),), "{}", "deps")
        identity = {"revision": None, "source_digest": "source-a"}
        self.assertNotEqual(self.app.bundle_cache_key(one, s.DEFAULT_CONFIG, identity),
                            self.app.bundle_cache_key(two, s.DEFAULT_CONFIG, identity))
        self.assertNotEqual(self.app.bundle_cache_key(one, s.DEFAULT_CONFIG, identity),
                            self.app.bundle_cache_key(one, replace(s.DEFAULT_CONFIG, seed=43), identity))
        self.assertNotEqual(self.app.bundle_cache_key(one, s.DEFAULT_CONFIG, identity),
                            self.app.bundle_cache_key(one, s.DEFAULT_CONFIG,
                                                      {"revision": None, "source_digest": "source-b"}))

    def test_TC41_cached_bundle_reuses_training_for_same_identity(self):
        from data import Snapshot
        snapshot = Snapshot((("x.csv", b"one"),), "{}", "deps")
        self.app._cached_bundle.clear()
        with patch.object(self.app, "load_dataset", return_value=object()), \
             patch.object(self.app, "build_scoring_bundle", return_value=self.bundle) as build, \
             patch.object(self.app, "source_identity", return_value={"revision": None, "source_digest": "source"}):
            first = self.app.cached_bundle(snapshot, s.DEFAULT_CONFIG)
            second = self.app.cached_bundle(snapshot, s.DEFAULT_CONFIG)
        self.assertIs(first, second)
        self.assertEqual(build.call_count, 1)


class StreamlitFixtureTests(unittest.TestCase):
    def fixture_app(self):
        from streamlit.testing.v1 import AppTest
        tests = Path(__file__).parent
        return AppTest.from_string(f"""\
import sys
sys.path.insert(0, {str(tests)!r})
import streamlit as st
from app import render_portfolio
from test_app import bundle_fixture
render_portfolio(bundle_fixture(), st.session_state)
""").run(timeout=20)

    def test_TC33_TC34_fixture_app_renders_two_tabs_and_suppresses_failed_values(self):
        at = self.fixture_app()
        self.assertFalse(at.exception)
        self.assertEqual([tab.label for tab in at.tabs], ["Engaging", "Prospecting"])
        insufficient = next(frame.value for frame in at.dataframe
                            if "P-BAD" in frame.value["ID"].tolist())
        self.assertIn("Dados insuficientes", insufficient["Faixa"].tolist())
        self.assertNotIn("Probabilidade", insufficient.columns)
        self.assertNotIn("Receita esperada (valor catálogo)", insufficient.columns)

    def test_TC35_TC37_TC38_TC39_apptest_manager_filter_pin_and_reset(self):
        at = self.fixture_app()
        at.selectbox[2].set_value("E-A").run()
        self.assertFalse(any(button.label == "Prioridade temporária do gestor" for button in at.button))
        at.selectbox[0].set_value("Gestor").run()
        at.selectbox[2].set_value("Norte").run()
        at.selectbox[3].set_value("Beto").run()
        at.selectbox[4].set_value("E-B").run()
        pin = next(button for button in at.button if button.label == "Prioridade temporária do gestor")
        pin.click().run()
        pinned = next(frame.value for frame in at.dataframe if "Gestor" in frame.value.columns)
        self.assertEqual(pinned.loc[0, "ID"], "E-B")
        self.assertEqual(pinned.loc[0, "Probabilidade"], .7)
        next(button for button in at.button if button.label == "Recalcular prioridades").click().run()
        self.assertFalse(any("Gestor" in frame.value.columns for frame in at.dataframe))


class PlaywrightJourneyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.directory = tempfile.TemporaryDirectory()
        path = Path(cls.directory.name) / "fixture_app.py"
        path.write_text(f"""\
import sys
sys.path.insert(0, {str(Path(__file__).parent)!r})
import streamlit as st
from app import render_portfolio
from test_app import bundle_fixture
render_portfolio(bundle_fixture(), st.session_state)
""", encoding="utf-8")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            cls.port = probe.getsockname()[1]
        cls.server = subprocess.Popen((sys.executable, "-m", "streamlit", "run", str(path),
            "--server.headless=true", f"--server.port={cls.port}", "--browser.gatherUsageStats=false"),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 20
        while True:
            try:
                with urlopen(f"http://127.0.0.1:{cls.port}/_stcore/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Streamlit fixture não iniciou")
                time.sleep(.1)
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.terminate()
        try:
            cls.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.server.kill()
            cls.server.wait(timeout=5)
        cls.directory.cleanup()

    @staticmethod
    def choose(page, index, value):
        page.get_by_role("combobox").nth(index).click()
        page.get_by_role("option", name=value, exact=True).click()

    def test_TC34_TC35_TC36_TC37_TC38_TC39_rendered_journeys(self):
        seller_context = self.browser.new_context()
        seller = seller_context.new_page()
        seller.goto(f"http://127.0.0.1:{self.port}")
        seller.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        seller.get_by_role("tab", name="Prospecting").click()
        seller.get_by_text("Dados insuficientes", exact=True).first.wait_for()
        self.choose(seller, 3, "P-BAD")
        seller.get_by_text("Corrija product no cadastro", exact=False).wait_for()
        self.assertEqual(seller.get_by_role("button", name="Prioridade temporária do gestor").count(), 0)
        seller_context.close()

        manager_context = self.browser.new_context()
        manager = manager_context.new_page()
        manager.goto(f"http://127.0.0.1:{self.port}")
        manager.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for()
        self.choose(manager, 0, "Gestor")
        self.choose(manager, 2, "Norte")
        self.choose(manager, 3, "Beto")
        self.choose(manager, 4, "E-B")
        manager.get_by_text("Origem:", exact=False).wait_for()
        manager.get_by_role("button", name="Prioridade temporária do gestor").click()
        manager.get_by_text("Gestor Mara ·", exact=False).wait_for()
        manager.get_by_role("button", name="Recalcular prioridades").click()
        self.assertEqual(manager.get_by_text("Gestor Mara ·", exact=False).count(), 0)
        manager_context.close()


if __name__ == "__main__":
    unittest.main()
