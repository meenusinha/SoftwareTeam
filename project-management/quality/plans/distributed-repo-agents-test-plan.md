# Test Plan: Distributed Independent Repo Agents

**Date**: 2026-05-09  
**Feature**: Distributed Repo Agents with RAG + MCP  
**Tester**: Tester Agent

---

## Scope

### In Scope
- `OrchestratorRouter` — routing logic, exclusion of requesting repo, embedding-based scoring
- Per-repo `RepoRAG` — isolation (each repo only indexes its own content)
- `generate_feature_analysis` — document structure, LLM fallback template
- Per-repo MCP servers — tool response format
- Full integration flow — router → own RAG → peer MCPs → document

### Out of Scope
- LLM synthesis (requires external API token)
- C++ source compilation (mock repos, no build system)
- VS Code Copilot UI

---

## Test Strategy

| Level | Tests | Framework |
|-------|-------|-----------|
| Unit | OrchestratorRouter, RepoRAG isolation, feature_analysis generator | pytest |
| Integration | Router MCP server, per-repo MCP servers | pytest + subprocess |
| System | Full demo flow end-to-end | pytest |

---

## Test Cases

### T-01: Router excludes requesting repo
- Input: requesting_repo="expose_sequence", any feature
- Expected: "expose_sequence" NOT in returned targets

### T-02: Router returns top_k results
- Input: top_k=2, 3 repos available (excluding requesting)
- Expected: exactly 2 repos returned

### T-03: Router score range and fallback
- Input: mock _mcp_call returning rich content for all peers
- Expected: scores are floats in [0.0, 1.0]
- Input: mock _mcp_call returning "No relevant knowledge found." for all peers
- Expected: still returns top_k repos (fallback behavior), all scores 0.0

### T-04: RAG isolation — scan_manager
- Expected: scan_manager RAG returns content only from scan_manager files
  (collection names: repo_scan_manager_docs, repo_scan_manager_code)

### T-05: RAG isolation — illumination
- Expected: illumination RAG uses illumination collections only

### T-06: RAG isolation — expose_sequence
- Expected: expose_sequence RAG uses expose_sequence collections only

### T-07: RAG returns relevant content
- Input: "stage position feedback" → scan_manager RAG
- Expected: non-empty result containing position/stage-related content

### T-08: Feature analysis document structure
- Expected: document contains "## Current State" and "## Solution Design" sections

### T-09: Feature analysis LLM fallback
- Input: llm=None
- Expected: document produced without error, contains template text

### T-10: Feature analysis includes all repos
- Input: own_knowledge + 2 peer_responses
- Expected: document mentions all 3 repos in Current State

### T-11: Router MCP server responds correctly
- Launch router_mcp_server.py as subprocess, send MCP call
- Expected: valid JSON-RPC response with repo names

### T-12: Per-repo MCP server responds correctly
- Launch each repo's mcp_server.py, call query_repo
- Expected: response contains repo name + RELEVANT KNOWLEDGE section

### T-13: Integration — router + RAG pipeline
- Instantiate IndependentRepoAgent without MCP subprocesses
- Verify router targets + own RAG result populated

### T-14: Full demo runs without error
- Run run_demo.py as subprocess
- Expected: exit code 0, "Feature Analysis Document" in stdout
