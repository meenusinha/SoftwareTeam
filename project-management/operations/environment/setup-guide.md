# Environment Setup Guide: Distributed Repo Agents

## Prerequisites

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.11 | Required |
| pip | any | Required |
| git | 2.39+ | Required |
| gh CLI | 2.85+ | Required |

## Python Virtual Environment

A `.venv` is already present in the project root with all dependencies installed.

To activate:
```bash
source .venv/bin/activate   # Mac/Linux
```

## Dependencies (requirements.txt)

| Package | Purpose |
|---------|---------|
| `langgraph` | Agent state machine (LangGraph) |
| `langchain-openai` | LLM integration (optional — for synthesis) |
| `chromadb` | Per-repo vector store for RAG |
| `sentence-transformers` | Embedding model (all-MiniLM-L6-v2) |
| `mcp` (fastmcp) | MCP server/client framework |
| `python-dotenv` | .env loading |
| `pytest` | Test runner |
| `numpy` | Vector math for router |

To reinstall:
```bash
bash scripts/build.sh
```

## Environment Variables (.env)

Copy `.env.example` to `.env` and set:

```
GITHUB_TOKEN=your_github_models_token
```

`GITHUB_TOKEN` is **optional**. Without it, the LLM synthesis step is skipped and the Feature Analysis Document is produced using a template fallback. The RAG + routing flow works fully without it.

## Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| Run demo | `bash scripts/run.sh` | Full distributed agent flow |
| Run tests | `bash scripts/test.sh` | pytest on orchestrator/tests/ |
| Install deps | `bash scripts/build.sh` | pip install -r requirements.txt |

## Verified On

- macOS 14 (Sonoma), Python 3.11, .venv active
- All 4 baseline tests pass: `pytest orchestrator/tests/ -v`
