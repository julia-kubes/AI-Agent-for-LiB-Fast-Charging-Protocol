"""Environment-backed application settings with conservative safety limits."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load repository-local credentials for CLI and Streamlit development.
# Existing process environment variables retain priority.
load_dotenv(override=False)


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error
    if value < 1:
        raise ValueError(f"{name} must be positive")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str | None
    llm_base_url: str
    llm_api_key: str | None
    llm_model: str
    embedding_model: str
    max_agent_rounds: int
    max_searches: int
    max_retrieved_chunks: int
    max_evidence_characters: int
    max_output_tokens: int
    request_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            database_url=os.getenv("DATABASE_URL"),
            llm_base_url=os.getenv(
                "LLM_BASE_URL", "https://parley.api.mit.edu/v1"
            ).rstrip("/"),
            llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("PARLEY_API_KEY"),
            llm_model=os.getenv("LLM_MODEL", ""),
            embedding_model=os.getenv(
                "EMBEDDING_MODEL", "Alibaba-NLP/gte-modernbert-base"
            ),
            max_agent_rounds=_positive_int("MAX_AGENT_ROUNDS", 3),
            max_searches=_positive_int("MAX_SEARCHES", 2),
            max_retrieved_chunks=_positive_int("MAX_RETRIEVED_CHUNKS", 12),
            max_evidence_characters=_positive_int("MAX_EVIDENCE_CHARACTERS", 36_000),
            max_output_tokens=_positive_int("MAX_OUTPUT_TOKENS", 1_500),
            request_timeout_seconds=_positive_int("REQUEST_TIMEOUT_SECONDS", 90),
        )

    def require_llm(self) -> None:
        missing = []
        if not self.llm_api_key:
            missing.append("LLM_API_KEY (or PARLEY_API_KEY)")
        if not self.llm_model:
            missing.append("LLM_MODEL")
        if missing:
            raise RuntimeError("Missing required LLM setting(s): " + ", ".join(missing))
