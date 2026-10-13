"""Analyse Jira requirements, acceptance criteria, and testability risks."""

import re


class RequirementAgent:
    name = "Requirement Intelligence"

    HIGH_RISK_PRIORITIES = {"critical", "highest", "high"}
    UNCLEAR_TERMS = {
        "appropriate",
        "correct",
        "proper",
        "quickly",
        "seamless",
        "successful",
        "works",
    }
    STOP_WORDS = {"a", "an", "and", "are", "be", "is", "once", "the", "to"}

    @classmethod
    def _tokens(cls, value: str) -> set[str]:
        words = re.findall(r"[a-z0-9]+", value.lower())
        return {
            word[:5]
            for word in words
            if word not in cls.STOP_WORDS and len(word) > 2
        }

    @classmethod
    def _is_covered(cls, criterion: str, scenarios: list[str]) -> bool:
        criterion_tokens = cls._tokens(criterion)
        if not criterion_tokens:
            return False
        return any(
            len(criterion_tokens & cls._tokens(scenario)) / len(criterion_tokens) >= 0.5
            for scenario in scenarios
        )

    def analyse(
        self,
        release: dict,
        resolve_requirement_risks: bool = False,
    ) -> dict:
        stories = release.get("stories", [])
        regression_results = release.get("wdio_results", release.get("tests", []))
        components = sorted({story.get("component", "Unknown") for story in stories})
        high_risk = [
            story
            for story in stories
            if story.get("priority", "").lower() in self.HIGH_RISK_PRIORITIES
        ]
        dependencies = sorted({
            dependency
            for story in stories
            for dependency in story.get("dependencies", [])
        })
        unclear_criteria = []
        untested_criteria = []
        for story in stories:
            scenarios = [
                result.get("scenario", "")
                for result in regression_results
                if result.get("story_id") == story.get("id")
            ]
            for criterion in story.get("acceptance_criteria", []):
                criterion_record = {
                    "story_id": story.get("id"),
                    "criterion": criterion,
                    "component": story.get("component", "Unknown"),
                }
                criterion_words = set(re.findall(r"[a-z]+", criterion.lower()))
                if len(criterion_words) < 3 or criterion_words & self.UNCLEAR_TERMS:
                    unclear_criteria.append(criterion_record)
                if not self._is_covered(criterion, scenarios):
                    untested_criteria.append(criterion_record)

        if resolve_requirement_risks:
            high_risk = []
            unclear_criteria = []
            untested_criteria = []

        findings = [
            f"{len(stories)} Jira stories affect {len(components)} components.",
            f"{len(high_risk)} high-risk requirements require focused validation.",
        ]
        if resolve_requirement_risks:
            findings.append(
                "High-risk requirements and acceptance criteria are simulated as validated."
            )
        if unclear_criteria:
            findings.append(
                f"{len(unclear_criteria)} acceptance criteria may be unclear or ambiguous."
            )
        if untested_criteria:
            findings.append(
                f"{len(untested_criteria)} acceptance criteria have no clearly matching WDIO scenario."
            )
        if dependencies:
            findings.append(f"Cross-component dependencies: {', '.join(dependencies)}.")

        return {
            "agent": self.name,
            "story_count": len(stories),
            "acceptance_criteria_count": sum(
                len(story.get("acceptance_criteria", [])) for story in stories
            ),
            "critical_story_count": sum(
                story.get("priority", "").lower() == "critical" for story in stories
            ),
            "high_risk_story_count": len(high_risk),
            "components": components,
            "dependencies": dependencies,
            "high_risk_requirements": [
                {"id": story.get("id"), "title": story.get("title"), "component": story.get("component")}
                for story in high_risk
            ],
            "unclear_acceptance_criteria": unclear_criteria,
            "potentially_untested_acceptance_criteria": untested_criteria,
            "findings": findings,
        }
