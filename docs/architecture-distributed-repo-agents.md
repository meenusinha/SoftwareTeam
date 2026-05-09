# Architecture: Distributed Independent Repo Agents

## Overview

Each repository in the lithography scanner software system hosts its own fully independent AI agent. The agent owns the RAG index for its repo and exposes an MCP server. The orchestrator is demoted to a **router-only** — it returns repo names, never content.

---

## Architecture Diagram

```
                    ┌────────────────────────────┐
                    │   ORCHESTRATOR (router only) │
                    │                              │
                    │  OrchestratorRouter          │
                    │  · Embeds repo descriptions  │
                    │  · Cosine-scores vs query    │
                    │  · Returns repo names only   │
                    │                              │
                    │  MCP Tool:                   │
                    │  get_relevant_repos(         │
                    │    requesting_repo,          │
                    │    feature_description       │
                    │  ) -> list[repo_name]        │
                    └────────────┬─────────────────┘
                                 │ ① which repos?
                                 │
        ┌────────────────────────▼──────────────────────────┐
        │             REQUESTING REPO AGENT                  │
        │             e.g. expose_sequence                   │
        │                                                    │
        │  IndependentRepoAgent                              │
        │  ① Call orchestrator router MCP                   │
        │  ② Query own RepoRAG                              │
        │  ③ Call peer repo MCPs directly                   │
        │  ④ Generate Feature Analysis Document             │
        └──────────┬─────────────────────────┬──────────────┘
                   │ ③ direct MCP call        │ ③ direct MCP call
                   │                          │
     ┌─────────────▼──────────┐  ┌────────────▼──────────────┐
     │   scan_manager Agent    │  │   illumination Agent       │
     │                         │  │                            │
     │  RepoRAG (own only)     │  │  RepoRAG (own only)       │
     │  · .knowledge/*.md      │  │  · .knowledge/*.md        │
     │  · *.thrift interfaces  │  │  · *.thrift interfaces    │
     │  · *.h headers          │  │  · *.h headers            │
     │  · *.cpp implementations│  │  · *.cpp implementations  │
     │                         │  │                            │
     │  MCP Tool: query_repo() │  │  MCP Tool: query_repo()   │
     └─────────────────────────┘  └────────────────────────────┘
```

---

## Before vs After

| Aspect | Before (Centralized) | After (Distributed) |
|--------|---------------------|---------------------|
| RAG location | One central `OrchestratorAgent` holds all repo RAG indexes | Each repo has its own `RepoRAG` instance |
| Orchestrator role | Queries all repos, scores responses, picks top-2 | Router only: scores repo descriptions, returns names |
| Repo MCP tool | `query_knowledge(question)` via generic `repo_mcp_server.py --repo` | `query_repo(feature_request)` via per-repo `mcp_server.py` |
| Repo agent | Single central `RepoAgent` | `IndependentRepoAgent` per repo |
| Repo-to-repo comms | Through central orchestrator | Direct MCP calls between repos |
| Output | Consultation summary | Structured Feature Analysis Document (Current State + Solution Design) |

---

## File Structure

```
orchestrator/
  router.py                        ← OrchestratorRouter (embedding-based routing, no RAG)
  independent_repo_agent.py        ← IndependentRepoAgent (shared class, one per repo)
  feature_analysis.py              ← Feature Analysis Document generator
  rag/
    repo_rag.py                    ← RepoRAG (shared class, each repo owns an instance)
  mcp/
    router_mcp_server.py           ← NEW: get_relevant_repos MCP tool
    repo_mcp_server.py             ← kept for backward compatibility
    orchestrator_mcp_server.py     ← legacy (kept but superseded)
  config_loader.py                 ← unchanged
  demo/
    run_demo.py                    ← updated: uses IndependentRepoAgent

repos/
  {scan_manager, illumination, expose_sequence}/
    agent/
      __init__.py
      repo_agent.py                ← per-repo entry point for IndependentRepoAgent
    mcp/
      __init__.py
      mcp_server.py                ← per-repo MCP server: query_repo tool
    .knowledge/
      overview.md
      components.md
      interfaces.md
      agent-info.md                ← NEW: documents this repo's agent and MCP
    (existing source files unchanged)
```

---

## Feature Request Flow (step-by-step)

Given: developer submits a feature request to the `expose_sequence` agent.

```
Step 1:  expose_sequence IndependentRepoAgent receives feature_request

Step 2:  Agent calls → orchestrator/mcp/router_mcp_server.py
           Tool: get_relevant_repos("expose_sequence", feature_request)
           Returns: ["scan_manager", "illumination"]   ← names only, no content

Step 3:  Agent queries → own RepoRAG (expose_sequence)
           Searches: .knowledge/*.md + *.thrift + *.h + *.cpp
           Returns: relevant snippets from this repo's own files

Step 4:  Agent calls → repos/scan_manager/mcp/mcp_server.py   (direct)
           Tool: query_repo(feature_request)
           scan_manager RAG searches its own files → returns structured response

Step 5:  Agent calls → repos/illumination/mcp/mcp_server.py   (direct)
           Tool: query_repo(feature_request)
           illumination RAG searches its own files → returns structured response

Step 6:  Agent generates Feature Analysis Document:
           ## Current State
             expose_sequence (own): ...
             scan_manager: ...
             illumination: ...
           ## Solution Design
             (LLM synthesis or structured template)

Step 7:  Document printed to stdout + saved to output/feature-analysis-{ts}.md
```

---

## How to Run the Demo

```bash
bash scripts/run.sh
```

This runs `orchestrator/demo/run_demo.py` which uses the `expose_sequence` agent with the feature request configured in `workflow-config.json`.

---

## How to Run Any Repo Agent Standalone

```bash
# From project root
source .venv/bin/activate
PYTHONPATH=. python repos/expose_sequence/agent/repo_agent.py "your feature request here"
PYTHONPATH=. python repos/scan_manager/agent/repo_agent.py "your feature request here"
PYTHONPATH=. python repos/illumination/agent/repo_agent.py "your feature request here"
```

---

## How to Use the MCP Servers in VS Code Copilot

Each repo's `.vscode/mcp.json` registers:
- `orchestrator_router` — call `get_relevant_repos` to find which repos to consult
- `{repo}_knowledge` (own) — call `query_repo` on your own repo
- All peer repo `query_repo` tools

Open a repo's `.code-workspace` file in VS Code to get the full MCP tool set for that repo. Copilot can then use `get_relevant_repos` + `query_repo` calls to answer feature questions autonomously.

---

## How to Add a New Repo

1. Add the repo entry to `workflow-config.json` under `"repos"`
2. Create `repos/{new_repo}/.knowledge/` with `overview.md`, `components.md`, `interfaces.md`, `agent-info.md`
3. Copy `repos/expose_sequence/mcp/mcp_server.py` → `repos/{new_repo}/mcp/mcp_server.py`, change `REPO_NAME`
4. Copy `repos/expose_sequence/agent/repo_agent.py` → `repos/{new_repo}/agent/repo_agent.py`, change `REPO_NAME`
5. Add the new repo's MCP server to each other repo's `.vscode/mcp.json`
6. The `OrchestratorRouter` picks it up automatically from config — no code changes needed

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Embedding-based router (not LLM-based) | No API call needed for routing; fast; same embedding model already loaded by RAG |
| Router embeds repo descriptions (not full RAG) | Keeps orchestrator truly lightweight — startup < 3s, no ChromaDB |
| Per-repo MCP servers as separate scripts | Each repo is fully self-contained; mirrors a real "one Copilot agent per repo" setup |
| Shared `RepoRAG` and `IndependentRepoAgent` classes | Avoids code duplication; each repo gets its own instance |
| Feature Analysis Document (not raw summary) | Structured output gives developers an actionable artifact: current state survey + solution design |
