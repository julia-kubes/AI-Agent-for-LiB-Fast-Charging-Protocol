"""Minimal Streamlit interface for the fast-charging literature assistant."""

from __future__ import annotations

import os

import streamlit as st

from app.agent import ResearchAgent
from app.config import Settings
from app.demo import DemoLLM, DemoRetrieval
from app.llm_client import OpenAICompatibleLLM
from app.retrieval_adapter import NeonRetrievalAdapter


def build_agent(settings: Settings) -> tuple[ResearchAgent, bool]:
    demo = os.getenv("APP_DEMO_MODE", "false").lower() == "true"
    if demo:
        return ResearchAgent(DemoRetrieval(), DemoLLM(), settings), True
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return (
        ResearchAgent(
            NeonRetrievalAdapter(settings.database_url, settings.embedding_model),
            OpenAICompatibleLLM(settings),
            settings,
        ),
        False,
    )


def main() -> None:
    st.set_page_config(page_title="Fast-Charging Literature Assistant")
    st.title("Fast-Charging Literature Assistant")
    st.caption(
        "Literature synthesis only—not a validated charging controller. Verify all "
        "recommendations against manufacturer limits and controlled experiments."
    )

    question = st.text_area("Research question", height=120)
    with st.expander("Optional operating conditions"):
        chemistry = st.text_input("Cell chemistry")
        temperature = st.text_input("Temperature")
        soc_range = st.text_input("Starting and target SOC")
        objective = st.text_input("Optimization objective")

    if not st.button("Analyze", type="primary"):
        return
    if not question.strip():
        st.warning("Enter a research question.")
        return

    settings = Settings.from_env()
    conditions = {
        key: value
        for key, value in {
            "chemistry": chemistry,
            "temperature": temperature,
            "soc_range": soc_range,
            "objective": objective,
        }.items()
        if value.strip()
    }
    try:
        agent, demo = build_agent(settings)
        with st.spinner("Retrieving and analyzing evidence..."):
            result = agent.answer(question, conditions)
    except Exception as error:
        st.error(str(error))
        return

    if demo:
        st.warning("Demo mode is active; all evidence and answers are synthetic.")
    st.subheader("Summary")
    st.write(result.answer.get("summary", ""))
    st.subheader("Protocol suggestions")
    for suggestion in result.answer.get("protocol_suggestions", []):
        st.markdown(f"**{suggestion.get('strategy', 'Suggestion')}**")
        st.write(suggestion.get("rationale", ""))
        st.caption(
            f"Confidence: {suggestion.get('confidence', 'unknown')} · "
            f"Evidence: {', '.join(suggestion.get('evidence_chunk_ids', []))}"
        )

    for heading, field in (
        ("Conflicting evidence", "conflicting_evidence"),
        ("Missing information", "missing_information"),
        ("Safety notes", "safety_notes"),
    ):
        values = result.answer.get(field) or []
        if values:
            st.subheader(heading)
            for value in values:
                st.write(f"- {value}")

    with st.expander("Evidence and execution details"):
        for chunk in result.evidence:
            st.markdown(f"**{chunk.chunk_id} — {chunk.title or chunk.record_id}**")
            st.caption(f"Section: {chunk.section or 'unknown'} · Pages: {chunk.page_numbers}")
            st.write(chunk.text)
        st.json(
            {
                "validation": result.validation.status,
                "warnings": result.validation.warnings,
                "agent_rounds": result.agent_rounds,
                "tool_calls": result.tool_calls,
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
            }
        )


if __name__ == "__main__":
    main()
