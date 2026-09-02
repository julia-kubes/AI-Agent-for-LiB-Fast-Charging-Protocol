# Structured protocol v2

## Purpose

Branch: `codex/structured-protocol-v2`

This branch responds to the first concrete-protocol evaluation, where outputs were
longer but still vague and included unsupported currents that passed because they
were merely labeled as extrapolations. Version 2 replaces narrative protocol steps
with structured parameter records and replaces free extrapolation with **anchored
extrapolation**.

## Central design rules

1. Return one primary protocol.
2. Return at most one alternative, and only if it is materially different.
3. Present stages as a table-like structure rather than paragraphs.
4. Every operational value is `reported`, `anchored_extrapolation`, or `unresolved`.
5. An extrapolated value requires a cited source value and an explicit adjustment
   rule. Disclosure alone is insufficient.
6. Unresolved values must be represented as `null`; vague prose cannot substitute
   for a parameter.
7. An `executable_candidate` cannot contain unresolved critical parameters.
8. Structurally rejected output receives one repair attempt with tools disabled.
9. Output that remains invalid after repair is not displayed as a protocol.

## Output structure

Each protocol has:

- A `primary` or `alternative` designation.
- An `executable_candidate` or `partially_specified` status.
- Structured target conditions.
- An ordered set of numbered stages.
- A validation plan, limitations, confidence, and evidence citations.
- A protocol-level extrapolation summary when applicable.

Each stage has:

- Stage number and name.
- Control mode: CC, CV, rest, terminate, or other.
- Start condition.
- Structured current.
- Structured voltage limit.
- Structured temperature limit.
- Structured transition criterion.
- Monitoring requirements.
- Stop conditions.

Each structured parameter has:

- Proposed value and unit.
- Evidence basis.
- Cited source value and unit when extrapolated.
- Source conditions.
- Adjustment rule.
- Scientific rationale.
- Field-level evidence chunk IDs.
- Confidence.

## Anchored extrapolation

Version 1 allowed an unsupported value to pass with a warning when extrapolation
was disclosed. Version 2 requires an auditable chain:

```text
cited reported value
→ source conditions
→ explicit adjustment rule
→ proposed target value
→ scientific rationale
```

For example, reducing a reported 6C value to a proposed 4C requires the response to
cite evidence containing 6C, describe the cell on which 6C was reported, state that
the proposed value is 4C, and explain the rule and reason for the reduction.

## Files changed

### `app/prompts.py`

- Replaced the narrative protocol objective with a table-oriented output contract.
- Limited output to one primary and at most one materially different alternative.
- Prohibited selecting values merely because they appear plausible or meet a time
  target.
- Defined reported, anchored-extrapolated, and unresolved parameter records.
- Required measurable transition criteria for executable candidates.
- Added a dedicated deterministic-validation repair instruction.

### `app/validation.py`

- Enforces the primary/alternative designations and two-protocol limit.
- Requires structured target conditions and sequential stage numbers.
- Validates control modes and measurable transition fields.
- Validates every current, voltage, temperature, and transition parameter.
- Checks that reported values appear in field-level cited evidence.
- Checks that extrapolated source values appear in cited evidence.
- Requires source conditions, an adjustment rule, rationale, and citations for every
  anchored extrapolation.
- Requires unresolved parameters to use `null` values.
- Rejects executable candidates containing unresolved critical parameters.
- Detects common vague operational phrases and emits warnings.

### `app/agent.py`

- Adds one repair attempt when valid JSON fails deterministic protocol validation.
- Disables tools during repair.
- Stops with an error when the repaired protocol still fails validation rather than
  presenting a rejected protocol to the user.

### `app/ui.py`

- Replaces paragraph-style stages with a protocol table.
- Displays stage, mode, start, current, voltage limit, temperature limit, and
  transition in fixed columns.
- Keeps stage-specific monitoring and stop conditions adjacent to the table.
- Shows protocol designation, readiness status, confidence, evidence, extrapolation
  disclosure, and validation plan.
- Updates copied Markdown output to use the same table structure.

### `evaluation/run_evaluation.py`

- Updates collaborator-friendly evaluation reports to render the structured
  protocol table and target conditions.
- Preserves extrapolation disclosures and validation plans for comparison.

### `app/demo.py`

- Updates the offline demonstration to the v2 schema.
- Uses a partially specified protocol with null values because the synthetic demo
  evidence contains no defensible numerical protocol.

### Tests

- `tests/test_validation.py` now tests a fully structured reported protocol,
  field-level citations, anchored extrapolation, rejection of unanchored
  extrapolation, and rejection of unresolved executable protocols.
- `tests/test_agent.py` verifies one validation-repair attempt with tools disabled.
- `tests/test_ui.py` verifies the table-style protocol rendering and retains legacy
  presentation-tolerance tests.

## Verification

- 23 unit tests pass.
- Application and evaluation modules compile.
- Git whitespace checks pass.
- The offline end-to-end CLI returns a v2 response with `validation=pass`.

## Remaining limitations

- Text matching confirms that a reported or source value appears in cited evidence;
  it does not prove scientific entailment.
- An explicit adjustment rule can be scientifically weak even when structurally
  complete. Human review remains necessary.
- The retrieval system must still recover protocol tables and complete schedules.
  The stricter output contract cannot reconstruct information absent from the
  retrieved evidence.
- Live evaluation is still required to determine whether the selected model can
  reliably satisfy the larger structured schema without excessive repair calls.

