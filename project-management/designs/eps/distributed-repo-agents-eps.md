# Engineering Product Specification: Distributed Independent Repo Agents

## Overview

Each repository in the lithography scanner software system hosts its own fully independent AI agent. An agent owns the RAG index for its repo and exposes an MCP server. When a developer submits a feature request to any repo agent, that agent autonomously routes to peer repos via the orchestrator, queries them directly over MCP, and produces a **Feature Analysis Document** combining a current-state survey and a cross-repo solution design.

## User Stories

**Primary**: As a developer on the `expose_sequence` team, I want to submit a feature request to my repo's agent and receive a document showing what already exists across all relevant repos and how I should implement the feature end-to-end — without needing to know which other repos are involved.

**Secondary**: As a developer on any repo team, I want my repo's agent to answer peer queries about my repo's components, interfaces, and source files — independently, without going through a central system that owns all knowledge.

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | Each repo (`scan_manager`, `illumination`, `expose_sequence`) SHALL have its own RAG index, agent, and MCP server |
| FR-2 | Each repo's RAG SHALL index only that repo's own content (`.knowledge/` docs, `.thrift` interfaces, `.h` headers, `.cpp` implementations) |
| FR-3 | Each repo's MCP server SHALL expose a `query_repo(feature_request)` tool that returns structured knowledge (relevant components, interfaces, files, current behavior) |
| FR-4 | The orchestrator SHALL be a pure router: given a feature description, return the names of relevant repos — no RAG, no content retrieval |
| FR-5 | The orchestrator SHALL expose `get_relevant_repos(requesting_repo, feature_description)` as an MCP tool |
| FR-6 | When a repo agent receives a feature request, it SHALL: (1) call the orchestrator MCP for routing, (2) query its own RAG, (3) call each peer repo's MCP directly, (4) produce a Feature Analysis Document |
| FR-7 | The Feature Analysis Document SHALL contain two sections: **Current State** (what exists today in relevant repos) and **Solution Design** (cross-repo implementation recommendation) |
| FR-8 | A single-command demo SHALL execute the full flow: feature request → routing → peer queries → output document |
| FR-9 | Architecture documentation SHALL be written describing the distributed design |

## User Interface

The system is a CLI demo. The developer runs:

```bash
bash scripts/run.sh
```

The output is a Feature Analysis Document printed to stdout (and optionally saved to `output/`):

```
════════════════════════════════════════════════════════════════
 DISTRIBUTED REPO AGENT DEMO
 Requesting Repo  : ExposeSequence
 Feature Request  : Add adaptive dose correction based on real-time stage position feedback
════════════════════════════════════════════════════════════════

[STEP 1] expose_sequence Agent → Orchestrator MCP
  Tool: get_relevant_repos("Add adaptive dose correction...")
  Orchestrator response: ['scan_manager', 'illumination']

[STEP 2] expose_sequence Agent → scan_manager MCP (direct)
  Tool: query_repo("Add adaptive dose correction...")
  Response: [components, interfaces, files returned]

[STEP 3] expose_sequence Agent → illumination MCP (direct)
  Tool: query_repo("Add adaptive dose correction...")
  Response: [components, interfaces, files returned]

════════════════════════════════════════════════════════════════
 FEATURE ANALYSIS DOCUMENT
════════════════════════════════════════════════════════════════

## Current State
...

## Solution Design
...
```

## Success Criteria

- Each of the 3 repos starts and answers queries independently
- Orchestrator returns only repo names (no content) — confirmed by inspection
- Feature Analysis Document is produced for the demo feature request
- All unit and integration tests pass
- Architecture document is checked into the repo
