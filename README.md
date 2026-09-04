# AI-Agent-for-LiB-Fast-Charging-Protocol
This repository contains scripts and instructions for creating the AI Agent,
including PDF parsing, chunking, vector-database storage, metadata import, the
WebUI, and the RAG pipeline.

For adding papers, start with the metadata-first DOI workflow in
[`parse_pdf/README.md`](parse_pdf/README.md), then follow the chunking details in
[`chunk/README.md`](chunk/README.md). Collection files are resolved from the
current folder (or an explicit `--root`), so the workflow does not depend on a
specific user's local directory structure.
