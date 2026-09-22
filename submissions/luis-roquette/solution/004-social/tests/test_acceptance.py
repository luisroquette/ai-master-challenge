from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublishedAnalysisAcceptanceTests(unittest.TestCase):
    def test_published_csv_parses_in_fresh_process_with_default_field_limit(self):
        completed = subprocess.run(
            [sys.executable, "-c", "import csv,sys; assert csv.field_size_limit()==131072; f=open(sys.argv[1],newline=''); rows=list(csv.DictReader(f)); f.close(); assert rows; assert csv.field_size_limit()==131072", str(ROOT / "evidence.csv")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_published_queue_matches_export_order_and_recomputes_priority(self):
        with (ROOT / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["record_type"] == "recommendation"]
        report = (ROOT / "analysis.md").read_text(encoding="utf-8").split("## O que os dados", 1)[0]
        cited = re.findall(r"Evidência: ([\w-]+)", report)
        self.assertEqual(len(rows), 3)
        self.assertEqual(cited, [row["evidence_id"] for row in rows])
        for rank, row in enumerate(rows, 1):
            self.assertEqual(row["method_version"], "2.0.0")
            self.assertEqual(int(row["rank"]), rank)
            values, normalization = json.loads(row["priority_values"]), json.loads(row["normalization"])
            impact = sum(min(value / normalization[key], 1) if normalization[key] else 0 for key, value in values.items()) / 3
            self.assertAlmostEqual(float(row["impact"]), impact)
            expected = 100 * impact * float(row["strength"]) * float(row["recency"])
            self.assertAlmostEqual(float(row["priority"]), expected, delta=abs(expected) * 1e-12)
            self.assertIn(f"{expected:.6g}", report)
            frequency = json.loads(row["frequency_hypothesis"])
            self.assertEqual(frequency["status"], "test")
            self.assertEqual(frequency["period_month"], json.loads(row["context"])["period_month"])
            self.assertEqual(frequency["coverage_rule"], "complete_iso_weeks_within_calendar_month_and_scope")
            self.assertIn(f"mês {frequency['period_month']}", report)
            self.assertIn(frequency["coverage_rule"], report)
            self.assertIn(f"Testar {frequency['value']:g} posts por creator por semana ISO completa", report)
            self.assertIn(f"{frequency['sample_creator_weeks']} creator-semanas", report)
            self.assertIn(f"{frequency['observed_complete_weeks']} semanas observadas", report)

    def test_every_evidence_id_cited_by_report_exists_in_export(self):
        with (ROOT / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            exported = {row["evidence_id"] for row in csv.DictReader(handle) if row["record_type"] == "evidence"}
        cited = set(re.findall(r"`((?:summary|dimension|sponsorship(?:-overview)?|audience(?:-overview)?)-[0-9a-f]{16})`", (ROOT / "analysis.md").read_text(encoding="utf-8")))
        self.assertTrue(cited)
        self.assertEqual(cited - exported, set())

    def test_report_covers_mandatory_analysis_and_strategy_topics(self):
        report = (ROOT / "analysis.md").read_text(encoding="utf-8").lower()
        for term in ("plataforma", "conteúdo", "categoria", "creator", "audiência", "patrocínio", "frequência", "parar/revisar", "quick wins", "roi", "causalidade"):
            with self.subTest(term=term):
                self.assertIn(term, report)


if __name__ == "__main__":
    unittest.main()
