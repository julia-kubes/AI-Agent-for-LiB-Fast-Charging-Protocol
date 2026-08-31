# Development log

This file records implementation bugs, fixes, behavioral changes, and verification
results while the application is under active development. Credentials and raw
database connection information must never be recorded here.

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
