"""Run specialist agents and assemble the final assessment."""

from copy import deepcopy
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from agents.defect_agent import DefectAgent
from agents.release_guardian import ReleaseGuardian
from agents.requirement_agent import RequirementAgent
from agents.test_agent import RegressionIntelligenceAgent
from services.risk_engine import RiskEngine


class Orchestrator:
    def __init__(self, config: dict):
        self.requirement_agent = RequirementAgent()
        self.regression_agent = RegressionIntelligenceAgent()
        self.defect_agent = DefectAgent()
        self.risk_engine = RiskEngine(config)
        self.guardian = ReleaseGuardian()

    def run(self, release: dict, scenario: dict | None = None) -> dict:
        pipeline = []
        pipeline_started = perf_counter()
        scenario = scenario or {}
        working_release = self.apply_scenario(release, scenario)

        def run_stage(stage: str, actor: str, operation, summary):
            started = perf_counter()
            output = operation()
            pipeline.append({
                "stage": stage,
                "actor": actor,
                "status": "Completed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_ms": round((perf_counter() - started) * 1000, 2),
                "summary": summary(output),
            })
            return output

        pipeline.append({
            "stage": "Evidence received",
            "actor": "Release trigger",
            "status": "Completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": 0,
            "summary": (
                f"{len(working_release.get('stories', []))} Jira stories, "
                f"{len(self._regression_results(working_release))} WDIO results and "
                f"{len(working_release.get('defects', []))} Jira defects ingested."
            ),
        })
        requirements = run_stage(
            "Jira requirements analysed",
            self.requirement_agent.name,
            lambda: self.requirement_agent.analyse(
                working_release,
                resolve_requirement_risks=scenario.get(
                    "resolve_requirement_risks", False
                ),
            ),
            lambda output: (
                f"{output['story_count']} stories; "
                f"{len(output['potentially_untested_acceptance_criteria'])} criteria may be untested."
            ),
        )
        regression = run_stage(
            "WDIO regression analysed",
            self.regression_agent.name,
            lambda: self.regression_agent.analyse(working_release),
            lambda output: (
                f"{output['execution_coverage']:.0%} executed; "
                f"{output['failed']} failures found."
            ),
        )
        defects = run_stage(
            "Defects triaged",
            self.defect_agent.name,
            lambda: self.defect_agent.analyse(
                working_release, requirements, regression
            ),
            lambda output: (
                f"{output['open_count']} open; "
                f"{len(output['correlated_defects'])} correlated with release evidence."
            ),
        )
        analyses = {
            "requirements": requirements,
            "regression": regression,
            "defects": defects,
        }
        risk = run_stage(
            "Risk calculated",
            "Deterministic Risk Engine",
            lambda: self.risk_engine.calculate(analyses),
            lambda output: f"Risk score calculated as {output['score']}/100.",
        )
        assessment = run_stage(
            "Decision generated",
            self.guardian.name,
            lambda: self.guardian.assess(working_release, analyses, risk),
            lambda output: (
                f"{output['level']} risk — {output['recommendation']} recommended."
            ),
        )
        return {
            "release": working_release,
            "analyses": analyses,
            "assessment": assessment,
            "pipeline": pipeline,
            "run_metadata": {
                "run_id": (
                    datetime.now(timezone.utc).strftime("ARG-%Y%m%d-%H%M%S")
                    + f"-{uuid4().hex[:6]}"
                ),
                "triggered_at": pipeline[0]["timestamp"],
                "duration_ms": round((perf_counter() - pipeline_started) * 1000, 2),
                "status": "Completed",
            },
        }

    @staticmethod
    def apply_scenario(release: dict, scenario: dict) -> dict:
        simulated = deepcopy(release)
        resolve_blockers = (
            scenario.get("resolve_blocker_defects")
            or scenario.get("resolve_critical_defects")
            or scenario.get("resolve_high_defects")
        )
        if resolve_blockers:
            for defect in simulated.get("defects", []):
                if defect.get("severity", "").lower() in DefectAgent.BLOCKER_SEVERITIES:
                    defect["status"] = "Resolved"
        if scenario.get("pass_failed_tests"):
            for test in Orchestrator._regression_results(simulated):
                if test.get("status") == "FAIL":
                    test["status"] = "PASS"
        if scenario.get("execute_unrun_tests"):
            for test in Orchestrator._regression_results(simulated):
                if test.get("status") in {"NOT_RUN", "SKIPPED"}:
                    test["status"] = "PASS"
        return simulated

    @staticmethod
    def _regression_results(release: dict) -> list[dict]:
        return release.get("wdio_results", release.get("tests", []))
