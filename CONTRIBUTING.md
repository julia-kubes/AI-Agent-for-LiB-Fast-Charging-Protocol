# Contributing

## Choose the correct base branch

- Base literature-synthesis changes on `literature-synthesis`.
- Base actionable-protocol changes on `protocol-generation`.
- Use `main` only for repository-wide coordination documentation.

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

## Shared changes

For a change intended for both versions:

1. Implement and test it against one clearly identified version.
2. Open a pull request into that version.
3. Port the same commit or branch into the other maintained version.
4. Resolve conflicts and rerun that version's tests.
5. Confirm both pull requests before considering the shared change complete.

Do not assume that a merge into one maintained version automatically reaches the other.

## Repository hygiene

- Never commit `.env`, API keys, database passwords, or populated secret files.
- Do not commit local virtual environments, model caches, branch-preview worktrees, or temporary outputs.
- Preserve complete evaluation reports when they document an intentional comparison.
- Identify whether numerical protocol values are reported, transferred, engineering judgments, or unresolved.
- Keep archived tags unchanged.
