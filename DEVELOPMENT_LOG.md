# Development log

This file records implementation bugs, fixes, behavioral changes, and verification
results while the application is under active development. Credentials and raw
database connection information must never be recorded here.

## 2026-09-01 - First five-query live evaluation

**Artifacts**

- Human-readable, query-separated report:
  [`development_logs/live_evaluation_2026-09-01.md`](development_logs/live_evaluation_2026-09-01.md)
- Machine-readable results with full answer and evidence traces:
  [`evaluation/results_live_2026-09-01.jsonl`](evaluation/results_live_2026-09-01.jsonl)
- Reusable five-question set:
  [`evaluation/questions_live_5.jsonl`](evaluation/questions_live_5.jsonl)

**Execution summary**

- Exactly five live Neon-to-Parley queries ran with `gpt-5.4-mini`.
- Four results validated `pass`; the analogue-transfer result validated
  `pass_with_warnings`; no query raised an execution error.
- No JSON repair was required.
- Total usage was 38,465 input tokens and 9,023 output tokens across the five runs.
- Individual runs retained 10-17 evidence chunks from 4-6 distinct papers.
- The readable report reproduces each exact query, supplied conditions, intended
  test, execution metrics, structured answer, evidence table, and evidence excerpts.

**Initial observations for joint review**

- The known NCM523 query recovered the expected Part IV and Part V experimental
  papers and produced more concrete rates than the broad query.
- The unsafe universal-protocol challenge explicitly stated that the requested
  universal claim was unsupported.
- The analogue-transfer query's two warnings flag `10 °C` from the supplied target
  condition as absent verbatim from cited evidence; they do not indicate that a new
  charging current or voltage was fabricated.
- Incorrect chunk-level titles such as `You may also like` remain visible in the
  report and reinforce the title-provenance issue found in the adapter audit.
- Detailed scientific and usability scoring is pending collaborator review.

## 2026-09-01 - Live retrieval adapter audit

**Scope**

- Read-only Neon checks; no Parley calls and no database mutations.
- Audited database mappings, section-heading coverage, live semantic search,
  record-specific filtering, neighboring chunks, metadata lookup, source diversity,
  and metadata completeness.

**Passed checks**

- Live semantic retrieval returned eight ranked chunks from seven distinct papers.
- No introduction, abstract, reference, or bibliography heading appeared in the
  eight default-filter results.
- Record-specific search returned five chunks and no foreign record IDs.
- Neighbor retrieval returned indices 2-6 around index 4, all from the anchor paper.
- Metadata lookup returned the expected metadata object for the top-ranked paper.
- Vector rank, vector similarity, reranker score, page numbers, section paths, stable
  chunk IDs, and record IDs survived adapter mapping.

**Database findings**

- 3,970 chunks represent 69 distinct paper records.
- `paper_metadata` contains 67 rows. `guo_2014` and `spingler_2000` have chunks but
  no metadata; no metadata-only orphan records were found.
- Section headings identify 133 introduction chunks, 157 abstract chunks, and 624
  reference-like chunks. Twenty-two chunks have no headings and therefore cannot be
  excluded using heading rules.
- The top eight results included seven papers; one paper supplied two chunks. One
  title explicitly identified itself as a review.

**Metadata completeness**

- DOI, cathode chemistry, paper title, and review notes: 67/67 records.
- Form factor: 66/67; experimental ambient temperature: 65/67; SOC information:
  58/67; manufacturer or source organization: 43/67.
- The top result's metadata contained useful applicability fields: NCM523/graphite,
  custom reference laboratory cells, 30 C experiments, and 0-80%/0-90% SOC ranges.

**Open quality concerns**

- Some chunk-level `metadata.title` values are incorrect document titles, including
  `You may also like`, `RESEARCH ARTICLE`, and introduction headings. Retrieval output
  currently displays this chunk-level value instead of the cleaner
  `paper_metadata.paper_title` field.
- Two records cannot supply applicability or citation metadata until their mappings
  are repaired.
- The 22 heading-less chunks can bypass section exclusions.
- Review classification is not stored as a dedicated field; detecting reviews from
  title text alone is incomplete.

**Status**

- Adapter functionality passed. Data-cleanup and metadata-consumer changes remain
  open and should be prioritized through the protocol-specificity evaluation.

## Open quality issue - Protocol suggestions are too general

**Observed behavior**

- The application can complete retrieval and generation, but the resulting protocol
  is too general to be practically useful.
- It is not yet clear whether the dominant cause is insufficiently specific retrieved
  evidence, an underspecified user question, an underspecified output contract, or a
  combination of these factors.
- Considerable paper and chunk metadata is available, but much of it is not currently
  used to constrain retrieval, compare source and target cells, or structure the final
  recommendation. Its marginal value and maintenance cost are therefore unclear.

**Questions to resolve**

- Do the top-ranked chunks contain concrete protocol parameters and experimental
  conditions, or mainly qualitative review/background language?
- Does the user input provide enough target conditions: chemistry, form factor,
  capacity, temperature, initial/final SOC, allowable voltage, charging-time goal,
  and degradation or safety objective?
- Does the output schema explicitly require a staged protocol with currents, SOC or
  voltage transition criteria, temperature constraints, monitoring requirements,
  provenance, assumptions, and unresolved values?
- Which metadata fields improve retrieval filters, applicability assessment,
  citations, or user interpretation? Which fields are generated but unused?
- Are review articles or broadly written chunks crowding out primary experimental
  evidence?

**Planned investigation**

1. Save one representative query, its top vector candidates, reranked chunks, and
   final answer as a trace.
2. Judge evidence specificity before changing the prompt: identify which requested
   protocol fields are actually present in the retrieved text.
3. Repeat generation against the same frozen evidence using a more specific protocol
   schema. This isolates prompt/output-contract quality from retrieval quality.
4. Repeat retrieval with primary-paper preference, metadata constraints, and source
   diversity. Compare the answer while holding the generation prompt fixed.
5. Produce a metadata usage inventory: stored field, generation cost, current
   consumer, demonstrated value, and keep/simplify/remove recommendation.
6. Use the comparison to decide whether to change retrieval, prompting, metadata, or
   all three.

**Status**

- Open; deliberately deferred for structured evaluation.

## 2026-08-31 - Truncated or malformed final JSON

**Observed behavior**

- Live retrieval and the Parley request completed, but the CLI crashed with an
  `Unterminated string` JSON decoding error near the end of the model response.
- The Hugging Face authentication warning was unrelated to the failure.

**Cause**

- The 1,500-token output ceiling was too small for some structured answers.
- The provider client's `finish_reason` was discarded, so token-limit truncation
  could not be distinguished from other malformed output.
- The agent attempted strict JSON parsing once and had no bounded recovery path.

**Changes**

- Increased the default and example `MAX_OUTPUT_TOKENS` value from 1,500 to 3,000.
- Preserved `finish_reason` in `ModelReply`.
- Added explicit detection of `finish_reason=length`.
- Added one JSON-only regeneration attempt for truncated or malformed final output.
- Prohibited retrieval tool calls during the repair attempt.
- Added a clear terminal error if the single repair remains truncated or invalid.
- Accepted an otherwise valid JSON object wrapped in one Markdown code fence.
- Limited final output to no more than three concise protocol suggestions.

**Verification**

- Eight offline unit tests pass, including successful one-time repair, bounded
  failure after an invalid repair, and Markdown-fenced JSON parsing.
- Python compilation and Git whitespace checks pass.
- Local configuration resolves `MAX_OUTPUT_TOKENS` to 3,000.
- Pending repeat of the live Parley query that exposed the bug.

**Files changed**

- `.env.example`
- `app/config.py`
- `app/schemas.py`
- `app/llm_client.py`
- `app/prompts.py`
- `app/agent.py`
- `app/validation.py`
- `tests/test_agent.py`
- `tests/test_validation.py`

## 2026-09-01 - Out-of-domain casual-query test

**Exact query**

- `What's up?`

**Intended behavior**

- Recognize that the query is unrelated to lithium-ion fast charging.
- Avoid literature retrieval and protocol generation.
- Respond conversationally or briefly redirect the user toward the application's
  fast-charging scope.

**Observed behavior**

- The agent made one retrieval tool call and retained five chunks from five papers.
- It interpreted the query as an underspecified request for a charging protocol,
  summarized three battery studies, and asked for missing operating conditions.
- The returned object used an alternate refusal schema and failed final validation
  because five required fields were absent.
- Validation status: `reject`; 2 agent rounds; 1 tool call; 3,244 input tokens;
  489 output tokens; 3,733 total tokens; 37.75 seconds; 0 repair attempts.

**Assessment**

- Failed the intended out-of-domain behavior. The response was cautious rather than
  unsafe, but it performed irrelevant retrieval, spent unnecessary tokens, and did
  not comply with the required response schema.
- This exposes the need for explicit scope classification or an out-of-domain path
  before retrieval, plus schema-compatible handling of non-protocol responses.

**Artifacts**

- `evaluation/question_unrelated.jsonl`
- `evaluation/results_unrelated_2026-09-01.jsonl`
- `development_logs/live_evaluation_unrelated_2026-09-01.md`

**Status**

- Resolved on 2026-09-01 with a deterministic pre-retrieval scope gate.

**Implemented fix**

- Added `app/scope.py` to detect inputs with no battery fast-charging domain signal.
- Supplied battery operating conditions keep short or ambiguous prompts in scope.
- Clearly unrelated questions now return a normal schema-valid response before the
  retrieval backend or LLM is called.
- The early response records no evidence, zero agent rounds, zero tool calls, and
  zero token usage.
- Added tests for casual input, a clearly unrelated request, an ordinary in-domain
  charging question, and a short question accompanied by battery conditions.

**Post-fix verification**

- All 11 offline unit tests pass.
- Repeated the exact `What's up?` evaluation through the live-configured runner.
- Post-fix result: `pass`; 0 evidence chunks; 0 agent rounds; 0 tool calls; 0 input
  tokens; 0 output tokens; 0.0 reported seconds.
- The rerun completed inside the network-restricted environment, confirming that it
  made no Parley or Neon request.

**Post-fix artifacts**

- `evaluation/results_unrelated_post_fix_2026-09-01.jsonl`
- `development_logs/live_evaluation_unrelated_post_fix_2026-09-01.md`

**Streamlit verification correction**

- The first manual UI retest still retrieved evidence because the Streamlit process
  started before the scope fix had not reloaded the edited code.
- Its automatic file watcher was repeatedly failing while inspecting optional
  Transformers image modules, so hot reload was not reliable.
- Restarted Streamlit on port 8504 with file watching disabled.
- Submitted the exact query `What's up?` through the rendered UI and confirmed the
  out-of-domain response, no displayed evidence, `pass` validation, 0 agent rounds,
  0 tool calls, and 0 input/output tokens.

## 2026-09-01 - Streamlit specifications and response copying

**Requested changes**

- Rename `Optional operating conditions` to `Optional Specifications`.
- Add `Form factor` as an optional user-supplied specification.
- Add a button that copies the complete generated response to the clipboard.

**Implementation**

- Added the `Form factor` text field and pass non-empty values to the agent as the
  `form_factor` condition.
- Added a Markdown formatter covering summary, every protocol-suggestion field,
  conflicting evidence, missing information, safety notes, and follow-up questions.
- Added a browser-side `Copy entire response` button with visible `Copied!` feedback
  and a compatibility fallback when the modern clipboard API is unavailable.
- The response is copied locally in the browser; it is not sent to another service.
- Added follow-up questions to the visible Streamlit response so all generated
  answer sections are represented in the interface.

**Verification**

- All 13 unit tests pass, including complete-response and out-of-domain clipboard
  formatting tests.
- Restarted the live Streamlit app and verified the renamed panel and `Form factor`
  field in the rendered page.
- Generated an out-of-domain response, clicked the copy button, observed `Copied!`,
  and verified that the clipboard contained the formatted response.

## 2026-09-01 - Manual Tesla pulse-charging prompt retained

- Added the exact prompt `Give me a pulse charging protocol for my 2020 tesla model
  5.` and the complete copied Streamlit response to
  `development_logs/live_evaluation_2026-09-01.md`.
- Labeled it as an additional manual UI evaluation and stated that automated
  execution statistics were not captured, preserving the distinction from the five
  automated live runs.
- The case tests handling of an ambiguous or incorrect model name, missing vehicle
  and pack specifications, mixed pulse-charging evidence, and safety boundaries.

## 2026-09-01 - Character-separated response fields in reports

**Observed behavior**

- Some `limitations` values appeared as `T; h; e; ...` in the live evaluation
  Markdown report.

**Cause**

- The model returned a single string for three `limitations` fields even though the
  usual response shape is a list of strings.
- The report formatter passed the string directly to `join`, which iterated over its
  individual characters.

**Fix**

- Added one shared presentation helper that normalizes a string, collection, empty
  value, or unexpected scalar into a list of display strings.
- Applied it to limitations, applicable conditions, evidence IDs, and other list-like
  answer sections in both the evaluation report and Streamlit clipboard/UI rendering.
- Corrected the three already-generated NCM523 limitation lines in the saved readable
  evaluation report. The raw JSONL remains unchanged as an audit record.

**Verification**

- Added a regression test covering string-valued limitations, conditions, and
  evidence IDs.
- All 14 unit tests pass.
- No character-separated limitation lines remain in the saved evaluation report.

## 2026-09-02 - Rejected answers remain visible to users

**Observed behavior**

- Deterministic validation can assign an answer a `reject` status when required
  fields, evidence citations, confidence values, or origin classifications are
  invalid.
- The agent still returns the rejected answer, and the Streamlit interface displays
  it as a normal result. The validation status and errors are shown only in the
  expandable execution-details section.
- The existing controlled repair attempt applies only to malformed or truncated
  JSON. An answer that parses correctly but fails validation is not repaired.

**Risk**

- A user may act on or copy an answer that the application itself has classified as
  invalid, particularly if the execution-details section is not opened.
- The distinction between `pass`, `pass_with_warnings`, and `reject` is therefore not
  sufficiently reflected in the user-facing behavior.

**Required fix**

- Do not present a rejected answer as a normal successful result.
- Show a prominent user-facing rejection message and the relevant validation errors.
- Decide whether to add one bounded validation-repair attempt for schema-valid
  answers that fail deterministic validation.
- If repair is implemented, disable retrieval tools during repair, preserve the
  original answer and errors for auditability, revalidate the regenerated answer,
  and stop after one failed repair.
- Add tests confirming that rejected answers are blocked or clearly quarantined and
  that `pass_with_warnings` remains visibly distinguishable from `pass`.

**Status**

- Open; documented for implementation and verification.

## 2026-09-02 - Safeguard and validation improvement backlog

**Current limitations**

- The final output schema is supplied to the LLM as an instructional example rather
  than enforced through a provider-level structured-output or JSON-schema feature.
- Deterministic validation checks the required top-level fields but validates only
  selected fields within each protocol suggestion. It does not currently enforce
  the complete type and field contract represented by `FINAL_SCHEMA`.
- The maximum of three protocol suggestions is a prompt instruction and is not
  programmatically enforced after generation.
- Numerical values that do not appear verbatim in cited evidence generate warnings
  rather than automatic rejection.
- Numerical support is checked through normalized text matching. This does not prove
  that a cited passage supports the surrounding claim, units, interpretation, or
  transfer to the target cell.
- As recorded in `Rejected answers remain visible to users`, a rejected answer can
  currently be displayed by the UI.
- The controlled repair path handles malformed or truncated JSON but does not repair
  an answer that parses correctly and subsequently fails deterministic validation.
- Validation results are not fed back into the agentic evidence loop. They therefore
  cannot currently trigger another search when a failure may reflect missing
  evidence rather than a formatting problem.
- Automated validation cannot establish that a literature-derived charging protocol
  is experimentally safe, scientifically correct, optimal, or suitable for hardware
  deployment.

**Potential improvements**

- Use provider-supported structured output or full JSON-schema enforcement when the
  selected provider and model reliably support it.
- Define and enforce the complete per-suggestion schema, including field presence,
  field types, list types, allowed values, and a hard maximum of three suggestions.
- Separate validation outcomes into issues that require answer-only repair, issues
  that may justify one additional evidence search, and terminal safety-critical
  rejection conditions.
- Add one bounded post-validation correction path with full audit logging and no
  possibility of an unbounded repair or retrieval loop.
- Strengthen numerical checks to normalize equivalent units and distinguish values
  copied from evidence from values inferred or transferred to different conditions.
- Evaluate claim-to-citation support with labeled human-reviewed examples before
  relying on any semantic-support validator.
- Make `pass`, `pass_with_warnings`, and `reject` visibly distinct in the UI and in
  copied or exported responses.
- Preserve explicit language that all protocol suggestions are literature-derived
  hypotheses requiring manufacturer-limit review and controlled experimental
  validation.

**Status**

- Open backlog; prioritize user-visible rejection handling and complete schema
  enforcement before adding more permissive generation behavior.
