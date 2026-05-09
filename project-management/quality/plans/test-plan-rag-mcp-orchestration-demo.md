# Test Plan: rag-mcp-orchestration-demo

**Date**: 2026-05-09

## Scope

| Layer | What is tested |
|-------|---------------|
| C++ stubs | Compile successfully; method calls return expected stub values |
| Python RAG | ChromaDB indexes build; `query()` returns non-empty relevant strings |
| Python config | `load_config`, `get_repo_config`, `get_all_repo_names` work correctly; error on bad repo name |
| MCP server (smoke) | Server starts, indexes load, `query_knowledge` tool returns a result |
| End-to-end (manual) | Full agent dialogue runs with GITHUB_TOKEN set |

## Out of Scope

- LLM output quality (non-deterministic)
- Real Thrift RPC communication
- Network / cloud infrastructure

## Test Cases

### C++ (3 suites × ~4 assertions each)
- `test_illumination`: LightSource power set/get, enable/disable; LensSystem focus/aperture
- `test_scan_manager`: StageController move/home/ready; ScanSequencer start/stop/status
- `test_expose_sequence`: ExposureController start/stop/status; DoseManager set/calibrate/correct

### Python RAG (6 tests)
- Each repo: `test_rag_indexes_and_queries` — result length > 10
- Each repo: `test_rag_returns_string` — result is str

### Python Config (4 tests)
- `test_load_config` — 3 repos in config
- `test_get_all_repo_names` — all three names present
- `test_get_repo_config` — correct fields returned
- `test_get_repo_config_invalid` — ValueError raised

## Pass Criteria

- All automated tests pass with exit code 0
- No compilation errors for C++ stubs
- `bash scripts/run.sh` completes without exceptions when GITHUB_TOKEN is set
