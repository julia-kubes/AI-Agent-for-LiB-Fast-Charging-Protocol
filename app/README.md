# Application infrastructure

The application layer supports deterministic offline demo mode and live
Neon retrieval through the shared vector-search and reranking pipeline.

## Offline checks

From the repository root:

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```

```powershell
& ".\.venv\Scripts\python.exe" -m app.cli --demo --question "What factors should constrain a fast-charging protocol?"
```

```powershell
& ".\.venv\Scripts\python.exe" -m evaluation.run_evaluation
```

## Offline UI

Set demo mode for the current PowerShell process:

```powershell
$env:APP_DEMO_MODE = "true"
```

Then launch Streamlit:

```powershell
& ".\.venv\Scripts\python.exe" -m streamlit run .\app\ui.py
```

Demo mode uses synthetic evidence and must never be presented as a real research
result.

## Live configuration

From the repository root, create a private local configuration file from the
tracked template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and enter values for `DATABASE_URL` and `LLM_API_KEY`. The MIT Parley
URL and initial `gpt-5.4-mini` model are already supplied by the template. The
app loads `.env` automatically and Git ignores it. Never commit or share a
populated `.env`; each collaborator should use their own Parley key so usage is
attributed to the correct account.

The complete live settings are:

- `DATABASE_URL`
- `LLM_BASE_URL`
- `LLM_API_KEY` (or `PARLEY_API_KEY`)
- `LLM_MODEL`

Do not pass `--demo`, and set `APP_DEMO_MODE=false` for the UI.

The first live retrieval loads the GTE embedding model and reranker and can take
longer while their files are downloaded and cached. The adapter uses
parameterized SQL and short-lived database connections.

Final answers have a 3,000-token ceiling by default. If Parley truncates or
returns malformed final JSON, the agent requests one concise JSON-only
regeneration and then fails clearly rather than retrying without a bound.

Implementation bugs and fixes are recorded in `DEVELOPMENT_LOG.md`.
