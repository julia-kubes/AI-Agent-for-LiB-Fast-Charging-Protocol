# Contributing

## Choose the correct base branch

- Base literature-synthesis changes on `literature-synthesis`.
- Base actionable-protocol changes on `protocol-generation`.
- Use `main` only for repository-wide coordination documentation. It does not contain a runnable app or vector database pipeline.

## Make a change

1. Pull the latest version branch.
2. Create a short-lived feature or fix branch.
3. Make the smallest coherent change.
4. Run the offline test suite.
5. Push the branch and open a pull request into the correct maintained version.

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```

Live evaluations use the configured database and LLM service, consume API credits, and are nondeterministic. Run them when a change affects prompts, retrieval, agent behavior, output structure, or validation, and attach the query set, branch commit, model, and full outputs to the evaluation record.

## Shared vector database and infrastructure changes

The complete PDF parsing, chunking, metadata, embedding, storage, and retrieval workflow is present in both maintained app branches. Shared pipeline work may begin from either app version; choose the version where the change is easiest to develop and test.

For a change intended for both versions:

1. Create a short-lived branch from either `literature-synthesis` or `protocol-generation`.
2. Implement and test the focused pipeline or infrastructure change against that version.
3. Open a pull request into that version and label it **shared**.
4. Port the same commit or focused change into a branch based on the other maintained version.
5. Resolve conflicts and rerun that version's tests.
6. Open and confirm both pull requests before considering the shared change complete.

Do not assume that a merge into one maintained version automatically reaches the other.
Do not place pipeline code on `main`; `main` is only the repository landing and coordination branch.

## Repository hygiene

- Never commit `.env`, API keys, database passwords, or populated secret files.
- Do not commit local virtual environments, model caches, branch-preview worktrees, or temporary outputs.
- Preserve complete evaluation reports when they document an intentional comparison.
- Identify whether numerical protocol values are reported, transferred, engineering judgments, or unresolved.
- Keep archived tags unchanged.
