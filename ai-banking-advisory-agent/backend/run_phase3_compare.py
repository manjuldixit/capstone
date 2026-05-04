"""
Phase 3 comparison runner.
- Loads test queries from ai-banking-advisory-agent/data/evaluation_test_set.json
- For each prompt variant, calls the LLM client and records outputs
- Produces a JSON export with per-query, per-prompt results for analysis

Usage:
    python run_phase3_compare.py --provider=mock
    python run_phase3_compare.py --provider=openai

If no API key is provided for chosen provider, the mock fallback will be used.
"""
import argparse
import json
from pathlib import Path
from datetime import datetime
from llm_client import LLMClient
from llm_prompts import PROMPT_VARIANTS, DEFAULT_PROMPT

DATA_PATH = Path(__file__).resolve().parents[1] / "data"
TEST_SET_PATH = DATA_PATH / "evaluation_test_set.json"
OUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_test_queries():
    with open(TEST_SET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("phase_2_basic_test_queries", [])


def run_comparison(provider: str = "mock"):
    llm = LLMClient(provider)
    queries = load_test_queries()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"phase3_comparison_{provider}_{timestamp}.json"

    results = {
        "provider": provider,
        "timestamp": timestamp,
        "prompt_variants": list(PROMPT_VARIANTS.keys()),
        "queries": []
    }

    for q in queries:
        q_record = {
            "id": q.get("id"),
            "query": q.get("query"),
            "expected_category": q.get("category"),
            "results": {}
        }

        for variant_name, template in PROMPT_VARIANTS.items():
            prompt = template.format(query=q.get("query"))
            resp = llm.generate(prompt)
            q_record["results"][variant_name] = {
                "response": resp.get("response"),
                "confidence": resp.get("confidence", 0.0),
                "raw": resp.get("raw")
            }

        results["queries"].append(q_record)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Phase 3 comparison exported: {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", type=str, default="mock", help="LLM provider: mock|openai|anthropic|ollama")
    args = parser.parse_args()
    run_comparison(args.provider)

