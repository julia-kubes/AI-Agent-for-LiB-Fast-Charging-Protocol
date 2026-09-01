# Development log

This file records implementation bugs, fixes, behavioral changes, and verification
results while the application is under active development. Credentials and raw
database connection information must never be recorded here.

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
