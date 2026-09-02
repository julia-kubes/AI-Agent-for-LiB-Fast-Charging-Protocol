"""Minimal Streamlit interface for the fast-charging literature assistant."""

from __future__ import annotations

import base64
import os
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from app.agent import ResearchAgent
from app.config import Settings
from app.demo import DemoLLM, DemoRetrieval
from app.llm_client import OpenAICompatibleLLM
from app.presentation import text_items
from app.retrieval_adapter import NeonRetrievalAdapter


def format_response_for_clipboard(answer: dict[str, Any]) -> str:
    """Format every generated-answer field as readable Markdown text."""

    lines = ["# Fast-Charging Literature Assistant Response", ""]
    summary = str(answer.get("summary") or "").strip()
    lines.extend(["## Summary", "", summary or "No summary provided.", ""])

    lines.extend(["## Protocol suggestions", ""])
    suggestions = answer.get("protocol_suggestions") or []
    if not suggestions:
        lines.extend(["No protocol suggestions provided.", ""])
    for index, suggestion in enumerate(suggestions, start=1):
        lines.extend(
            [
                f"### {index}. {suggestion.get('strategy', 'Suggestion')}",
                "",
                str(suggestion.get("rationale") or ""),
                "",
                f"- Origin: {suggestion.get('reported_or_inferred', 'unknown')}",
                f"- Confidence: {suggestion.get('confidence', 'unknown')}",
                "- Applicable conditions: "
                + "; ".join(
                    text_items(
                        suggestion.get("applicable_conditions"), ["Not provided"]
                    )
                ),
                "- Extrapolation used: "
                + str((suggestion.get("extrapolation") or {}).get("used", False)),
                "- Limitations: "
                + "; ".join(
                    text_items(suggestion.get("limitations"), ["Not provided"])
                ),
                "- Evidence chunks: "
                + ", ".join(
                    text_items(suggestion.get("evidence_chunk_ids"), ["None"])
                ),
                "",
            ]
        )
        steps = suggestion.get("protocol_steps") or []
        lines.extend(["#### Protocol steps", ""])
        for step_index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            lines.extend(
                [
                    f"{step_index}. **{step.get('stage', 'Stage')}**",
                    f"   - Current/C-rate: {step.get('current_or_c_rate', 'Unresolved')}",
                    f"   - Start: {step.get('start_condition', 'Not provided')}",
                    f"   - Transition: {step.get('transition_criterion', 'Not provided')}",
                    "   - Temperature constraints: "
                    + "; ".join(text_items(step.get("temperature_constraints"), ["Not provided"])),
                    "   - Monitoring: "
                    + "; ".join(text_items(step.get("monitoring"), ["Not provided"])),
                    "   - Stop conditions: "
                    + "; ".join(text_items(step.get("stop_conditions"), ["Not provided"])),
                    f"   - Value basis: {step.get('value_basis', 'unknown')}",
                    "",
                ]
            )
        extrapolation = suggestion.get("extrapolation") or {}
        if extrapolation.get("used"):
            lines.extend(
                [
                    "#### Extrapolation disclosure",
                    "",
                    f"- Justification: {extrapolation.get('justification', '')}",
                    "- Source conditions: "
                    + "; ".join(text_items(extrapolation.get("source_conditions"))),
                    "- Target conditions: "
                    + "; ".join(text_items(extrapolation.get("target_conditions"))),
                    "- Key differences: "
                    + "; ".join(text_items(extrapolation.get("key_differences"))),
                    "",
                ]
            )
        lines.extend(
            [
                "#### Validation plan",
                "",
                *[
                    f"- {item}"
                    for item in text_items(suggestion.get("validation_plan"))
                ],
                "",
            ]
        )

    for heading, field in (
        ("Conflicting evidence", "conflicting_evidence"),
        ("Missing information", "missing_information"),
        ("Safety notes", "safety_notes"),
        ("Follow-up questions", "follow_up_questions"),
    ):
        lines.extend([f"## {heading}", ""])
        values = text_items(answer.get(field))
        lines.extend([f"- {value}" for value in values] or ["None provided."])
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def show_copy_button(response_text: str) -> None:
    """Render a browser-side copy button without sending response text elsewhere."""

    encoded = base64.b64encode(response_text.encode("utf-8")).decode("ascii")
    components.html(
        f"""
        <div style="display:flex;align-items:center;gap:0.75rem;font-family:sans-serif;">
          <button id="copy-response" style="
            border:1px solid rgba(49,51,63,0.2);border-radius:0.5rem;
            background:white;color:#31333f;padding:0.45rem 0.8rem;cursor:pointer;
            font-size:0.95rem;">
            Copy entire response
          </button>
          <span id="copy-status" role="status" style="font-size:0.9rem;"></span>
        </div>
        <script>
          const encodedResponse = "{encoded}";
          const responseBytes = Uint8Array.from(atob(encodedResponse), c => c.charCodeAt(0));
          const responseText = new TextDecoder().decode(responseBytes);
          const button = document.getElementById("copy-response");
          const status = document.getElementById("copy-status");

          button.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText(responseText);
              status.textContent = "Copied!";
            }} catch (error) {{
              const temporary = document.createElement("textarea");
              temporary.value = responseText;
              temporary.style.position = "fixed";
              temporary.style.opacity = "0";
              document.body.appendChild(temporary);
              temporary.select();
              const copied = document.execCommand("copy");
              temporary.remove();
              status.textContent = copied ? "Copied!" : "Copy failed";
            }}
          }});
        </script>
        """,
        height=48,
    )


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
    with st.expander("Optional Specifications"):
        chemistry = st.text_input("Cell chemistry")
        form_factor = st.text_input("Form factor")
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
            "form_factor": form_factor,
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
    show_copy_button(format_response_for_clipboard(result.answer))
    st.subheader("Summary")
    st.write(result.answer.get("summary", ""))
    st.subheader("Protocol suggestions")
    for suggestion in result.answer.get("protocol_suggestions", []):
        st.markdown(f"**{suggestion.get('strategy', 'Suggestion')}**")
        st.write(suggestion.get("rationale", ""))
        st.caption(
            f"Confidence: {suggestion.get('confidence', 'unknown')} · "
            "Evidence: "
            + ", ".join(text_items(suggestion.get("evidence_chunk_ids"), ["None"]))
        )
        steps = suggestion.get("protocol_steps") or []
        if steps:
            st.markdown("**Candidate protocol**")
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    continue
                st.markdown(f"**Stage {index}: {step.get('stage', 'Stage')}**")
                st.write(f"Current/C-rate: {step.get('current_or_c_rate', 'Unresolved')}")
                st.write(f"Start: {step.get('start_condition', 'Not provided')}")
                st.write(f"Transition: {step.get('transition_criterion', 'Not provided')}")
                st.write(
                    "Temperature constraints: "
                    + "; ".join(text_items(step.get("temperature_constraints"), ["Not provided"]))
                )
                st.write(
                    "Monitoring: "
                    + "; ".join(text_items(step.get("monitoring"), ["Not provided"]))
                )
                st.write(
                    "Stop conditions: "
                    + "; ".join(text_items(step.get("stop_conditions"), ["Not provided"]))
                )
                st.caption(f"Value basis: {step.get('value_basis', 'unknown')}")
        extrapolation = suggestion.get("extrapolation") or {}
        if extrapolation.get("used"):
            st.markdown("**Extrapolation disclosure**")
            st.write(extrapolation.get("justification", ""))
            st.caption(
                "Key source–target differences: "
                + "; ".join(text_items(extrapolation.get("key_differences"), ["Not provided"]))
            )
        validation_plan = text_items(suggestion.get("validation_plan"))
        if validation_plan:
            st.markdown("**Validation plan**")
            for item in validation_plan:
                st.write(f"- {item}")

    for heading, field in (
        ("Conflicting evidence", "conflicting_evidence"),
        ("Missing information", "missing_information"),
        ("Safety notes", "safety_notes"),
        ("Follow-up questions", "follow_up_questions"),
    ):
        values = text_items(result.answer.get(field))
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
