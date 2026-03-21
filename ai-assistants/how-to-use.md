# Getting Started with AI Assistants

This guide helps you set up and use AI assistants for your software project.

## IMPORTANT: Automatic Workflow Enforcement

This template includes configuration files that instruct AI assistants to follow the agentic workflow:

| AI Tool | Config File | Purpose |
|---------|-------------|---------|
| Claude Code | `CLAUDE.md` | Instructions for Claude Code CLI |
| GitHub Copilot | `.github/copilot-instructions.md` + `.vscode/settings.json` | Instructions for GitHub Copilot |
| Cursor | `.cursorrules` | Instructions for Cursor IDE |
| Windsurf | `.windsurfrules` | Instructions for Windsurf IDE |
| Continue | `.continuerules` | Instructions for Continue extension |
| Aider | `.aider.conf.yml` + `.aider.conventions.md` | Instructions for Aider CLI |

These files ensure the AI **always starts as IT-agent** and follows the complete workflow.

## Quick Setup (5 minutes)

### Step 1: Choose Your AI Provider

Pick one AI service to use:

| Provider | Cost | Best For |
|----------|------|----------|
| **Anthropic (Claude)** | Pay per use | Best for software projects (recommended) |
| **Google (Gemini)** | Pay per use | Google ecosystem |
| **OpenAI (GPT-4)** | Pay per use | General coding |

### Step 2: Get Your API Key

1. **Anthropic**: Go to https://console.anthropic.com/
2. **Google Gemini**: Go to https://aistudio.google.com/ → Click "Get API Key"
3. **OpenAI**: Go to https://platform.openai.com/api-keys

### Step 3: Configure Your Provider

```bash
# Set your API key:
# Linux/macOS (add to ~/.bashrc or ~/.zshrc for persistence):
export LLM_API_KEY="your-api-key-here"

# Windows (PowerShell — add to $PROFILE for persistence):
# $env:LLM_API_KEY = "your-api-key-here"
```

### Step 4: Install an AI Coding Tool

Choose one:

**Option A: Claude Code (Recommended - Best for software projects)**
```bash
npm install -g @anthropic-ai/claude-code
claude
```

**Option B: Aider (Works with Gemini and OpenAI)**
```bash
pip install aider-chat
aider
```

**Option C: Cursor IDE**
Download from https://cursor.sh

## How the Agent System Works

When you interact with the AI, it will automatically:

1. **Start as IT agent** - ALWAYS the first role for any request
2. **Customize the template** - Update domain info and agent skills for your project
3. **Adopt specialized roles** - Architect, Developer, Tester, IT as needed
4. **Follow the workflow** - Requirements, design, implement, test, release
5. **Create pull requests** - For your review before merging

### What Happens on First Request

When you give the AI its first task, the IT agent will:
1. Start the agentic pixel animation, verify that git and gh CLI are installed and authenticated.
Then Product Owner will
2. Update agent files in `ai-assistants/agents/` with your project's domain information
3. Update agent skills in `ai-assistants/agents/` for your project type
4. Create a user story documenting your request
5. Then proceed with the normal workflow

### The 6 Agent Roles

| Agent | What They Do |
|-------|--------------|
| **Product Owner** | Gathers requirements, creates user stories, coordinates agents |
| **Architect** | Designs systems, creates technical specifications |
| **Developer** | Writes code, implements features |
| **Tester** | Tests code, reports bugs, validates quality |
| **IT** | Manages builds, releases, infrastructure |
| **Cost Analyst** | Estimates token costs, warns before expensive operations |

## Example Conversations

### Building a New Feature

You say:
> "I want to add a login page with email and password"

The AI will:
1. IT-agent: Start pixel agentic animation, verify git and gh installations and authentications.
2. Product Owner: Create user story with acceptance criteria
3. Architect: Design the login flow with technical specs
4. Developer: Implement the code
5. Tester: Validate it works
6. Create a PR for your review

### Fixing a Bug

You say:
> "Users can't save their profile changes"

The AI will:
1. Product Owner: Document the issue
2. Tester: Investigate and document the bug
3. Developer: Fix the issue
4. Tester: Verify the fix
5. Create a PR for your review

## Project Structure

```
your-project/
├── agent_animation/         # Pixel agentic animation
├── ai-assistants/           # AI configuration (you are here)
│   ├── agents/              # Agent role definitions
│   ├── provider-setup/      # Your AI provider config
│   └── how-to-use.md        # This guide
│
├── project-management/      # Project documentation
│   ├── tasks/               # Task tracking
│   ├── designs/             # Architecture docs
│   ├── requirements/        # Feature requirements
│   ├── quality/             # Test plans
│   └── operations/          # Release docs
│
├── modules/                 # Software modules
│   ├── module-name/         # Each module is self-contained
│   │   ├── src/             # Module source code
│   │   ├── test/            # Module tests
│   │   ├── release/         # Module release output
│   │   ├── debug/           # Module debug output
│   │   ├── build-config/    # Build configuration
│   │   └── Makefile         # Module build script
│   └── example-module/      # Template to copy for new modules
│
├── output/                  # Combined output (all modules)
│   ├── release/             # Combined release builds
│   └── debug/               # Combined debug builds
│
├── Makefile                 # Top-level build script
└── .github/                 # GitHub workflows
```

## Need Help?

- **Agent definitions**: See `ai-assistants/agents/`
- **Provider setup**: See `ai-assistants/provider-setup/README.md`
- **Workflow details**: See your AI tool's workflow guide (CLAUDE.md, .cursorrules, etc.) in project root
