from __future__ import annotations

import csv
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from analysis import executive_summary, export_evidence
from tests.helpers import csv_bytes, make_post


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


def run_cli(path: Path) -> tuple[int, bytes]:
    with tempfile.TemporaryDirectory() as directory:
        output_csv = Path(directory) / "evidence.csv"
        output_html = Path(directory) / "summary.html"
        completed = subprocess.run(
            [sys.executable, str(APP_ROOT / "analysis.py"), str(path), "--evidence", str(output_csv), "--summary", str(output_html)],
            capture_output=True,
            check=False,
        )
        return completed.returncode, output_csv.read_bytes() if output_csv.exists() else b""


class ExportTests(unittest.TestCase):
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
