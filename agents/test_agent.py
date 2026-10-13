"""Analyse WDIO regression results and identify release-relevant failures."""


class RegressionIntelligenceAgent:
    name = "Regression Intelligence"

    def analyse(self, release: dict) -> dict:
        results = release.get("wdio_results", release.get("tests", []))
        stories_by_id = {
            story.get("id"): story for story in release.get("stories", [])
        }
        normalized_results = []
        for result in results:
            enriched = dict(result)
            story = stories_by_id.get(result.get("story_id"), {})
            enriched.setdefault("component", story.get("component", "Unknown"))
            normalized_results.append(enriched)

        executed = [
            result for result in normalized_results
            if result.get("status") in {"PASS", "FAIL"}
        ]
        passed = [result for result in normalized_results if result.get("status") == "PASS"]
        failed = [result for result in normalized_results if result.get("status") == "FAIL"]
        skipped = [
            result for result in normalized_results
            if result.get("status") in {"NOT_RUN", "SKIPPED"}
        ]
        automated = [
            result for result in normalized_results
            if result.get("automation", "Automated") == "Automated"
        ]
        critical_untested = [
            result for result in skipped if result.get("critical")
        ]

        total = len(normalized_results)
        execution_coverage = len(executed) / total if total else 0
        pass_rate = len(passed) / len(executed) if executed else 0
        automation_coverage = len(automated) / total if total else 0
        impacted_components = sorted({
            result.get("component", "Unknown") for result in failed
        })
        relevant_failures = [
            {
                "id": result.get("id"),
                "story_id": result.get("story_id"),
                "scenario": result.get("scenario"),
                "component": result.get("component", "Unknown"),
                "error_message": result.get(
                    "error_message", "No WDIO error message was supplied."
                ),
            }
            for result in failed
        ]

        findings = [
            f"{len(failed)} of {len(executed)} executed WDIO tests failed.",
            f"{len(skipped)} WDIO tests were skipped or not run.",
        ]
        if impacted_components:
            findings.append(
                f"Failures may affect: {', '.join(impacted_components)}."
            )
        if critical_untested:
            findings.append(f"{len(critical_untested)} critical scenarios have not been executed.")

        return {
            "agent": self.name,
            "total": total,
            "executed": len(executed),
            "passed": len(passed),
            "failed": len(failed),
            "not_run": len(skipped),
            "execution_coverage": execution_coverage,
            "pass_rate": pass_rate,
            "automation_coverage": automation_coverage,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "critical_untested": critical_untested,
            "impacted_components": impacted_components,
            "relevant_failures": relevant_failures,
            "findings": findings,
        }
