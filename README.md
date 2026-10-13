# A³R³ — AI-Powered Autonomous Release Risk & Readiness Agent

A demo-ready MVP that turns structured release evidence into an explainable,
human-controlled release recommendation.

## What the MVP demonstrates

- Three focused intelligence agents analyse Jira requirements, WDIO regression
  results, and Jira defects before the Release Guardian makes a recommendation.
- A deterministic, configurable risk engine produces a 0–100 score.
- Every recommendation includes risk reasons and concrete next actions.
- A what-if lab shows how mitigations move a release from `HOLD` to
  `CONDITIONAL GO` or `GO`.
- Executive analytics include test-status, risk-contribution, component-exposure,
  and mitigation-trajectory charts.
- PDF, print-ready HTML, JSON, and CSV reports can be downloaded for audit and
  stakeholder communication.
- A release manager accepts or overrides the recommendation. The app never
  deploys autonomously.
- An optional LLM boundary is included for future organisation-approved narrative
  enhancement; no API credentials are needed for the MVP.

## Run locally

Requires Python 3.10 or newer.

```bash
cd AI-Release-Guardian
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Demo script

1. Click **Assess this release**. ABC-5.4 starts at **77 / HIGH / HOLD**.
2. On **Recommendation**, explain the score, blockers, and specialist findings.
3. Open **Charts** to show test health, risk concentration, and component exposure.
4. Open **Try fixes** and select **Fix Critical and High bugs**: the result moves
   to **MEDIUM / CONDITIONAL GO**.
5. Select the remaining mitigations: the result moves to **LOW / GO**.
6. Open **Approve**: accept the recommendation or demonstrate a mandatory
   override rationale.
7. Download the governed decision from **Download** as PDF, HTML, JSON, or CSV.
8. Upload another JSON release or adjust weights in the sidebar to demonstrate
   configurability.

## Architecture

```text
Jira Requirements → WDIO Regression Results → Jira Defects
                          │
                          ▼
                AI Release Guardian
                ├── Requirement Intelligence
                ├── Regression Intelligence
                └── Defect Intelligence
                          │
                          ▼
              Risk Engine (deterministic)
                          │
                          ▼
             GO / CONDITIONAL GO / HOLD
                          │
                          ▼
                 Human approval gate
```

## Risk model

Maximum weights are stored in `config/risk_config.json` and can be changed in the UI.
A factor scores between 0 and its maximum; the four maxima add up to 100.

- Open defect exposure: 30 maximum
- WDIO failure exposure: 20 maximum
- WDIO coverage gap: 20 maximum
- Jira requirement risk: 30 maximum

Classification:

- 0–30: LOW → GO
- 31–60: MEDIUM → CONDITIONAL GO
- 61–100: HIGH → HOLD

## Project structure

```text
agents/       Specialist analysis and orchestration
app/          Streamlit dashboard
config/       Risk weights and environment template
data/         Realistic demonstration release
services/     Risk engine, downloadable reports, and optional LLM boundary
tests/        End-to-end flow tests (Python unittest)
```

## Next integrations

Replace the JSON input adapters incrementally with approved Jira and WDIO APIs.
Keep the agent result contracts and risk engine unchanged so those integrations
remain independently testable.
