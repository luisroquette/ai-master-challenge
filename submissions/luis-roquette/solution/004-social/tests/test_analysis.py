from __future__ import annotations

import unittest

import pandas as pd

from analysis import analyze, derive_metrics, follower_band, load_csv
from tests.helpers import (
    alert_for_target,
    csv_bytes,
    default_scope,
    frame_with_target,
    make_cohort,
    make_post,
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

    def test_follower_band_boundaries(self):
        values = [0, 9_999, 10_000, 49_999, 50_000, 99_999, 100_000, 499_999, 500_000]
        self.assertEqual(
            [follower_band(value) for value in values],
            ["0–9,999", "0–9,999", "10,000–49,999", "10,000–49,999", "50,000–99,999", "50,000–99,999", "100,000–499,999", "100,000–499,999", "500,000+"],
        )


class ContextEvidenceTests(unittest.TestCase):
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
        for frame in (make_cohort(4, 10), make_cohort(5, 5)):
            self.assertEqual(analyze(frame, default_scope(target_start="2024-12-01", target_end="2024-12-31"), "hash")["alerts"], [])

    def test_target_creator_is_excluded_and_constant_iqr_is_not_strong(self):
        base = make_cohort(6, 6, [4])
        same_creator = base.iloc[[0]].copy()
        same_creator["id"] = "same"
        same_creator["content_id"] = "same"
        same_creator["source_row_id"] = "hash:same"
        same_creator["post_date"] = pd.Timestamp("2024-12-20")
        target = frame_with_target(pd.concat([base, same_creator], ignore_index=True), 20, creator_id="creator-0")
        result = analyze(target, default_scope(), "hash")
        alert = alert_for_target(result)
        self.assertNotIn("hash:same", alert["benchmark"]["source_row_ids"])
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
        self.assertEqual(result["sponsorship"]["strata"][0]["delta_erv_pp"], 4.0)

    def test_priority_is_reproducible_and_exposes_components(self):
        reference = make_cohort(20, 5, [2, 4, 6, 8, 10])
        frame = frame_with_target(reference, 30)
        first = analyze(frame, default_scope(), "hash")["recommendations"]
        second = analyze(frame, default_scope(), "hash")["recommendations"]
        self.assertEqual(first, second)
        self.assertEqual(set(first[0]["priority_components"]), {"impact", "strength", "recency"})
        self.assertEqual(first[0]["action_type"], "test")


if __name__ == "__main__":
    unittest.main()
