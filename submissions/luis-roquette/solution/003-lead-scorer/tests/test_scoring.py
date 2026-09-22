"""Fixed-policy temporal evidence tests. Real final labels are consumed once here.

Synthetic decision tables exercise policy without choosing it from real outcomes.
Later SDD steps extend this file with active scoring/explanation tests.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scoring as s


def history_fixture(n=1000):
    rows = []
    for i in range(n):
        won = i % 10 == 0 or i % 10 >= 6
        rows.append(dict(opportunity_id=f"{i:05}", deal_stage="Won" if won else "Lost",
            close_date=date(2020, 1, 1)+timedelta(days=i//10), engage_date=date(2019, 1, 1),
            close_value=float(100+i%7) if won else 0., financial_eligible=True,
            eligible_history=True, eligible_active=False, sales_agent=f"seller-{i%3}",
            manager=f"manager-{i%2}", regional_office=f"region-{i%2}",
            product="low" if i%10 < 5 else "high", series="base", sales_price=100.,
            account=f"account-{i%3}", account_match="both", product_match="both",
            seller_match="both", year_established=1990+i%3, route="full"))
    return rows


def period_fixture():
    return tuple(s.PeriodEvidence(name, tuple(f"{name}-{i}" for i in range(n)), n//2,
        n-n//2, n, ()) for name, n in (("train", 200), ("calibration", 100), ("test", 100)))


def evaluation_fixture(candidate="logistic", route="full", status="passed", **kwargs):
    periods = period_fixture()
    default = dict(evaluation_id=f"fixture-{candidate}-{route}", candidate=candidate, route=route,
        status=status, config_fingerprint=s.DEFAULT_CONFIG.fingerprint, split_fingerprint="fixture-split",
        feature_fingerprint="fixture-features", feature_names=("product_low",), periods=periods,
        train_boundary="2020-01-01", calibration_boundary="2020-02-01", baseline_rate=.5,
        brier=.15, log_loss=.4, baseline_brier=.25, baseline_log_loss=.69,
        bands=(s.BandEvidence("baixa", 50, .2, .2, True, ()),
               s.BandEvidence("media", 0, None, None, False, ("empty_band",)),
               s.BandEvidence("alta", 50, .8, .8, True, ())),
        top_k=(s.TopKMetric(.1, 10, .5, .3, None), s.TopKMetric(.2, 20, .5, .5, None)),
        segments=(), reasons=() if status == "passed" else ("fixture_rejection",),
        unavailable_reasons=(), natural_missing_account_count=0, financial_valid_count=100)
    default.update(kwargs)
    return s.CandidateEvaluation(**default)


def score_fixture(state="calibrated", stage="Engaging", **kwargs):
    """Concrete C3 fixture for independent UI development; never runtime defaults."""
    base = dict(opportunity_id="fixture-001", stage=stage, sales_agent="Vendedor",
        manager="Gestora", regional_office="Sul", product="Produto", account="Conta",
        state=state, potential_revenue=100., fingerprint="fixture-only",
        diagnostics=(), next_action="Sem ação recomendada com os dados atuais")
    if state == "calibrated":
        base.update(route="full", origin="logistic", band="alta", band_kind="probability",
            probability=.8, expected_revenue=80., evaluation_id="fixture-logistic-full",
            observed_n=50, effective_support=50., evidence_strength="moderada",
            explanation_scale="calibrated_log_odds", base_value=0.,
            factors=(s.Factor("product", "Produto", math.log(4), "favoravel", "Referência", True),))
    elif state == "relative":
        base.update(route="prospecting" if stage == "Prospecting" else "fallback",
            origin="historical_evidence", band="media", band_kind="relative", relative_index=.5,
            observed_n=25, prior_strength=20., effective_support=45., evidence_strength="fraca",
            explanation_scale="relative_index", base_value=.5)
    else:
        base.update(diagnostics=(s.diagnostic("unknown_product", "Produto não encontrado",
            "Corrija product no cadastro", field="product", opportunity_id="fixture-001", scope="row"),))
    base.update(kwargs)
    return s.ScoreResult(**base)


def bundle_fixture(scores=None):
    evaluations = tuple(evaluation_fixture(candidate, route) for candidate in ("logistic", "boosting")
        for route in ("full", "fallback"))
    return s.ScoringBundle("fixture-only", s.DEFAULT_CONFIG.version, evaluations,
        tuple(s.select_route(evaluations, route) for route in ("full", "fallback")),
        tuple(scores) if scores is not None else (score_fixture(opportunity_id="fixture-calibrated"),
            score_fixture("relative", "Prospecting", opportunity_id="fixture-prospecting"),
            score_fixture("insufficient_data", opportunity_id="fixture-insufficient")),
        (), {"revision": None, "source_digest": "fixture-only"})


class ContractTests(unittest.TestCase):
    def test_TC13_config_provenance_immutable_and_digest_sensitive(self):
        config = s.DEFAULT_CONFIG
        with self.assertRaises(FrozenInstanceError):
            config.seed = 1
        self.assertNotEqual(config.fingerprint, replace(config, seed=43).fingerprint)
        self.assertEqual(set(s.FEATURE_PROVENANCE), set(config.full_features))
        for name, inputs in s.FEATURE_PROVENANCE.items():
            self.assertEqual(inputs, (name,))
        for field in ("close_value", "close_date", "deal_stage", "sales_agent", "manager",
                      "regional_office", "sales_price", "close_value_log", "days_to_close"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "provenance"):
                replace(config, full_features=config.full_features+(field,))

    def test_TC12_TC16_mutating_forbidden_fields_cannot_change_feature_vectors(self):
        row = history_fixture(1)[0]
        mutation = dict(row, deal_stage="Engaging", close_value=9999999, close_date=date(2099,1,1),
            sales_agent="Other", manager="Other", regional_office="Other", sales_price=1000000,
            days_to_close=9999, close_value_log=22, account="Other")
        for route in ("full", "fallback"):
            self.assertEqual(s.feature_record(row, route), s.feature_record(mutation, route))
        mutation["year_established"] = None
        self.assertEqual(s.feature_record(row, "fallback"), s.feature_record(mutation, "fallback"))

    def test_C3_variants_serialize_without_unvalidated_probability_keys(self):
        for state, stage in (("calibrated", "Engaging"), ("relative", "Engaging"),
                             ("relative", "Prospecting"), ("insufficient_data", "Engaging")):
            with self.subTest(state=state, stage=stage):
                result = score_fixture(state, stage)
                encoded = json.loads(json.dumps(result.to_dict(), allow_nan=False))
                self.assertEqual("probability" in encoded, state == "calibrated")
                self.assertEqual("expected_revenue" in encoded, state == "calibrated")
                self.assertEqual("relative_index" in encoded, state == "relative")
                with self.assertRaises(FrozenInstanceError):
                    result.state = "relative"
        self.assertEqual(len(bundle_fixture().to_dict()["candidate_evaluations"]), 4)
        self.assertEqual(len({row.opportunity_id for row in bundle_fixture().scores}), 3)
        with self.assertRaises(ValueError):
            replace(bundle_fixture(), candidate_evaluations=())
        with self.assertRaises(ValueError):
            score_fixture("calibrated", "Prospecting")
        with self.assertRaises(ValueError):
            score_fixture("relative", probability=.5)
        with self.assertRaises(ValueError):
            score_fixture("insufficient_data", relative_index=.3)

    def test_C3_phase_boundary_does_not_publish_placeholder_active_scores(self):
        with self.assertRaisesRegex(NotImplementedError, "03a"):
            s.build_scoring_bundle(object())

    def test_TC43_probability_bounds_and_invalid_values(self):
        for value in (0., 1e-12, 1-1e-12, 1.):
            with self.subTest(valid=value):
                s.validate_probabilities((value,))
                self.assertEqual(score_fixture(probability=value, expected_revenue=value*100).probability, value)
        for value in (-1e-12, 1+1e-12, float("nan"), float("inf"), None):
            with self.subTest(invalid=value), self.assertRaises(ValueError):
                score_fixture(probability=value, expected_revenue=0.)
        self.assertTrue(all(math.isfinite(value) for value in s.probability_losses((0,1), (1.,0.))))
        with self.assertRaises(ValueError):
            s.probability_losses((1,), (1+1e-12,))


class TemporalTests(unittest.TestCase):
    def test_TC08_closed_membership_disjoint_tied_dates(self):
        rows = history_fixture()
        active = dict(rows[0], opportunity_id="active", deal_stage="Engaging", eligible_history=True)
        invalid = dict(rows[0], opportunity_id="invalid", eligible_history=False)
        split = s.split_closed_history(rows+[active, invalid])
        ids = [set(row["opportunity_id"] for row in period) for period in (split.train, split.calibration, split.test)]
        self.assertEqual([len(part) for part in ids], [600,200,200])
        self.assertFalse(ids[0] & ids[1] or ids[1] & ids[2] or ids[0] & ids[2])
        self.assertEqual(set.union(*ids), {row["opportunity_id"] for row in rows})
        self.assertEqual(split.train_boundary, date(2020,2,29))
        self.assertEqual(split.calibration_boundary, date(2020,3,20))
        self.assertEqual(split.fingerprint, s.split_closed_history(list(reversed(rows))).fingerprint)

    def test_TC09_cutoff_boundary_neighbors(self):
        split = s.split_closed_history(history_fixture())
        membership = {row["close_date"]: name for name in ("train", "calibration", "test") for row in getattr(split, name)}
        for cutoff, expected in ((split.train_boundary, ("train", "train", "calibration")),
                                 (split.calibration_boundary, ("calibration", "calibration", "test"))):
            for delta, name in zip((-1,0,1), expected):
                with self.subTest(cutoff=cutoff, delta=delta):
                    self.assertEqual(membership[cutoff+timedelta(days=delta)], name)
        # One oversized date group cannot be divided merely to obtain 60/20/20.
        rows = history_fixture(100)
        for i, row in enumerate(rows):
            row["close_date"] = date(2020,1,1)+timedelta(days=0 if i<85 else 1 if i<95 else 2)
        tied = s.split_closed_history(rows)
        self.assertEqual(tuple(map(len, (tied.train,tied.calibration,tied.test))), (85,10,5))

    def test_TC10_empty_periods_and_single_class_diagnostics(self):
        for rows in ([], history_fixture(10), history_fixture(20)):
            with self.subTest(count=len(rows)), self.assertRaisesRegex(s.ScoringValidationError, "insufficient_temporal_periods"):
                s.split_closed_history(rows)
        rows = history_fixture()
        for row in rows:
            row["deal_stage"] = "Won"
        split = s.split_closed_history(rows)
        fitted = s.fit_candidate(split, "logistic", "full")
        self.assertIsNone(fitted.pipeline)
        evaluation = s.evaluate_candidate(fitted, split)
        self.assertEqual(evaluation.status, "rejected")
        self.assertIn("training_requires_both_classes", evaluation.reasons)
        self.assertIsNone(evaluation.brier)
        rows = history_fixture()
        for row in rows[600:800]:
            row["deal_stage"] = "Won"
        split = s.split_closed_history(rows)
        fitted = s.fit_candidate(split, "logistic", "fallback")
        self.assertIsNotNone(fitted.pipeline)
        self.assertIsNone(fitted.calibrated)
        self.assertIn("calibration_requires_both_classes", s.evaluate_candidate(fitted, split).reasons)

    def test_TC11_train_frozen_support_exact_exclusions_and_feature_names(self):
        rows = history_fixture()
        rows[610]["product"] = "never-trained"
        rows[620]["series"] = "never-trained"
        rows[810]["year_established"] = 2000
        rows[820]["account_match"] = "left_only"
        split = s.split_closed_history(rows)
        full = s.fit_candidate(split, "logistic", "full")
        fallback = s.fit_candidate(split, "logistic", "fallback")
        excluded_cal = dict(full.evidence[1].excluded)
        self.assertIn("unseen_product", excluded_cal["00610"])
        self.assertIn("unseen_series", excluded_cal["00620"])
        self.assertEqual(dict(full.evidence[2].excluded)["00810"], ("year_outside_training_support",))
        self.assertEqual(dict(full.evidence[2].excluded)["00820"], ("unsupported_account_year",))
        self.assertEqual(fallback.evidence[2].count, 200)
        self.assertEqual(full.evidence[2].count, 198)
        self.assertEqual(full.support.year_max, 1992)
        scaler = full.pipeline.named_steps["preprocessor"].named_transformers_["numeric"]
        self.assertAlmostEqual(scaler.mean_[0], 1991.)
        for fitted in (full, fallback):
            for name in fitted.feature_names:
                self.assertTrue(name.startswith(("categorical__product_", "categorical__series_", "numeric__year_established")))
            self.assertNotIn("never-trained", " ".join(fitted.feature_names))
            self.assertEqual(sum(period.count+len(period.excluded) for period in fitted.evidence), len(rows))
        self.assertFalse(any("year" in name for name in fallback.feature_names))

    def test_TC17_calibration_fit_consumes_only_intermediate_ids(self):
        from sklearn.pipeline import Pipeline
        from sklearn.calibration import CalibratedClassifierCV
        pipeline_fit, calibrated_fit = Pipeline.fit, CalibratedClassifierCV.fit
        seen = {"train": [], "calibration": []}
        def record_train(model, frame, labels, **kwargs):
            seen["train"].append(tuple(frame.index))
            return pipeline_fit(model, frame, labels, **kwargs)
        def record_calibration(model, frame, labels, **kwargs):
            seen["calibration"].append(tuple(frame.index))
            return calibrated_fit(model, frame, labels, **kwargs)
        split = s.split_closed_history(history_fixture())
        with patch.object(Pipeline, "fit", record_train), patch.object(CalibratedClassifierCV, "fit", record_calibration):
            fitted = s.fit_candidate(split, "logistic", "fallback")
        self.assertEqual(seen["train"], [fitted.evidence[0].ids])
        self.assertEqual(seen["calibration"], [fitted.evidence[1].ids])
        coefficients = fitted.pipeline.named_steps["estimator"].coef_.copy()
        evaluated = s.evaluate_candidate(fitted, split)
        self.assertEqual(evaluated.test_ids, fitted.evidence[2].ids)
        self.assertTrue((coefficients == fitted.pipeline.named_steps["estimator"].coef_).all())
        with self.assertRaisesRegex(ValueError, "Policy changed"):
            s.evaluate_candidate(fitted, split, replace(s.DEFAULT_CONFIG, seed=99))

    def test_controlled_convergence_failure_distinct_from_rejection(self):
        from sklearn.exceptions import ConvergenceWarning
        split = s.split_closed_history(history_fixture())
        with patch("sklearn.pipeline.Pipeline.fit", side_effect=ConvergenceWarning("fixture nonconvergence")):
            fitted = s.fit_candidate(split, "logistic", "full")
        result = s.evaluate_candidate(fitted, split)
        self.assertEqual(result.status, "failed")
        self.assertIsNone(result.brier)
        self.assertIn("fit_failed:ConvergenceWarning", " ".join(result.reasons))

    def test_TC43_invalid_estimator_probability_fails_without_clipping(self):
        import numpy as np
        split = s.split_closed_history(history_fixture())
        fitted = s.fit_candidate(split, "logistic", "fallback")
        probabilities = np.tile([-.1, 1.1], (len(split.test), 1))
        with patch.object(fitted.calibrated, "predict_proba", return_value=probabilities):
            result = s.evaluate_candidate(fitted, split)
        self.assertEqual(result.status, "failed")
        self.assertIsNone(result.brier)
        self.assertFalse(result.bands)
        self.assertIn("invalid_probability", " ".join(result.reasons))


class PublicationPolicyTests(unittest.TestCase):
    def test_TC18_probability_publication_decision_table(self):
        periods, bands = period_fixture(), evaluation_fixture().bands
        for name, brier, loss, selected_bands, allowed in (
            ("all_pass", .15, .4, bands, True),
            ("brier_equal", .25, .4, bands, False),
            ("loss_equal", .15, .69, bands, False),
            ("one_band", .15, .4, bands[:1], False),
            ("bad_populated", .15, .4, (replace(bands[0], supported=False), bands[2]), False),
            ("nonmonotonic", .15, .4, (replace(bands[0], observed_rate=.9), bands[2]), False)):
            with self.subTest(name=name):
                self.assertEqual(not s.publication_reasons(periods, brier, loss, .25, .69, selected_bands), allowed)

    def test_TC19_loss_equality_strict_epsilon_boundaries(self):
        periods, bands = period_fixture(), evaluation_fixture().bands
        epsilon = s.DEFAULT_CONFIG.comparison_epsilon
        for metric in ("brier", "log_loss"):
            for difference in (-2*epsilon, 0., epsilon/2, 2*epsilon):
                with self.subTest(metric=metric, baseline_difference=difference):
                    brier, loss = (.25-difference, .4) if metric == "brier" else (.15, .69-difference)
                    reasons = s.publication_reasons(periods, brier, loss, .25, .69, bands)
                    self.assertEqual(f"{metric}_not_strictly_better" not in reasons, difference > epsilon)

    def test_TC20_band_edges_support_and_coherence_boundaries(self):
        for cutoff, lower, upper in ((.4,"baixa","media"),(.7,"media","alta")):
            for delta, expected in ((-1e-12,lower),(0.,upper),(1e-12,upper)):
                with self.subTest(cutoff=cutoff, delta=delta):
                    self.assertEqual(s.probability_band(cutoff+delta), expected)
        for n in (29,30,31):
            evidence = s.band_evidence([0]*n,[.1]*n)[0]
            self.assertEqual(evidence.supported, n >= 30)
        for delta in (-1e-12,0.,1e-12):
            evidence = s.band_evidence([0]*30,[.1+delta]*30)[0]
            self.assertEqual(evidence.supported, delta <= 0)
        periods, bands = period_fixture(), evaluation_fixture().bands
        for index, minimum in ((0,200),(1,100),(2,100)):
            for n in (minimum-1,minimum,minimum+1):
                changed = list(periods)
                changed[index] = replace(changed[index], ids=tuple(str(i) for i in range(n)), wins=n//2, losses=n-n//2)
                reasons = s.publication_reasons(changed,.15,.4,.25,.69,bands)
                self.assertEqual(f"{changed[index].period}_support_below_{minimum}" in reasons, n < minimum)
        for n in (19,20,21):
            changed = tuple(replace(item, wins=n, losses=item.count-n) for item in periods)
            reasons = s.publication_reasons(changed,.15,.4,.25,.69,bands)
            self.assertEqual(any("class_support" in reason for reason in reasons), n < 20)

    def test_TC21_candidate_selection_fixed_rule_cohorts_and_failures(self):
        logistic = evaluation_fixture()
        boosting = evaluation_fixture("boosting", brier=.14, log_loss=.39,
            top_k=(s.TopKMetric(.1,10,.6,.4,None),s.TopKMetric(.2,20,.6,.6,None)))
        self.assertEqual(s.select_route((logistic,boosting),"full").candidate,"boosting")
        for name, changed in (
            ("precision_equal",replace(boosting,top_k=(replace(boosting.top_k[0],precision=.5),boosting.top_k[1]))),
            ("share_equal",replace(boosting,top_k=(boosting.top_k[0],replace(boosting.top_k[1],realized_value_share=.5)))),
            ("loss_worse",replace(boosting,log_loss=.41)),
            ("rejected",replace(boosting,status="rejected")),
            ("failed",replace(boosting,status="failed")),
            ("financial_missing",replace(boosting,top_k=(replace(boosting.top_k[0],realized_value_share=None,financial_unavailable_reason="missing"),boosting.top_k[1]))),
            ("other_cohort",replace(boosting,periods=boosting.periods[:2]+(replace(boosting.periods[2],ids=("other",)+boosting.test_ids[1:]),))),
            ("other_k",replace(boosting,top_k=(replace(boosting.top_k[0],k=11),boosting.top_k[1])))):
            with self.subTest(name=name):
                self.assertEqual(s.select_route((logistic,changed),"full").candidate,"logistic")
        self.assertIsNone(s.select_route((replace(logistic,status="rejected"),replace(boosting,status="failed")),"full").candidate)
        self.assertEqual(s.select_route((replace(logistic,status="rejected"),boosting),"full").candidate,"boosting")

    def test_TC21_top_k_band_then_expected_catalog_revenue_financial_validity(self):
        rows = history_fixture(10)
        for row in rows:
            row["deal_stage"] = "Lost"
            row["close_value"] = 0.
        rows[0].update(deal_stage="Won",close_value=50.,sales_price=1.)
        rows[1].update(deal_stage="Won",close_value=50.,sales_price=10000.)
        probabilities = (.8,.6)+(.1,)*8
        top = s.ranking_metrics(rows,probabilities)
        self.assertEqual((top[0].k,top[0].precision,top[0].realized_value_share),(1,1.,.5))
        self.assertEqual((top[1].k,top[1].realized_value_share),(2,1.))
        rows[5]["financial_eligible"] = False
        self.assertTrue(all(item.realized_value_share is None and item.financial_unavailable_reason == "incomplete_financial_labels"
            for item in s.ranking_metrics(rows,probabilities)))
        for row in rows:
            row.update(close_value=0.,financial_eligible=True)
        self.assertEqual(s.ranking_metrics(rows,probabilities)[0].financial_unavailable_reason,"no_positive_realized_total")


class ZRealDataEvaluationTests(unittest.TestCase):
    def test_TC14_real_four_routes_frozen_policy_and_complete_evidence(self):
        import data
        # Freeze/check the dependency and policy identities before final-set access.
        self.assertEqual(hashlib.sha256((ROOT/"requirements.txt").read_bytes()).hexdigest(), s.DEFAULT_CONFIG.dependency_digest)
        frozen = s.DEFAULT_CONFIG.fingerprint
        print("FROZEN_POLICY", frozen, "DEPENDENCIES", s.DEFAULT_CONFIG.dependency_digest, flush=True)
        dataset = data.load_dataset(data.read_snapshot(ROOT/"data/raw", ROOT/"data/manifest.json"))
        split, fitted, evaluations, selections = s.evaluate_history(dataset.opportunities)
        self.assertEqual(s.DEFAULT_CONFIG.fingerprint,frozen)
        self.assertEqual({(item.candidate,item.route) for item in evaluations},
            {(candidate,route) for candidate in ("logistic","boosting") for route in ("full","fallback")})
        self.assertTrue(all(item.status in ("passed","rejected","failed") for item in evaluations))
        self.assertTrue(all(item.status != "failed" for item in evaluations), [(item.candidate,item.route,item.reasons) for item in evaluations])
        self.assertEqual(len(selections),2)
        for item, model in zip(evaluations,fitted):
            self.assertEqual(item.split_fingerprint,split.fingerprint)
            self.assertEqual(item.config_fingerprint,frozen)
            self.assertEqual(item.periods,model.evidence)
            self.assertEqual(item.natural_missing_account_count,0)
            self.assertTrue(item.limitations)
            self.assertIsNotNone(item.brier)
            self.assertIsNotNone(item.baseline_brier)
            self.assertEqual(len(item.bands),3)
            self.assertEqual(len(item.top_k),2)
            self.assertTrue(item.segments)
            self.assertEqual(item.baseline_rate,item.periods[0].wins/item.periods[0].count)
            if item.status == "rejected":
                self.assertTrue(item.reasons)
        summaries = [dict(candidate=item.candidate, route=item.route, status=item.status,
            evaluation_id=item.evaluation_id, split_fingerprint=item.split_fingerprint,
            feature_fingerprint=item.feature_fingerprint, counts=[p.count for p in item.periods],
            exclusions=[len(p.excluded) for p in item.periods], brier=item.brier,
            log_loss=item.log_loss, baseline_brier=item.baseline_brier,
            baseline_log_loss=item.baseline_log_loss, bands=s.serialize(item.bands),
            top_k=s.serialize(item.top_k), reasons=item.reasons,
            natural_missing_account_count=item.natural_missing_account_count) for item in evaluations]
        print("REAL_EVALUATIONS",json.dumps(summaries,sort_keys=True,allow_nan=False),flush=True)
        print("REAL_SELECTIONS",json.dumps(s.serialize(selections),sort_keys=True),flush=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
