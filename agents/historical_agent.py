"""Find historical incidents related to components changed in a release."""


class HistoricalRiskAgent:
    name = "Historical Risk"

    def analyse(self, release: dict, requirement_result: dict) -> dict:
        changed_components = set(requirement_result.get("components", []))
        incidents = release.get("historical_incidents", [])
        matches = [
            incident for incident in incidents
            if incident.get("component") in changed_components
        ]

        findings = []
        for incident in matches:
            findings.append(
                f"{incident.get('component')} had a {incident.get('severity', '').lower()} "
                f"incident in {incident.get('release')}: {incident.get('incident')}."
            )
        if not findings:
            findings.append("No historical incidents match the changed components.")

        return {
            "agent": self.name,
            "similar_incident_count": len(matches),
            "matches": matches,
            "findings": findings,
        }
