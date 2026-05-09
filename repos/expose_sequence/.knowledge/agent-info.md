# expose_sequence Agent Info

## Independent Agent

The `expose_sequence` repo runs its own independent AI agent with its own RAG index and MCP server.

## MCP Server

- **Script**: `repos/expose_sequence/mcp/mcp_server.py`
- **Tool**: `query_repo(feature_request: str) -> str`
- **Indexes**: `.knowledge/*.md`, `**/*.thrift`, `**/*.h`, `**/*.cpp` (this repo only)

## Agent Entry Point

- **Script**: `repos/expose_sequence/agent/repo_agent.py`
- Run standalone: `python repos/expose_sequence/agent/repo_agent.py "your feature request"`

## Workflow

When this agent receives a feature request:
1. Calls the orchestrator router MCP to get relevant peer repos
2. Queries its own RAG
3. Calls each peer repo's MCP server directly
4. Produces a Feature Analysis Document (Current State + Solution Design)

## Components

- **ExposureController** — exposure triggering, shot coordination, fault management
- **DoseManager** — dose budget, cumulative energy tracking, power correction commands
