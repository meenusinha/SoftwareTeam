# Agentic Workflow Template

A **provider-agnostic template** for AI-assisted multi-agent development workflows.

## One-Command Setup (Recommended)

Paste ONE command to launch a browser-based setup wizard that handles everything:

**Mac / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/meenusinha/BigProjPOC/template/agentic-workflow-gui/setup/setup.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/meenusinha/BigProjPOC/template/agentic-workflow-gui/setup/setup.ps1 | iex
```

**New here? See [QUICK-START.md](QUICK-START.md)** for a simple 5-step guide.

---

## What is this?

A structured approach to software development using specialized AI agents:

- **Product Owner**: Customer-facing, gathers requirements, creates user stories
- **Architect**: Designs systems and creates technical specifications
- **Developer**: Implements features and writes code
- **Tester**: Tests and validates implementations
- **IT**: Manages infrastructure and releases
- **Cost Analyst**: Estimates token costs, warns before expensive operations

## Who is this for?

- **Non-programmers** who want AI help building software
- **Teams** wanting structured AI-assisted workflows
- **Projects** needing consistent development processes

## Works With Any AI

| Provider | Models | Recommended Tools |
|----------|--------|-------------------|
| **Anthropic** | Claude 3.5, Opus 4 | Claude Code (recommended) |
| **Google** | Gemini 1.5 Pro, Flash | Aider, Cursor, Windsurf |
| **OpenAI** | GPT-4o, GPT-4 Turbo | Aider, Cursor, Windsurf |
| **Azure** | GPT-4, GPT-3.5 | Aider, Cursor, Windsurf |
| **GitHub** | Copilot | GitHub Copilot (VS Code) |
| **Ollama** | Local models | Aider, Continue |

---

## Quick Start (For Developers)

```bash
# 1. Clone this template
git clone <repo-url> my-project
cd my-project

# 2. Set up your AI provider
cp ai-assistants/provider-setup/config.template.json ai-assistants/provider-setup/config.json

# Linux/macOS:
export ANTHROPIC_API_KEY="your-api-key"  # or GOOGLE_API_KEY or OPENAI_API_KEY
# Windows (PowerShell): $env:ANTHROPIC_API_KEY = "your-api-key"
# Windows (CMD): set ANTHROPIC_API_KEY=your-api-key

# 3. Start your AI tool and describe what you want to build
claude           # For Claude Code (recommended)
aider            # For Aider (Gemini/OpenAI)
cursor .         # For Cursor IDE
# Or: Windsurf, Continue (VS Code), GitHub Copilot
```

## Alternative Setup Methods

<details>
<summary>Click to expand manual setup options</summary>

### Option 1: GitHub Fork

1. Click the **Fork** button at the top right of this repository
2. Select your account/organization
3. Clone your forked repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/YOUR-FORK-NAME.git
   cd YOUR-FORK-NAME
   ```
4. Start building with your preferred AI tool!

### Option 2: Use as GitHub Template

If the repository owner has enabled "Template repository":
1. Click **"Use this template"** → **"Create a new repository"**
2. Name your new repository and set visibility
3. Clone and start building

### Option 3: Manual Clone (No GitHub Account)

```bash
# Clone the template branch
git clone -b template/agentic-workflow https://github.com/REPO-OWNER/REPO-NAME.git my-project
cd my-project

# Remove original remote and set up your own
git remote remove origin
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git

# Push to your repository
git push -u origin main
```

### After Setup

1. Update `README.md` with your project details
2. Configure your AI provider (see [Setup by Provider](#setup-by-provider))
3. Customize agent roles in `ai-assistants/agents/` if needed
4. Start describing what you want to build!

</details>

## Features

- **LLM Provider Agnostic** - Works with any AI
- **Multi-agent workflow** with peer review
- **Git worktree support** for parallel work
- **Task management system**
- **GitHub Actions** for automation
- **Secure API key handling** (environment variables, gitignored)

## Structure

```
├── CLAUDE.md                # Claude Code workflow instructions
├── .github/copilot-instructions.md  # GitHub Copilot workflow instructions
├── .vscode/settings.json   # VS Code settings (enables Copilot instructions)
├── .cursorrules             # Cursor IDE workflow instructions
├── .windsurfrules           # Windsurf IDE workflow instructions
├── .continuerules           # Continue extension workflow instructions
├── .aider.conf.yml          # Aider CLI configuration
│
├── ai-assistants/           # AI setup and configuration
│   ├── agents/              # Agent role definitions
│   ├── provider-setup/      # LLM provider configuration
│   └── how-to-use.md        # Getting started guide
│
├── project-management/      # Project documentation
│   ├── tasks/               # Task assignments
│   │   └── backlog/         # User stories (Product Owner)
│   ├── designs/             # Architecture docs
│   ├── requirements/        # Feature requirements
│   ├── quality/             # Test plans and QA
│   └── operations/          # Releases and infrastructure
│
├── modules/                 # Software modules
│   └── [module-name]/       # Each module is self-contained
│
├── scripts/                 # Build, test, run scripts
│   ├── build.sh             # Build all modules
│   ├── test.sh              # Run all tests
│   ├── run.sh               # Run the application
│   └── clean.sh             # Clean build artifacts
│
├── output/                  # Combined build output (all modules)
├── Makefile                 # Top-level build script
├── .github/workflows/       # GitHub Actions
└── AI-WORKFLOW.md           # Main workflow documentation
```

## How It Works

1. You describe what you want to build
2. Product Owner clarifies requirements, creates user story
3. Cost Analyst estimates resource usage (warns if expensive)
4. Architect enriches with technical specifications
5. Product Owner assigns tasks to agents
6. Agents work independently in git worktrees
7. Peer review ensures quality
8. PRs are created for your review

## Setup by Provider

### Anthropic Claude (Recommended)
```bash
# Linux/macOS:
export ANTHROPIC_API_KEY="sk-ant-..."
# Windows (PowerShell): $env:ANTHROPIC_API_KEY = "sk-ant-..."

npm install -g @anthropic-ai/claude-code
claude
```

### Google Gemini
```bash
# Linux/macOS:
export GOOGLE_API_KEY="your-key-here"
# Windows (PowerShell): $env:GOOGLE_API_KEY = "your-key-here"

pip install aider-chat
aider --model gemini/gemini-1.5-pro-latest
```

### OpenAI (GPT-4)
```bash
# Linux/macOS:
export OPENAI_API_KEY="sk-..."
# Windows (PowerShell): $env:OPENAI_API_KEY = "sk-..."

pip install aider-chat
aider
```

See `ai-assistants/provider-setup/README.md` for detailed setup instructions.

## Customization

1. **Configure your AI provider** - Edit `ai-assistants/provider-setup/config.json`
2. **Add domain expertise** - Update agent files in `ai-assistants/agents/`
3. **Customize structure** - Modify directories for your project
4. **Configure builds** - Add your build system
5. **Update workflows** - Modify `.github/workflows/`

## Security

- API keys stored as **environment variables**
- Secrets are **automatically gitignored**
- No keys in code or config files

## License

[Add your license here]
