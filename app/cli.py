"""Command-line entry point for offline and live application testing."""

from __future__ import annotations

import argparse
import json

from .agent import ResearchAgent
from .config import Settings
from .demo import DemoLLM, DemoRetrieval
from .llm_client import OpenAICompatibleLLM
from .retrieval_adapter import NeonRetrievalAdapter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument(
        "--demo", action="store_true", help="use synthetic offline backends"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings.from_env()
    if args.demo:
        retrieval = DemoRetrieval()
        llm = DemoLLM()
    else:
        if not settings.database_url:
            raise SystemExit("DATABASE_URL is required outside demo mode")
        retrieval = NeonRetrievalAdapter(
            settings.database_url, settings.embedding_model
        )
        llm = OpenAICompatibleLLM(settings)

    result = ResearchAgent(retrieval, llm, settings).answer(args.question)
    print(json.dumps(result.answer, ensure_ascii=False, indent=2))
    print(
        f"\nvalidation={result.validation.status} rounds={result.agent_rounds} "
        f"tools={result.tool_calls} tokens={result.usage.total_tokens}"
    )
    return 0 if result.validation.status != "reject" else 1


if __name__ == "__main__":
    raise SystemExit(main())

