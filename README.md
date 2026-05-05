# SoftwareTeam - Turn any AI tool into a structured software team—using simple markdown files.
### An AI-powered software team that turns your idea into a working system.

Demo and usage youtube link: https://youtube.com/playlist?list=PL9pyH9gllMkrA0EhM40H-duz9qwhVVqh9&si=9lE_S8cR7zQUVMs2

- **Give it a task** - Your agentic team plans, designs, and builds it automatically in your AI tool.

- **Works two ways**: Agents run with full GitHub integration (auto branches, PRs, and multi-agent review) — or entirely locally with no GitHub needed.

- **Predefined AI agents** work out-of-the-box, or **use this as a template** to customize your workflows.
[Pixel based animation makes AI collaboration feel alive and tangible.]

## SoftwareTeam comes with predefined AI agents prompts that mimic the workflow of a software team: ##

- **Product Owner**: Customer-facing, gathers requirements, creates user stories
- **Architect**: Designs systems and creates technical specifications
- **Developer**: Implements features and writes code
- **Tester**: Tests and validates implementations
- **IT**: Manages infrastructure and releases
- **Cost Analyst**: Estimates token costs, warns before expensive operations

**Your team collaborates automatically. You simply open your AI tool (Claude, Cursor, vscode-Copilot, etc.) and provide your task prompt.**


## Quick Installation 
Go to [One-Command Setup Recommended)](#one-command-setup-recommended)


#### [Attribution (optional but appreciated)]:
If you use this project, please consider linking back to:
https://github.com/meenusinha/SoftwareTeam

---

# Why not just use Claude, ChatGPT, Cursor, or Copilot?

Those tools are powerful—but they are unstructured:
 - You rely on prompts for each step
 - You manually guide the entire process
 - There is no built-in collaboration between roles
 - Outputs vary depending on how you prompt

SoftwareTeam gives you a system, not just AI
 - A repeatable development workflow
 - Specialized AI roles (Product Owner, Architect, Developer, Tester)
 - Structured outputs at each stage
 - Collaborative AI agents working together
 - Consistent results across projects

## The key idea

It’s just markdown files.

But those files define:

- how your AI works
- how it collaborates
- how it builds software

## The difference

- With Cursor/Claude/etc: You are the system.

- With SoftwareTeam: The system runs for you.

## The result
- No complex setup
- No new platform to learn
- Works with your existing AI tools

**You don’t just talk to AI.**
**You run a structured AI-powered software team.**

“This is what you would build if AI tools already worked together like a real software team.”

# Why SoftwareTeam?

Modern AI tools can generate code—but they often lack structure, documentation, long term vision, and control.

SoftwareTeam changes that by introducing a collaborative agent workflow only using prompts and markdown files:

- Multiple AI agents work together like a real software team
- Each agent produces work that is documentated, reviewed and approved before moving forward
- You stay in control by final review/approval while agents handle execution
- The system enables action-driven progress, with agents asking the necessary “what”, “how”, and “why” questions along the way when necessary
- It maintains consistency across runs
- Frees you for other important tasks while the agentic system manages coordination


## Features

- **LLM Provider Agnostic** - Works with any AI
- **Multi-agent workflow** with peer review
- **Git worktree support** for versioned work
- **Task management system**
- **GitHub Actions** for automation
- **Secure API key handling** (environment variables, gitignored)

---


# Built for Simplicity and Extensibility

## SoftwareTeam is intentionally lightweight:
- No heavy frameworks required
- No hidden abstractions
- Built on:
   > Markdown-based workflows
   > Git-based collaboration scripts

**This makes it:**
- Easy to understand
- Easy to customize
- Easy to extend with advanced systems like:
   - RAG
   - MCP
- Custom AI pipelines

---


## Documentation as a First-Class Output

### Agents contributes to:
- system design
- requirements
- implementation
- testing
- operations

**Result: a fully documented, modular system generated as part of the workflow.**

**This gives you:**
- Clear architecture visibility
- Reusable knowledge
- Maintainibility of the software over time and across teams
- High-quality documentation without extra effort

---


## Example Workflow

**"Build a task management app"**
- Product Owner creates user stories
- Architect designs system
- Developer implements features
- Tester validates the work
- IT handles infrastructure and release

All coordinated through agent collaboration and mandatory approval-before-handover steps.

---


## Platform supported
Works on **Mac, Windows, and Linux**, and supports multiple [AI providers](#works-with-any-ai).

---


## Prerequisites

The setup wizard can install everything automatically, but you can install these manually first — it's the most reliable way to avoid permission issues.

<details>
<summary><strong>Python 3.6+</strong> &nbsp;(required to run the wizard)</summary>

**macOS**
```bash
brew install python3
```
`brew install python3` always installs the latest Python 3 (currently 3.12), so it's always 3.6+.
Or download from [python.org](https://www.python.org/downloads/) and run the installer.

**Ubuntu / Linux / WSL**
```bash
sudo apt-get update && sudo apt-get install -y python3
```

**Windows** (run in PowerShell)
```powershell
winget install Python.Python.3.12
```
Or download from [python.org](https://www.python.org/downloads/) — tick ✅ **"Add Python to PATH"** during install.
</details>

<details>
<summary><strong>Git</strong> &nbsp;(required for version control)</summary>

**macOS**
```bash
brew install git
# or: xcode-select --install
```

**Ubuntu / Linux / WSL**
```bash
sudo apt-get update && sudo apt-get install -y git
```

**Windows** (run in PowerShell)
```powershell
winget install Git.Git
```
Or download from [git-scm.com](https://git-scm.com).
</details>

<details>
<summary><strong>GitHub CLI (gh)</strong> &nbsp;(required for GitHub workflow; optional for local-only)</summary>

**macOS**
```bash
brew install gh
```

**Ubuntu / Linux / WSL**
```bash
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update && sudo apt-get install -y gh
```

**Windows** (run in PowerShell)
```powershell
winget install GitHub.cli
```
</details>

> **Already installed them?** Skip straight to the [One-Command Setup](#one-command-setup-recommended) below — the wizard will detect them automatically.

---

## One-Command Setup (Recommended)

Open your terminal / command line, paste ONE command, and press Enter.
This will launch a browser-based setup wizard that installs and configures everything.

**Mac / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.ps1 | iex
```

**New here? See [QUICK-START.md](QUICK-START.md)** for a simple 5-step guide.

---


## What is this? 
**A structured approach to software development using specialized AI agents — designed to work with your preferred tools and workflows.**

## Who is this for?
- **Non-programmers** who want AI help building software
- **Deveopers** wanting structured AI-assisted workflows
- **Projects** needing consistent development processes

## How You Can Use It?
**SoftwareTeam** supports different ways of working:

**1. With GitHub** (recommended for developers)
- Agents automatically create a task branch and their own feature branches
- Each agent opens a PR when their work is done
- **Multi-agent PR review launches automatically** — other agents review the PR, flag issues, and the author agent reworks until approved
- You merge with a click or by commenting `/merge` — keeping you in control
- Ideal for teams and structured projects

**2. Without GitHub** (local-only)
- Agents do all the same work but skip branches and PRs
- Everything stays on your machine
- **Great for beginners and quick experiments**

**3. Optional: Use as a Template**
- Start with the predefined AI workflow.
- **Modify agent** roles, workflows, or directories via markdown.
- Ideal for creating **custom AI-assisted software development pipelines**.

---


## Works With Any AI
<details>
<summary>Click to open AI tools options</summary>

| Provider | Models | Recommended Tools |
|----------|--------|-------------------|
| **Anthropic** | Claude 3.5, Opus 4 | Claude Code (recommended) |
| **Google** | Gemini 1.5 Pro, Flash | Aider, Cursor, Windsurf |
| **OpenAI** | GPT-4o, GPT-4 Turbo | Aider, Cursor, Windsurf |
| **Azure** | GPT-4, GPT-3.5 | Aider, Cursor, Windsurf |
| **GitHub** | Copilot | GitHub Copilot (VS Code) |
| **Ollama** | Local models | Aider, Continue |
---
</details>

## Quick Start (For Developers)
<details>
<summary>Click to open quickstart guide</summary>

git clone <repo-url> mySoftwareTeam
```bash
# 1. Clone this template
git clone https://github.com/meenusinha/SoftwareTeam.git mySoftwareTeam
cd mySoftwareTeam

# 2. Set up your AI provider
# Linux/macOS:
export LLM_API_KEY="your-api-key"  # provider api key e.g., anthropic, gemini etc
# Windows (PowerShell): $env:LLM_API_KEY = "your-api-key"
# Windows (CMD): set LLM_API_KEY=your-api-key

# 3. Start your AI tool and describe what you want to build
claude           # For Claude Code (recommended)
aider            # For Aider (Gemini/OpenAI)
cursor .         # For Cursor IDE
# Or: Windsurf, Continue (VS Code), GitHub Copilot
```

## Alternative Setup Methods
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
git clone -b main https://github.com/REPO-OWNER/REPO-NAME.git my-project
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

---


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
└── .github/workflows/       # GitHub Actions
```

## How It Works

1. You describe what you want to build
2. Product Owner clarifies requirements, creates user story
3. Cost Analyst estimates resource usage (warns if expensive)
4. Architect enriches with technical specifications
5. IT agent takes care of necessary infrastructure and tools' installations
6. Product Owner assigns tasks to agents
7. Agents work independently in git worktrees
8. Peer review ensures quality
9. PRs, reviewed by agents, are presented for your final merge action

## Setup by Provider
<details>
<summary>Click to expand AI tool setup options</summary>

### Anthropic Claude (Recommended)
```bash
# Linux/macOS:
export LLM_API_KEY="sk-ant-..."
# Windows (PowerShell): $env:LLM_API_KEY = "sk-ant-..."

npm install -g @anthropic-ai/claude-code
claude
```

### Google Gemini
```bash
# Linux/macOS:
export LLM_API_KEY="your-key-here"
# Windows (PowerShell): $env:LLM_API_KEY = "your-key-here"

pip install aider-chat
aider --model gemini/gemini-1.5-pro-latest
```

### OpenAI (GPT-4)
```bash
# Linux/macOS:
export LLM_API_KEY="your-key-here"
# Windows (PowerShell): $env:LLM_API_KEY = "sk-..."

pip install aider-chat
aider
```

See `ai-assistants/provider-setup/README.md` for detailed setup instructions.
</details>

## Optional Customization 

1. **Configure your AI provider** - Set your `LLM_API_KEY` environment variable (see `ai-assistants/provider-setup/README.md`)
2. **Add domain expertise** - Update agent files in `ai-assistants/agents/`
3. **Customize structure** - Modify directories for your project
4. **Configure builds** - Add your build system
5. **Update workflows** - Modify `.github/workflows/`

## Security

- API keys stored as **environment variables**
- Secrets are **automatically gitignored**
- No keys in code or config files

## License

[MIT License](LICENSE)
