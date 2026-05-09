# ADR-001: LangGraph + MCP stdio + ChromaDB

**Date**: 2026-05-09  
**Status**: Accepted

## Decision
Use LangGraph for orchestration, MCP stdio transport for inter-agent calls, and ChromaDB with sentence-transformers for RAG.

## Reasons
- **LangGraph**: Graph-based flow maps directly to the demo's step-by-step dialogue — easy to explain and visualise. Simpler than CrewAI for a linear 4-step flow.
- **MCP stdio**: Requires no network ports, no server startup complexity. Each repo MCP server is a subprocess of the demo runner — clean lifecycle.
- **ChromaDB local**: No separate server process, persists to disk, re-indexes transparently. Works offline in a demo setting.
- **sentence-transformers**: Local embeddings — no OpenAI key needed for RAG, only an Anthropic key for LLM calls.
- **Claude Haiku 4.5**: Fastest and cheapest Anthropic model — keeps demo LLM latency low and token cost minimal.

## Trade-offs
- MCP stdio is not suitable for production multi-process deployments (use SSE/HTTP instead), but is ideal for a single-machine demo.
- ChromaDB local is not scalable beyond demo, but perfectly adequate for 3 repos × 3 knowledge files each.
