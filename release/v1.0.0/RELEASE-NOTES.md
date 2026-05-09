# Release Notes: Distributed Independent Repo Agents v1.0.0

**Date**: 2026-05-09  
**Branch**: `master_distributed-repo-agents`  
**Tag**: `v1.0.0-distributed-repo-agents`

---

## What's New

This release replaces the centralized RAG+MCP orchestration demo with a fully **distributed peer-to-peer architecture** where each repo is an autonomous agent.

### Architecture Change: Centralized → Distributed

| Before | After |
|--------|-------|
| Single `OrchestratorAgent` owns all RAG indexes | Each repo has its own `RepoRAG` instance |
| Orchestrator queries all repos and picks the best | Orchestrator is a **router only** — returns repo names |
| One generic `repo_mcp_server.py --repo <name>` | Per-repo `mcp_server.py` at `repos/{repo}/mcp/` |
| Single central `RepoAgent` | `IndependentRepoAgent` per repo at `repos/{repo}/agent/` |
| Consultation summary output | Structured **Feature Analysis Document** |

### New Components

- **`orchestrator/router.py`** — `OrchestratorRouter`: embedding-based routing on repo descriptions only
- **`orchestrator/mcp/router_mcp_server.py`** — MCP tool: `get_relevant_repos(requesting_repo, feature_description)`
- **`orchestrator/independent_repo_agent.py`** — `IndependentRepoAgent`: LangGraph agent owning full feature-request lifecycle
- **`orchestrator/feature_analysis.py`** — Feature Analysis Document generator (Current State + Solution Design)
- **`repos/{repo}/mcp/mcp_server.py`** — Per-repo MCP server: `query_repo(feature_request)` (3 repos)
- **`repos/{repo}/agent/repo_agent.py`** — Per-repo agent entry point (3 repos)
- **`repos/{repo}/.knowledge/agent-info.md`** — Agent metadata for each repo (3 repos)
- **`docs/architecture-distributed-repo-agents.md`** — Full architecture documentation

### Tests

- **42 tests** — all passing
  - 7 unit tests: `OrchestratorRouter`
  - 9 unit tests: per-repo RAG isolation
  - 10 unit tests: Feature Analysis Document generator
  - 13 integration/system tests: MCP servers + full demo flow
  - 4 regression tests: config loader (existing)

---

## How to Run

```bash
bash scripts/run.sh
```

Output: Feature Analysis Document printed to stdout and saved to `output/feature-analysis-{timestamp}.md`

```bash
bash scripts/test.sh
```

Runs all 42 tests.

---

## How to Run Any Repo Agent Standalone

```bash
source .venv/bin/activate
PYTHONPATH=. python repos/expose_sequence/agent/repo_agent.py "your feature request"
PYTHONPATH=. python repos/scan_manager/agent/repo_agent.py "your feature request"
PYTHONPATH=. python repos/illumination/agent/repo_agent.py "your feature request"
```

---

## VS Code Copilot Integration

Open any repo's `.code-workspace` file. Each workspace registers:
- `orchestrator_router` — `get_relevant_repos` tool
- Own repo's `query_repo` tool
- All peer repos' `query_repo` tools

---

## Commits in This Release

| Commit | Agent | Description |
|--------|-------|-------------|
| ea1e3be | Product Owner | User story: distributed repo agents |
| d2f3f43 | Cost Analyst | Cost estimate (~$2.01, HIGH) |
| 755a673 | Architect | EPS, EDS, interface contracts, technical tasks |
| 0e25dcb | IT Setup | Baseline merge, scripts, env setup |
| 5d0971b | Developer | Full implementation |
| 5bc3d33 | Tester | 42 tests, test plan, test report |
