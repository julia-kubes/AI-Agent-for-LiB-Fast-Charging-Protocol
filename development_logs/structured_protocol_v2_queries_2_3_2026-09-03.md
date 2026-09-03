# Structured protocol v2 — Queries 2 and 3 live comparison

- Generated: 2026-09-03T20:24:33.378043+00:00
- Mode: `live`
- Model: `gpt-5.4-mini`
- Query count: 2
- Branch/version: `codex/structured-protocol-v2`
- Final-attempt output ceiling: 6,000 tokens
- Purpose: compare the structured, evidence-anchored protocol version against the earlier concrete-protocol v1 results using the same Query 2 and Query 3 wording.

The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.

## Comparison summary

| Source query | Concrete protocol v1 | Structured protocol v2 | What the v2 result shows |
|---|---|---|---|
| Q2 — NMC811 pouch cell | `pass_with_warnings`; 104.21 s; 2 protocols | **Error**; 115.05 s on the documented 6,000-token run | The model's repaired final response was not valid JSON, so no protocol was accepted or displayed. |
| Q3 — NCM523 laboratory cell | `pass_with_warnings`; 97.54 s; 3 protocols | **Error**; 111.35 s on the documented 6,000-token run | The model generated protocols, but validation rejected three current/transition values because the stated source values could not be found in the cited evidence. |

The first v2 attempt used the application's default 3,000-token ceiling. Both answers exhausted that allowance and remained truncated after one repair attempt (Q2: 127.20 s; Q3: 70.52 s). The unchanged queries were then rerun at 6,000 tokens. This removed simple truncation as the recorded final failure, but exposed output-format and evidence-grounding failures instead. No application code or prompt criteria were changed between these attempts.

These are failed test executions rather than usable protocol recommendations. That distinction is important: compared with v1, v2's safeguards prevented vague or unsupported output from being presented as a valid protocol, but the generation/repair path does not yet reliably satisfy the stricter schema.

## Query 2: Specific NMC811 pouch-cell target

### Exact query

> Propose an evidence-supported starting fast-charge protocol for a 5 Ah graphite/NMC811 pouch cell at 25 °C, charging from 10% to 80% SOC with a target time of 20 minutes while limiting lithium plating. Give current stages and transition criteria only when supported, and clearly identify values that cannot be determined from the evidence.

### Intended test

Structured protocol v2: whether the system produces one table-ready primary protocol, uses field-level citations, leaves unsupported parameters unresolved, and permits only evidence-anchored extrapolation.

### Supplied operating conditions

- chemistry: graphite/NMC811
- form_factor: 5 Ah pouch cell
- temperature: 25 °C
- soc_range: 10-80%
- objective: target 20 minutes while limiting lithium plating

### Execution result

**ERROR:** ValueError: Model final answer is not valid JSON

- Elapsed time: 115.05 seconds
- Interpretation: the final response could not be parsed into the required structured protocol schema, even after the agent's single bounded repair attempt.

## Query 3: Known NCM523 evidence target

### Exact query

> Using retrieved experimental evidence, describe a starting fast-charge protocol design for an NCM523/graphite laboratory cell at 30 °C over 0-80% SOC that is intended to avoid lithium plating. Distinguish directly reported protocol elements from synthesis and inference.

### Intended test

Structured protocol v2: whether retrieval recovers the known Part V evidence and converts it into measurable structured stages without vague transitions or unanchored numerical extrapolation.

### Supplied operating conditions

- chemistry: NCM523/graphite
- form_factor: laboratory cell
- temperature: 30 °C
- soc_range: 0-80%
- objective: avoid lithium plating

### Execution result

**ERROR:** RuntimeError: LLM protocol remained invalid after one repair attempt: protocol_suggestions[1].protocol_steps[1].transition source value was not found in its cited evidence; protocol_suggestions[2].protocol_steps[1].transition source value was not found in its cited evidence; protocol_suggestions[2].protocol_steps[2].current source value was not found in its cited evidence

- Elapsed time: 111.35 seconds
- Interpretation: the structural response was far enough along for field-level validation, but the validator found three claimed evidence anchors that did not exist in their cited passages. The tool therefore withheld the protocols instead of presenting unsupported numerical details.

## Suggested next iteration

The next development step should focus on making the model produce a smaller schema reliably: one primary protocol and no alternative unless the primary validates, shorter citation metadata, and a repair prompt containing only the invalid fields plus the relevant evidence excerpts. This would preserve the stricter safeguards without asking the model to regenerate the entire large response.
