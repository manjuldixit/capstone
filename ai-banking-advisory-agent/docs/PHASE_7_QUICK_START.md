# Phase 7: Adaptive Behaviour

## What Phase 7 delivers

This phase introduces adaptive behavior based on user feedback:
- Collect and store explicit feedback signals
- Extract feedback cues such as clarity, conciseness, detail, examples, and escalation
- Modify future responses based on feedback patterns
- Demonstrate before vs after behavior for the same query
- Explain what changed and why

## New files

- `capstone/ai-banking-advisory-agent/backend/feedback_manager.py` — feedback storage and adaptation cues
- `capstone/ai-banking-advisory-agent/backend/adaptive_agent.py` — agent that adapts using feedback
- `capstone/ai-banking-advisory-agent/backend/run_phase7_adaptive.py` — before/after adaptive demo runner
- `capstone/ai-banking-advisory-agent/docs/PHASE_7_QUICK_START.md` — this guide

## Run the Phase 7 demo

```bash
cd capstone/ai-banking-advisory-agent/backend
python run_phase7_adaptive.py
```

Expected output:
- A baseline response before feedback
- Feedback collection with rating and comments
- A changed response after feedback
- A follow-up query demonstrating persisted adaptation behavior
- `outputs/phase7_adaptive_demo_results.json`
- `outputs/adaptive_logs_*.json`

## Adaptive behaviour

### Feedback signals

The agent stores feedback entries with:
- query
- response
- rating (1-5)
- user comments

It then extracts adaptation cues from comments, such as:
- clarity
- conciseness
- detail
- examples
- escalation

### Behaviour adjustment logic

When feedback includes low ratings, the agent adapts by:
- providing clearer language for clarity issues
- shortening responses for conciseness requests
- adding specific product details for detail requests
- including practical examples for example requests
- offering human assistance for escalation requests

### Why this matters

This phase moves the agent from static memory-based answers to a responsive system that learns from explicit user feedback. The result is behavior that changes over time, improving user experience and trust.

