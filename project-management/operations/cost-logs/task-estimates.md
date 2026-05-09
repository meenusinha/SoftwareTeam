# Cost Estimates — Task Log

---

## Task: distributed-repo-agents
**Date**: 2026-05-09  
**Description**: Refactor the RAG+MCP orchestration demo so each repo has its own independent agent, RAG, and MCP server. The orchestrator becomes a router-only. Repos communicate peer-to-peer via MCP. Output is a Feature Analysis Document.

### Model Pricing Used
| Model | Input | Output |
|-------|-------|--------|
| Claude Sonnet 4.6 | $3.00 / 1M tokens | $15.00 / 1M tokens |

### Per-Agent Estimate

| Agent | Role | Est. Input Tokens | Est. Output Tokens | Est. Cost |
|-------|------|------------------|--------------------|-----------|
| Architect | System design, technical spec, interface contracts, architecture docs | 50,000 | 25,000 | $0.525 |
| IT Setup | Env setup, dependency install, scripts | 10,000 | 5,000 | $0.105 |
| Developer | Refactor orchestrator; implement 3× per-repo RAG, 3× MCP servers, 3× agents; feature analysis doc generator; demo script | 80,000 | 40,000 | $0.840 |
| Tester | Unit tests (per-repo RAG, router), integration test (full flow), test report | 40,000 | 20,000 | $0.420 |
| IT Release | Package release artifacts, release notes, git tag | 15,000 | 5,000 | $0.120 |
| **TOTAL** | | **195,000** | **95,000** | **$2.01** |

### Threshold
**HIGH** ($1.00 – $10.00) — explicit user approval required before proceeding.

### Assumptions
- Model: Claude Sonnet 4.6 throughout all agents
- Input tokens include: existing codebase context (3 repos × ~6 files), design docs, conversation history
- Output tokens include: new source files, test files, documentation
- Developer step is the dominant cost driver (~42% of total)
- No retries or rework cycles included — actual cost may be 10–30% higher if corrections are needed
- Token counts are estimates; actual usage depends on context window compression

### Notes
- This is a **refactor + extension** task, not greenfield. Existing code will be read and partially rewritten.
- The Developer step touches every major file in `orchestrator/` and adds new files for each of the 3 repos.
- Documentation requirement (user: "document it also") adds ~5K output tokens to Architect and Developer steps — already included above.
