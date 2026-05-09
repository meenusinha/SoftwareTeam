# User Story: Distributed Independent Repo Agents with RAG + MCP

**As a** developer working across multiple instrument software repositories
**I want** each repository to have its own independent AI agent with its own RAG and MCP server
**So that** any repo agent can independently handle feature requests by consulting the orchestrator for routing and then directly querying peer repo agents for cross-repo context — producing a structured analysis and design document as output

---

## Background

The current `rag-mcp-orchestration-demo` has a single centralized orchestrator that owns all the RAG indexes and routes queries itself. This is a centralized design.

The desired architecture is **decentralized (peer-to-peer)**: each repo is a fully autonomous agent. The orchestrator is demoted to a **router only** — it no longer holds RAG or answers questions about repos. Instead it tells the requesting repo *which other repos* are relevant, and the repos talk directly to each other.

---

## Acceptance Criteria

### Repo Agent Independence
- [ ] Each repo (`scan_manager`, `illumination`, `expose_sequence`) has its own RAG instance, indexed only on that repo's `.knowledge/` docs, interfaces, source files, and headers
- [ ] Each repo has its own MCP server exposing a `query_repo` tool
- [ ] Each repo has its own agent (`repo_agent.py` or equivalent) that uses its local RAG to answer questions about its own codebase

### Orchestrator as Router Only
- [ ] The orchestrator no longer holds any RAG indexes
- [ ] The orchestrator's only responsibility is: given a feature description, return the list of repo names that are relevant
- [ ] The orchestrator exposes this as an MCP tool: `get_relevant_repos(feature_description) -> [repo_names]`

### Feature Request Flow
- [ ] When a repo agent receives a feature request, it first calls the orchestrator MCP to get the list of relevant repos
- [ ] The requesting repo agent then calls each returned repo's MCP server directly with the feature context
- [ ] Each queried repo agent consults its own RAG (interfaces, docs, source) and returns:
  - Which of its components are relevant
  - Which implementation files / interfaces are affected
  - What the current behavior/state is in that area
- [ ] The requesting repo agent collects all peer responses and produces a **Feature Analysis Document** containing:
  - **Current State**: what exists today across all relevant repos related to this feature
  - **Solution Design**: a cross-repo design suggestion naming which components in which repos need to change and how

### Documentation
- [ ] Architecture document written describing the new distributed agent design (data flow, component responsibilities, MCP interface contracts)
- [ ] Each repo's `.knowledge/` files updated if needed to reflect the new agent setup
- [ ] A demo script or run command that shows the full flow end-to-end: submit a feature request → orchestrator routes → repos respond → analysis document is produced

### Tests
- [ ] Unit tests for each repo's RAG (verify it indexes and retrieves from its own repo only)
- [ ] Unit tests for the orchestrator router (verify it returns correct repo names for a given feature)
- [ ] Integration test: full flow from feature request → orchestrator routing → peer repo queries → output document

---

## Priority

High

---

## Scope

**In scope:**
- Refactor orchestrator to router-only role
- Add per-repo RAG instances
- Add per-repo MCP servers
- Add per-repo agents
- Implement direct repo-to-repo MCP communication
- Feature Analysis Document generation (current state + solution design)
- Architecture documentation

**Out of scope:**
- UI / web interface
- Authentication between agents
- Deployment / containerization
- Real GitHub API integration (repos remain local mock repos)

---

## Notes

- User explicitly requested documentation of the new architecture
- "Document it also" — architecture docs and per-repo `.knowledge/` updates are mandatory deliverables
- The feature request initiator role can be played by any repo agent; the flow is symmetric
- The demo should use the existing 3 mock repos: `scan_manager`, `illumination`, `expose_sequence`

---

## Status

- [ ] Assigned to Architect
- [ ] Technical design complete
- [ ] Implementation in progress
- [ ] Testing
- [ ] Ready for acceptance
- [ ] Accepted
