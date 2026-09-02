"""Run repeatable demo or explicitly enabled live evaluations."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.agent import ResearchAgent
from app.config import Settings
from app.demo import DemoLLM, DemoRetrieval
from app.llm_client import OpenAICompatibleLLM
from app.presentation import text_items
from app.retrieval_adapter import NeonRetrievalAdapter


ROOT = Path(__file__).resolve().parent


def _safe_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def _parameter_text(parameter: Any) -> str:
    if not isinstance(parameter, dict) or parameter.get("value") is None:
        return "Unresolved"
    return f"{parameter['value']} {parameter.get('unit', '')} ({parameter.get('basis', 'unknown')})"


def _transition_text(transition: Any) -> str:
    if not isinstance(transition, dict) or transition.get("value") is None:
        return "Unresolved"
    return (
        f"{transition.get('variable', 'value')} {transition.get('operator', '')} "
        f"{transition['value']} {transition.get('unit', '')} "
        f"({transition.get('basis', 'unknown')})"
    )


def _answer_markdown(answer: dict[str, Any]) -> list[str]:
    lines = ["### Generated answer", "", answer.get("summary", "") or "*(No summary.)*", ""]
    suggestions = answer.get("protocol_suggestions") or []
    lines.extend(["#### Protocol suggestions", ""])
    if not suggestions:
        lines.extend(["*(No protocol suggestions.)*", ""])
    for index, suggestion in enumerate(suggestions, start=1):
        lines.extend(
            [
                f"**{index}. {suggestion.get('strategy', 'Unnamed suggestion')}**",
                "",
                f"- Designation: `{suggestion.get('designation', 'not supplied')}`",
                f"- Protocol status: `{suggestion.get('protocol_status', 'not supplied')}`",
                f"- Origin: `{suggestion.get('reported_or_inferred', 'not supplied')}`",
                f"- Confidence: `{suggestion.get('confidence', 'not supplied')}`",
                f"- Rationale: {suggestion.get('rationale', '')}",
                "- Target conditions: "
                + "; ".join(
                    f"{key}={value}"
                    for key, value in (suggestion.get("target_conditions") or {}).items()
                ),
                "- Extrapolation used: "
                + str((suggestion.get("extrapolation") or {}).get("used", False)),
                "- Limitations: "
                + "; ".join(
                    text_items(suggestion.get("limitations"), ["not supplied"])
                ),
                "- Evidence chunks: "
                + ", ".join(
                    f"`{item}`"
                    for item in text_items(suggestion.get("evidence_chunk_ids"))
                ),
                "",
            ]
        )
        steps = suggestion.get("protocol_steps") or []
        lines.extend(
            [
                "##### Candidate protocol table",
                "",
                "| Stage | Mode | Start | Current | Voltage limit | Temperature limit | Transition |",
                "|---:|---|---|---|---|---|---|",
            ]
        )
        for step_index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            lines.append(
                f"| {step.get('stage_number', step_index)}. {_safe_cell(step.get('stage_name', 'Stage'))} "
                f"| {_safe_cell(step.get('control_mode'))} | {_safe_cell(step.get('start_condition'))} "
                f"| {_safe_cell(_parameter_text(step.get('current')))} "
                f"| {_safe_cell(_parameter_text(step.get('voltage_limit')))} "
                f"| {_safe_cell(_parameter_text(step.get('temperature_limit')))} "
                f"| {_safe_cell(_transition_text(step.get('transition')))} |"
            )
            lines.extend(
                [
                    "",
                    f"- Stage {step_index} monitoring: "
                    + "; ".join(text_items(step.get("monitoring"), ["not supplied"])),
                    f"- Stage {step_index} stop conditions: "
                    + "; ".join(text_items(step.get("stop_conditions"), ["not supplied"])),
                    "",
                ]
            )
        extrapolation = suggestion.get("extrapolation") or {}
        if extrapolation.get("used"):
            lines.extend(
                [
                    "##### Extrapolation disclosure",
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
        lines.extend(["##### Validation plan", ""])
        lines.extend(
            [f"- {item}" for item in text_items(suggestion.get("validation_plan"))]
            or ["*(Not supplied.)*"]
        )
        lines.append("")
    for heading, field in (
        ("Conflicting evidence", "conflicting_evidence"),
        ("Missing information", "missing_information"),
        ("Safety notes", "safety_notes"),
        ("Follow-up questions", "follow_up_questions"),
    ):
        values = text_items(answer.get(field))
        lines.extend([f"#### {heading}", ""])
        lines.extend([f"- {value}" for value in values] or ["*(None supplied.)*"])
        lines.append("")
    return lines


def write_report(results: list[dict[str, Any]], path: Path, mode: str, model: str) -> None:
    lines = [
        "# Five-query live RAG evaluation",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Mode: `{mode}`",
        f"- Model: `{model}`",
        f"- Query count: {len(results)}",
        "- Purpose: diagnose retrieval relevance, protocol specificity, analogue transfer, and appropriate refusal.",
        "",
        "The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.",
        "",
    ]
    for index, item in enumerate(results, start=1):
        lines.extend(
            [
                f"## Query {index}: {item.get('label', item['id'])}",
                "",
                "### Exact query",
                "",
                f"> {item['question']}",
                "",
                "### Intended test",
                "",
                item.get("what_it_tests", "Not specified."),
                "",
            ]
        )
        conditions = item.get("conditions") or {}
        lines.extend(["### Supplied operating conditions", ""])
        lines.extend([f"- {key}: {value}" for key, value in conditions.items()] or ["*(None.)*"])
        lines.append("")
        if item.get("error"):
            lines.extend(["### Execution result", "", f"**ERROR:** {item['error']}", ""])
            continue
        lines.extend(
            [
                "### Execution and validation",
                "",
                f"- Validation: `{item['validation']}`",
                f"- Warnings: {len(item['warnings'])}",
                f"- Agent rounds: {item['agent_rounds']}",
                f"- Tool calls: {item['tool_calls']}",
                f"- JSON repair attempts: {item['repair_attempts']}",
                f"- Input tokens: {item['input_tokens']}",
                f"- Output tokens: {item['output_tokens']}",
                f"- Total tokens: {item['input_tokens'] + item['output_tokens']}",
                f"- Elapsed seconds: {item['elapsed_seconds']}",
                f"- Retrieved chunks retained: {len(item['evidence'])}",
                f"- Distinct papers retained: {len({e['record_id'] for e in item['evidence']})}",
                "",
            ]
        )
        if item["warnings"]:
            lines.extend(["#### Validation warnings", ""])
            lines.extend([f"- {warning}" for warning in item["warnings"]])
            lines.append("")
        lines.extend(_answer_markdown(item["answer"]))
        lines.extend(
            [
                "### Retrieved evidence",
                "",
                "| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |",
                "|---:|---|---|---|---:|---:|---|",
            ]
        )
        for rank, evidence in enumerate(item["evidence"], start=1):
            metadata = evidence.get("metadata") or {}
            lines.append(
                f"| {rank} | {_safe_cell(evidence.get('title') or evidence['record_id'])} | "
                f"{_safe_cell(evidence.get('section') or 'unknown')} | {_safe_cell(evidence.get('page_numbers'))} | "
                f"{_safe_cell(metadata.get('reranker_score'))} | {_safe_cell(metadata.get('vector_similarity'))} | "
                f"`{evidence['chunk_id']}` |"
            )
        lines.extend(["", "#### Evidence excerpts", ""])
        for rank, evidence in enumerate(item["evidence"], start=1):
            excerpt = " ".join(evidence["text"].split())
            if len(excerpt) > 700:
                excerpt = excerpt[:697] + "..."
            lines.extend([f"**{rank}. `{evidence['chunk_id']}`**", "", excerpt, ""])
        lines.extend(["---", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, default=ROOT / "questions.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "results.jsonl")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--live",
        action="store_true",
        help="use configured Neon and Parley services; consumes API credits",
    )
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    settings = Settings.from_env()
    if args.live:
        if not settings.database_url:
            raise SystemExit("DATABASE_URL is required for --live")
        settings.require_llm()
        agent = ResearchAgent(
            NeonRetrievalAdapter(settings.database_url, settings.embedding_model),
            OpenAICompatibleLLM(settings),
            settings,
        )
    else:
        agent = ResearchAgent(DemoRetrieval(), DemoLLM(), settings)

    questions = []
    with args.questions.open("r", encoding="utf-8") as source:
        for line in source:
            if line.strip():
                questions.append(json.loads(line))
    if args.limit is not None:
        if args.limit < 1:
            raise SystemExit("--limit must be positive")
        questions = questions[: args.limit]

    results = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(questions, start=1):
        print(f"[{index}/{len(questions)}] {item['id']}: {item['question']}", flush=True)
        started = time.perf_counter()
        try:
            result = agent.answer(item["question"], item.get("conditions"))
            recorded = {
                **item,
                "answer": result.answer,
                "evidence": [chunk.to_dict() for chunk in result.evidence],
                "validation": result.validation.status,
                "errors": list(result.validation.errors),
                "warnings": list(result.validation.warnings),
                "agent_rounds": result.agent_rounds,
                "tool_calls": result.tool_calls,
                "repair_attempts": result.repair_attempts,
                "input_tokens": result.usage.input_tokens,
                "output_tokens": result.usage.output_tokens,
                "elapsed_seconds": round(time.perf_counter() - started, 2),
                "demo": not args.live,
                "model": settings.llm_model if args.live else "demo",
            }
        except Exception as error:
            recorded = {
                **item,
                "error": f"{type(error).__name__}: {error}",
                "elapsed_seconds": round(time.perf_counter() - started, 2),
                "demo": not args.live,
                "model": settings.llm_model if args.live else "demo",
            }
        results.append(recorded)
        with args.output.open("w", encoding="utf-8", newline="\n") as output:
            for saved in results:
                output.write(json.dumps(saved, ensure_ascii=False) + "\n")
        if args.report:
            write_report(
                results,
                args.report,
                "live" if args.live else "demo",
                settings.llm_model if args.live else "demo",
            )
        print(f"    saved ({recorded.get('validation', 'error')})", flush=True)
    print(f"Wrote {len(results)} evaluation result(s) to {args.output}")
    if args.report:
        print(f"Wrote readable report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
