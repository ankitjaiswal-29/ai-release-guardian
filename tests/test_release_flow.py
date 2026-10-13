"""End-to-end tests for deterministic release assessment."""

import json
import unittest
from pathlib import Path

from agents.orchestrator import Orchestrator


ROOT = Path(__file__).resolve().parents[1]


class ReleaseFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        release = json.loads((ROOT / "data" / "release.json").read_text())
        config = json.loads((ROOT / "config" / "risk_config.json").read_text())
        cls.release = release
        cls.orchestrator = Orchestrator(config)

    def test_baseline_release_is_held(self):
        result = self.orchestrator.run(self.release)

        self.assertEqual(result["assessment"]["score"], 77)
        self.assertEqual(result["assessment"]["level"], "HIGH")
        self.assertEqual(result["assessment"]["recommendation"], "HOLD")
        self.assertEqual(result["analyses"]["defects"]["critical_count"], 2)
        self.assertEqual(result["analyses"]["defects"]["high_count"], 1)
        self.assertEqual(result["analyses"]["defects"]["blocker_count"], 3)
        self.assertEqual(result["analyses"]["regression"]["failed"], 4)
        self.assertTrue(
            result["analyses"]["requirements"][
                "potentially_untested_acceptance_criteria"
            ]
        )
        self.assertTrue(result["analyses"]["defects"]["correlated_defects"])
        self.assertEqual(len(result["pipeline"]), 6)
        self.assertEqual(result["pipeline"][0]["stage"], "Evidence received")
        self.assertEqual(result["pipeline"][-1]["stage"], "Decision generated")
        self.assertEqual(result["run_metadata"]["status"], "Completed")

    def test_resolving_blockers_reduces_risk_without_mutating_source(self):
        result = self.orchestrator.run(
            self.release, {"resolve_blocker_defects": True}
        )

        self.assertEqual(result["assessment"]["level"], "MEDIUM")
        self.assertEqual(result["assessment"]["recommendation"], "CONDITIONAL GO")
        self.assertEqual(result["analyses"]["defects"]["blocker_count"], 0)
        self.assertEqual(
            self.orchestrator.run(self.release)["analyses"]["defects"]["blocker_count"],
            3,
        )

    def test_full_mitigation_reaches_go(self):
        result = self.orchestrator.run(
            self.release,
            {
                "resolve_blocker_defects": True,
                "pass_failed_tests": True,
                "execute_unrun_tests": True,
                "resolve_requirement_risks": True,
            },
        )

        self.assertEqual(result["assessment"]["score"], 0)
        self.assertEqual(result["assessment"]["recommendation"], "GO")
        self.assertEqual(
            result["assessment"]["factors"]["Jira requirement risk"],
            0,
        )

    def test_unresolved_requirement_risk_remains_visible(self):
        result = self.orchestrator.run(
            self.release,
            {
                "resolve_blocker_defects": True,
                "pass_failed_tests": True,
                "execute_unrun_tests": True,
            },
        )

        self.assertEqual(result["assessment"]["score"], 16)
        self.assertEqual(
            result["assessment"]["factors"]["Jira requirement risk"],
            16.2,
        )

    def test_empty_evidence_is_held(self):
        result = self.orchestrator.run({})

        self.assertEqual(result["assessment"]["score"], 100)
        self.assertEqual(result["assessment"]["recommendation"], "HOLD")
        self.assertTrue(result["assessment"]["insufficient_evidence"])

    def test_score_cannot_exceed_one_hundred(self):
        inflated = json.loads((ROOT / "config" / "risk_config.json").read_text())
        inflated["weights"] = {
            "critical_defects": 80,
            "failed_tests": 80,
            "coverage": 80,
            "requirement_risk": 80,
        }
        result = Orchestrator(inflated).run(self.release)

        self.assertEqual(result["assessment"]["score"], 100)

    def test_run_ids_are_unique(self):
        ids = {self.orchestrator.run(self.release)["run_metadata"]["run_id"] for _ in range(5)}

        self.assertEqual(len(ids), 5)


if __name__ == "__main__":
    unittest.main()
