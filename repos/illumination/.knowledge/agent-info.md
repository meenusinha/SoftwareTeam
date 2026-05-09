# illumination Agent Info

## Independent Agent

The `illumination` repo runs its own independent AI agent with its own RAG index and MCP server.

## MCP Server

- **Script**: `repos/illumination/mcp/mcp_server.py`
- **Tool**: `query_repo(feature_request: str) -> str`
- **Indexes**: `.knowledge/*.md`, `**/*.thrift`, `**/*.h`, `**/*.cpp` (this repo only)

## Agent Entry Point

- **Script**: `repos/illumination/agent/repo_agent.py`
- Run standalone: `python repos/illumination/agent/repo_agent.py "your feature request"`

## Workflow

When this agent receives a feature request:
1. Calls the orchestrator router MCP to get relevant peer repos
2. Queries its own RAG
3. Calls each peer repo's MCP server directly
4. Produces a Feature Analysis Document (Current State + Solution Design)

## Components

- **LightSource** — laser power control, dose measurement, power correction
- **LensSystem** — numerical aperture, beam conditioning, illumination uniformity
