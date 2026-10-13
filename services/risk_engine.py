"""Transparent, deterministic release-risk scoring."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskDecision:
    level: str
    recommendation: str
    colour: str


class RiskEngine:
    def __init__(self, config: dict):
        self.weights = config["weights"]
        self.thresholds = config["thresholds"]
        self.scoring = config["scoring"]

    @staticmethod
    def _capped_ratio(value: float, maximum: float) -> float:
        return min(1.0, value / maximum) if maximum else 0.0

    def calculate(self, analyses: dict) -> dict:
        requirements = analyses["requirements"]
        regression = analyses["regression"]
        defects = analyses["defects"]

        defect_units = (
            defects["critical_count"]
            + defects["high_count"] * self.scoring["high_defect_equivalent"]
        )
        defect_score = self.weights["critical_defects"] * self._capped_ratio(
            defect_units, self.scoring["critical_defects_for_max"]
        )

        failed_rate = (
            regression["failed"] / regression["executed"]
            if regression["executed"]
            else 0
        )
        failed_score = self.weights["failed_tests"] * self._capped_ratio(
            failed_rate, self.scoring["failed_test_rate_for_max"]
        )

        insufficient_evidence = (
            not requirements["story_count"]
            and not regression["total"]
            and not defects.get("open_count")
            and not defects.get("blocker_count")
        )
        coverage_gap = 1 - regression["execution_coverage"]
        coverage_ratio = self._capped_ratio(
            coverage_gap, self.scoring["coverage_gap_for_max"]
        )
        if regression["critical_untested"]:
            coverage_ratio += self.scoring["critical_untested_penalty_ratio"]
        if insufficient_evidence:
            coverage_ratio = 0
        coverage_score = self.weights["coverage"] * min(1.0, coverage_ratio)

        story_risk = self._capped_ratio(
            requirements["high_risk_story_count"],
            max(1, requirements["story_count"]),
        )
        criteria_risk = self._capped_ratio(
            len(requirements["unclear_acceptance_criteria"])
            + len(requirements["potentially_untested_acceptance_criteria"]),
            max(1, requirements["acceptance_criteria_count"]),
        )
        requirement_score = self.weights["requirement_risk"] * (
            story_risk + criteria_risk
        ) / 2

        factors = {
            "Open defect exposure": defect_score,
            "WDIO failure exposure": failed_score,
            "WDIO coverage gap": coverage_score,
            "Jira requirement risk": requirement_score,
        }
        score = min(100, round(sum(factors.values())))
        if insufficient_evidence:
            score = 100
        decision = self.classify(score)

        return {
            "score": score,
            "level": decision.level,
            "recommendation": decision.recommendation,
            "colour": decision.colour,
            "insufficient_evidence": insufficient_evidence,
            "factors": {name: round(value, 1) for name, value in factors.items()},
            "max_factors": {
                "Open defect exposure": self.weights["critical_defects"],
                "WDIO failure exposure": self.weights["failed_tests"],
                "WDIO coverage gap": self.weights["coverage"],
                "Jira requirement risk": self.weights["requirement_risk"],
            },
        }

    def classify(self, score: int) -> RiskDecision:
        if score <= self.thresholds["low_max"]:
            return RiskDecision("LOW", "GO", "#067647")
        if score <= self.thresholds["medium_max"]:
            return RiskDecision("MEDIUM", "CONDITIONAL GO", "#B54708")
        return RiskDecision("HIGH", "HOLD", "#B42318")
