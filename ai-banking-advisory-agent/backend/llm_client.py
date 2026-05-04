"""
Lightweight LLM client wrapper supporting a mock fallback and optional providers.
- Provider selection via environment variable `LLM_PROVIDER` (mock|openai|anthropic|ollama)
- API keys read from env: OPENAI_API_KEY, ANTHROPIC_API_KEY
- If no provider or keys available, uses a local mock responder for offline testing
"""
import os
import json
from typing import Optional

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()


class LLMClient:
    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or LLM_PROVIDER).lower()
        # Lazy imports for optional SDKs
        self.client = None
        if self.provider == "openai":
            try:
                import openai
                self.client = openai
            except Exception:
                self.client = None
        elif self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic
            except Exception:
                self.client = None
        elif self.provider == "ollama":
            # Ollama integration would use requests to local Ollama server
            import requests  # type: ignore
            self.client = requests

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.2) -> dict:
        """
        Generate a response from the configured LLM provider.
        Returns a dict: {"response": str, "confidence": float, "raw": Any}
        """
        if self.provider == "openai" and self.client:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return self._mock_response(prompt, reason="missing_openai_key")
            try:
                completion = self.client.ChatCompletion.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4"),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    api_key=api_key
                )
                text = completion.choices[0].message.content
                return {"response": text, "confidence": 0.8, "raw": completion}
            except Exception as e:
                return self._mock_response(prompt, reason=str(e))

        if self.provider == "anthropic" and self.client:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return self._mock_response(prompt, reason="missing_anthropic_key")
            try:
                # Minimal Anthropic example
                client = self.client.Client(api_key=api_key)
                resp = client.completions.create(model=os.getenv("ANTHROPIC_MODEL", "claude-2"),
                                                 prompt=prompt,
                                                 max_tokens_to_sample=max_tokens,
                                                 temperature=temperature)
                text = resp.completion
                return {"response": text, "confidence": 0.8, "raw": resp}
            except Exception as e:
                return self._mock_response(prompt, reason=str(e))

        if self.provider == "ollama" and self.client:
            try:
                # Local ollama call example (requires Ollama running)
                url = os.getenv("OLLAMA_URL", "http://localhost:11434")
                model = os.getenv("OLLAMA_MODEL", "llama2")
                r = self.client.post(f"{url}/api/v1/generate", json={"model": model, "prompt": prompt})
                text = r.json().get("result", "")
                return {"response": text, "confidence": 0.7, "raw": r}
            except Exception as e:
                return self._mock_response(prompt, reason=str(e))

        # Default: mock
        return self._mock_response(prompt)

    def _mock_response(self, prompt: str, reason: Optional[str] = None) -> dict:
        # Simple deterministic mock: echo and a tiny transformation to simulate reasoning
        lines = [l.strip() for l in prompt.splitlines() if l.strip()]
        summary = lines[-1] if lines else prompt
        resp = (
            f"[MOCK LLM RESPONSE] Based on your query: '{summary}'. "
            "I recommend reviewing commercial equipment rates (6.5-9.5%) and "
            "considering leasing options for construction equipment (5.5-8.5%)."
        )
        return {"response": resp, "confidence": 0.65, "raw": {"mock_reason": reason}}


if __name__ == "__main__":
    client = LLMClient()
    print(json.dumps(client.generate("What are current rates for equipment financing?"), indent=2))
