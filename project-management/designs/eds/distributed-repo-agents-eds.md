# Engineering Design Specification: Distributed Independent Repo Agents

## Architecture Overview

```
                        ┌─────────────────────────────────┐
                        │     ORCHESTRATOR (router only)   │
                        │                                  │
                        │  OrchestratorRouter              │
                        │  · Embeds repo descriptions      │
                        │  · Scores by cosine similarity   │
                        │  · Returns repo names only       │
                        │                                  │
                        │  MCP: router_mcp_server.py       │
                        │  Tool: get_relevant_repos(...)   │
                        └──────────────┬──────────────────┘
                                       │ (1) route: which repos?
                                       │
              ┌────────────────────────▼──────────────────────────┐
              │           REQUESTING REPO AGENT                    │
              │           e.g. expose_sequence                     │
              │                                                    │
              │  IndependentRepoAgent                              │
              │  · Owns its own RepoRAG                           │
              │  · Calls orchestrator MCP for routing             │
              │  · Calls peer repo MCPs directly                  │
              │  · Generates Feature Analysis Document            │
              └──────┬───────────────────────────────┬────────────┘
                     │ (2) direct MCP call            │ (3) direct MCP call
                     │                               │
        ┌────────────▼──────────┐       ┌────────────▼──────────┐
        │  scan_manager Agent   │       │  illumination Agent   │
        │                       │       │                        │
        │  RepoRAG (own index)  │       │  RepoRAG (own index)  │
        │  Indexes:             │       │  Indexes:             │
        │  · .knowledge/*.md    │       │  · .knowledge/*.md    │
        │  · *.thrift           │       │  · *.thrift           │
        │  · *.h / *.cpp        │       │  · *.h / *.cpp        │
        │                       │       │                        │
        │  MCP: mcp_server.py   │       │  MCP: mcp_server.py   │
        │  Tool: query_repo()   │       │  Tool: query_repo()   │
        └───────────────────────┘       └───────────────────────┘
```

## Component Design

### 1. OrchestratorRouter (replaces OrchestratorAgent)

**Location**: `orchestrator/router.py`

**Responsibility**: Route a feature request to relevant repo names by querying each peer repo's RAG via MCP and ranking by how much relevant content is returned. Routing is based on actual knowledge found across docs, interfaces, and source — not description embeddings.

**Design**:
```python
class OrchestratorRouter:
    def __init__(self, config: dict, root: Path = None):
        # Builds repo_name → MCP script path mapping from config["repos"][].path
        # No embedding model loaded — uses subprocess MCP calls for routing

    def get_relevant_repos(
        self, requesting_repo: str, feature_description: str, top_k: int = 2
    ) -> tuple[list[str], dict[str, float]]:
        # For each peer repo: calls its query_repo MCP tool via stdio subprocess
        # Scores response: 0.0 if "no relevant knowledge found", else min(content_len/800, 1.0)
        # Returns top_k repos sorted by score descending
```

**Why RAG-based routing**: Description embeddings can miss relevance that only appears in interfaces or implementation. Querying each repo's actual knowledge base ensures routing decisions are grounded in real content, not just description text.

---

### 2. RepoRAG (per-repo, unchanged class)

**Location**: `orchestrator/rag/repo_rag.py` (shared class, unchanged)

**Each repo instantiates its own `RepoRAG`** scoped to its own `knowledge_path` and `repo_root`. The ChromaDB collections are already per-repo keyed (`repo_{name}_docs`, `repo_{name}_code`). No structural change needed — each repo agent owns its own instance.

---

### 3. IndependentRepoAgent (new — one per repo)

**Location**: `repos/{repo}/agent/repo_agent.py`

**Responsibility**: Owns the full feature request lifecycle for one repo.

```python
class IndependentRepoAgent:
    def __init__(self, repo_name: str, config: dict):
        self._repo_name = repo_name
        self._rag = RepoRAG(repo_name, config)
        self._rag.build_or_load_index()

    def handle_feature_request(self, feature_request: str) -> str:
        # 1. Call orchestrator MCP → get_relevant_repos()
        targets = self._call_orchestrator_mcp(feature_request)

        # 2. Query own RAG
        own_knowledge = self._rag.query(feature_request)

        # 3. Call each peer repo's MCP directly → query_repo()
        peer_responses: dict[str, str] = {}
        for target in targets:
            peer_responses[target] = self._call_repo_mcp(target, feature_request)

        # 4. Generate Feature Analysis Document
        return generate_feature_analysis(
            requesting_repo=self._repo_name,
            feature_request=feature_request,
            own_knowledge=own_knowledge,
            peer_responses=peer_responses,
        )
```

**State graph** (LangGraph): same pattern as existing `RepoAgent` —
`ask_orchestrator → [query_own_rag] → consult_peer_1 → consult_peer_2 → generate_document → END`

---

### 4. Per-Repo MCP Server

**Location**: `repos/{repo}/mcp/mcp_server.py`

**Tool exposed**: `query_repo(feature_request: str) -> str`

Returns a structured response:
```
[scan_manager Knowledge]

RELEVANT COMPONENTS:
  · StageController — manages XYZ wafer stage positioning
  · ScanSequencer — coordinates scan gate open/close

RELEVANT INTERFACES:
  · StageController.thrift: GetPosition(), SetVelocity(), EnableFeedback()
  · ScanSequencer.thrift: StartScan(), StopScan(), GetScanStatus()

RELEVANT SOURCE:
  · StageController.cpp: real-time position feedback loop implementation
  · ScanSequencer.h: scan gate coordination API

CURRENT BEHAVIOR:
  [RAG retrieved text from .knowledge/ and source files]
```

---

### 5. Router MCP Server (replaces orchestrator_mcp_server.py)

**Location**: `orchestrator/mcp/router_mcp_server.py`

**Tool exposed**: `get_relevant_repos(requesting_repo: str, feature_description: str) -> str`

Returns a plain list of repo names plus brief rationale:
```
Routing result for: "Add adaptive dose correction..."
Requesting repo: expose_sequence

Relevant repos (by RAG content relevance):
  1. scan_manager  — score: 0.87
  2. illumination  — score: 0.74

Consult these repos next using their query_repo MCP tools.
```

---

### 6. Feature Analysis Document Generator

**Location**: `orchestrator/feature_analysis.py` (shared utility)

**Input**: requesting repo, feature request, own RAG knowledge, dict of peer responses
**Output**: Markdown document

```markdown
# Feature Analysis: {feature_request}

**Requesting Repo**: {requesting_repo}
**Date**: {date}

---

## Current State

### {requesting_repo} (own)
{own_knowledge}

### {peer_repo_1}
{peer_response_1}

### {peer_repo_2}
{peer_response_2}

---

## Solution Design

{LLM synthesis or structured template if no LLM}
```

## Data Flow

```
Developer submits feature request to expose_sequence agent
  │
  ▼
expose_sequence IndependentRepoAgent.handle_feature_request(feature)
  │
  ├─[1]─► OrchestratorRouter MCP: get_relevant_repos("expose_sequence", feature)
  │           └─► Returns: ["scan_manager", "illumination"]
  │
  ├─[2]─► expose_sequence own RepoRAG.query(feature)
  │           └─► Returns: knowledge from .knowledge/ + thrift + src
  │
  ├─[3]─► scan_manager MCP: query_repo(feature)
  │           └─► scan_manager RepoRAG.query(feature)
  │           └─► Returns: structured response with components/interfaces/files
  │
  ├─[4]─► illumination MCP: query_repo(feature)
  │           └─► illumination RepoRAG.query(feature)
  │           └─► Returns: structured response with components/interfaces/files
  │
  └─[5]─► generate_feature_analysis(own + peer responses)
              └─► Feature Analysis Document (stdout + output/feature-analysis-{ts}.md)
```

## Interface Specifications

See `project-management/designs/interfaces/mcp-interface-contracts.md`.

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| `mcp` (fastmcp) | existing | MCP server/client framework |
| `sentence-transformers` | existing | Embedding model for RAG + router |
| `chromadb` | existing | Vector store for RAG indexes |
| `langgraph` | existing | Agent state machine |
| `langchain-openai` | existing | LLM synthesis (optional) |
| `python-dotenv` | existing | .env loading |

No new dependencies introduced.

## File Structure (after implementation)

```
orchestrator/
  router.py                        ← NEW: OrchestratorRouter (router-only)
  orchestrator_agent.py            ← REMOVED (or kept for backward compat)
  repo_agent.py                    ← REMOVED (logic moves to per-repo agents)
  feature_analysis.py              ← NEW: Feature Analysis Document generator
  rag/
    repo_rag.py                    ← UNCHANGED (shared class)
  mcp/
    router_mcp_server.py           ← NEW: exposes get_relevant_repos tool
    repo_mcp_server.py             ← KEPT: used by each repo's MCP server
    orchestrator_mcp_server.py     ← REMOVED (replaced by router_mcp_server.py)
  config_loader.py                 ← UNCHANGED
  demo/
    run_demo.py                    ← UPDATED: uses IndependentRepoAgent
  tests/
    test_config_loader.py          ← UNCHANGED
    test_router.py                 ← NEW: unit tests for OrchestratorRouter
    test_repo_rag.py               ← NEW: unit tests for per-repo RAG isolation
    test_integration.py            ← NEW: full flow integration test

repos/
  {scan_manager, illumination, expose_sequence}/
    agent/
      __init__.py                  ← NEW
      repo_agent.py                ← NEW: IndependentRepoAgent for this repo
    mcp/
      __init__.py                  ← NEW
      mcp_server.py                ← NEW: per-repo MCP server
    .knowledge/                    ← UPDATED: add agent-info.md
    (existing source unchanged)
```

## Constraints

- No new Python package dependencies — all libs are already installed
- Per-repo MCP servers communicate over stdio (subprocess), same as current pattern
- Orchestrator router must NOT load per-repo RAG indexes (only repo descriptions)
- Feature Analysis Document must be produced even when LLM is unavailable (template fallback)
- ChromaDB collections remain per-repo keyed — no data migration needed
