from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from analysis import executive_summary, export_evidence, analysis_report, analyze, load_csv
from tests.helpers import csv_bytes, make_post, default_scope, sponsorship_frequency_rows


APP_ROOT = Path(__file__).resolve().parents[1]


def sample_result() -> dict[str, object]:
    return {
        "source": {"source_hash": "abc", "rows": 1, "period_start": "2025-01-01", "period_end": "2025-01-01", "platforms": ["Instagram"]},
        "scope": {"method_version": "1.0.0", "target_start": "2025-01-01", "target_end": "2025-01-01"},
        "metrics": {"posts": 1, "views": 100, "interactions": 10, "median_erv": 10.0},
        "dimensions": {"platform": [{"evidence_id": "dimension-1", "dimension": "platform", "value": "Instagram", "posts": 1, "views": 100, "interactions": 10, "median_erv": 10.0, "source_row_ids": ["abc:1"]}]},
        "alerts": [], "cohorts": {"editorial": []},
        "sponsorship": {"strata": [], "uncovered_strata": [], "coverage": 0.0, "required_financial_data": ["investment"]},
        "recommendations": [{"evidence_id": "dimension-1", "action": "Testar padrão", "owner": "Gestor", "execution_window": "7 dias", "review_window": "7 dias", "priority": 10.0}],
        "pending": [], "row_references": {"abc:1": 2},
    }


def result_with_texts(texts: list[str]) -> dict[str, object]:
    result = sample_result()
    result["dimensions"] = {"text": [{"evidence_id": f"text-{index}", "dimension": "text", "value": text, "posts": 1, "metric_value": 10.0, "source_row_ids": []} for index, text in enumerate(texts)]}
    return result


def parse_export(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8"))))


def sample_decisions() -> list[dict[str, object]]:
    return [{"decision_id": "d-1", "evidence_id": "dimension-1", "status": "accepted", "owner": "Gestor"}]


def run_cli(path: Path) -> tuple[int, tuple[bytes, ...]]:
    with tempfile.TemporaryDirectory() as directory:
        output_csv = Path(directory) / "evidence.csv"
        output_html = Path(directory) / "summary.html"
        output_report = Path(directory) / "analysis.md"
        completed = subprocess.run(
            [sys.executable, str(APP_ROOT / "analysis.py"), str(path), "--evidence", str(output_csv), "--summary", str(output_html), "--report", str(output_report)],
            capture_output=True,
            check=False,
        )
        return completed.returncode, tuple(output.read_bytes() if output.exists() else b"" for output in (output_csv, output_html, output_report))


class ExportTests(unittest.TestCase):
    def test_formula_prefix_after_whitespace_and_controls_preserves_original_text(self):
        unsafe = [prefix + marker + "1" for prefix in ("  ", "\n", " \t\r\n\x00\x7f\ufeff", "\u00a0") for marker in "=+-@"]
        safe = ["  texto", "\ntexto", "   ", ""]
        result = result_with_texts(unsafe + safe)
        rows = parse_export(export_evidence(result, [{"text": value} for value in unsafe + safe]))
        for record_type in ("evidence", "decision"):
            actual = [row["text"] for row in rows if row["record_type"] == record_type and (record_type == "decision" or row["evidence_id"].startswith("text-"))]
            self.assertEqual(actual, ["'" + value for value in unsafe] + safe)
        result["recommendations"][0]["delta_erv_pp"] = -0.25
        recommendation = next(row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "recommendation")
        self.assertEqual(recommendation["delta_erv_pp"], "-0.25")

    def test_frequency_is_reconciled_in_csv_and_reports_for_test_and_collect(self):
        for weeks, end, expected_status in ((2, "2025-01-19", "test"), (1, "2025-01-12", "collect")):
            with self.subTest(status=expected_status):
                result = analyze(sponsorship_frequency_rows(weeks), default_scope(target_start="2025-01-06", target_end=end, reference_date=end), "hash")
                item = result["recommendations"][0]
                frequency = item["frequency_hypothesis"]
                row = next(row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "recommendation")
                self.assertEqual(json.loads(row["frequency_hypothesis"]), frequency)
                for report in (analysis_report(result), executive_summary(result, [])):
                    self.assertIn(item["evidence_id"], report)
                    self.assertIn(f"status {expected_status}", report)
                    for key in ("unit", "method", "action_type", "window_start", "window_end", "limitation"):
                        self.assertIn(str(frequency[key]), report)
                    for label, key in (("creator-semanas", "sample_creator_weeks"), ("creators", "sample_creators"), ("semanas completas disponíveis", "complete_weeks_available"), ("semanas observadas", "observed_complete_weeks")):
                        self.assertIn(f"{frequency[key]} {label}", report)
                    self.assertIn(f"mínimo de {frequency['collection_requirement_weeks']} semanas", report)
                    self.assertIn("ausência de linha não equivale a zero", report)
                    if expected_status == "test":
                        self.assertIn("Testar 3 posts por creator por semana ISO completa", report)
                    else:
                        self.assertIn("Coletar antes de sugerir cadência; valor não definido", report)

    def test_recommendations_reconcile_csv_markdown_and_html_in_engine_order(self):
        result = sample_result()
        result["recommendations"] = [
            {"evidence_id": f"recommendation-{index}", "recommendation_key": f"recommendation-{index}",
             "context": {"platform": "TikTok", "content_type": "video", "content_category": str(index), "follower_band": "500,000+"},
             "priority": 100 * 0.5 * 0.8 * recency, "priority_components": {"impact": 0.5, "strength": 0.8, "recency": recency},
             "priority_values": {"views": 100, "interactions": 20, "followers": 50},
             "normalization": {"views": 200, "interactions": 40, "followers": 100},
             "delta_erv_pp": -0.1, "representative_date": "2024-01-01", "action_type": "test", "topic": "sponsorship",
             "action": f"Teste {index}", "owner": "Gestor", "execution_window": "próximos 7 dias", "review_window": "7 dias após o teste", "metric": "ERv e volume"}
            for index, recency in [(2, 1e-12), (1, 5e-13), (3, 2e-13)]
        ]
        rows = [row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "recommendation"]
        self.assertEqual([row["evidence_id"] for row in rows], [item["evidence_id"] for item in result["recommendations"]])
        for rank, (row, item) in enumerate(zip(rows, result["recommendations"], strict=True), 1):
            self.assertEqual(int(row["rank"]), rank)
            for key in ("priority", "delta_erv_pp"):
                self.assertEqual(float(row[key]), item[key])
            for key, value in item["priority_components"].items():
                self.assertEqual(float(row[key]), value)
            for key in ("normalization", "priority_values", "context"):
                self.assertEqual(json.loads(row[key]), item[key])
            for key in ("action", "action_type", "owner", "execution_window", "review_window", "representative_date", "metric"):
                self.assertEqual(row[key], item[key])
            self.assertAlmostEqual(float(row["priority"]), 100 * float(row["impact"]) * float(row["strength"]) * float(row["recency"]), delta=1e-25)
        for output in (analysis_report(result), executive_summary(result, [])):
            positions = [output.index(item["evidence_id"]) for item in result["recommendations"]]
            self.assertEqual(positions, sorted(positions))
            for item in result["recommendations"]:
                self.assertIn(f"{item['priority']:.6g}", output)
                self.assertIn(item["execution_window"], output)
                self.assertIn(item["review_window"], output)

    def test_compact_references_round_trip_opaque_ids_and_physical_lines(self):
        frame, errors = load_csv(csv_bytes([
            make_post(id="id:one", content_description="first line\nsecond line"),
            make_post(id="two", content_id="different"),
        ]))
        self.assertEqual(errors, [])
        self.assertEqual(frame["source_line"].tolist(), [2, 4])
        result = analyze(frame, {"include_post_alerts": False}, str(frame["source_hash"].iloc[0]))
        references = [row for row in parse_export(export_evidence(result, [])) if row["record_type"] == "source_ref"]
        self.assertTrue(references)
        for row in references:
            ids, lines = json.loads(row["source_row_id"]), json.loads(row["source_line"])
            self.assertEqual(len(ids), len(lines))
            for source_id, line in zip(ids, lines, strict=True):
                self.assertEqual(result["row_references"][f"{row['source_hash']}:{source_id}"], line)

    def test_export_csv_keeps_numbers_numeric_and_neutralizes_formula_text(self):
        rows = parse_export(export_evidence(result_with_texts(["=1+1", "+cmd", "-2+3", "@SUM(A1)", "\t=1"]), []))
        evidence = [row for row in rows if row["record_type"] == "evidence" and row["evidence_id"].startswith("text-")]
        self.assertTrue(all(row["text"].startswith("'") for row in evidence))
        self.assertEqual(float(next(row for row in evidence if row["metric_value"])["metric_value"]), 10.0)

    def test_export_rows_join_through_evidence_and_source_ids(self):
        rows = parse_export(export_evidence(sample_result(), sample_decisions()))
        evidence_ids = {row["evidence_id"] for row in rows if row["record_type"] == "evidence"}
        self.assertTrue(all(row["evidence_id"] in evidence_ids for row in rows if row["record_type"] in {"source_ref", "decision"}))

    def test_executive_html_escapes_input_and_has_no_active_content(self):
        page = executive_summary(result_with_texts(["<script>alert(1)</script>"]), [])
        self.assertIn("&lt;script&gt;", page)
        self.assertNotIn("<script", page.lower())
        self.assertNotRegex(page, r"https?://")

    def test_cli_is_deterministic_and_invalid_csv_returns_exit_two(self):
        with tempfile.TemporaryDirectory() as directory:
            valid = Path(directory) / "valid.csv"
            invalid = Path(directory) / "invalid.csv"
            valid.write_bytes(csv_bytes([make_post()]))
            invalid.write_bytes(b"invalid")
            first_code, first_bytes = run_cli(valid)
            second_code, second_bytes = run_cli(valid)
            invalid_code, _ = run_cli(invalid)
        self.assertEqual((first_code, second_code), (0, 0))
        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(invalid_code, 2)


if __name__ == "__main__":
    unittest.main()
