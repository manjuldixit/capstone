# Phase 6: Planning, Memory & Context

## What Phase 6 delivers

This phase adds multi-turn memory, planning assistance, and improved conversation quality:
- Short-term memory for the active session
- Long-term memory for stable profile facts
- Memory reset and retention rules
- Multi-step planning responses for complex financing requests
- Context-aware follow-up answers

## New files

- `capstone/ai-banking-advisory-agent/backend/memory_manager.py` — memory storage and retrieval logic
- `capstone/ai-banking-advisory-agent/backend/memory_agent.py` — Phase 6 agent using memory and planning
- `capstone/ai-banking-advisory-agent/backend/run_phase6_memory.py` — multi-turn demo runner
- `capstone/ai-banking-advisory-agent/docs/PHASE_6_QUICK_START.md` — this guide

## Run the Phase 6 demo

```bash
cd capstone/ai-banking-advisory-agent/backend
python run_phase6_memory.py
```

Expected output:
- A planning-oriented response for the first complex question
- Follow-up answers that reuse earlier business profile details
- Memory reset behavior after the reset query
- Fresh generic response after memory is cleared
- `outputs/phase6_memory_demo_results.json`
- `outputs/memory_logs_*.json`

## Phase 6 behavior

### Memory

- Short-term memory keeps the last 5 conversational facts
- Long-term memory stores stable profile details like credit score, business type, and equipment preference
- Memory is never stored if it contains PII
- A reset query such as "forget" or "clear memory" clears stored details

### Planning

- Complex queries trigger step-by-step planning guidance
- The plan recommends equipment needs, eligibility assessment, cost estimation, and document preparation
- This helps the agent move from single-turn templated replies to multi-step reasoning

### Conversation quality

- Follow-up questions can use remembered context for tailored answers
- After memory reset, the agent starts a fresh session with generic guidance
- The agent maintains a clean session log and exports memory snapshots for analysis

## Next step

Phase 7 will integrate stronger personalization and adaptive memory pruning, while keeping safety and compliance intact.

