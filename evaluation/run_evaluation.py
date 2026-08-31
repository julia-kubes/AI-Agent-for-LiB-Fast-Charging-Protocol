"""Run the offline evaluation harness; switch adapters after retrieval integration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.agent import ResearchAgent
from app.config import Settings
from app.demo import DemoLLM, DemoRetrieval


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=ROOT / "questions.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "results.jsonl")
    args = parser.parse_args()

    agent = ResearchAgent(DemoRetrieval(), DemoLLM(), Settings.from_env())
    results = []
    with args.questions.open("r", encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            item = json.loads(line)
            result = agent.answer(item["question"])
            results.append(
                {
                    **item,
                    "answer": result.answer,
                    "validation": result.validation.status,
                    "warnings": result.validation.warnings,
                    "agent_rounds": result.agent_rounds,
                    "tool_calls": result.tool_calls,
                    "input_tokens": result.usage.input_tokens,
                    "output_tokens": result.usage.output_tokens,
                    "demo": True,
                }
            )
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        for item in results:
            output.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {len(results)} evaluation result(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
