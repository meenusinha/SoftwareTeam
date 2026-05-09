# User Story: Generic Multi-Repo RAG + MCP Agentic Orchestration Demo

**As a** software architect / engineering lead presenting at the office
**I want to** demonstrate a generic agentic orchestration framework where three distributed repositories consult each other via RAG, MCP, and an agent orchestrator when a new feature request arrives
**So that** the audience understands how AI agents can autonomously discover relevant design and implementation knowledge across distributed codebases and synthesise a solution design

---

## Context

The demo uses a **Lithography domain** as the concrete example, with three repos:
- **Illumination** — manages light source, lens, and illumination optics subsystem
- **ScanManager** — manages wafer stage scanning, motion control, and scan sequencing
- **ExposeSequence** — manages the exposure sequence, dose control, and shot coordination

Each repo contains:
- Thrift interface definitions (in a dedicated `interfaces/` folder)
- C++ implementation (in a dedicated `src/` folder)
- Subfunctional knowledge documents in a `.knowledge/` folder (design docs, API notes, component descriptions)

The entire framework is **config-driven**: all repo names, paths, and component names live in a single `workflow-config.json`. Swapping to any other three repos requires only editing that file.

---

## Acceptance Criteria

- [ ] A single `workflow-config.json` at the root lists all three repo names, their local paths, their component folders, and their knowledge folder paths
- [ ] Each of the three repos has minimal stub Thrift interfaces + C++ implementation (2–3 components per repo) and `.knowledge/` docs describing their design
- [ ] An **Agent Orchestrator** (LangGraph-based) receives a new feature request and determines which other repos are relevant to consult
- [ ] The requesting repo's agent queries the two identified repos via **MCP tools** to retrieve relevant knowledge
- [ ] Each repo exposes an **MCP server** that wraps a **RAG index** over its `.knowledge/` folder, answering queries about its design and implementation
- [ ] After gathering cross-repo knowledge, the requesting repo's agent produces a **consultation summary**: existing design/impl context + proposed solution design/impl
- [ ] The full agent dialogue is printed to the console in a clear, readable format (who asked, what tool was called, what was returned, final summary)
- [ ] The framework is generic: replacing the three repo names/paths in `workflow-config.json` should work without touching any agent or MCP code
- [ ] A single command (`bash scripts/run.sh`) runs the full demo end-to-end

---

## Scope

**In scope:**
- Generic orchestration framework (config-driven)
- Three lithography demo repos (Illumination, ScanManager, ExposeSequence) within this repository as separate top-level folders (no need for actual separate GitHub repos for the demo)
- Minimal Thrift interface stubs + C++ stub implementations (compilable but not fully functional)
- RAG over `.knowledge/` markdown docs using a lightweight vector store (ChromaDB or FAISS)
- MCP servers per repo (Python, stdio transport)
- LangGraph multi-agent orchestrator (Python)
- Console log output of the full agent dialogue
- Single `workflow-config.json` controlling all names and paths

**Out of scope:**
- Production-grade C++ builds or actual lithography logic
- Real Thrift RPC communication between services
- Cloud deployment or Docker
- GUI or web interface

---

## Priority
High — this is a demo for an office presentation

## Tech Stack (user inputs)
- Interfaces: Thrift IDL
- Implementation: C++ (stub level)
- Testing: C++ + Python
- Agents / Orchestration: Python + LangGraph
- RAG vector store: ChromaDB (lightweight, no server needed)
- MCP transport: stdio (simplest)
- Config: `workflow-config.json` (single file)

## Notes
- "Generic" is the key design principle: agents, MCP tools, and RAG must reference config values, never hardcoded repo names
- Keep it visually impressive but code-simple — the demo audience is engineers, not AI researchers
- The three repos are sibling folders inside this project, not actual remote repositories

---

## Status
- [ ] Assigned to Architect
- [ ] Technical design complete
- [ ] Implementation in progress
- [ ] Testing
- [ ] Ready for acceptance
- [ ] Accepted
