# MCP Interface Contracts: Distributed Repo Agents

## 1. Orchestrator Router MCP

**Server**: `orchestrator/mcp/router_mcp_server.py`  
**Transport**: stdio (subprocess)  
**Launch**: `python orchestrator/mcp/router_mcp_server.py`

### Tool: `get_relevant_repos`

```
Tool name:   get_relevant_repos
Description: Given a feature description, return the names of the repos most
             relevant to consult. Uses embedding similarity on repo descriptions.
             Does NOT query repo content — routing only.

Arguments:
  requesting_repo    (str, required)  — name of the repo making the request
                                        (excluded from results)
  feature_description (str, required) — natural-language feature request

Returns: (str) — plaintext listing repo names and similarity scores, e.g.:
  "Routing result for: '...'
   Relevant repos:
     1. scan_manager  — score: 0.87
     2. illumination  — score: 0.74"

Errors: Returns error string if config cannot be loaded.
```

**Contract guarantees**:
- Never returns the `requesting_repo` itself
- Returns at most `top_k` repos (default 2, configurable in workflow-config.json)
- Does not call any repo's RAG or MCP
- Response time < 100ms (embedding cached at startup)

---

## 2. Per-Repo Knowledge MCP

**Server**: `repos/{repo}/mcp/mcp_server.py`  
**Transport**: stdio (subprocess)  
**Launch**: `python repos/{repo}/mcp/mcp_server.py`  
(One server per repo; each is a standalone process)

### Tool: `query_repo`

```
Tool name:   query_repo
Description: Query this repo's knowledge base for a feature request. Returns
             which components, interfaces, and source files are relevant and
             what the current behavior is in that area.

Arguments:
  feature_request  (str, required) — natural-language feature request or question

Returns: (str) — structured response, e.g.:
  "[scan_manager Knowledge]

   RELEVANT COMPONENTS:
     · StageController — manages XYZ wafer stage positioning
     · ScanSequencer — coordinates scan gate open/close timing

   RELEVANT INTERFACES:
     · StageController.thrift: GetPosition(), SetVelocity(), EnableFeedback()
     · ScanSequencer.thrift: StartScan(), StopScan()

   CURRENT BEHAVIOR:
     [RAG-retrieved text from .knowledge/ docs and source files]"

Errors: Returns "(no relevant knowledge found)" if RAG finds nothing.
        Returns error string if RAG index cannot be built.
```

**Contract guarantees**:
- Only queries this repo's own content — never calls other repos or orchestrator
- RAG index is built/loaded at server startup (not per-request)
- Searches docs first; falls back to source code if docs result is thin
- Response time < 2s (ChromaDB local query)

---

## 3. Feature Analysis Document Format

Produced by `orchestrator/feature_analysis.py`, output by `IndependentRepoAgent`.

```markdown
# Feature Analysis: {feature_request_title}

**Requesting Repo**: {repo_display_name}
**Date**: YYYY-MM-DD HH:MM

---

## Current State

### {requesting_repo} (own knowledge)
{own_rag_result}

### {peer_repo_1_display_name}
{peer_mcp_response_1}

### {peer_repo_2_display_name}
{peer_mcp_response_2}

---

## Solution Design

### Overview
{LLM synthesis or structured template}

### Changes Required per Repo

#### {requesting_repo}
- [component] [interface/file] — [what changes]

#### {peer_repo_1}
- [component] [interface/file] — [what changes]

#### {peer_repo_2}
- [component] [interface/file] — [what changes]

### Cross-Repo Interface Touch Points
- {interface_1}: used by {repo_a}, consumed by {repo_b}
- {interface_2}: ...
```

---

## 4. VsCode `.vscode/mcp.json` Contract (per repo)

Each repo workspace registers its own MCP server and the orchestrator router:

```json
{
  "servers": {
    "{repo}_knowledge": {
      "type": "stdio",
      "command": "python",
      "args": ["repos/{repo}/mcp/mcp_server.py"],
      "env": { "PYTHONPATH": "${workspaceFolder}" }
    },
    "orchestrator_router": {
      "type": "stdio",
      "command": "python",
      "args": ["orchestrator/mcp/router_mcp_server.py"],
      "env": { "PYTHONPATH": "${workspaceFolder}" }
    }
  }
}
```

The top-level orchestrator workspace (`orchestrator.code-workspace`) registers all 3 repo MCP servers and the router.
