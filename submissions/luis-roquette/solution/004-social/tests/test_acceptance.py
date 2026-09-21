from __future__ import annotations

import csv
import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublishedAnalysisAcceptanceTests(unittest.TestCase):
    def test_published_queue_matches_export_order_and_recomputes_priority(self):
        csv.field_size_limit(sys.maxsize)
        with (ROOT / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["record_type"] == "recommendation"]
        report = (ROOT / "analysis.md").read_text(encoding="utf-8").split("## O que os dados", 1)[0]
        cited = re.findall(r"Evidência: ([\w-]+)", report)
        self.assertEqual(len(rows), 3)
        self.assertEqual(cited, [row["evidence_id"] for row in rows])
        for rank, row in enumerate(rows, 1):
            self.assertEqual(int(row["rank"]), rank)
            values, normalization = json.loads(row["priority_values"]), json.loads(row["normalization"])
            impact = sum(min(value / normalization[key], 1) if normalization[key] else 0 for key, value in values.items()) / 3
            self.assertAlmostEqual(float(row["impact"]), impact)
            expected = 100 * impact * float(row["strength"]) * float(row["recency"])
            self.assertAlmostEqual(float(row["priority"]), expected, delta=abs(expected) * 1e-12)
            self.assertIn(f"{expected:.6g}", report)

    def test_every_evidence_id_cited_by_report_exists_in_export(self):
        csv.field_size_limit(sys.maxsize)
        with (ROOT / "evidence.csv").open(encoding="utf-8", newline="") as handle:
            exported = {row["evidence_id"] for row in csv.DictReader(handle) if row["record_type"] == "evidence"}
        cited = set(re.findall(r"`((?:summary|dimension|sponsorship(?:-overview)?)-[0-9a-f]{16})`", (ROOT / "analysis.md").read_text(encoding="utf-8")))
        self.assertTrue(cited)
        self.assertEqual(cited - exported, set())

    def test_report_covers_mandatory_analysis_and_strategy_topics(self):
        report = (ROOT / "analysis.md").read_text(encoding="utf-8").lower()
        for term in ("plataforma", "conteúdo", "categoria", "creator", "audiência", "patrocínio", "frequência", "parar/revisar", "quick wins", "roi", "causalidade"):
            with self.subTest(term=term):
                self.assertIn(term, report)


if __name__ == "__main__":
    unittest.main()
