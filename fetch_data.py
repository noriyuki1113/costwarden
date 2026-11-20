#!/usr/bin/env python3
"""Fetch LiteLLM model prices and write a curated data/prices.json.

Source: https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json
License: the LiteLLM model_prices data file is part of the MIT-licensed
litellm core. We only read this data file; no code from litellm's
`enterprise/` directory (commercial license) is used anywhere.

Zero dependencies: Python 3 standard library only.
Run: python3 fetch_data.py
"""
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

SOURCE_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)
OUT = Path(__file__).parent / "data" / "prices.json"

# Curated set of widely used chat models. Only entries actually present in
# the fetched data (with both input and output prices) are written out.
CURATED = [
    # OpenAI
    "gpt-5", "gpt-5-mini", "gpt-5-nano",
    "gpt-4.1", "gpt-4.1-mini",
    "gpt-4o", "gpt-4o-mini",
    "o3", "o4-mini",
    # Anthropic
    "claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5",
    # Google
    "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
    # DeepSeek
    "deepseek/deepseek-chat", "deepseek/deepseek-reasoner",
]

PROVIDER_LABEL = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "vertex_ai-language-models": "Google",
    "vertex_ai": "Google",
    "gemini": "Google",
    "deepseek": "DeepSeek",
}


def main() -> int:
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "costwarden-fetch"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = json.load(resp)

    models = []
    missing = []
    for model_id in CURATED:
        entry = raw.get(model_id)
        if not entry or entry.get("input_cost_per_token") is None \
                or entry.get("output_cost_per_token") is None:
            missing.append(model_id)
            continue
        provider = PROVIDER_LABEL.get(entry.get("litellm_provider", ""), entry.get("litellm_provider", ""))
        models.append({
            "id": model_id,
            "provider": provider,
            "input_per_token": entry["input_cost_per_token"],
            "output_per_token": entry["output_cost_per_token"],
            "max_input_tokens": entry.get("max_input_tokens"),
            "max_output_tokens": entry.get("max_output_tokens"),
        })

    if missing:
        print(f"warning: not found in source data, skipped: {missing}", file=sys.stderr)
    if not models:
        print("error: no curated models found in source data", file=sys.stderr)
        return 1

    payload = {
        "source": SOURCE_URL,
        "source_project": "BerriAI/litellm model_prices_and_context_window.json (MIT)",
        "fetched": date.today().isoformat(),
        "models": models,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} with {len(models)} models (fetched {payload['fetched']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
