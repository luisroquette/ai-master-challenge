from __future__ import annotations

import csv
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublishedAnalysisAcceptanceTests(unittest.TestCase):
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
