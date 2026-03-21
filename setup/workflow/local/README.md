# Agentic Workflow Template (Local Mode)

A **provider-agnostic template** for AI-assisted multi-agent development workflows.

This is the **local-only** version -- no GitHub account, no git, no pull requests required. Everything runs on your computer.

---

## Get Started

Copy this project to your computer and start building. No account setup, no repositories, no version control required.

1. Copy the project folder to your desired location
2. Configure your AI provider (see [Setup by Provider](#setup-by-provider))
3. Open the project in your preferred AI tool
4. Start describing what you want to build!

---

## Works With Any AI

| Provider | Models | Recommended Tools |
|----------|--------|-------------------|
| **Anthropic** | Claude 3.5, Opus 4 | Claude Code (recommended) |
| **Google** | Gemini 1.5 Pro, Flash | Aider, Cursor, Windsurf |
| **OpenAI** | GPT-4o, GPT-4 Turbo | Aider, Cursor, Windsurf |
| **Azure** | GPT-4, GPT-3.5 | Aider, Cursor, Windsurf |
| **GitHub** | Copilot | GitHub Copilot (VS Code) |
| **Ollama** | Local models | Aider, Continue |

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
- **Users who prefer working locally** without cloud services or version control

---

## **New here? Start with [QUICK-START.md](QUICK-START.md)**

A simple guide for non-programmers to get up and running.

---

## Quick Start (For Developers)

```bash
# 1. Set up your AI provider
# Linux/macOS:
export ANTHROPIC_API_KEY="your-api-key"  # or GOOGLE_API_KEY or OPENAI_API_KEY
# Windows (PowerShell): $env:ANTHROPIC_API_KEY = "your-api-key"
# Windows (CMD): set ANTHROPIC_API_KEY=your-api-key

# 2. Start your AI tool and describe what you want to build
claude           # For Claude Code (recommended)
aider            # For Aider (Gemini/OpenAI)
cursor .         # For Cursor IDE
# Or: Windsurf, Continue (VS Code), GitHub Copilot
```

## Features

- **LLM Provider Agnostic** - Works with any AI
- **Multi-agent workflow** with structured handoffs
- **Task management system**
- **Secure API key handling** (environment variables)
- **Works entirely offline** (except for AI API calls)
- **No account setup required** (beyond your AI provider)

## Structure

```
├── CLAUDE.md                # Claude Code workflow instructions
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
```

## How It Works

1. You describe what you want to build
2. Product Owner clarifies requirements, creates user story
3. Cost Analyst estimates resource usage (warns if expensive)
4. Architect enriches with technical specifications
5. Product Owner assigns tasks to agents
6. Agents work directly in the project directory
7. Each agent presents work for your review before handing off
8. You review and approve at each step

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

1. **Configure your AI provider** - Set your `LLM_API_KEY` environment variable (see `ai-assistants/provider-setup/README.md`)
2. **Add domain expertise** - Update agent files in `ai-assistants/agents/`
3. **Customize structure** - Modify directories for your project
4. **Configure builds** - Add your build system

## Security

- API keys stored as **environment variables**
- No keys in code or config files
- All work stays on your local machine

## License

[Add your license here]
