"""Convert specialist-agent evidence into an explainable release decision."""


class ReleaseGuardian:
    name = "Release Guardian"

    def assess(self, release: dict, analyses: dict, risk: dict) -> dict:
        defects = analyses["defects"]
        regression = analyses["regression"]
        requirements = analyses["requirements"]

        risks = []
        actions = []

        if risk.get("insufficient_evidence"):
            risks.append(
                "Release evidence is incomplete: no Jira stories, WDIO results, "
                "or defects were supplied."
            )
            actions.append(
                "Upload a complete release JSON with stories, WDIO results, and defects."
            )
            return {
                **risk,
                "agent": self.name,
                "summary": (
                    f"{release.get('release', 'This release')} cannot be scored from "
                    "the supplied evidence. Recommendation: HOLD."
                ),
                "top_risks": risks,
                "recommended_actions": actions,
            }

        if defects["blockers"]:
            ids = ", ".join(defect["id"] for defect in defects["blockers"])
            risks.append(
                f"{defects['blocker_count']} Critical/High defects remain open ({ids})."
            )
            actions.append(f"Resolve and verify release blockers: {ids}.")
        if regression["failed"]:
            components = ", ".join(regression["impacted_components"])
            risks.append(
                f"{regression['failed']} WDIO regression tests failed"
                f"{f' in {components}' if components else ''}."
            )
            actions.append("Fix the failed scenarios and rerun the impacted regression suite.")
        if regression["critical_untested"]:
            risks.append(
                f"{len(regression['critical_untested'])} critical WDIO scenarios are unexecuted."
            )
            actions.append("Execute all outstanding critical scenarios.")
        if requirements["potentially_untested_acceptance_criteria"]:
            risks.append(
                f"{len(requirements['potentially_untested_acceptance_criteria'])} Jira "
                "acceptance criteria have no clearly matching WDIO scenario."
            )
            actions.append("Add or link WDIO scenarios for uncovered acceptance criteria.")
        if requirements["unclear_acceptance_criteria"]:
            risks.append(
                f"{len(requirements['unclear_acceptance_criteria'])} Jira acceptance "
                "criteria may be ambiguous."
            )
            actions.append("Clarify ambiguous acceptance criteria before release approval.")
        if not risks:
            risks.append("No material release blockers were identified.")
            actions.append("Complete standard release checks and obtain manager approval.")

        summary = (
            f"{release.get('release', 'This release')} is {risk['level']} risk "
            f"({risk['score']}/100). Recommendation: {risk['recommendation']}."
        )
        return {
            **risk,
            "agent": self.name,
            "summary": summary,
            "top_risks": risks[:5],
            "recommended_actions": actions[:5],
        }
