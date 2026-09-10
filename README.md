# AI Agent for Li-ion Battery Fast-Charging Protocols

This private repository contains two actively maintained versions of the research tool. Each maintained app branch includes the complete literature database pipeline, retrieval-augmented generation infrastructure, application, tests, and evaluation materials.

## Active tool versions

| Version | Branch | Purpose |
|---|---|---|
| Literature synthesis | [`literature-synthesis`](../../tree/literature-synthesis) | Evidence-conservative literature retrieval and synthesis. It reports supported strategies and limitations without forcing a complete numerical protocol. |
| Protocol generation | [`protocol-generation`](../../tree/protocol-generation) | Produces structured experimental starting protocols and distinguishes reported values from evidence-informed transfers, engineering judgments, and unresolved parameters. |

`main` is the repository landing and coordination branch and intentionally contains documentation rather than runnable pipeline or application code. Do not assume that running `main` reproduces either maintained tool version; select one of the branches above.

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

## Shared vector database and infrastructure changes

Both maintained app branches contain the complete vector database creation workflow, including PDF parsing, chunking, metadata import, embedding, storage, and retrieval. A vector database or shared infrastructure change may be developed from either `literature-synthesis` or `protocol-generation`.

Label these pull requests **shared** and port the same focused change into the other maintained app branch. Open a separate pull request into each branch and test each version independently before merging. A shared change is not complete until both app branches contain it; do not add pipeline code to `main` as a synchronization mechanism.

## Configuration and secrets

Copy `.env.example` to `.env` for local live use. Never commit a populated `.env`. Each collaborator should use an individually issued LLM API key and an appropriately scoped database credential.

## Historical versions

Superseded development branches were preserved as dated `archive/*` Git tags before branch cleanup. Tags are read-only historical reference points and should not receive new work.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the collaboration workflow.
