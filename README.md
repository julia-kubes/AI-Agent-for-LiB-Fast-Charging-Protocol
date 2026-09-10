# AI Agent for Li-ion Battery Fast-Charging Protocols

This private repository contains the literature database pipeline, retrieval-augmented generation infrastructure, evaluation materials, and two actively maintained versions of the research tool.

## Active tool versions

| Version | Branch | Purpose |
|---|---|---|
| Literature synthesis | [`literature-synthesis`](../../tree/literature-synthesis) | Evidence-conservative literature retrieval and synthesis. It reports supported strategies and limitations without forcing a complete numerical protocol. |
| Protocol generation | [`protocol-generation`](../../tree/protocol-generation) | Produces structured experimental starting protocols and distinguishes reported values from evidence-informed transfers, engineering judgments, and unresolved parameters. |

`main` is the repository landing and coordination branch. Do not assume that running `main` reproduces either maintained tool version; select one of the branches above.

## Working on a version

Clone the repository once, then switch to the version you want:

```powershell
git switch literature-synthesis
git pull
```

or:

```powershell
git switch protocol-generation
git pull
```

Create a short-lived branch before editing:

```powershell
git switch -c feature/brief-short-description
```

Push that branch and open a pull request into the tool-version branch from which it was created. Do not open a version-specific change against `main`.

## Shared infrastructure changes

Changes to retrieval, parsing, database access, ingestion, or general UI infrastructure may apply to both versions. Label those pull requests **shared** and open a separate pull request into each maintained version. Each version should be tested independently before merging because their prompts, schemas, and validation rules differ.

## Configuration and secrets

Copy `.env.example` to `.env` for local live use. Never commit a populated `.env`. Each collaborator should use an individually issued LLM API key and an appropriately scoped database credential.

## Historical versions

Superseded development branches were preserved as dated `archive/*` Git tags before branch cleanup. Tags are read-only historical reference points and should not receive new work.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the collaboration workflow.
