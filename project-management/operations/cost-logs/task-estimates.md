# Cost Estimates

## Task: rag-mcp-orchestration-demo
**Date**: 2026-05-09
**Model**: Claude Sonnet 4.6 — Input $3/1M tokens · Output $15/1M tokens

### Scope
Building a generic multi-repo RAG + MCP agentic orchestration demo with:
- 3 demo repos (Illumination, ScanManager, ExposeSequence) — Thrift IDL + C++ stubs + knowledge docs
- Python MCP server per repo (wrapping ChromaDB RAG)
- LangGraph multi-agent orchestrator
- Generic config file (`workflow-config.json`)
- Scripts (run, build, test, clean)
- All agent workflow deliverables (design docs, test reports, release notes)

### Per-Agent Breakdown

| Agent Step | Input Tokens | Output Tokens | Input Cost | Output Cost | Subtotal |
|------------|-------------|---------------|------------|-------------|---------|
| Product Owner (done) | 15,000 | 6,000 | $0.045 | $0.090 | $0.135 |
| Cost Analyst (this) | 8,000 | 3,000 | $0.024 | $0.045 | $0.069 |
| Architect — design docs, tech specs, interfaces | 55,000 | 30,000 | $0.165 | $0.450 | $0.615 |
| IT — project setup, scripts, deps | 25,000 | 12,000 | $0.075 | $0.180 | $0.255 |
| Developer — 3× (Thrift + C++ + knowledge docs + MCP server) + orchestrator + config | 120,000 | 90,000 | $0.360 | $1.350 | $1.710 |
| Tester — test plans, C++/Python tests, test report | 35,000 | 18,000 | $0.105 | $0.270 | $0.375 |
| IT Release — packaging, release notes, tagging | 15,000 | 6,000 | $0.045 | $0.090 | $0.135 |
| Product Owner Acceptance | 10,000 | 4,000 | $0.030 | $0.060 | $0.090 |
| **TOTAL** | **283,000** | **169,000** | **$0.849** | **$2.535** | **$3.384** |

### Threshold Assessment
- Estimated total: **~$3.40**
- Threshold: **HIGH** ($1–$10)

```
COST WARNING

This operation is estimated to be moderately expensive:
- Task: Generic multi-repo RAG+MCP orchestration demo (full 9-step workflow)
- Estimated input tokens:  283,000
- Estimated output tokens: 169,000
- Estimated total cost:    ~$3.40  (Claude Sonnet 4.6)
- Threshold:               HIGH ($1–$10)

The Developer step is the dominant cost driver (~50% of total)
because it generates 3 repos × (Thrift IDL + C++ stubs + knowledge
docs + Python MCP server) plus the LangGraph orchestrator.

This estimate assumes one pass per agent with minimal rework.
If the user requests rework or additional iterations, add ~$0.50–$1.00
per major revision cycle.
```

### Assumptions
- One pass per agent, minimal back-and-forth rework
- Knowledge docs are concise markdown (~500–800 words each)
- C++ stubs are minimal (function signatures + stub bodies, ~100–200 LOC per component)
- Thrift IDL files are small (~30–50 lines each)
- LangGraph orchestrator: ~200–300 LOC Python
- MCP servers: ~100–150 LOC Python each

### Optimization Notes
- The framework is config-driven, so the Developer generates reusable code once — no per-repo duplication of agent logic
- ChromaDB is local, so no ongoing RAG API costs
- LangGraph runs locally — no cloud orchestration costs

### User Approved
- [ ] Yes
- [ ] No
