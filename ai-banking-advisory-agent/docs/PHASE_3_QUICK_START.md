# Phase 3 Quick Start: LLM Integration & Prompt Experiments

This quick-start shows how to run Phase 3 comparisons locally using a mock LLM or a real provider.

Prerequisites
- Python 3.10+
- Install backend dependencies:

```bash
cd capstone/ai-banking-advisory-agent/backend
pip install -r requirements.txt
```

Provider selection
- Use env var `LLM_PROVIDER` or pass `--provider` to the runner.
- Supported values: `mock`, `openai`, `anthropic`, `ollama`.
- For `openai` set `OPENAI_API_KEY`; for `anthropic` set `ANTHROPIC_API_KEY`.

Run Phase 3 comparison (mock):

```bash
cd capstone/ai-banking-advisory-agent/backend
python run_phase3_llm_prompts.py --provider=mock
```

Run Phase 3 with OpenAI:

```bash
export OPENAI_API_KEY="sk-..."
python run_phase3_llm_prompts.py --provider=openai
```

Outputs
- Exports: `capstone/ai-banking-advisory-agent/outputs/phase3_comparison_{provider}_{timestamp}.json`
- Each export contains per-query results for each prompt variant (safety, reasoning, domain)

Default prompt
- The runner runs all 3 variants. The recommended default after experiments is the `reasoning` prompt (balances safety and explanation).

Next steps
- Provide API keys to evaluate real LLM performance.
- Run multiple seeds and aggregate confidence/relevance metrics.
- Optionally extend runner to call existing agent pipeline and let the LLM produce category labels.

