# Developer Task Specifications: rag-mcp-orchestration-demo

## Task 1: Create `workflow-config.json`

**File**: `workflow-config.json` (project root)

Create the single config file as specified in EDS section "Component Design § 1". Include all three repos (illumination, scan_manager, expose_sequence) with their paths, descriptions, components, and knowledge paths. Include `llm`, `rag`, and `demo` sections.

**Acceptance Criteria**:
- [ ] File exists at project root
- [ ] All three repos defined with name, display_name, path, knowledge_path, description, components
- [ ] `llm.model` set to `claude-haiku-4-5-20251001`
- [ ] `rag.embedding_model` set to `all-MiniLM-L6-v2`
- [ ] `demo.requesting_repo` = `expose_sequence`, `demo.feature_request` = the adaptive dose correction feature

---

## Task 2: Create Three Repo Folder Structures

For each of `repos/illumination/`, `repos/scan_manager/`, `repos/expose_sequence/`:

**Sub-task 2a: Thrift IDL files** (`interfaces/`)
Create the 2 Thrift files per repo exactly as specified in `project-management/designs/interfaces/thrift-interface-specs.md`.

**Sub-task 2b: C++ stub implementations** (`src/{Component}/`)
For each component create `{Component}.h` and `{Component}.cpp`:
- Header: class declaration with method signatures matching the Thrift interface
- Implementation: stub bodies returning default values (0, false, empty string, default struct)
- No real logic — stubs only

**Sub-task 2c: Knowledge documents** (`.knowledge/`)
Create 3 markdown files per repo:
- `overview.md` — What this subsystem does in a lithography scanner; its role; key responsibilities
- `components.md` — For each component: what it controls, its key state, how it interacts with other subsystems
- `interfaces.md` — Description of each Thrift interface method: what it does, when it's called, what it returns

Knowledge docs must be detailed enough for the RAG to return meaningful answers about cross-repo dependencies. Aim for 300–500 words per file.

**Acceptance Criteria**:
- [ ] All 3 repos have `interfaces/`, `src/`, `tests/`, `.knowledge/` folders
- [ ] Each repo has 2 `.thrift` files in `interfaces/`
- [ ] Each repo has C++ header + stub `.cpp` per component in `src/`
- [ ] Each repo has `overview.md`, `components.md`, `interfaces.md` in `.knowledge/`
- [ ] Knowledge docs contain meaningful domain content (not placeholder text)

---

## Task 3: Generic RAG Module (`orchestrator/rag/repo_rag.py`)

Implement `RepoRAG` class:
```python
class RepoRAG:
    def __init__(self, repo_name: str, config: dict): ...
    def build_or_load_index(self) -> None: ...
    def query(self, question: str) -> str: ...
```
- Loads knowledge files from `config["knowledge_path"]`
- Chunks markdown by paragraph (split on `\n\n`)
- Embeds with `sentence-transformers/all-MiniLM-L6-v2` via ChromaDB's embedding function
- Persists collection to `.chroma_db/{repo_name}`
- `query()` returns top-k chunks joined by `\n---\n`

**Acceptance Criteria**:
- [ ] Works for any repo by passing repo config dict
- [ ] Rebuilds index if collection missing, loads from disk if present
- [ ] Returns non-empty string for any reasonable query

---

## Task 4: Generic MCP Server (`orchestrator/mcp/repo_mcp_server.py`)

Implement a generic MCP server launched with `--repo {repo_name}`:
- Loads config, finds the repo's config dict
- Creates a `RepoRAG` instance for that repo
- Exposes one MCP tool: `query_knowledge(question: str) -> str`
- Uses `mcp` Python SDK, stdio transport

**Acceptance Criteria**:
- [ ] Runs as `python repo_mcp_server.py --repo illumination` (and for the other two)
- [ ] `query_knowledge` tool returns RAG results
- [ ] No repo-specific code — all parameterised from config

---

## Task 5: Orchestrator Agent (`orchestrator/orchestrator_agent.py`)

Implement `OrchestratorAgent`:
```python
class OrchestratorAgent:
    def decide_consultations(self, requesting_repo: str, feature_request: str) -> list[str]:
        """Returns list of 2 repo names to consult."""
```
- Uses `langchain_openai.ChatOpenAI` with GitHub Models endpoint:
  ```python
  from langchain_openai import ChatOpenAI
  llm = ChatOpenAI(
      model="gpt-4o-mini",
      base_url="https://models.inference.ai.azure.com",
      api_key=os.environ["GITHUB_TOKEN"]
  )
  ```
- Prompt: given repo descriptions from config + the feature request, pick the 2 most relevant repos to consult (excluding the requesting repo)
- Returns repo names as a list

**Acceptance Criteria**:
- [ ] Reads repo descriptions from config (not hardcoded)
- [ ] Returns exactly 2 repo names
- [ ] Works for any requesting repo

---

## Task 6: Repo Agent (`orchestrator/repo_agent.py`)

Implement `RepoAgent` as a LangGraph graph:

Nodes:
1. `ask_orchestrator` — calls `OrchestratorAgent.decide_consultations()`
2. `consult_repo_1` — launches MCP server subprocess for target 1, calls `query_knowledge`, captures result, shuts down
3. `consult_repo_2` — same for target 2
4. `generate_summary` — calls GitHub Models (gpt-4o-mini via `langchain_openai`) with feature request + both knowledge snippets, generates structured summary

State: `{ requesting_repo, feature_request, targets, knowledge_1, knowledge_2, summary }`

**Acceptance Criteria**:
- [ ] Uses LangGraph `StateGraph`
- [ ] Each node logs its action to console with `[STEP N]` prefix
- [ ] MCP subprocess lifecycle managed cleanly (start, call, stop)
- [ ] Summary clearly shows "Existing Design Context" and "Proposed Solution Design" sections

---

## Task 7: Config Loader (`orchestrator/config_loader.py`)

Simple module:
```python
def load_config(path: str = "workflow-config.json") -> dict: ...
def get_repo_config(config: dict, repo_name: str) -> dict: ...
def get_all_repo_names(config: dict) -> list[str]: ...
```

**Acceptance Criteria**:
- [ ] Raises clear error if config file not found
- [ ] Raises clear error if repo_name not in config

---

## Task 8: Demo Runner (`orchestrator/demo/run_demo.py`)

Entry point:
1. Load config
2. Print banner (repo name + feature request)
3. Build/load RAG indexes for all repos (print progress)
4. Create and run `RepoAgent`
5. Print final summary in the formatted box shown in EDS

**Acceptance Criteria**:
- [ ] Single script, runs the whole demo
- [ ] Prints each step clearly as it happens
- [ ] Handles missing `ANTHROPIC_API_KEY` gracefully (clear error message)

---

## Task 9: Tests

**C++ tests** (`repos/{repo}/tests/cpp/test_{repo}.cpp`):
- Include each component header
- Instantiate each component class
- Call stub methods, assert they don't crash
- Use a simple `assert()` or minimal test harness (no Catch2 dependency for simplicity)

**Python tests** (`repos/{repo}/tests/python/test_{repo}.py`):
- Test that `RepoRAG` indexes and queries successfully for each repo
- Test that `OrchestratorAgent` returns 2 valid repo names
- Test that `config_loader` loads correctly

**Acceptance Criteria**:
- [ ] C++ test files compile with `g++ -std=c++17`
- [ ] Python tests pass with `pytest`

---

## Task 10: Scripts

Update `scripts/run.sh`:
1. Check for `.venv/` and create + install deps if missing
2. Source `.env` if it exists
3. Check `ANTHROPIC_API_KEY` is set
4. Run `python orchestrator/demo/run_demo.py`

Update `scripts/test.sh`:
1. Activate venv
2. Run `pytest repos/*/tests/python/ -v`
3. Attempt C++ compile check for each repo's test

Update `scripts/build.sh`:
- Attempt Thrift IDL validation (`thrift --version` check, then `thrift -r --gen cpp`)
- Compile C++ stubs if `g++` available

**Acceptance Criteria**:
- [ ] `bash scripts/run.sh` runs end-to-end from a clean clone (installs deps on first run)
- [ ] `bash scripts/test.sh` runs all Python tests
