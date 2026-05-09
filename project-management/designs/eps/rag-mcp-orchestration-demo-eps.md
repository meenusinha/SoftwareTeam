# Engineering Product Specification: Generic Multi-Repo RAG + MCP Agentic Orchestration Demo

## Overview

A runnable demo showing how AI agents in three distributed software repositories can autonomously consult each other's design knowledge — via RAG retrieval and MCP tool calls — when a new feature request arrives. The entire framework is config-driven so it can be reused with any three repos by editing a single JSON file.

## User Stories

**As a** presenter at an engineering office demo
**I want to** trigger a feature request for one repo and watch agents automatically consult the other two repos
**So that** the audience sees a concrete, understandable example of multi-repo agentic orchestration using RAG + MCP

## Functional Requirements

### FR-1: Single Config File
All repo names, paths, component names, and knowledge locations are defined in `workflow-config.json`. No repo-specific names appear anywhere in agent, MCP, or RAG code.

### FR-2: Three Demo Repos (Lithography Domain)
Three sibling folders simulate three distributed repositories:
- `repos/illumination/` — Illumination subsystem (light source, lens, optics)
- `repos/scan_manager/` — Scan management subsystem (stage, motion, scan sequencing)
- `repos/expose_sequence/` — Exposure sequencing subsystem (dose control, shot coordination)

Each repo has:
- `interfaces/` — Thrift IDL interface definitions (2 files per repo)
- `src/` — C++ stub implementations (one folder per component)
- `.knowledge/` — Markdown knowledge docs (3 files: overview, components, interfaces)

### FR-3: RAG Knowledge Retrieval
Each repo's `.knowledge/` folder is indexed into a local ChromaDB vector store. A generic RAG module can query any repo's knowledge base given a natural language question.

### FR-4: MCP Server Per Repo
Each repo exposes a generic MCP server (stdio transport) that wraps its RAG index. The MCP server exposes one tool: `query_knowledge(question: str) -> str`. The server is launched with the repo name as argument; it reads config to find the knowledge path.

### FR-5: Agent Orchestrator
A LangGraph-based orchestrator receives a feature request for a specified repo and decides which other repos to consult (by analysing the request and repo descriptions from config).

### FR-6: Repo Agent
A generic repo agent (one instance per repo, parameterised from config):
1. Sends the feature request to the orchestrator to get consultation targets
2. Calls the MCP `query_knowledge` tool on each target repo
3. Aggregates the responses
4. Generates a structured consultation summary (existing design context + proposed solution)

### FR-7: Console Output
The demo prints a clear, human-readable dialogue log showing each step: which agent spoke, what tool was called, what was returned, and the final summary.

### FR-8: Single Run Command
`bash scripts/run.sh` installs dependencies (first run) and launches the full demo.

## User Interface

- **Input**: A feature request string + the name of the "requesting repo" (passed via command line or hardcoded in demo script for presentation)
- **Output**: Console log of the full multi-agent dialogue + final consultation summary

## Success Criteria

- Swapping the three repo names in `workflow-config.json` to any other three repos makes the framework work without code changes
- The console output clearly shows each agent step and MCP call
- A first-time viewer can follow the flow without explanation
- `bash scripts/run.sh` runs the complete demo in one command
