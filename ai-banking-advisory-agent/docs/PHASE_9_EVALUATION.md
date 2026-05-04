# Phase 9 Evaluation & Engineering Review

## Objective

Phase 9 validates ai-banking-advisory-agent behavior through structured evaluation prompts, quality metrics, failure analysis, and safety/ethics review. It also captures concrete improvement recommendations for the next development iteration.

## Evaluation Design

- `backend/run_phase9_evaluation.py`: evaluation harness that executes test queries, computes metrics, and exports results.
- `backend/mockdata/test_queries.csv`: extensive domain and safety scenarios used as a core evaluation corpus.
- `backend/mockdata/phase9_evaluation_scenarios.json`: curated Phase 9 prompts for quality, safety, consistency, and ethical validation.

## Key Metrics

- Response quality: average confidence and coverage of successful responses.
- Safety/ethics: pass rate on risk-sensitive queries and refusal/escalation enforcement.
- Consistency: repeat query similarity across semantically similar follow-ups.
- Failure analysis: exception count, low-confidence responses, safety warnings, and potential root causes.

## How to Run

From `capstone/ai-banking-advisory-agent/backend`:

```powershell
python run_phase9_evaluation.py
```

Optional flags:

- `--test-set mockdata/test_queries.csv`
- `--scenario-file mockdata/phase9_evaluation_scenarios.json`
- `--output-dir outputs`
- `--force-reinit`

### Streamlit UI

A frontend UI is available under `capstone/ai-banking-advisory-agent/frontend`:

```powershell
cd capstone/ai-banking-advisory-agent
pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```

The app connects to the backend API, shows conversation history, and allows feedback submission for adaptive model behavior.

## Failure Analysis Approach

The evaluation harness identifies failures by:

- catching exceptions during agent processing
- flagging low-confidence responses below a threshold
- checking safety/ethics responses for refusal or escalation language
- evaluating consistency across repeated or parallel prompts

This produces a failure summary and a recommended remediation list.

## Safety and Ethics Review

Phase 9 checks that the agent:

- refuses unauthorized financial transactions
- protects PII and sensitive data
- avoids out-of-scope advice
- escalates complex or ambiguous requests rather than guessing
- uses explicit, polite safety language when needed

## Preliminary Improvement Roadmap

1. Improve guardrail coverage and refusal wording for safety-sensitive queries.
2. Refine confidence calibration by aligning retrieval evidence with response certainty.
3. Harden repeated-response consistency for semantically similar follow-ups.
4. Add stronger exception handling around tool and retrieval interactions.
5. Expand evaluation coverage over domain-specific edge cases and policy boundary queries.

## Output

The harness writes a timestamped JSON file to `backend/outputs/`, including:

- aggregated metrics
- per-query response records
- safety pass rates
- consistency scores
- recommended next-step improvements

## Notes

This phase is designed to be lightweight and executable in the ai-banking-advisory-agent backend without modifying the core production agent. It establishes a repeatable engineering review workflow for subsequent phases.

