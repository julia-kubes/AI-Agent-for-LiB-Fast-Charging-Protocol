# Concrete protocol branch: implementation summary

## Branch and purpose

- Branch: `codex/concrete-protocol-output`
- Concrete-protocol implementation commit: `d1b9a91`
- Retrieval-integration merge commit: `647df92`
- Starting branch: `llm-rag-integration`

This branch tests a different balance between evidence conservatism and practical
usefulness. The original application generally avoided giving numerical protocol
details unless they appeared directly in retrieved evidence. This branch instead
asks the model to produce one or more concrete **experimental candidate charging
protocols** whenever the available literature can support a reasonable starting
point.

Extrapolation is permitted, but it must be visible and auditable. The model must
identify adapted values, describe the source and target conditions, explain why the
transfer may be reasonable, disclose important differences, lower confidence when
appropriate, and propose a conservative validation plan. The output must not claim
that a literature-derived or extrapolated protocol is universally safe, optimized,
or ready for deployment.

## Summary of the behavioral change

The intended output changed from a broad recommendation such as:

> Use a staged charging strategy and validate it for the target cell.

to a structured candidate protocol containing:

1. An ordered sequence of charging stages.
2. Current or C-rate for each stage, or an explicit unresolved value.
3. Starting conditions and transition criteria.
4. Temperature constraints.
5. Required measurements and monitoring.
6. Stop conditions.
7. A label identifying each value as reported, extrapolated, or unresolved.
8. Source-to-target extrapolation details.
9. A staged experimental validation plan.
10. Evidence references, limitations, and confidence.

## Script-by-script changes

### `app/prompts.py`

This file contains the principal behavior change. It defines the system prompt,
the requested final-answer structure, the tools available to the model, and the
instructions used for initial generation and repair.

#### System-prompt objective

The prompt now states that the primary objective is to create one or more concrete
candidate charging protocols that a qualified researcher could evaluate. It no
longer encourages the model to avoid all extrapolation merely because an exact
literature match is unavailable.

The new instructions ask for:

- Ordered charging stages.
- Current or C-rate.
- SOC- and/or voltage-based starting and transition conditions.
- Temperature constraints.
- Monitoring requirements.
- Stop conditions.
- A conservative validation plan.

#### Extrapolation policy

The prompt distinguishes four evidence origins:

- `reported`: directly stated in cited evidence.
- `synthesized`: constructed by combining findings from cited sources.
- `extrapolated`: adapted from source conditions to different target conditions.
- `inferred`: reasoned from the evidence but not directly reported or presented as
  a specific source-to-target transfer.

When extrapolation is used, the prompt requires the model to:

- Label adapted or estimated values.
- Identify source conditions.
- Identify target conditions.
- Explain the transfer rationale.
- Identify important source-target differences.
- Reduce confidence appropriately.
- Avoid false numerical precision.
- Describe how the candidate protocol should be tested before escalation.

#### Preserved safety boundaries

The prompt still prohibits the model from:

- Presenting extrapolated values as directly reported.
- Claiming that a literature-derived protocol is validated for deployment.
- Issuing commands to charging hardware.
- Omitting known conflicts or missing operating conditions.
- Producing a protocol when the evidence cannot support even a conservative
  experimental starting point.

The prompt continues to limit the response to no more than three candidate
protocols.

#### Expanded output contract

Each protocol suggestion now includes `protocol_steps`. Every step requests:

- `stage`
- `current_or_c_rate`
- `start_condition`
- `transition_criterion`
- `temperature_constraints`
- `monitoring`
- `stop_conditions`
- `value_basis`

Each suggestion also includes an `extrapolation` object containing:

- `used`
- `source_conditions`
- `target_conditions`
- `justification`
- `key_differences`

A nonempty `validation_plan` is also required.

The existing summary, rationale, citations, applicable conditions, limitations,
confidence, conflicting evidence, missing information, safety notes, and follow-up
questions remain part of the response.

### `app/validation.py`

The deterministic validator was expanded so that the new structure is not merely
a suggestion in the prompt.

#### New accepted classifications

`extrapolated` was added to the permitted origin classifications. Protocol-step
values must be labeled as one of:

- `reported`
- `extrapolated`
- `unresolved`

#### Required protocol fields

Every protocol suggestion must now contain the complete set of expected fields,
including protocol steps, extrapolation details, and a validation plan. A protocol
with no steps is rejected.

Every step is checked for all required fields. Missing stage details or an invalid
`value_basis` cause rejection.

#### Maximum number of protocols

The limit of three protocols is now enforced in application code. Previously, this
limit existed only as a prompt instruction.

#### Extrapolation disclosure enforcement

If a suggestion is classified as extrapolated, its `extrapolation.used` value must
be true. When extrapolation is used, the following fields must be nonempty:

- Source conditions.
- Target conditions.
- Justification.
- Key differences.

An extrapolated suggestion that hides or omits these details is rejected.

#### Numerical evidence checking

The numerical checker now examines protocol steps and applicable conditions in
addition to the strategy and rationale. It detects values with common charging
units, including C-rate, current, voltage, temperature, SOC, and time.

The result depends on how the value is presented:

- A numerical value found verbatim in the cited evidence can pass normally.
- A value not found in the cited evidence is rejected when extrapolation has not
  been disclosed.
- A value not found in the cited evidence can proceed with a warning when the
  suggestion contains a complete extrapolation disclosure.

This policy permits practical candidate values while preventing the model from
silently presenting an estimated value as a published result.

#### Validation-plan requirement

Every protocol suggestion must have a nonempty validation plan. A concrete
protocol without a proposed path for cell-specific verification is rejected.

### `app/ui.py`

The Streamlit interface and clipboard export were expanded to present the new
protocol structure in a readable form.

#### Candidate protocol display

For every stage, the UI now displays:

- Stage name.
- Current or C-rate.
- Starting condition.
- Transition criterion.
- Temperature constraints.
- Monitoring requirements.
- Stop conditions.
- Whether the values are reported, extrapolated, or unresolved.

#### Extrapolation display

When extrapolation is used, the UI shows a separate disclosure section with the
transfer justification and important source-target differences. This keeps the
disclosure visible rather than burying it in a general limitations paragraph.

#### Validation-plan display

The experimental validation plan is displayed directly beneath each proposed
protocol.

#### Clipboard export

The full response-copying function was updated to include protocol steps,
extrapolation details, and the validation plan. Copied reports therefore retain the
information needed for review by collaborators.

This file also contains earlier UI work that was present before the concrete-
protocol branch was created, including response-copy support and tolerant handling
of model fields that arrive as a single string instead of a list.

### `app/demo.py`

The deterministic offline model was updated to return a response matching the new
contract.

The demonstration response now contains:

- A candidate workflow with an ordered step.
- An unresolved current value rather than a fabricated number.
- Monitoring and stop conditions.
- An explicit extrapolation disclosure.
- A validation plan.
- Low confidence and a warning that the evidence is synthetic.

This keeps offline development and tests functional without representing synthetic
evidence as a real charging recommendation.

### `evaluation/run_evaluation.py`

The readable Markdown report generator was updated to preserve the new output
fields. Evaluation reports now show:

- Whether extrapolation was used.
- Every candidate protocol stage.
- Current or C-rate.
- Start and transition conditions.
- Temperature constraints.
- Monitoring requirements.
- Stop conditions.
- Value basis.
- Source and target extrapolation conditions.
- Transfer justification.
- Key differences.
- Experimental validation plan.

This allows the new branch to be compared with the earlier baseline at the level of
actual protocol specificity rather than only summary quality.

### `tests/test_validation.py`

The baseline valid-answer fixture was expanded to contain a complete protocol step,
extrapolation object, and validation plan.

Two important behavioral tests were added:

1. An unsupported numerical value without extrapolation disclosure must be
   rejected.
2. The same kind of unsupported numerical value may pass with a warning when the
   extrapolation is fully disclosed.

These tests encode the central design goal of this branch: permit accountable
extrapolation, but reject hidden extrapolation.

### `tests/test_ui.py`

The UI formatting tests were expanded to verify that copied output includes:

- Protocol-stage names.
- Current values.
- SOC transitions.
- Extrapolation rationale.
- Source-target differences.
- Validation-plan steps.

The preexisting tests for empty protocol lists and string-versus-list normalization
remain in place.

### `app/presentation.py`

This helper was already present as uncommitted work when the concrete-protocol
branch was created and was committed with the branch state.

It normalizes model-produced values for display. In particular, it prevents a
single string from being treated as a sequence of individual characters when a
list was expected. Both the UI and evaluation report use this helper.

Although it was not introduced specifically for extrapolation, it is important to
the new protocol display because many new fields contain lists of constraints,
measurements, and validation steps.

## Non-script artifacts committed with the branch

The following earlier work was present in the working tree and was committed with
the concrete-protocol implementation after explicit approval:

- `DEVELOPMENT_LOG.md`
- `development_logs/live_evaluation_2026-09-01.md`
- `AI_Query_System_Flow.png`
- `AI_Query_System_Flow_Horizontal.png`
- `Agentic_Loop_Figure.svg`
- `Agentic_Loop_Figure_4K.png`

These files document prior evaluation results and provide presentation diagrams.
They do not change runtime protocol-generation behavior.

## Collaborator retrieval changes merged afterward

The collaborator's retrieval changes originated on `origin/app-experimental`.
They were first incorporated into the local `llm-rag-integration` branch and then
merged into this branch in commit `647df92`.

Those changes are intentionally separate from the concrete-protocol design and
include:

- `app/retrieval_adapter.py`
- `retrieval/retrieval.v2.py`
- `retrieval/retrieval.v3.py`
- `import-paper-metadata.py`
- `tests/test_retrieval_adapter.py`
- `tests/test_retrieval_v3.py`

The retrieval changes improve evidence selection, section filtering, curated title
handling, review-paper limits, and paper-type metadata. They affect which evidence
the concrete-protocol prompt receives, but they were authored on the collaborator's
branch rather than as part of the concrete-protocol prompt experiment.

## Verification completed

After the concrete-protocol changes:

- All 16 tests then present passed.
- Python compilation passed.
- Git whitespace checks passed.
- The offline CLI completed with `validation=pass` using the expanded schema.

After the collaborator retrieval changes were merged:

- All 21 tests passed.
- Application, retrieval, and evaluation modules compiled successfully.
- The working tree was clean before this documentation file was added.

## Current safety interpretation

This branch is intended to produce **experimentally actionable hypotheses**, not
validated charging-controller settings. Its safeguards improve traceability but do
not establish electrochemical safety.

Specifically:

- A citation check confirms that a cited chunk was retrieved; it does not prove
  that the chunk logically supports every part of the recommendation.
- The numerical checker uses normalized text matching; it is not a scientific
  entailment model.
- A disclosed extrapolation can pass with a warning, but disclosure does not prove
  that the extrapolation is physically appropriate.
- Manufacturer limits, cell characterization, controlled instrumentation, and
  experimental review remain necessary before applying a candidate protocol.

## Recommended comparison test

Run the existing five-query live evaluation set on this branch and save the results
under new filenames. Compare those answers with the September 1 baseline using the
following criteria:

1. Does each applicable answer contain an executable sequence of stages?
2. Are reported and extrapolated values clearly distinguishable?
3. Are source and target conditions stated?
4. Are source-target differences scientifically meaningful?
5. Are monitoring and stop conditions usable?
6. Is the validation plan sufficiently conservative?
7. Does the output avoid unjustified precision?
8. Does the unsafe universal-protocol challenge still receive an appropriate
   refusal rather than a fabricated protocol?

