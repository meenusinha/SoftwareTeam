# Technical Tasks: Distributed Independent Repo Agents

Reference design: `project-management/designs/eds/distributed-repo-agents-eds.md`

---

## Task 1: Merge existing implementation from rag-mcp branch

### Objective
The existing orchestrator code lives on `master_rag-mcp-orchestration-demo`. Bring it into `master_distributed-repo-agents` as the baseline for refactoring.

### Implementation Details
- Cherry-pick or merge the relevant commits from `master_rag-mcp-orchestration-demo`
- Files needed: `orchestrator/`, `repos/`, `workflow-config.json`, `requirements.txt`, `scripts/`, `.vscode/` workspace files
- Do NOT bring IT-Release artifacts (release/ folder) — only source

### Acceptance Criteria
- [ ] All existing Python source files present on the new task branch
- [ ] `bash scripts/run.sh` runs without error on the new branch (existing demo works)
- [ ] No regression in existing tests

---

## Task 2: Implement OrchestratorRouter (RAG-based MCP routing)

### Objective
Replace `OrchestratorAgent` (which does RAG internally) with `OrchestratorRouter` that routes by querying each peer repo's RAG via MCP and ranking by actual content relevance.

### File
`orchestrator/router.py`

### Implementation Details
```python
class OrchestratorRouter:
    def __init__(self, config: dict, root: Path = None):
        # Build repo_name → MCP script path from config["repos"][].path + root
        # No embedding model — routing uses subprocess MCP calls

    def get_relevant_repos(
        self, requesting_repo: str, feature_description: str, top_k: int = 2
    ) -> tuple[list[str], dict[str, float]]:
        # For each peer repo: call query_repo via _mcp_call() stdio subprocess
        # Score: 0.0 if "no relevant knowledge found", else min(content_len/800, 1.0)
        # Return top_k repos sorted by score; fallback to highest even if score=0.0
```

### Acceptance Criteria
- [x] `OrchestratorRouter` never instantiates `RepoRAG`
- [x] Excludes `requesting_repo` from results
- [x] Routes based on actual RAG content returned, not description embeddings
- [x] Falls back gracefully when no repo returns relevant content

---

## Task 3: Implement router MCP server

### Objective
Replace `orchestrator_mcp_server.py` with a router-only MCP server.

### File
`orchestrator/mcp/router_mcp_server.py`

### Implementation Details
- Instantiate `OrchestratorRouter` at module level (cached)
- Expose tool `get_relevant_repos(requesting_repo, feature_description)` via FastMCP
- Return structured string: repo names + similarity scores
- Remove (or deprecate) `orchestrator/mcp/orchestrator_mcp_server.py`

### Acceptance Criteria
- [ ] Tool responds correctly to sample routing requests
- [ ] Response contains only repo names + scores — no RAG content
- [ ] Old `orchestrator_mcp_server.py` is removed or clearly deprecated

---

## Task 4: Implement per-repo MCP servers

### Objective
Each repo gets its own standalone MCP server with a `query_repo` tool.

### Files (create for each repo)
- `repos/scan_manager/mcp/__init__.py`
- `repos/scan_manager/mcp/mcp_server.py`
- `repos/illumination/mcp/__init__.py`
- `repos/illumination/mcp/mcp_server.py`
- `repos/expose_sequence/mcp/__init__.py`
- `repos/expose_sequence/mcp/mcp_server.py`

### Implementation Details
Each server:
- Instantiates `RepoRAG` for its own repo at startup
- Exposes `query_repo(feature_request: str) -> str`
- Returns structured response per the MCP interface contract (see `interfaces/mcp-interface-contracts.md`)
- Format: RELEVANT COMPONENTS, RELEVANT INTERFACES, CURRENT BEHAVIOR sections

### Acceptance Criteria
- [ ] Each server can be launched independently: `python repos/{repo}/mcp/mcp_server.py`
- [ ] `query_repo` returns structured response with component names from that repo's `.knowledge/`
- [ ] Server only indexes its own repo content (verified by checking ChromaDB collection names)

---

## Task 5: Implement IndependentRepoAgent (per-repo)

### Objective
Each repo gets its own agent that owns the full feature-request lifecycle.

### Files (create for each repo)
- `repos/{repo}/agent/__init__.py`
- `repos/{repo}/agent/repo_agent.py`

### Implementation Details
```python
class IndependentRepoAgent:
    def __init__(self, repo_name: str, config: dict): ...

    def handle_feature_request(self, feature_request: str) -> str:
        # LangGraph state machine:
        # ask_orchestrator → query_own_rag → consult_peer_1 → consult_peer_2 → generate_document → END
        # Returns: Feature Analysis Document (markdown string)

    def _call_orchestrator_mcp(self, feature_request: str) -> list[str]:
        # Subprocess MCP call to router_mcp_server.py
        # Returns list of repo names

    def _call_repo_mcp(self, target_repo: str, feature_request: str) -> str:
        # Subprocess MCP call to repos/{target}/mcp/mcp_server.py
        # Returns structured knowledge string
```

### Acceptance Criteria
- [ ] Agent calls orchestrator MCP first (confirmed by step logging)
- [ ] Agent calls each peer repo's MCP directly (not via orchestrator)
- [ ] Agent queries its own RAG
- [ ] Output is a Feature Analysis Document with Current State + Solution Design sections

---

## Task 6: Implement Feature Analysis Document generator

### Objective
Shared utility that formats the combined knowledge into a structured markdown document.

### File
`orchestrator/feature_analysis.py`

### Implementation Details
```python
def generate_feature_analysis(
    requesting_repo: str,
    feature_request: str,
    own_knowledge: str,
    peer_responses: dict[str, str],
    llm=None,          # optional LangChain LLM for synthesis
) -> str:
    # Build Current State section from own_knowledge + peer_responses
    # If llm: call LLM for Solution Design synthesis
    # If no llm: build template Solution Design from knowledge snippets
    # Return complete markdown document
```

### Acceptance Criteria
- [ ] Document has both "Current State" and "Solution Design" sections
- [ ] Works without LLM (template fallback)
- [ ] Works with LLM when GITHUB_TOKEN is set
- [ ] Output saved to `output/feature-analysis-{timestamp}.md`

---

## Task 7: Update per-repo .knowledge/ with agent metadata

### Objective
Each repo's `.knowledge/` directory gets an `agent-info.md` file describing its agent, MCP tool, and how to interact with it.

### Files
- `repos/scan_manager/.knowledge/agent-info.md`
- `repos/illumination/.knowledge/agent-info.md`
- `repos/expose_sequence/.knowledge/agent-info.md`

### Acceptance Criteria
- [ ] Each file documents: repo role, MCP tool name, how to call it, what it returns

---

## Task 8: Update .vscode/mcp.json files

### Objective
Each repo's VS Code workspace registers its own MCP server and the orchestrator router (not the old orchestrator MCP).

### Files to update
- `repos/scan_manager/.vscode/mcp.json`
- `repos/illumination/.vscode/mcp.json`
- `repos/expose_sequence/.vscode/mcp.json`
- `orchestrator/.vscode/mcp.json`
- Top-level workspace files

### Acceptance Criteria
- [ ] Each repo workspace has `{repo}_knowledge` server pointing to `repos/{repo}/mcp/mcp_server.py`
- [ ] Each repo workspace has `orchestrator_router` server pointing to `orchestrator/mcp/router_mcp_server.py`
- [ ] Old `orchestrator_mcp_server.py` references removed

---

## Task 9: Update demo script and run.sh

### Objective
`orchestrator/demo/run_demo.py` uses `IndependentRepoAgent` and shows the new flow.

### Implementation Details
- Import `IndependentRepoAgent` from `repos/{requesting_repo}/agent/repo_agent.py`
- Show step-by-step output: orchestrator routing → peer queries → document
- Save Feature Analysis Document to `output/feature-analysis-{timestamp}.md`
- `scripts/run.sh` runs `python orchestrator/demo/run_demo.py`

### Acceptance Criteria
- [ ] `bash scripts/run.sh` executes the full new flow end-to-end
- [ ] Output document is saved to `output/`
- [ ] Step logging shows: orchestrator call, own RAG query, peer MCP calls

---

## Task 10: Write tests

### Files
- `orchestrator/tests/test_router.py` — unit tests for `OrchestratorRouter`
- `orchestrator/tests/test_repo_rag.py` — unit tests for per-repo RAG isolation
- `orchestrator/tests/test_integration.py` — full flow integration test
- Update existing `test_config_loader.py` if needed

### Acceptance Criteria
- [ ] `test_router.py`: verifies correct repos returned for sample requests, excludes requesting_repo
- [ ] `test_repo_rag.py`: verifies each repo's RAG only returns content from its own repo
- [ ] `test_integration.py`: runs full flow, verifies Feature Analysis Document structure
- [ ] All tests pass: `bash scripts/test.sh`

---

## Task 11: Write architecture documentation

### File
`docs/architecture-distributed-repo-agents.md` (or update README.md)

### Content
- Diagram of the distributed architecture (ASCII)
- Before/after comparison with centralized architecture
- How to add a new repo agent
- How to run the demo
- How to use the MCP servers in VS Code Copilot

### Acceptance Criteria
- [ ] Document checked into repo
- [ ] Diagram matches actual implementation
- [ ] "How to run" section works when followed
