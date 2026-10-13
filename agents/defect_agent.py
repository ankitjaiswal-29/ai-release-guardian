"""Analyse Jira defects and correlate them with requirements and WDIO failures."""


class DefectAgent:
    name = "Defect Intelligence"
    CLOSED_STATUSES = {"closed", "resolved", "done"}
    BLOCKER_SEVERITIES = {"critical", "high"}

    def analyse(
        self,
        release: dict,
        requirements: dict | None = None,
        regression: dict | None = None,
    ) -> dict:
        defects = release.get("defects", [])
        requirements = requirements or {}
        regression = regression or {}
        open_defects = [
            defect for defect in defects
            if defect.get("status", "").lower() not in self.CLOSED_STATUSES
        ]
        blockers = [
            defect for defect in open_defects
            if defect.get("severity", "").lower() in self.BLOCKER_SEVERITIES
        ]
        critical = [
            defect for defect in blockers
            if defect.get("severity", "").lower() == "critical"
        ]
        high = [
            defect for defect in blockers
            if defect.get("severity", "").lower() == "high"
        ]
        failed_story_ids = {
            failure.get("story_id") for failure in regression.get("relevant_failures", [])
        }
        failed_components = set(regression.get("impacted_components", []))
        requirement_ids = {
            requirement.get("id")
            for requirement in requirements.get("high_risk_requirements", [])
        }
        correlated = []
        for defect in open_defects:
            links = []
            if defect.get("story_id") in failed_story_ids:
                links.append("WDIO failure for the same Jira story")
            elif defect.get("component") in failed_components:
                links.append("WDIO failure in the same component")
            if defect.get("story_id") in requirement_ids:
                links.append("high-risk Jira requirement")
            if links:
                correlated.append({**defect, "correlations": links})

        findings = [f"{len(open_defects)} release-related Jira defects remain open."]
        if blockers:
            findings.append(
                f"{len(blockers)} Critical/High defects are release blockers."
            )
        if correlated:
            findings.append(
                f"{len(correlated)} open defects correlate with WDIO failures or high-risk stories."
            )

        return {
            "agent": self.name,
            "open_count": len(open_defects),
            "critical_count": len(critical),
            "high_count": len(high),
            "blocker_count": len(blockers),
            "blockers": blockers,
            "open_defects": open_defects,
            "correlated_defects": correlated,
            "affected_components": sorted({d.get("component", "Unknown") for d in open_defects}),
            "findings": findings,
        }
