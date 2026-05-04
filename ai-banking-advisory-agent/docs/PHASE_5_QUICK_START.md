# Phase 5: Enable Tool Usage

## What Phase 5 delivers

This phase adds tool usage capability to the equipment financing agent:
- Agent chooses tools based on user intent
- Tool schemas describe valid inputs and outputs
- Guardrails block PII and out-of-scope requests
- Tool failures are handled safely
- Loop prevention limits repeated tool calls

## New files

- `capstone/ai-banking-advisory-agent/backend/toolbox.py` — tool schemas, selection, safety checks
- `capstone/ai-banking-advisory-agent/backend/tool_agent.py` — tool-enabled agent logic
- `capstone/ai-banking-advisory-agent/backend/run_phase5_tool_demo.py` — demo runner
- `capstone/ai-banking-advisory-agent/docs/PHASE_5_QUICK_START.md` — this guide

## Run the Phase 5 demo

```bash
cd capstone/ai-banking-advisory-agent/backend
python run_phase5_tool_demo.py
```

Expected output:
- Correct tool use for eligibility and payment estimate
- A failed tool call for an incomplete payment request
- A safeguarded refusal for an out-of-scope transfer request
- `outputs/phase5_tool_demo_results.json`
- `outputs/tool_agent_logs_*.json`

## Tool suite

### `loan_payment_calculator`
Parameters:
- `amount`: Loan amount in USD
- `term_months`: Loan term in months
- `apr`: Annual percentage rate

### `credit_score_assessment`
Parameters:
- `credit_score`: Numeric credit score between 300 and 850

## Safeguards

- PII detection blocks tool usage for sensitive inputs
- Out-of-scope keywords prevent tool selection for transfers and account actions
- Maximum `2` tool calls per session prevents loops
- Tool parsing errors return safe user-facing fallback responses

## Demonstrated behaviors

| Query | Expected behavior |
|---|---|
| `Am I eligible for equipment financing with a 680 credit score?` | Correct tool selection and credit assessment |
| `Calculate the monthly payment for $120,000 over 60 months at 7.5% APR.` | Correct payment calculator tool usage |
| `What will my payment be?` | Tool selected but fails due missing parameters; safe fallback returned |
| `Transfer $5,000 to my savings account.` | Blocked as out-of-scope; no tool is allowed |

## Next step

Phase 6 will add memory and conversational state. For now, Phase 5 demonstrates tool orchestration, guardrails, and safe error handling.

