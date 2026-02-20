# AI-Assisted Agentic Workflow Template

---

## MANDATORY INSTRUCTIONS FOR AI ASSISTANTS

**CRITICAL**: If you are an AI assistant (Claude, GPT, Gemini, Copilot, Cursor, Windsurf, Continue, Aider, Cody, etc.), you MUST follow these instructions for EVERY user request:

### 0. ⚠️ OPTIONAL: LLM Provider Configuration (Only for Automated Reviews)

**LLM Provider is ONLY needed for automated peer reviews (GitHub Actions).**

**For IDE work ONLY** (Copilot, Claude Code, Cursor, Windsurf, Continue, Aider, Cody, etc.):
- ✅ **No LLM_PROVIDER needed** - Your AI tool authenticates separately
- ✅ **No LLM_API_KEY needed** - IDE handles authentication  
- ✅ **Start working immediately** - Skip provider setup

**For automated peer reviews**:

```bash
# Check if LLM_PROVIDER is set (ONLY needed for automated reviews)
if [ -z "$LLM_PROVIDER" ]; then
    echo "ℹ️  LLM_PROVIDER not set"
    echo "   • IDE work: ✅ Works fine (your AI tool authenticates separately)"
    echo "   • Automated reviews: ❌ Won't work"
    echo "   • To enable reviews: See quickstart/providers/ for setup"
else
    echo "✅ LLM Provider: $LLM_PROVIDER (automated reviews enabled)"
fi

# Check if LLM_API_KEY is set (only needed for automated reviews with non-Copilot providers)
if [ -n "$LLM_PROVIDER" ] && [ "$LLM_PROVIDER" != "copilot" ] && [ -z "$LLM_API_KEY" ]; then
    echo "⚠️  WARNING: LLM_API_KEY is not set!"
    echo "This is required for automated peer reviews with $LLM_PROVIDER"
    echo "See: quickstart/providers/${LLM_PROVIDER}-setup.md"
elif [ "$LLM_PROVIDER" = "copilot" ]; then
    echo "✅ Using GitHub Copilot provider (no API key needed)"
elif [ -n "$LLM_PROVIDER" ] && [ -n "$LLM_API_KEY" ]; then
    echo "✅ LLM_API_KEY: Configured for automated reviews"
fi

# For Azure, also check endpoint
if [ "$LLM_PROVIDER" = "azure" ] && [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "❌ ERROR: AZURE_OPENAI_ENDPOINT is not set!"
    echo "Azure OpenAI requires both LLM_API_KEY and AZURE_OPENAI_ENDPOINT"
    exit 1
fi
```

**If you want to use automated peer reviews:**
1. **LLM_PROVIDER is REQUIRED** - Set to: openai, anthropic, gemini, azure, cohere, mistral, or copilot
2. **LLM_API_KEY is REQUIRED** - Except for `LLM_PROVIDER=copilot` (uses GitHub authentication)
3. **See**: [QUICK-START.md](QUICK-START.md#mandatory-choose-your-llm-provider) for setup

**If you're only using IDE tools (Copilot, Claude Code, Cursor, Windsurf, Continue, Aider, Cody, etc.):**
1. **LLM_PROVIDER is NOT needed** - Your AI tool authenticates separately
2. **LLM_API_KEY is NOT needed** - IDE handles authentication
3. **You can skip** the provider setup and start working immediately

**Environment Variables (Only for Automated Reviews):**
- `LLM_PROVIDER` - One of: openai, anthropic, gemini, azure, cohere, mistral, copilot
- `LLM_API_KEY` - Required except for copilot (uses GitHub authentication)
- `AZURE_OPENAI_ENDPOINT` - Only required if LLM_PROVIDER=azure

**Summary**: IDE work doesn't need LLM_PROVIDER. Only automated peer reviews need it.

### 1. Reading Order (NO CIRCULAR REFERENCES)

**This file (AI-WORKFLOW.md) is the single entry point.** Read agent files only when this workflow tells you to. Agent files contain role-specific content only — they do NOT redirect you back here.

```
Reading flow (one-way, no loops):

Tool entry file (CLAUDE.md, .cursorrules, etc.)
    → AI-WORKFLOW.md (you are here — workflow, protocols, common rules)
        → ai-assistants/agents/it-agent.md      (when adopting IT Agent role)
        → ai-assistants/agents/product-owner-agent.md (when adopting PO role)
        → ai-assistants/agents/cost-analyst-agent.md  (when adopting Cost Analyst role)
        → ai-assistants/agents/architect-agent.md     (when adopting Architect role)
        → ai-assistants/agents/developer-agent.md     (when adopting Developer role)
        → ai-assistants/agents/tester-agent.md        (when adopting Tester role)
```

**Rules:**
- Read each agent file **only when you adopt that role** in the workflow below
- Agent files do NOT send you back to this file — you've already read it
- All workflow, handover, and common protocols are HERE (not in agent files)

### 1b. IT Agent Runs FIRST
- Read `ai-assistants/agents/it-agent.md` for role-specific instructions
- Verify & install `git` and `gh` CLI, authenticate `gh`
- This ensures all agents can branch, commit, and create PRs

### 1c. Then Start as Product Owner
- Read `ai-assistants/agents/product-owner-agent.md` for role-specific instructions
- Adopt Product Owner role for requirements gathering
- Never skip straight to coding

### 2. First Task? Customize the Template
**⚠️ MANDATORY FOR NEW PROJECTS**

When this is the FIRST task in a NEW project, Product Owner MUST:
1. **Read** `ai-assistants/agents/product-owner-agent.md` for detailed steps
2. **Update domain expertise** in ALL agent files (`ai-assistants/agents/*.md`)
3. **Commit changes** before creating user story
4. This ensures all agents have project-specific context for reviews and work

**Do NOT skip this step** - agents won't provide relevant guidance without domain expertise.

### 3. Follow the Agent Workflow
```
User Request → IT Agent (verify git & gh CLI)
    → Product Owner (requirements) → Cost Analyst (estimate cost)
    → Architect (design) → IT Agent (setup) → Developer (implement)
    → Tester (validate) → IT Agent (release) → Product Owner (accept)
```
**Cost Analyst** is advisory — consulted after Product Owner and before any expensive operation.

### 4. Never Skip Steps
Even for "simple" tasks, follow the workflow. This ensures quality and documentation.

---

## Overview

This is a **provider-agnostic template** for setting up a multi-agent AI workflow. It works with any LLM (Large Language Model) provider and AI coding assistant.

**Supported AI Providers:**
- Anthropic (Claude)
- OpenAI (GPT-4, GPT-4o)
- Azure OpenAI
- Google (Gemini)
- Ollama (Local models)
- Any OpenAI-compatible API

**Compatible AI Coding Tools:**
- Claude Code, GitHub Copilot, Cursor, Windsurf, Continue, Aider, Cody, and more

**This template is designed for non-programmers** who want to leverage AI-assisted development workflows.

## Quick Start

1. **Fork or clone this repository**
2. **Configure your LLM provider** (see `ai-assistants/provider-setup/README.md`)
3. **Set your API key** as an environment variable
4. **Start your AI assistant** and describe what you want to build

---

## LLM Provider Setup

See `ai-assistants/provider-setup/README.md` for detailed setup instructions.

### Quick Configuration

```bash
# 1. Copy the config template
cp ai-assistants/provider-setup/config.template.json ai-assistants/provider-setup/config.json

# 2. Set your API key
# Linux/macOS (add to ~/.bashrc or ~/.zshrc):
export LLM_API_KEY="your-api-key"

# Windows (PowerShell — add to $PROFILE for persistence):
# $env:LLM_API_KEY = "your-api-key"

# Windows (CMD):
# set LLM_API_KEY=your-api-key

# 3. Start your AI tool
# For Claude Code:
claude

# For Aider (works with multiple providers):
aider --model gpt-4o  # or --model claude-3-opus
```

---

## Domain: [Your Project Domain]

**CUSTOMIZE THIS SECTION** for your specific project.

Replace this section with your project's domain context. Examples:

### Example: E-commerce Platform
```
**Industry**: Retail Technology
- Online shopping systems
- Payment processing and checkout flows
- Inventory management and fulfillment
- Customer experience and personalization
```

### Example: Healthcare Application
```
**Industry**: Healthcare IT
- Patient data management
- HIPAA compliance requirements
- Clinical workflow integration
- Electronic health records (EHR)
```

### Example: Financial Services
```
**Industry**: FinTech
- Transaction processing
- Regulatory compliance (SOX, PCI-DSS)
- Real-time data processing
- Risk management and fraud detection
```

**Agent Domain Expertise**:
All agents should understand your project's domain to make informed decisions. Update the agent files in `ai-assistants/agents/` to include relevant domain expertise.

---

## Project Structure

```
YourProject/
├── ai-assistants/               # AI configuration
│   ├── agents/                  # Agent role definitions
│   │   ├── product-owner-agent.md    # Requirements lead and backlog manager
│   │   ├── it-agent.md              # Infrastructure specialist
│   │   ├── architect-agent.md       # System designer
│   │   ├── developer-agent.md       # Implementation specialist
│   │   └── tester-agent.md          # QA specialist
│   ├── provider-setup/          # LLM provider configuration
│   │   ├── config.template.json     # Config template
│   │   ├── config.json              # Your config (gitignored)
│   │   └── README.md                # Setup instructions
│   └── how-to-use.md            # Getting started guide
│
├── project-management/          # Project documentation
│   ├── tasks/                   # Task management system
│   ├── designs/                 # Architecture docs (EPS, EDS)
│   ├── requirements/            # Feature requirements
│   ├── quality/                 # Test plans and QA docs
│   ├── operations/              # Infrastructure and releases
│   └── workflow/                # Team coordination docs
│
├── modules/                     # Software modules
│   ├── module-name/             # Each module is self-contained
│   │   ├── src/                 # Module source code
│   │   ├── test/                # Module tests
│   │   ├── release/             # Module release output
│   │   ├── debug/               # Module debug output
│   │   ├── build-config/        # Build configuration
│   │   └── Makefile             # Module build script
│   └── another-module/          # Add more modules as needed
│
├── output/                      # Combined build output
│   ├── release/                 # Combined release (all modules)
│   └── debug/                   # Combined debug (all modules)
│
├── scripts/                     # Build, test, run scripts
│   ├── build.sh                 # Build all modules
│   ├── test.sh                  # Run all tests
│   ├── run.sh                   # Run the application
│   └── clean.sh                 # Clean build artifacts
│
├── Makefile                     # Top-level build script
├── .github/                     # GitHub configuration
│   ├── workflows/               # GitHub Actions
│   └── scripts/                 # Automation scripts
│
├── AI-WORKFLOW.md               # This file
└── README.md                    # Project readme
```

---

## Agent System

This template uses a **multi-agent system** where the AI assistant adopts specialized roles based on the task. The agents work together through a structured workflow.

### Agent Roles

#### Product Owner Agent
**Role**: Customer-Facing Requirements Lead and Backlog Manager

- **Optional**: Verify LLM_PROVIDER and LLM_API_KEY are set if automated peer reviews are needed (see Step 0 above)
- **ALWAYS activates first** for new user requests
- Gathers and clarifies user requirements
- Creates high-level user stories (WHAT to build, not HOW)
- Coordinates work across all agents
- Accepts completed work

**Activates for**: Any new task from user, requirements, prioritization

**Note**: Product Owner focuses on WHAT to build. Technical details are filled in by Architect.

#### Architect Agent
**Role**: System Architect and Design Lead

- **Optional**: Verify LLM_PROVIDER and LLM_API_KEY are set if automated peer reviews are needed (see Step 0 above)
- Enriches user stories with technical specifications
- Designs interfaces and APIs
- Creates detailed development tasks
- Makes architectural decisions

**Activates for**: New features, specifications, design, architecture

**Note**: Architect creates *technical specifications*. Product Owner creates *high-level requirements*.

#### Developer Agent
**Role**: Software Developer and Implementation Specialist

- **Optional**: Verify LLM_PROVIDER and LLM_API_KEY are set if automated peer reviews are needed (see Step 0 above)
- Implements features and interfaces
- Writes clean, maintainable code
- Creates unit tests
- Follows specifications

**Activates for**: Implementation, coding, bug fixes, unit tests

#### Tester Agent
**Role**: Quality Assurance and Testing Specialist

- **Optional**: Verify LLM_PROVIDER and LLM_API_KEY are set if automated peer reviews are needed (see Step 0 above)
- Creates test plans
- Writes automated tests
- Validates implementations
- Reports bugs

**Activates for**: Testing, QA, validation, bug reporting

#### IT Agent
**Role**: Infrastructure and Operations Specialist

- **Optional**: Verify LLM_PROVIDER and LLM_API_KEY are set if automated peer reviews are needed (see Step 0 above)

- **Installs prerequisite tools** before project dependencies (see below)
- Maintains build infrastructure
- Manages releases and versioning
- Sets up CI/CD pipelines
- Documents infrastructure

**Activates for**: Build systems, releases, infrastructure, tools

**⚠️ IT Agent: Prerequisite Tool Verification (MANDATORY FIRST)**:

Before installing ANY project dependencies, IT Agent MUST verify and install the tools needed to perform those installations. This includes package managers, language runtimes, `git`, and `gh` CLI. See `ai-assistants/agents/it-agent.md` for full scripts.

**Summary of what IT Agent does automatically:**

1. **Detects OS** (Linux, macOS, Windows)
2. **Detects/installs package manager**:
   - Linux: `apt-get`, `dnf`, `yum`, `pacman`, `apk`, `zypper` (all major distros)
   - macOS: Installs Homebrew automatically if missing
   - Windows: Uses `winget` if available, otherwise auto-installs Chocolatey
3. **Installs `git`** (required for version control, branching, commits)
4. **Installs `gh` CLI** (required for PR creation and the handover protocol)
5. **Verifies `gh` authentication** (prompts user to run `gh auth login` if needed)
6. **Installs project-specific tools** from Architect's tech stack (Node.js, Python, Rust, etc.)

```bash
# Quick reference - IT Agent runs these steps automatically:

# Step 0: Detect OS and package manager
OS_TYPE="$(uname -s)"  # Linux, Darwin, MINGW/MSYS/CYGWIN

# Step 1: Detect package manager (apt-get/dnf/yum/pacman/apk/zypper/brew/winget/choco)
# Step 2: Install git and gh CLI using detected package manager
# Step 3: Verify gh authentication
# Step 4: Install project-specific tools from Architect's tech stack
# Step 5: Final verification of all tools

# See it-agent.md for complete cross-platform scripts
```

**The general principle**: If a tool is needed to install project dependencies (e.g., `npm` needs `node`, `pip` needs `python`, `cargo` needs `rust`), IT Agent MUST install that tool first. IT Agent also installs `git` and `gh` CLI which are required for the workflow's branching and PR creation. Never assume tools are pre-installed on the user's machine.

#### Cost Analyst Agent
**Role**: Resource Analyst and Cost Optimization Specialist (ADVISORY)

- **Runs after Product Owner** creates the user story — estimates total task cost
- Estimates token consumption before expensive operations
- Warns user before high-cost tasks (> $1.00 requires explicit approval)
- Logs usage for transparency
- Recommends cost optimization strategies
- **Does NOT create PRs or deliverables** — reports estimates back to Product Owner/user

**Activates for**: After every user story (mandatory), before expensive operations (any agent can request), cost estimation, usage reporting

### Agent Workflow

**⚠️ EVERY agent MUST verify LLM provider configuration before starting work (see Step 0 above).**

The agents work together in a collaborative workflow:

```
User Request
    ↓
Read ai-assistants/agents/it-agent.md → IT Agent (verify git, gh CLI)  ← FIRST
    ↓
[Optional: Verify LLM_PROVIDER & LLM_API_KEY — only for automated reviews]
    ↓
Read ai-assistants/agents/product-owner-agent.md → Product Owner (requirements)
    ↓
Read ai-assistants/agents/cost-analyst-agent.md → Cost Analyst (estimate cost)  ← ADVISORY
    ↓
Read ai-assistants/agents/architect-agent.md → Architect (design)
    ↓
Read ai-assistants/agents/it-agent.md → IT Agent (install deps, setup scripts/)
    ↓
Read ai-assistants/agents/developer-agent.md → Developer (implement in modules/)
    ↓
Read ai-assistants/agents/tester-agent.md → Tester (validate)
    ↓
Read ai-assistants/agents/it-agent.md → IT Agent (build release artifacts)
    ↓
Read ai-assistants/agents/product-owner-agent.md → Product Owner (accept & present)
```

**IMPORTANT**:
- **IT Agent runs FIRST**: Before any other agent, IT Agent verifies that `git` and `gh` CLI are installed and authenticated. Without these, no agent can branch, commit, or create PRs.
- **IT Agent activates THREE times**: First (git/gh setup), after Architect (project setup), and before Release (build)
- **Cost Analyst is ADVISORY**: Consulted after Product Owner creates the user story. Also consulted by any agent before expensive operations (> $1.00). Does NOT create PRs or deliverables — reports cost estimates back to Product Owner for go/no-go decision.
- **LLM Configuration Check**: Only needed for automated peer reviews, not for IDE work

### MANDATORY HANDOVER PROTOCOL (ALL AGENTS)

**CRITICAL: This is a BLOCKING GATE. Every agent MUST complete this before the next agent starts.**

When an agent finishes their work and is ready to hand over to the next agent:

1. **STOP** - Do not proceed to the next agent role yet
2. **Commit all work** to your branch: `git add -A && git commit -m "[Agent Name] Description"`
3. **Push to remote**: `git push -u origin {llm-name}/{agent}-{task_name}-{sessionID}`
4. **Provide handover context** — the outgoing agent MUST document:
   - What was completed
   - Key decisions made and why
   - Any open questions or known issues
   - What the next agent needs to know
   - **The ONE simple command to run/test the project** (if applicable — Developer, Tester, and Product Owner MUST provide this)
5. **Ask the user**:
   > "My work as [Agent Name] is complete. Before handing over to [Next Agent]:
   > - Would you like me to **create a PR** for review? (Recommended)
   > - Or should I **continue directly** to [Next Agent] without a PR?
   >
   > Creating a PR allows you to review my work before proceeding."
6. **Wait for user response** - Do NOT assume the answer
7. **If user wants PR**: Create PR using the [PR Creation Process](#pr-creation-process) below, then:
   - **Tell the user how to trigger the peer review workflow** (see [How to Trigger Peer Review](#how-to-trigger-peer-review-manual--step-by-step)):
     > "PR created! To run the automated peer review:
     > 1. Go to the **Actions** tab in your repo
     > 2. Click **'Automated Multi-Agent Peer Review'** in the sidebar
     > 3. Click **'Run workflow'**, enter PR number **#[NUMBER]**, and click the green button
     > 4. Reviews will appear as comments on the PR in 1-3 minutes"
   - WAIT for user approval before proceeding
8. **If user says continue**: Proceed to the next agent role, noting that work is committed on the branch

**When the NEXT agent starts, it MUST** (see [Task Analysis & Collaboration Protocol](#task-analysis--collaboration-protocol)):
- Read the handover context from the previous agent
- Ask clarifying questions about anything unclear (**What**, **Why**, **How**, **Scope**, **Dependencies**, **Success Criteria**)
- The previous agent (or user) MUST answer these questions before work begins
- Document understanding and assumptions before starting work

**NEVER silently skip this step.** The user MUST be consulted at every handover.

**Why this matters**: Without this gate, agents skip PR creation entirely, breaking the review workflow. This was the #1 observed failure mode during testing.

#### Run Command at Handover (MANDATORY for Developer, Tester, Product Owner)

**Developer, Tester, and Product Owner** MUST give the user a **one-line command** to run or test the project at their handover. The command must be **platform-appropriate** — detect the current OS and give the right command:

| Platform | Run the app | Run the tests |
|----------|------------|---------------|
| **Mac/Linux** | `bash scripts/run.sh` | `bash scripts/test.sh` |
| **Windows** | `scripts\run.ps1` | `scripts\test.ps1` |

If the project uses a standard tool, prefer the direct command (e.g., `npm start`, `python app.py`, `npm test`, `pytest`) since these work cross-platform.

**Rules:**
- **ONE command** — the user should copy-paste it and see results immediately
- **Platform-native** — do NOT assume WSL or Git Bash on Windows; use `.ps1` or cross-platform commands
- **IT Agent creates the scripts** — `scripts/run.sh` + `scripts/run.ps1` (and test equivalents) should be created during IT setup phase
- **Developer** provides the run command, **Tester** provides the test command, **Product Owner** provides both at acceptance

#### Handover Points in the Workflow

| Completing Agent | Next Agent | Handover Gate |
|-----------------|------------|---------------|
| IT Agent (git/gh) | Product Owner | No gate — continue immediately |
| Product Owner | Cost Analyst | No gate — Cost Analyst reviews the user story |
| Cost Analyst | Architect | Reports cost estimate to user. If approved, continue to Architect |
| Architect | IT Agent (setup) | Ask user: PR or continue? |
| IT Agent (setup) | Developer | Ask user: PR or continue? |
| Developer | Tester | Ask user: PR or continue? |
| Tester | IT Agent (release) | Ask user: PR or continue? |
| IT Agent (release) | Product Owner | Ask user: PR or continue? |

**Note**: Cost Analyst can also be consulted mid-workflow by any agent before expensive operations. Any agent can request a cost estimate; Cost Analyst reports back to the requesting agent and the user.

### Task-Based Branching Strategy

When user gives ANY new task, Product Owner MUST first create a task master branch:

```bash
# Step 1: Create task master branch from template
git checkout template/agentic-workflow
git checkout -b master_{task_name}
git push -u origin master_{task_name}
```

**Examples of task master branches**:
- `master_joke-website`
- `master_user-authentication`
- `master_shopping-cart`

### Branch Naming Convention

| Branch Type | Pattern | Example |
|-------------|---------|---------|
| Task Master | `master_{task_name}` | `master_joke-website` |
| Agent Branch | `{llm-name}/{agent}-{task_name}-{sessionID}` | `copilot/developer-joke-website-abc123` |

### Git Worktree Workflow

Agents work in separate git worktrees to enable parallel work:

```bash
# Product Owner creates task master branch first
git checkout template/agentic-workflow
git checkout -b master_{task_name}
git push -u origin master_{task_name}

# Then creates worktrees for agents (branching from task master)
git checkout master_{task_name}
git worktree add ../worktree-architect {llm-name}/architect-{task_name}-{sessionID}
git worktree add ../worktree-developer {llm-name}/developer-{task_name}-{sessionID}

# Each agent works independently in their worktree
# When done, create PR to master_{task_name} (the task's main branch)
```

### PR Creation Process

**⚠️ CRITICAL: When creating a PR (either because user requested it at handover, or at task completion), follow this exact process:**

```bash
# Step 1: Commit all changes
git add -A
git commit -m "[Agent Name] Description of completed work"

# Step 2: Push to remote
git push -u origin {llm-name}/{agent}-{task_name}-{sessionID}

# Step 3: Create PR to task master branch (NOT main/master)
gh pr create \
  --base master_{task_name} \
  --head {llm-name}/{agent}-{task_name}-{sessionID} \
  --title "[Agent Name] Work description" \
  --body "## Summary
[What was accomplished]

## Changes
- [Change 1]
- [Change 2]

## Ready for
[Next Agent Name]"

# Step 4: Verify PR was created
gh pr list --head $(git branch --show-current)
```

**If PR creation fails**:
1. First try `gh auth status` to check authentication. If not logged in, run `gh auth login` to authenticate.
2. If `gh` can't determine which repository to target, run `gh repo set-default OWNER/REPO` (use the fork owner's username and repo name).
3. If authentication is fine but PR still fails, check the error message and fix the issue (e.g., branch not pushed, remote not set).
4. **You MUST create the PR yourself. NEVER ask the user to create a PR manually.** Keep troubleshooting until it succeeds.

**PR Creation Troubleshooting Checklist** (run these if `gh pr create` fails):
```bash
# 1. Check authentication
gh auth status

# 2. Check/set repository context (CRITICAL — most common failure)
gh repo set-default    # shows current default
# If not set or wrong, set it:
gh repo set-default OWNER/REPO   # e.g., gh repo set-default myuser/BigProjPOC

# 3. Verify remote is correct
git remote -v
# origin should point to your fork (not the template repo)

# 4. Ensure branch is pushed
git push -u origin $(git branch --show-current)
```

**REQUIREMENT**: Either `GITHUB_TOKEN` environment variable or `gh auth login` must be configured. The `gh` CLI supports both methods — browser login via `gh auth login` is sufficient for PR creation.

### ⚠️ PR Checklist for ALL Agents

**When creating a PR, verify:**
- [ ] All files committed: `git add -A && git commit -m "[Agent] Description"`
- [ ] Branch pushed: `git push -u origin [branch-name]`
- [ ] PR created on GitHub: `gh pr create ...`
- [ ] PR has title: `[Agent Name] Description`
- [ ] PR body includes Summary, Changes, and Ready for field
- [ ] User informed of PR URL

### Peer Review Process (CRITICAL)

**All PRs must be peer-reviewed by other agents BEFORE user reviews.**

#### Review Assignment Rules

| PR Author | Required Reviewers |
|-----------|-------------------|
| **Developer** | Architect, Tester |
| **Architect** | Developer |
| **Tester** | Developer |
| **IT** | Architect |

#### Review Checklist

Each reviewer checks:
- [ ] Code follows project standards
- [ ] Design patterns correctly applied
- [ ] Tests are present and pass
- [ ] Documentation updated

#### Two-Phase Review

1. **Phase 1 - Peer Review**: Agents review each other (2+ approvals required)
2. **Phase 2 - User Review**: After peer approval, user reviews and merges

**NEVER skip peer review** - Quality before speed

#### How to Trigger Peer Review (Manual — Step by Step)

The peer review workflows are **manual trigger only** (`workflow_dispatch`) to save LLM API costs. They do NOT run automatically when a PR is created. After an agent creates a PR, **guide the user through these steps**:

1. Go to the **Actions** tab in your GitHub repository
2. In the left sidebar, click **"Automated Multi-Agent Peer Review"**
3. Click the **"Run workflow"** button (top right, blue button)
4. Enter the **PR number** (e.g., `5`) in the input field
5. Click the green **"Run workflow"** button to start
6. Wait for the workflow to complete (usually 1-3 minutes)
7. Check the PR's **Conversation** tab for review summary comments
8. Check the PR's **Files changed** tab for inline code comments

**Optionally**, you can also trigger the **"PR Review Assignment (Manual)"** workflow first to add labels and a review checklist comment before the automated review.

**Prerequisites** (one-time setup):
- `LLM_API_KEY` repository secret must be configured (Settings > Secrets and variables > Actions)
- `LLM_PROVIDER` secret should be set (defaults to `openai` if not set)
- GitHub Actions must have **Read and write permissions** (Settings > Actions > General > Workflow permissions)

**IMPORTANT for agents**: After creating a PR, you MUST inform the user about these manual steps. Do NOT tell the user that reviews will happen automatically — they must manually trigger the workflow from the Actions tab.

---

## Task Management

### Task Folders

- `project-management/tasks/backlog/` - User stories (Product Owner)
- `project-management/tasks/it/` - Infrastructure tasks
- `project-management/tasks/architect/` - Design tasks
- `project-management/tasks/developer/` - Implementation tasks
- `project-management/tasks/tester/` - Testing tasks

### Creating Tasks

1. Copy `TEMPLATE.md` to new file
2. Fill in objective, requirements, deliverables
3. Set status and priority
4. Tell your AI assistant to process the task

### Task Lifecycle

```
pending → in-progress → completed → archived
              ↓
           blocked
```

---

## Development Guidelines

### Code Organization
- Organize code into self-contained modules in `modules/`
- Each module contains:
  - `src/` - Module source code
  - `test/` - Module tests
  - `release/` - Release build output (gitignored)
  - `debug/` - Debug build output (gitignored)
  - `build-config/` - Build configuration files
  - `Makefile` - Module build script
- Copy `modules/example-module/` to create new modules

### Git Workflow
- **Base branch**: `template/agentic-workflow`
- **Task branch**: `master_{task_name}` (created per task, see [Task-Based Branching Strategy](#task-based-branching-strategy))
- **Agent branches**: `{llm-name}/{agent}-{task_name}-{sessionID}` (created per agent from task branch)
- Always test before committing

### Testing Strategy

**Test Levels**:
1. **Unit Tests** (Developer) - Individual functions/classes
2. **Component Tests** (Tester) - Components in isolation
3. **Integration Tests** (Tester) - Component interactions
4. **System Tests** (Tester) - End-to-end workflows

---

## GitHub Integration

### Authentication - REQUIRED

**AI agents will automatically create PRs. You must set up GitHub authentication first.**

Before running any workflow, set up your GitHub token:

```bash
# Linux/macOS:
export GITHUB_TOKEN="your_github_token"

# Windows (PowerShell):
# $env:GITHUB_TOKEN = "your_github_token"

# Windows (CMD):
# set GITHUB_TOKEN=your_github_token
```

**To create a GitHub token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`, `admin:repo_hook`
4. Copy the token and set it using the command for your OS above

### Automated PR Creation

Agents will automatically create PRs after completing their work. This requires:

- ✅ GitHub token set in `GITHUB_TOKEN` environment variable
- ✅ `gh` CLI installed and authenticated
- ✅ All commits pushed to remote branch

**If GitHub token is not set**: Agents will halt and request that you set it before continuing.

### Installing `gh` CLI (If Not Already Installed)

**Note:** IT Agent (Step 0) installs `gh` automatically. If you need to install manually:

```bash
# Linux (Debian/Ubuntu):
sudo apt-get update && sudo apt-get install -y gh

# Linux (Fedora):
sudo dnf install -y gh

# macOS:
brew install gh

# Windows (PowerShell):
# winget install GitHub.cli
# OR: choco install gh -y

# After installation, authenticate (all platforms):
gh auth login
```

**Verify setup (all platforms):**
```bash
gh auth status
```

---

## Customization Guide

### 1. Configure Your LLM Provider

Edit `ai-assistants/provider-setup/config.json` with your provider settings. See `ai-assistants/provider-setup/README.md` for details.

### 2. Update Domain Expertise

Edit each agent file in `ai-assistants/agents/` to include your project's domain knowledge.

### 3. Customize Project Structure

Modify the directory structure to match your project's needs:
- Add source directories for your modules
- Configure build systems for your technology stack
- Set up test directories appropriate for your frameworks

### 4. Configure Build System

Add build scripts appropriate for your technology:
- Makefiles for C/C++ projects
- package.json for Node.js
- requirements.txt for Python
- build.gradle for Java

### 5. Update GitHub Workflows

Modify `.github/workflows/` for your CI/CD needs.

---

## Using with Different AI Tools

### Claude Code (Example Tool)
```bash
npm install -g @anthropic-ai/claude-code

# Linux/macOS:
export ANTHROPIC_API_KEY="your-key"
# Windows (PowerShell): $env:ANTHROPIC_API_KEY = "your-key"

cd your-project
claude  # or use your preferred AI tool
```

### Aider
```bash
pip install aider-chat

# Linux/macOS:
export OPENAI_API_KEY="your-key"  # or ANTHROPIC_API_KEY
# Windows (PowerShell): $env:OPENAI_API_KEY = "your-key"

cd your-project
aider
```

### Cursor
1. Download from cursor.sh
2. Open your project
3. Use Cmd/Ctrl+K for AI assistance

### Windsurf
1. Download from codeium.com/windsurf
2. Open your project
3. Use AI chat panel — reads `.windsurfrules` automatically

### Continue (VS Code)
1. Install Continue extension
2. Configure your API key
3. Use the Continue panel — reads `.continuerules` automatically

### GitHub Copilot
1. Install GitHub Copilot extension in VS Code
2. Sign in with your GitHub account
3. Enable instruction files in `.vscode/settings.json` (already configured in this template)
4. Use Copilot Chat — reads `.github/copilot-instructions.md` automatically

---

## Notes for AI Assistants

- Automatically adopt appropriate agent role based on task
- Read agent file in `ai-assistants/agents/` **only when adopting that role** (not upfront)
- Follow peer review process before creating PRs
- Document decisions in appropriate project-management folders
- Keep this file updated when structure changes
- API keys are stored as environment variables, never in code

---

## Getting Started

1. **Configure your AI provider** (see `ai-assistants/provider-setup/README.md`)
2. **Describe your project** to the AI assistant
3. The AI will ask clarifying questions
4. Work begins with Product Owner analysis
5. Agents collaborate to complete the work
6. Review and merge PRs

**Example first request**:
"I want to build a web application for managing tasks. It should have user authentication, task creation, and notifications."

---

## Security Best Practices

- **Never commit API keys** - Use environment variables
- **Use .gitignore** - API keys and secrets are automatically excluded
- **Rotate keys regularly** - Especially if accidentally exposed
- **Use least privilege** - Only grant necessary API permissions

---

## Common Agent Protocols

**All agents MUST follow these protocols. Individual agent files reference this section instead of duplicating it.**

### Task Analysis & Collaboration Protocol

**CRITICAL — MANDATORY AT EVERY HANDOVER**: When an agent receives work from another agent (or from the user), it MUST follow this protocol BEFORE starting any implementation. The handing-over agent (or user) MUST answer the receiving agent's questions.

#### 1. Task Analysis & Clarification (MANDATORY)
When receiving a handover or new task, ALWAYS:

- **Read the handover context**: What did the previous agent complete? What decisions were made?
- **Read & Understand**: Carefully read the task description, requirements, and acceptance criteria
- **Ask Clarifying Questions** — the receiving agent MUST ask, and the handing-over agent/user MUST answer:
  - **What**: What exactly needs to be built/changed?
  - **Why**: What is the purpose and business value?
  - **How**: Are there specific approaches or constraints?
  - **Scope**: What is in-scope vs out-of-scope?
  - **Dependencies**: What does this depend on? What depends on this?
  - **Success Criteria**: How will we know this is done correctly?
- **Do NOT proceed until questions are answered** — if answers are unclear, ask again

#### 2. Document Understanding
Record in the appropriate `project-management/` subfolder:
- Task understanding and interpretation
- Key decisions and rationale
- Assumptions made
- Risks identified

#### 3. Think Critically Before Implementing
- **Identify Flaws**: Look for potential issues, edge cases, or problems
- **Suggest Improvements**: Propose better approaches or alternatives
- **Consider Trade-offs**: Analyze pros/cons of different approaches
- **Long-term Impact**: Consider maintainability and scalability

#### 4. Collaborate with Other Agents
- **Share Analysis**: Document findings and questions
- **Request Input**: Ask relevant agents for their perspective
- **Reach Consensus**: Ensure agreement on approach before proceeding
- **Document Agreement**: Record the agreed-upon approach

#### 5. Get Approval Before Significant Work
- Present the refined plan to the user
- Confirm understanding and approach
- Get explicit go-ahead

#### 6. Execute with Documentation
- Follow the agreed-upon plan
- Document significant decisions as you go
- Note any deviations from the plan and why

**Why this matters**: Without this protocol, agents make assumptions, build the wrong thing, or miss requirements. Asking clarifying questions catches misunderstandings early — before code is written.

### Before Concluding Any Task (ALL AGENTS)

**CRITICAL**: Before marking a task as complete, ALWAYS:

1. **Check for uncommitted changes**: `git status`
2. **Commit all work**: `git add -A && git commit -m "[Agent Name] Description"`
3. **Push to remote**: `git push -u origin [branch-name]`
4. **Follow the [Handover Protocol](#mandatory-handover-protocol-all-agents)**: Ask user about PR
5. **If PR created**: Verify it exists on GitHub and inform user of the URL
6. **Update task status**: Mark task as completed in the task file

### Branch Name Validation (ALL AGENTS)

Before creating a PR, validate your branch name:
```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Branch should match: {llm-name}/{agent}-{task_name}-{sessionID}
# Examples: copilot/architect-login-page-abc123, claude/developer-api-xyz789
```

**Why this matters**: Automated peer review requires agent-specific branch names matching `{llm-name}/{agent}-{task_name}-{sessionID}`. Generic branch names will cause peer review automation to skip the PR.

---

**Template Version**: 2.2
**Last Updated**: 2026-02-06
