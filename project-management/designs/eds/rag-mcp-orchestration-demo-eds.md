# Engineering Design Specification: Generic Multi-Repo RAG + MCP Agentic Orchestration Demo

## Architecture Overview

```
workflow-config.json
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│                    Demo Runner (run_demo.py)               │
│   - Loads config                                          │
│   - Accepts: requesting_repo + feature_request string     │
│   - Starts MCP servers for all repos                      │
│   - Invokes Repo Agent for the requesting repo            │
└───────────────────────┬───────────────────────────────────┘
                        │
        ┌───────────────▼───────────────┐
        │        Repo Agent             │  ← generic, parameterised by repo name
        │  (repo_agent.py)              │
        │  1. Ask Orchestrator: which   │
        │     repos to consult?         │
        │  2. MCP call → Repo B         │
        │  3. MCP call → Repo C         │
        │  4. Generate summary          │
        └───────────┬───────────────────┘
                    │
        ┌───────────▼───────────────────┐
        │      Orchestrator Agent       │  ← LangGraph node
        │  (orchestrator_agent.py)      │
        │  Reads repo descriptions      │
        │  from config, picks 2 most    │
        │  relevant repos to consult    │
        └───────────────────────────────┘

MCP servers (one per repo, generic binary):
  repo_mcp_server.py --repo illumination
  repo_mcp_server.py --repo scan_manager
  repo_mcp_server.py --repo expose_sequence

RAG (ChromaDB, local, sentence-transformers embeddings):
  One collection per repo, indexed from .knowledge/*.md
```

## Component Design

### 1. `workflow-config.json` (root of project)

Single source of truth. All names, paths, descriptions read from here.

```json
{
  "repos": [
    {
      "name": "illumination",
      "display_name": "Illumination",
      "path": "repos/illumination",
      "knowledge_path": "repos/illumination/.knowledge",
      "description": "Manages light source, lens system, and illumination optics for the lithography scanner",
      "components": ["LightSource", "LensSystem", "IlluminationOptics"]
    },
    {
      "name": "scan_manager",
      "display_name": "ScanManager",
      "path": "repos/scan_manager",
      "knowledge_path": "repos/scan_manager/.knowledge",
      "description": "Controls wafer stage motion, scan sequencing, and position feedback for the scanner",
      "components": ["StageController", "ScanSequencer", "MotionPlanner"]
    },
    {
      "name": "expose_sequence",
      "display_name": "ExposeSequence",
      "path": "repos/expose_sequence",
      "knowledge_path": "repos/expose_sequence/.knowledge",
      "description": "Manages exposure sequences, dose control, and shot coordination for each wafer field",
      "components": ["ExposureController", "DoseManager", "ShotCoordinator"]
    }
  ],
  "llm": {
    "provider": "anthropic",
    "model": "claude-haiku-4-5-20251001",
    "note": "Using Haiku for cost efficiency in demo"
  },
  "rag": {
    "embedding_model": "all-MiniLM-L6-v2",
    "chroma_persist_dir": ".chroma_db",
    "top_k": 3
  },
  "demo": {
    "requesting_repo": "expose_sequence",
    "feature_request": "Add adaptive dose correction based on real-time stage position feedback during scan"
  }
}
```

### 2. Repo Folder Structure (identical for all three repos)

```
repos/{repo_name}/
├── interfaces/
│   ├── {Component1}.thrift
│   └── {Component2}.thrift
├── src/
│   ├── {Component1}/
│   │   ├── {Component1}.h
│   │   └── {Component1}.cpp
│   └── {Component2}/
│       ├── {Component2}.h
│       └── {Component2}.cpp
├── tests/
│   ├── cpp/
│   │   └── test_{repo_name}.cpp
│   └── python/
│       └── test_{repo_name}.py
└── .knowledge/
    ├── overview.md       ← What this subsystem does; role in lithography
    ├── components.md     ← Each component's responsibility and design
    └── interfaces.md     ← Thrift interface contracts and usage
```

### 3. Orchestration Layer (`orchestrator/`)

```
orchestrator/
├── config_loader.py          ← Loads workflow-config.json, provides typed access
├── orchestrator_agent.py     ← LangGraph node: decides which repos to consult
├── repo_agent.py             ← Generic repo agent (parameterised by repo name)
├── mcp/
│   └── repo_mcp_server.py    ← Generic MCP server (launched once per repo)
├── rag/
│   └── repo_rag.py           ← Generic RAG: index + query for a given repo
└── demo/
    └── run_demo.py           ← Entry point; wires everything together
```

### 4. Agent Flow (LangGraph Graph)

```
START
  │
  ▼
[repo_agent: send_to_orchestrator]
  │  Input: repo_name, feature_request
  │  Output: [consultation_target_1, consultation_target_2]
  ▼
[repo_agent: consult_repo_1]
  │  MCP call → repo_mcp_server (target 1): query_knowledge(feature_request)
  │  Output: knowledge_snippet_1
  ▼
[repo_agent: consult_repo_2]
  │  MCP call → repo_mcp_server (target 2): query_knowledge(feature_request)
  │  Output: knowledge_snippet_2
  ▼
[repo_agent: generate_summary]
  │  Input: feature_request + knowledge_snippet_1 + knowledge_snippet_2
  │  Output: consultation_summary (existing design context + proposed solution)
  ▼
END → print to console
```

### 5. MCP Server Design (`repo_mcp_server.py`)

- **Transport**: stdio (simplest, no network config)
- **Launched as**: `python repo_mcp_server.py --repo {repo_name}`
- **Tool exposed**:
  ```
  query_knowledge(question: str) -> str
    Queries the ChromaDB RAG index for this repo's .knowledge/ folder.
    Returns the top-3 most relevant knowledge snippets.
  ```
- **Generic**: repo name → config lookup → knowledge_path → ChromaDB collection

### 6. RAG Design (`repo_rag.py`)

- **Vector store**: ChromaDB (local, persisted to `.chroma_db/`)
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (local, no API key)
- **Documents**: Each `.md` file in `knowledge_path` split into chunks (~300 tokens)
- **Index build**: On first run, indexes all docs; on subsequent runs, loads from disk
- **Query**: Returns top-k chunks concatenated as a single string

### 7. Console Output Format

```
═══════════════════════════════════════════════════════════════
 MULTI-REPO AGENTIC ORCHESTRATION DEMO
 Requesting Repo : ExposeSequence
 Feature Request : Add adaptive dose correction based on real-time
                   stage position feedback during scan
═══════════════════════════════════════════════════════════════

[STEP 1] ExposeSequence Agent → Orchestrator
  Question: "Which repos should I consult for this feature?"
  ...
[STEP 2] Orchestrator → ExposeSequence Agent
  Response: Consult [ScanManager, Illumination]
  Reason: ScanManager owns stage position feedback; Illumination
          affects dose via light source control
  ...
[STEP 3] ExposeSequence Agent → ScanManager (via MCP)
  Tool call: query_knowledge("adaptive dose correction stage position feedback")
  Response: [knowledge snippets from ScanManager .knowledge/]
  ...
[STEP 4] ExposeSequence Agent → Illumination (via MCP)
  Tool call: query_knowledge("adaptive dose correction light source control")
  Response: [knowledge snippets from Illumination .knowledge/]
  ...
[STEP 5] ExposeSequence Agent → Generating Consultation Summary
  ...
═══════════════════════════════════════════════════════════════
 CONSULTATION SUMMARY
═══════════════════════════════════════════════════════════════
 Existing Design Context:
   [from ScanManager] ...
   [from Illumination] ...

 Proposed Solution Design:
   [how ExposeSequence should implement the new feature, given
    what it learned from the other two repos]
═══════════════════════════════════════════════════════════════
```

## Technology Stack

| Layer | Technology | Reason |
|-------|-----------|--------|
| Interfaces | Thrift IDL | User requirement |
| Implementation | C++ (stub) | User requirement |
| Agent framework | LangGraph (Python) | Best for multi-agent flow visualization |
| LLM | GitHub Models via OpenAI SDK (gpt-4o-mini) | Uses existing GitHub Copilot token; no separate API billing |
| IDE integration | VS Code + GitHub Copilot (`.vscode/mcp.json` per repo) | Each repo opened as its own workspace; Copilot can query other repos via MCP |
| RAG vector store | ChromaDB (local) | No server needed, simple |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 | Local, no API key |
| MCP transport | stdio | Simplest, no network config |
| Config | JSON | Single file, human-readable |
| Tests | C++ (clang++) + Python (pytest) | User requirement |

## Data Flow

1. `run_demo.py` loads `workflow-config.json`
2. `run_demo.py` starts 3 MCP server subprocesses (one per repo)
3. `run_demo.py` builds/loads RAG index for each repo
4. `run_demo.py` invokes `RepoAgent(requesting_repo, feature_request)`
5. `RepoAgent` creates a LangGraph graph and executes it:
   - Node 1: calls `OrchestratorAgent.decide(repos, feature_request)` → targets
   - Node 2: calls MCP tool on target repo 1 via stdio
   - Node 3: calls MCP tool on target repo 2 via stdio
   - Node 4: calls LLM to synthesise summary
6. Entire dialogue printed step-by-step to console

## Dependencies

```
Python packages (orchestrator):
  langgraph >= 0.2
  langchain-openai >= 0.3
  openai >= 1.50
  chromadb >= 0.5
  sentence-transformers >= 3.0
  mcp >= 1.0
  python-dotenv

C++ (stubs, compile-check only):
  thrift (for IDL compilation check)
  g++ or clang++

Python testing:
  pytest
```

## Constraints

- LLM API key: GitHub personal access token with `models:read` scope (set in `.env` as `GITHUB_TOKEN`)
- VS Code workspaces: four `.code-workspace` files at project root, each pointing to one repo/orchestrator folder; each folder has `.vscode/mcp.json` pre-configured so GitHub Copilot can call MCP tools on the other repos
- All repos are local folders (not actual remote git repos) for demo simplicity
- C++ stubs compile but contain no real logic (stub bodies return default values)
- ChromaDB persisted locally, re-indexed if `.chroma_db/` is missing

## Architecture Decision Records

See `project-management/designs/decisions/` for rationale on key choices.
