# Evidence-Informed Protocol Reasoning

## Purpose

This branch changes the protocol assistant from an exact-value literature extractor into an evidence-informed experimental design assistant. The previous structured-protocol validator required the source value for every extrapolated parameter to appear verbatim in cited evidence. That rule could reject scientifically defensible protocols whenever the requested cell did not exactly match a published experiment.

The revised policy permits bounded scientific reasoning while preserving provenance, uncertainty, and safety disclosures.

## Reasoning categories

Every operational value is assigned one of five bases:

1. `user_specified`: The exact value was supplied by the user as a target temperature, SOC endpoint, or time. It is not cited as a literature result, and validation checks it against the structured target conditions.
2. `reported`: The proposed value is directly reported in cited evidence. Exact value-and-unit verification remains a hard requirement.
3. `evidence_informed_transfer`: The value is adapted from cited literature to different target conditions. The response must disclose source conditions, its adjustment logic, rationale, citations, and confidence. A source value that cannot be matched verbatim now produces a review warning rather than automatic rejection.
4. `engineering_judgment`: The literature supports the relevant mechanism, range, or design direction, but the selected number is an explicit experimental assumption. It requires cited context and a scientific rationale and cannot claim high confidence.
5. `unresolved`: The evidence and defensible reasoning are insufficient. The value must remain null.

## Protocol status

- `literature_transferred_candidate`: A complete protocol assembled from reported and evidence-transferred values.
- `experimental_starting_protocol`: A complete protocol containing one or more values selected through disclosed engineering judgment.
- `partially_specified`: A protocol with unresolved critical parameters.

The first two statuses mean that the protocol is sufficiently specified for controlled evaluation. Neither status means that the protocol has been validated for deployment or for direct use on charging hardware.

## Safeguards retained

The validator continues to reject:

- citations to evidence that was not retrieved;
- directly reported values that are absent from their cited evidence;
- transferred or judgment-based values mislabeled as reported;
- evidence transfer without source conditions, adjustment logic, rationale, or citations;
- engineering judgment presented with high confidence;
- undisclosed use of evidence transfer or engineering judgment;
- incomplete operational protocols labeled as complete candidates;
- missing units, invalid control modes, malformed transitions, and other structural failures;
- candidates without a validation plan, monitoring requirements, or stop conditions.

## Files changed

### `app/prompts.py`

The system prompt now explicitly authorizes evidence-informed transfer and engineering judgment. It instructs the model to distinguish these from directly reported results, explain source-to-target reasoning, and describe the result as an experimental starting point. The response schema and repair instructions use the new basis and status labels. JSON repair is limited to one primary protocol to reduce response size and regeneration failures.

### `app/validation.py`

The deterministic validator recognizes the four reasoning categories and three protocol statuses. Exact text matching applies only to values claimed as reported. Evidence-transfer fields are checked for adequate reasoning and provenance; a non-verbatim source value is flagged for review instead of rejected. Engineering judgments require cited context, rationale, disclosure, and low or medium confidence.

The labeling repair adds `user_specified` as a fifth category. Temperature limits and SOC/time transitions that exactly match the structured target conditions are canonicalized to this basis, with literature citation fields removed. This prevents a user-requested operating condition from being misrepresented as a published result. Only unresolved current and transition values make a candidate operationally incomplete; unresolved voltage or temperature limits remain visible gaps but do not contradict the prompt's definition of a measurable starting protocol.

### `app/agent.py`

User-target normalization is applied after initial JSON parsing and after either repair path, before deterministic validation. This makes the correction reliable even when the language model initially assigns the wrong provenance label.

### `app/ui.py`

The interface now labels the relevant section “Evidence transfer and reasoning disclosure” so users are not led to treat all non-reported values as a single undifferentiated extrapolation category.

### `tests/test_validation.py`

Tests cover evidence transfer without exact target-value support, acceptable engineering judgment, prohibited high-confidence judgment, required disclosure, retained citation checks, and unresolved critical parameters.

### `tests/test_ui.py`

UI expectations use the new experimental protocol status.

## Verification

Run:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

At implementation time, all 30 tests passed.

## Recommended evaluation

Rerun the existing Q2 and Q3 comparison set. Review not only whether validation passes, but whether each inferred value has a comprehensible scientific argument, an appropriately cautious confidence level, practical monitoring and stop criteria, and a validation plan that would allow a researcher to test the assumption safely.
