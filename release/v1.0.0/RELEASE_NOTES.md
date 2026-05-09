# Release Notes — v1.0.0

**Date**: 2026-05-09  
**Branch**: master_rag-mcp-orchestration-demo

## What's in this release

Generic multi-repo RAG + MCP agentic orchestration demo using the Lithography domain.

### Three demo repos (simulated as sibling folders)

| Repo | Components | Knowledge docs |
|------|-----------|----------------|
| `repos/illumination/` | LightSource, LensSystem | overview, components, interfaces |
| `repos/scan_manager/` | StageController, ScanSequencer | overview, components, interfaces |
| `repos/expose_sequence/` | ExposureController, DoseManager | overview, components, interfaces |

Each repo has Thrift IDL interfaces and C++ stub implementations.

### Orchestration framework (`orchestrator/`)

- **Config-driven**: all repo names, paths, and LLM settings in `workflow-config.json`
- **RAG**: ChromaDB + sentence-transformers (local, no API key for embeddings)
- **MCP**: generic `repo_mcp_server.py` — launch with `--repo <name>`, exposes `query_knowledge` tool
- **LangGraph agents**: `OrchestratorAgent` selects repos to consult; `RepoAgent` runs the 4-step consultation graph
- **LLM**: GitHub Models `gpt-4o-mini` via `GITHUB_TOKEN` — no Anthropic account needed

### VS Code multi-session support

Four `.code-workspace` files at project root. Each workspace has `.vscode/mcp.json` pre-configured so GitHub Copilot in that window can query the other repos' knowledge via MCP.

## Test results

- C++ stubs: 3/3 compile and run ✅
- Python tests: 10/10 pass ✅
- Total: 13/13 ✅

## How to run

1. Copy `.env.example` → `.env` and add your `GITHUB_TOKEN`
2. `bash scripts/run.sh`

## How to reuse with your own repos

Edit `workflow-config.json`:
- Change `repos[].name`, `display_name`, `path`, `knowledge_path`, `description`, `components`
- Point `knowledge_path` to your repo's markdown knowledge folder
- No agent, MCP, or RAG code needs to change
