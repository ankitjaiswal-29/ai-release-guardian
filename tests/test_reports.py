"""Tests for downloadable decision report formats."""

import json
import unittest
from pathlib import Path

from agents.orchestrator import Orchestrator
from services.report_service import (
    build_csv_report,
    build_html_report,
    build_json_report,
    build_pdf_report,
)


ROOT = Path(__file__).resolve().parents[1]


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        release = json.loads((ROOT / "data" / "release.json").read_text())
        config = json.loads((ROOT / "config" / "risk_config.json").read_text())
        cls.result = Orchestrator(config).run(release)

    def test_json_report_contains_traceable_decision(self):
        report = json.loads(build_json_report(self.result))

        self.assertEqual(report["assessment"]["recommendation"], "HOLD")
        self.assertEqual(len(report["pipeline"]), 6)
        self.assertIn("regression", report["agent_analyses"])
        self.assertEqual(report["run"]["run_id"], self.result["run_metadata"]["run_id"])

    def test_csv_and_html_reports_contain_release_data(self):
        csv_report = build_csv_report(self.result)
        html_report = build_html_report(self.result)
        self.assertIn(b"WDIO failure exposure", csv_report)
        self.assertIn(b"Maximum points", csv_report)
        self.assertIn(b"ABC-5.4", html_report)
        self.assertIn(b"Maximum points", html_report)

    def test_pdf_report_is_valid_pdf_document(self):
        report = build_pdf_report(self.result)

        self.assertTrue(report.startswith(b"%PDF"))
        self.assertGreater(len(report), 1000)


if __name__ == "__main__":
    unittest.main()
