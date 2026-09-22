from __future__ import annotations

import csv
import unittest

import pandas as pd

from analysis import analyze, derive_metrics, follower_band, load_csv
from tests.helpers import (
    aggregate_effect_rows,
    alert_for_target,
    concentrated_reference,
    csv_bytes,
    default_scope,
    frame_from_rows,
    frame_with_target,
    make_cohort,
    make_post,
    sponsorship_frequency_rows,
    sponsorship_rows,
)


class CsvBoundaryTests(unittest.TestCase):
    def test_load_csv_accepts_valid_single_platform_subset(self):
        frame, errors = load_csv(csv_bytes([make_post(platform="Instagram")]))
        self.assertEqual(errors, [])
        self.assertEqual(frame["platform"].unique().tolist(), ["Instagram"])

    def test_load_csv_reports_missing_required_column_without_partial_frame(self):
        row = make_post()
        del row["views"]
        frame, errors = load_csv(csv_bytes([row]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "views")

    def test_load_csv_reports_negative_nonfinite_and_duplicate_identity(self):
        invalid = [
            make_post(id="1", content_id="a", views=-1),
            make_post(id="1", content_id="b", views="NaN"),
        ]
        frame, errors = load_csv(csv_bytes(invalid))
        self.assertIsNone(frame)
        self.assertEqual({error["column"] for error in errors}, {"id", "views"})

    def test_load_csv_accepts_zero_metrics_and_utf8_bom(self):
        raw = b"\xef\xbb\xbf" + csv_bytes(
            [make_post(views=0, likes=0, shares=0, comments_count=0)]
        )
        frame, errors = load_csv(raw)
        self.assertEqual(errors, [])
        self.assertEqual(int(frame.iloc[0]["views"]), 0)

    def test_load_csv_rejects_over_fifty_mib_before_parse(self):
        frame, errors = load_csv(b"x" * (50 * 1024 * 1024 + 1))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["problem"], "file_too_large")

    def test_load_csv_accepts_large_optional_text_and_restores_field_limit(self):
        original_limit = csv.field_size_limit()
        csv.field_size_limit(131_072)
        try:
            raw = csv_bytes([make_post(comments_text="x" * 140_000)])
            frame, errors = load_csv(raw)
            self.assertEqual(errors, [])
            self.assertIsNotNone(frame)
            self.assertEqual(len(frame.iloc[0]["comments_text"]), 140_000)
            self.assertEqual(csv.field_size_limit(), 131_072)
        finally:
            csv.field_size_limit(original_limit)

    def test_load_csv_rejects_mixed_timezone_semantics(self):
        raw = csv_bytes(
            [
                make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00"),
                make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00Z"),
            ]
        )
        frame, errors = load_csv(raw)
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["column"], "post_date")

    def test_load_csv_rejects_nat_and_incompatible_timezone_offsets(self):
        cases = (
            [make_post(post_date="NaT")],
            [
                make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00+00:00"),
                make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00-03:00"),
            ],
        )
        for rows in cases:
            with self.subTest(rows=rows):
                frame, errors = load_csv(csv_bytes(rows))
                self.assertIsNone(frame)
                self.assertTrue(any(error["column"] == "post_date" for error in errors))

    def test_load_csv_returns_diagnostic_for_integer_outside_int64(self):
        frame, errors = load_csv(csv_bytes([make_post(views=2**63)]))
        self.assertIsNone(frame)
        self.assertEqual(errors[0]["row"], 2)
        self.assertEqual(errors[0]["column"], "views")
        self.assertEqual(errors[0]["problem"], "integer_out_of_range")

    def test_load_csv_accepts_one_explicit_offset_with_datetime_dtype(self):
        raw = csv_bytes([
            make_post(id="1", content_id="a", post_date="2025-01-01T00:00:00+02:00"),
            make_post(id="2", content_id="b", post_date="2025-01-02T00:00:00+02:00"),
        ])
        frame, errors = load_csv(raw)
        self.assertEqual(errors, [])
        self.assertTrue(str(frame["post_date"].dtype).startswith("datetime64"))
        explicit_scope = {
            "target_start": "2025-01-01",
            "target_end": "2025-01-02",
            "reference_date": "2025-01-02",
            "filters": {},
        }
        result = analyze(frame, explicit_scope, str(frame.iloc[0]["source_hash"]))
        self.assertEqual(result["source"]["rows"], 2)
        self.assertTrue(str(result["scope"]["target_start"]).endswith("+02:00"))

    def test_load_csv_diagnostics_use_physical_line_after_multiline_field(self):
        raw = csv_bytes([
            make_post(id="1", content_id="a", content_description="linha 1\nlinha 2"),
            make_post(id="2", content_id="b", content_description="simples", views=-1, post_date="invalid"),
        ])
        frame, errors = load_csv(raw)
        self.assertIsNone(frame)
        locations = {(error["column"], error["row"]) for error in errors}
        self.assertIn(("views", 4), locations)
        self.assertIn(("post_date", 4), locations)

    def test_load_csv_rejects_empty_malformed_and_duplicate_headers(self):
        for raw in (b"", b'"unterminated', b"id,id,platform\n1,2,Instagram\n"):
            with self.subTest(raw=raw[:20]):
                frame, errors = load_csv(raw)
                self.assertIsNone(frame)
                self.assertTrue(errors)

    def test_metrics_use_views_denominator_and_preserve_undefined_rate(self):
        frame, _ = load_csv(
            csv_bytes(
                [
                    make_post(id="1", content_id="a", views=100, likes=5, shares=3, comments_count=2),
                    make_post(id="2", content_id="b", views=0, likes=0, shares=0, comments_count=0),
                ]
            )
        )
        result = derive_metrics(frame)
        self.assertEqual(int(result.iloc[0]["interactions"]), 10)
        self.assertEqual(float(result.iloc[0]["erv"]), 10.0)
        self.assertTrue(pd.isna(result.iloc[1]["erv"]))

    def test_int64_boundaries_do_not_wrap_derived_or_aggregate_metrics(self):
        maximum = 2**63 - 1
        frame, errors = load_csv(
            csv_bytes(
                [
                    make_post(
                        id=f"boundary-{index}",
                        content_id=f"boundary-content-{index}",
                        creator_id=f"boundary-creator-{index}",
                        views=maximum,
                        likes=maximum,
                        shares=1,
                        comments_count=0,
                        follower_count=maximum,
                    )
                    for index in range(2)
                ]
            )
        )
        self.assertEqual(errors, [])
        derived = derive_metrics(frame)
        self.assertEqual(int(derived.iloc[0]["interactions"]), maximum + 1)
        self.assertGreater(float(derived.iloc[0]["erv"]), 99.0)

        result = analyze(frame, default_scope(), str(frame.iloc[0]["source_hash"]))
        self.assertEqual(result["metrics"]["views"], 2 * maximum)
        self.assertEqual(result["metrics"]["interactions"], 2 * (maximum + 1))
        self.assertEqual(result["metrics"]["creator_exposure"], 2 * maximum)
        self.assertGreater(result["metrics"]["weighted_erv"], 99.0)
        platform = result["dimensions"]["platform"][0]
        self.assertEqual(platform["views"], 2 * maximum)
        self.assertEqual(platform["interactions"], 2 * (maximum + 1))
        self.assertEqual(platform["creator_exposure"], 2 * maximum)

    def test_follower_band_boundaries(self):
        values = [0, 9_999, 10_000, 49_999, 50_000, 99_999, 100_000, 499_999, 500_000]
        self.assertEqual(
            [follower_band(value) for value in values],
            ["0–9,999", "0–9,999", "10,000–49,999", "10,000–49,999", "50,000–99,999", "50,000–99,999", "100,000–499,999", "100,000–499,999", "500,000+"],
        )


class ContextEvidenceTests(unittest.TestCase):
    def test_analysis_exposes_auditable_required_dimensions(self):
        frame = frame_from_rows([
            make_post(id="a", content_id="a", platform="Instagram", content_type="video"),
            make_post(id="b", content_id="b", platform="TikTok", content_type="image"),
        ])
        result = analyze(frame, default_scope(target_start="2025-01-15", target_end="2025-01-15"), str(frame.iloc[0]["source_hash"]))
        self.assertEqual(set(result["dimensions"]), {"platform", "content_type", "content_category", "creator_band", "audience_age", "audience_gender", "audience_location", "month"})
        self.assertTrue(all(item["evidence_id"] and item["source_row_ids"] for items in result["dimensions"].values() for item in items))

    def test_post_alert_uses_post_distribution_not_creator_medians(self):
        frame = make_cohort(erv_values=[2, 4, 6, 8, 10, 12] * 5)
        ordinary = analyze(frame_with_target(frame, 8), default_scope(), "hash")
        extreme = analyze(frame_with_target(frame, 20), default_scope(), "hash")
        self.assertFalse(alert_for_target(ordinary)["is_outlier"])
        self.assertTrue(alert_for_target(extreme)["is_outlier"])

    def test_benchmark_fallback_and_sufficiency(self):
        base = make_cohort(5, 6, [4], audience_location="US")
        target = frame_with_target(base, 8, audience_location="BR")
        alert = alert_for_target(analyze(target, default_scope(), "hash"))
        self.assertIn("audience_location", alert["benchmark"]["removed_controls"])
        for key in ("platform", "content_type", "content_category", "follower_band", "is_sponsored"):
            self.assertEqual(alert["benchmark"]["effective_context"][key], alert["context"][key])
        for frame in (make_cohort(4, 10), make_cohort(5, 5)):
            self.assertEqual(analyze(frame, default_scope(target_start="2024-12-01", target_end="2024-12-31"), "hash")["alerts"], [])

    def test_target_creator_is_excluded_and_constant_iqr_is_not_strong(self):
        base = make_cohort(6, 6, [4])
        excluded_refs = set(base.loc[base["creator_id"] == "creator-0", "source_row_id"])
        target = frame_with_target(base, 20, creator_id="creator-0")
        result = analyze(target, default_scope(), "hash")
        alert = alert_for_target(result)
        self.assertTrue(excluded_refs.isdisjoint(alert["benchmark"]["source_row_ids"]))
        self.assertEqual(alert["benchmark"]["iqr"], 0)
        self.assertNotEqual(alert["strength_label"], "strong")

    def test_sponsorship_is_stratified_and_reports_uncovered_groups(self):
        result = analyze(
            sponsorship_rows(),
            default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31"),
            "hash",
        )
        self.assertEqual(len(result["sponsorship"]["strata"]), 1)
        self.assertGreater(len(result["sponsorship"]["uncovered_strata"]), 0)
        self.assertLess(result["sponsorship"]["coverage"], 1.0)
        self.assertEqual(result["sponsorship"]["period_granularity"], "calendar_month")
        self.assertEqual(result["sponsorship"]["strata"][0]["context"]["period_month"], "2025-01")
        self.assertEqual(result["sponsorship"]["strata"][0]["delta_erv_pp"], 4.0)

    def test_sponsorship_requires_both_arms_in_the_same_month(self):
        organic = make_cohort(5, 6, [4], sponsored=False, start="2025-01-01T12:00:00")
        sponsored = make_cohort(5, 6, [14], sponsored=True, start="2025-02-01T12:00:00")
        organic.loc[:, "post_date"] = pd.Timestamp("2025-01-05T12:00:00")
        sponsored.loc[:, "post_date"] = pd.Timestamp("2025-02-05T12:00:00")
        frame = pd.concat([organic, sponsored], ignore_index=True)
        frame["id"] = [f"temporal-{index}" for index in range(len(frame))]
        frame["content_id"] = [f"temporal-content-{index}" for index in range(len(frame))]
        frame["source_row_id"] = [f"hash:temporal-{index}" for index in range(len(frame))]

        result = analyze(
            frame,
            default_scope(target_start="2025-01-01", target_end="2025-02-28", reference_date="2025-02-28"),
            "hash",
        )
        sponsorship = result["sponsorship"]
        self.assertEqual(sponsorship["eligible_strata"], 0)
        self.assertEqual(sponsorship["coverage"], 0.0)
        self.assertEqual(sponsorship["uncovered_count"], 2)
        self.assertEqual(
            {(item["period_month"], item["organic_posts"], item["sponsored_posts"]) for item in sponsorship["uncovered_strata"]},
            {("2025-01", 30, 0), ("2025-02", 0, 30)},
        )

    def test_sponsorship_recency_uses_sponsored_target_group_median_date(self):
        frame = sponsorship_rows()
        sponsored_target = frame["is_sponsored"] & frame["content_type"].eq("video")
        frame.loc[:, "post_date"] = pd.Timestamp("2025-01-01T12:00:00")
        frame.loc[sponsored_target, "post_date"] = pd.Timestamp("2025-01-31T12:00:00")
        result = analyze(
            frame,
            default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31"),
            "hash",
        )
        evidence = result["sponsorship"]["strata"][0]
        recommendation = next(
            item for item in result["recommendations"]
            if item["evidence_id"] == evidence["evidence_id"]
        )
        self.assertEqual(pd.Timestamp(evidence["representative_date"]), pd.Timestamp("2025-01-31T12:00:00"))
        self.assertEqual(pd.Timestamp(recommendation["representative_date"]), pd.Timestamp("2025-01-31T12:00:00"))
        self.assertEqual(recommendation["priority_components"]["recency"], 1.0)

    def test_aggregate_normalization_includes_large_ineligible_nonempty_group(self):
        scope = default_scope(target_start="2025-01-01", target_end="2025-01-31", reference_date="2025-01-31")
        baseline_frame = sponsorship_rows()
        baseline = analyze(baseline_frame, scope, "hash")
        evidence_id = baseline["sponsorship"]["strata"][0]["evidence_id"]
        baseline_item = next(item for item in baseline["recommendations"] if item["evidence_id"] == evidence_id)

        large_group = frame_from_rows([
            make_post(
                id=f"large-{index}",
                content_id=f"large-content-{index}",
                creator_id=f"large-creator-{index}",
                content_type="text",
                post_date="2025-01-31T12:00:00",
                views=1_000_000,
                likes=100_000,
                shares=0,
                comments_count=0,
                follower_count=1_000_000,
                is_sponsored="TRUE",
            )
            for index in range(10)
        ])
        augmented = analyze(pd.concat([baseline_frame, large_group], ignore_index=True), scope, "hash")
        augmented_item = next(item for item in augmented["recommendations"] if item["evidence_id"] == evidence_id)

        self.assertGreater(augmented_item["normalization"]["views"], baseline_item["normalization"]["views"])
        self.assertLess(augmented_item["priority"], baseline_item["priority"])
        self.assertFalse(any(item["context"]["content_type"] == "text" for item in augmented["recommendations"]))

    def test_frequency_hypothesis_uses_creator_weeks_from_two_complete_iso_weeks(self):
        result = analyze(
            sponsorship_frequency_rows(2),
            default_scope(target_start="2025-01-06", target_end="2025-01-19", reference_date="2025-01-19"),
            "hash",
        )
        frequency = result["recommendations"][0]["frequency_hypothesis"]
        self.assertEqual(frequency["status"], "test")
        self.assertEqual(frequency["value"], 3.0)
        self.assertEqual(frequency["unit"], "posts_per_creator_per_complete_iso_week")
        self.assertEqual(frequency["sample_creator_weeks"], 10)
        self.assertEqual(frequency["observed_complete_weeks"], 2)
        self.assertEqual(frequency["window_start"], "2025-01-06T00:00:00")
        self.assertEqual(frequency["window_end"], "2025-01-19T00:00:00")

    def test_frequency_hypothesis_collects_before_suggesting_one_week_cadence(self):
        result = analyze(
            sponsorship_frequency_rows(1),
            default_scope(target_start="2025-01-06", target_end="2025-01-12", reference_date="2025-01-12"),
            "hash",
        )
        frequency = result["recommendations"][0]["frequency_hypothesis"]
        self.assertEqual(frequency["status"], "collect")
        self.assertIsNone(frequency["value"])
        self.assertEqual(frequency["observed_complete_weeks"], 1)
        self.assertEqual(frequency["action_type"], "collect_two_complete_weeks")

    def test_priority_is_reproducible_and_exposes_components(self):
        reference = make_cohort(20, 5, [2, 4, 6, 8, 10])
        frame = frame_with_target(reference, 30)
        first = analyze(frame, default_scope(), "hash")["recommendations"]
        second = analyze(frame, default_scope(), "hash")["recommendations"]
        self.assertEqual(first, second)
        self.assertEqual(set(first[0]["priority_components"]), {"impact", "strength", "recency"})
        self.assertEqual(first[0]["action_type"], "test")

    def test_strength_formula_penalizes_creator_concentration(self):
        balanced = analyze(frame_with_target(make_cohort(20, 5), 20), default_scope(), "hash")
        concentrated = analyze(frame_with_target(concentrated_reference(), 20), default_scope(), "hash")
        balanced_strength = alert_for_target(balanced)["strength"]
        concentrated_strength = alert_for_target(concentrated)["strength"]
        self.assertAlmostEqual(balanced_strength, 0.95)
        self.assertAlmostEqual(concentrated_strength, 0.05)
        self.assertGreater(balanced_strength, concentrated_strength)

    def test_aggregate_recommendation_exists_without_post_outlier(self):
        result = analyze(
            aggregate_effect_rows(),
            default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14"),
            "hash",
        )
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["recommendations"][0]["evidence_type"], "aggregate")
        self.assertEqual(result["recommendations"][0]["action_type"], "test")
        self.assertEqual(result["recommendations"][0]["supporting_topics"], ["audience", "creator", "frequency", "quick_win"])

    def test_strong_aligned_and_conflicting_editorial_signals_map_to_actions(self):
        scope = default_scope(target_start="2025-01-08", target_end="2025-01-14", reference_date="2025-01-14")
        positive = analyze(aggregate_effect_rows(creators=20), scope, "hash")
        negative = analyze(
            aggregate_effect_rows(creators=20, current_interactions=2), scope, "hash"
        )
        conflicting = analyze(
            aggregate_effect_rows(creators=20, current_views=50, current_interactions=3),
            scope,
            "hash",
        )
        self.assertEqual(positive["recommendations"][0]["action_type"], "scale_test")
        self.assertEqual(negative["recommendations"][0]["action_type"], "review_stop")
        self.assertEqual(conflicting["recommendations"][0]["action_type"], "test")
        allowed_topics = {"effort", "audience", "frequency", "sponsorship", "creator", "stop", "quick_win"}
        for result in (positive, negative, conflicting):
            self.assertTrue(all(item["topic"] in allowed_topics for item in result["recommendations"]))
            self.assertTrue(all(item["evidence_id"] for item in result["recommendations"]))


if __name__ == "__main__":
    unittest.main()
