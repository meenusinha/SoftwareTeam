# Quick Start Guide

Welcome! This guide will help you set up the AI-assisted workflow.

**No programming experience required.**

---

## Prerequisites - IMPORTANT!

Before choosing an AI tool path, you **MUST** set up these prerequisites.

> **Tip:** The setup wizard (see [one-command setup](#fastest-way-gui-setup-wizard-recommended) below) can install git and gh automatically. If you run into permission issues, install them manually using the commands below first — it's faster and more reliable.

### 0. Python 3.6+ (required to run the wizard)

The setup wizard itself needs Python 3.6+. If it's already installed, skip this.

**Mac:**
```bash
brew install python3
```
`brew install python3` always installs the latest Python 3 (currently 3.12), so it's always 3.6+.
Or download from https://python.org

**(Debian-based distributions) Ubuntu:**
```bash
sudo apt-get update && sudo apt-get install -y python3
```

**(RPM-based distributions) Red Hat / CentOS / Fedora:**
```bash
sudo dnf install -y python3

or, for older systems: sudo yum install -y python3
```

**Arch Linux / Manjaro:**
```bash
sudo pacman -Syu python
```

**Windows (PowerShell):**
```powershell
winget install Python.Python.3.12
```
Or download from https://python.org — tick ✅ **"Add Python to PATH"** during install.

---

### 1. Git Installation

**Mac:**
```bash
brew install git
# or: xcode-select --install
```

**Ubuntu / Linux / WSL:**
```bash
sudo apt-get update && sudo apt-get install -y git
```

**Windows (PowerShell):**
```powershell
winget install Git.Git
```
Or download from https://git-scm.com

**Linux (Fedora):**
```bash
sudo dnf install -y git
```

> **Note:** The setup wizard will also verify and install `git` automatically.

### 2. GitHub Account
- Go to https://github.com and sign up (or sign in)
- You'll need this for automatic PR creation

### 3. GitHub Token (REQUIRED for PR creation)

The AI agents will automatically create Pull Requests, which requires GitHub authentication:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "AI Agents")
4. Select these scopes:
   - ✅ `repo` - Full control of private repositories
   - ✅ `workflow` - Update GitHub Actions workflows
   - ✅ `admin:repo_hook` - Access to hooks
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

### 4. Save GitHub Token to Environment

**On Mac/Linux:**
```bash
echo 'export GITHUB_TOKEN="your_github_token_here"' >> ~/.bashrc
source ~/.bashrc
```

**On Windows (PowerShell as Administrator):**
```powershell
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "your_github_token_here", "User")
$env:GITHUB_TOKEN = "your_github_token_here"
```

### 5. Install `gh` CLI (for automatic PR creation)

**Mac:**
```bash
brew install gh
```

**Windows (PowerShell):**
```powershell
winget install GitHub.cli --accept-package-agreements --accept-source-agreements
```

**Ubuntu / Linux / WSL** — `gh` is not in the default apt repos; add the GitHub CLI repo first:
```bash
sudo mkdir -p -m 755 /etc/apt/keyrings
wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
  | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update && sudo apt-get install -y gh
```

**Linux (Fedora):**
```bash
sudo dnf install -y gh
```

**Verify installation (all platforms):**
```bash
gh auth login   # First time: authenticate
gh auth status  # Verify authentication
```

> **Note:** The setup wizard will also verify and install `gh` automatically.

---

## Fastest Way: GUI Setup Wizard (Recommended)

**Just paste ONE command** in your terminal — a browser-based wizard will guide you through everything:

**Mac / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/meenusinha/SoftwareTeam/main/setup/setup.ps1 | iex
```

The wizard will open in your browser and walk you through:
- Choosing workflow mode (GitHub or Local)
- Installing prerequisites (Git, GitHub CLI)
- GitHub authentication
- Project location & forking
- LLM provider configuration
- AI tool selection & launch

**That's it!** You can skip the rest of this guide if you use the wizard.

---

## Manual Setup (Alternative)

If you prefer to set things up manually, or the wizard doesn't work for your environment, follow the steps below.

> **New here?** First, [fork this template](README.md#fork-this-template) to create your own copy, then follow the steps below.

---

## LLM Provider (Only for Automated Reviews)

**LLM Provider is ONLY needed if you want automated peer reviews (GitHub Actions).**

- **For IDE work ONLY** (using Copilot, Claude Code, Cursor, etc.): No LLM_PROVIDER needed — your AI tool authenticates separately. Skip to [Choose Your Path](#choose-your-path).
- **For automated peer reviews**: See [Automated Peer Review Setup](#automated-peer-review-setup) for full instructions.

---

## ✅ Setup Checklist

Before proceeding to "Choose Your Path", verify:

- [ ] Git is installed (`git --version`)
- [ ] GitHub account created and logged in
- [ ] GITHUB_TOKEN environment variable set
- [ ] gh CLI installed and authenticated (`gh auth status`)
- [ ] **(Optional)** LLM_PROVIDER and LLM_API_KEY set - only if you want [automated peer reviews](#automated-peer-review-setup)

**If all checkboxes pass**, you're ready to proceed! 🚀

---

## Choose Your Path

Pick ONE path based on which AI tool you want to use:

| Path | AI Tool | Best For | Difficulty | Setup Guide |
|------|---------|----------|------------|-------------|
| **Path A** | Claude Code + Anthropic | Software projects | Easy (CLI) | [Setup Guide](quickstart/tools/claude-code-setup.md) |
| **Path B** | Cursor IDE | Beginners, visual | Easiest (GUI) | [Setup Guide](quickstart/tools/cursor-setup.md) |
| **Path C** | Windsurf IDE | Beginners, visual | Easiest (GUI) | [Setup Guide](quickstart/tools/windsurf-setup.md) |
| **Path D** | Aider + Gemini | Budget-conscious | Easy (CLI) | [Setup Guide](quickstart/tools/aider-gemini-setup.md) |
| **Path E** | Aider + OpenAI | GPT-4 users | Easy (CLI) | [Setup Guide](quickstart/tools/aider-openai-setup.md) |
| **Path F** | Continue + VS Code | VS Code users | Easy (Extension) | [Setup Guide](quickstart/tools/continue-setup.md) |
| **Path G** | GitHub Copilot | Copilot subscribers | Easiest (GUI) | [Setup Guide](quickstart/tools/github-copilot-setup.md) |

**Recommended**: 
- **Path A** (Claude Code) for best software development experience
- **Path G** (GitHub Copilot) if you already have a subscription

**⚠️ Important for GitHub Copilot users**: While Copilot works in your IDE without LLM_PROVIDER setup, you still need to configure an LLM provider for automated peer reviews. See [Path G guide](quickstart/tools/github-copilot-setup.md) for details.

**Click on your chosen setup guide above** for detailed installation and configuration instructions.

---

## After Setup: How the Agentic Workflow Works

Once you're set up, the AI follows a structured workflow:

```
You describe what you want
         ↓
      IT Agent
   (Verifies git and gh CLI are set up)
         ↓
   Product Owner
   (Understands your request, creates plan)
         ↓
   Cost Analyst
   (Estimates cost, warns if expensive)
         ↓
      Architect
   (Designs the solution)
         ↓
      IT Agent
   (Installs project dependencies)
         ↓
      Developer
   (Writes the code)
         ↓
       Tester
   (Validates it works)
         ↓
      IT Agent
   (Builds release artifacts)
         ↓
   Product Owner
   (Reviews and presents to you)
```

**Important**: The AI will automatically:
1. Start as **IT Agent** to verify tools are installed
2. Then **Product Owner** to understand your request
3. **Cost Analyst** estimates cost before proceeding
4. Follow the complete workflow for quality results
5. **Automatically create Pull Requests** using your GitHub token

### Branching Strategy

For each task, the AI uses this branch structure:

- **Base branch**: `main` (template for all tasks)
- **Task branch**: `master_{task_name}` (e.g., `master_login-feature`)
  - Created once per task
  - All agents work from this branch
  - All PRs merge into this branch
- **Agent branches**: `{llm-name}/{agent}-{task_name}-{sessionID}`
  - Created per agent (Developer, Architect, Tester, etc.)
  - Agent works on their task
  - Creates PR to `master_{task_name}`

**Example**: For "Create a login page" task:
```
main
  └─→ master_login-page (Product Owner creates this)
        ├─→ {llm-name}/architect-login-page-abc123 (Architect's work)
        ├─→ {llm-name}/developer-login-page-abc123 (Developer's work)
        └─→ {llm-name}/tester-login-page-abc123 (Tester's work)
```

See the Git Workflow section in your AI tool's workflow guide (CLAUDE.md, .cursorrules, etc.) for details.

---

## Example Requests

Just describe what you want in plain English!

**Building something new:**
> "I want to create a simple todo list application where users can add, complete, and delete tasks"

**Adding a feature:**
> "Add a search feature so users can find items by name"

**Fixing a problem:**
> "Users are reporting that the save button doesn't work on mobile devices"

**Understanding the code:**
> "Explain how the login system works"

---

## Quick Reference

| What you want | What to say |
|---------------|-------------|
| Build new feature | "Create a [feature] that does [what]" |
| Fix a bug | "Fix the issue where [problem]" |
| Understand code | "Explain how [feature] works" |
| Improve something | "Make [feature] faster/better/simpler" |
| Add tests | "Add tests for [feature]" |

---

## Project Structure

```
your-project/
├── CLAUDE.md             ← AI workflow instructions (Claude Code)
├── .cursorrules          ← AI workflow instructions (Cursor)
├── .windsurfrules        ← AI workflow instructions (Windsurf)
├── .continuerules        ← AI workflow instructions (Continue)
├── .aider.conf.yml       ← AI workflow instructions (Aider)
│
├── ai-assistants/        ← AI configuration
├── project-management/   ← Documentation and tasks
│   └── tasks/backlog/    ← User stories go here
├── modules/              ← Your software code
├── scripts/              ← Build, test, run scripts
├── output/               ← Built software
```

---

## Troubleshooting

### "API key not found" error
- Make sure you saved the key correctly
- Close and reopen your terminal
- Check for extra spaces in the key

### "GITHUB_TOKEN not set" error
- GitHub token is required for automatic PR creation
- Set it: `export GITHUB_TOKEN="your_token_here"`
- Verify: `echo $GITHUB_TOKEN`
- See [Prerequisites](#prerequisites---important) section

### "`gh` command not found" error
- `gh` CLI is required for automatic PR creation
- Install it from [Prerequisites](#prerequisites---important) section
- Verify: `gh --version`
- Authenticate: `gh auth login`

### "gh: authentication failed" error
- Run: `gh auth login`
- Select "GitHub.com"
- Select "HTTPS" protocol
- Select "Paste an authentication token"
- Paste your GitHub token (from Prerequisites)

### "Command not found" error
- Make sure you installed the tool
- Close and reopen your terminal
- On Windows, run as Administrator

### AI doesn't follow the workflow
- The AI config files (CLAUDE.md, .cursorrules, etc.) instruct the AI
- If issues persist, tell the AI: "Please follow the workflow guide" (this is the provider file: CLAUDE.md, .cursorrules, etc.)

### AI gives wrong answers
- Be more specific in your request
- Provide examples of what you want
- Break big requests into smaller steps

### PR creation fails
- Verify `GITHUB_TOKEN` is set: `echo $GITHUB_TOKEN`
- Verify `gh` is installed: `gh --version`
- Verify authentication: `gh auth status`
- See Prerequisites section if any fail

### Need more help?
- See `ai-assistants/how-to-use.md` for detailed guide
- See your AI tool's workflow guide (CLAUDE.md, .cursorrules, etc.) for full workflow documentation

---

## Cost Awareness

Using AI APIs costs money per request.

**Approximate costs:**
- Simple question: ~$0.01
- Small feature: ~$0.10
- Large feature: ~$1.00+

The **Cost Analyst** agent will warn you before expensive operations.

---

## Automated Peer Review Setup

This workflow automatically reviews your PRs using AI agents.

### Step 1: Choose Your LLM Provider

The automated review supports 7 LLM providers:

| Provider | Best For | Cost | Setup Guide |
|----------|----------|------|-------------|
| **GitHub Copilot** | Copilot subscribers | FREE* | [Copilot Setup](quickstart/tools/github-copilot-setup.md) |
| **OpenAI** | Most popular, GPT-4o | $$ | [OpenAI Setup](quickstart/providers/openai-setup.md) |
| **Anthropic** | Best code reviews, Claude | $$$ | [Anthropic Setup](quickstart/providers/anthropic-setup.md) |
| **Gemini** | Google's model, cost-effective | $ | [Gemini Setup](quickstart/providers/gemini-setup.md) |
| **Azure OpenAI** | Enterprise, compliance | $$$ | [Azure Setup](quickstart/providers/azure-setup.md) |
| **Cohere** | Fast responses, efficiency | $ | [Cohere Setup](quickstart/providers/cohere-setup.md) |
| **Mistral** | Open-source, privacy | $ | [Mistral Setup](quickstart/providers/mistral-setup.md) |

*GitHub Copilot uses repository authentication automatically. Copilot Pro/Individual provides IDE access only — for automated reviews you need Copilot Enterprise or a separate provider.

> Follow your chosen provider's setup guide above for API key acquisition, environment variable configuration, and verification steps.

### Step 2: Configure GitHub Repository Secrets

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **Repository secrets** tab → Click **"New repository secret"**

**For GitHub Copilot (Recommended):**
[For automated reviews you need Copilot Enterprise.]


```
Name: LLM_PROVIDER
Secret: copilot
```
That's it! No API key needed - uses repository authentication automatically.

**For OpenAI:**
```
Name: LLM_PROVIDER
Secret: openai

Name: LLM_API_KEY
Secret: your-openai-api-key
```

**For Anthropic (Claude):**
```
Name: LLM_PROVIDER
Secret: anthropic

Name: LLM_API_KEY
Secret: your-anthropic-api-key
```

**For Gemini:**
```
Name: LLM_PROVIDER
Secret: gemini

Name: LLM_API_KEY
Secret: your-google-api-key
```

**For Azure OpenAI:**
```
Name: LLM_PROVIDER
Secret: azure

Name: LLM_API_KEY
Secret: your-azure-api-key

Name: AZURE_OPENAI_ENDPOINT
Secret: https://your-resource.openai.azure.com/
```

**For Cohere:**
```
Name: LLM_PROVIDER
Secret: cohere

Name: LLM_API_KEY
Secret: your-cohere-api-key
```

**For Mistral:**
```
Name: LLM_PROVIDER
Secret: mistral

Name: LLM_API_KEY
Secret: your-mistral-api-key
```

### Step 3: Automated Review Runs Automatically

1. Create a PR following the branch naming pattern:
   - `{llm-name}/{agent-type}-{project}-{sessionID}`
   - Example: `copilot/developer-sudoku-webapp-123456`

2. The review workflow triggers automatically when the PR targets a `master_*` branch.

3. Go to the **Actions** tab to monitor progress.

4. Reviews are posted as PR comments with inline suggestions.

> **Manual trigger**: You can also go to **Actions** → **Automated Multi-Agent Peer Review** → **Run workflow** and enter a PR number to trigger a review manually on any PR.

### Switching Providers

Just update the `LLM_PROVIDER` secret in GitHub - no code changes needed!

```bash
# Example: Switch from OpenAI to Claude
# In GitHub: Settings → Secrets → Actions
# Edit LLM_PROVIDER: change "openai" to "anthropic"
# Edit LLM_API_KEY: change to your provider (e.g., Anthropic) key
```

---

