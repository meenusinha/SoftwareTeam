# Setup Wizard - Engineering Product Specification (EPS)

## 1. Product Overview

**Product Name:** Setup Wizard for AI-Assisted Development Workflow

**Version:** 1.0

**Date:** 2026-02-07

**Summary:** A browser-based setup wizard that enables non-programmers to set up and configure the AI-assisted agentic development workflow with a single command. The wizard eliminates the need for users to understand terminals, git, package managers, or configuration files.

## 2. Product Vision

### 2.1 Problem

The existing `QUICK-START.md` setup process requires 15+ manual steps involving terminal commands, GitHub UI navigation, environment variable exports, and package manager operations. This is a significant barrier for non-technical users who want to leverage AI-assisted development.

### 2.2 Solution

A single-command setup that opens a browser-based wizard with step-by-step visual guidance. The wizard handles all installations, configurations, and file operations behind the scenes while presenting a friendly UI.

### 2.3 Success Criteria

| Metric | Target |
|--------|--------|
| Steps for non-programmer to complete setup | 1 terminal command + follow wizard screens |
| Technical knowledge required | Ability to open Terminal/PowerShell and paste a command |
| Supported operating systems | macOS 12+, Ubuntu 20.04+, Fedora 36+, Windows 10+ |
| External dependencies required | Python 3 (auto-installed if missing) |
| Time to complete setup | Under 10 minutes |

## 3. User Personas

### 3.1 Non-Programmer ("Alex")

- **Background:** Small business owner, no coding experience
- **Goal:** Use AI tools to build a simple business application
- **Pain points:** Doesn't know what git, Terminal, or an API key is
- **Needs:** Visual guidance, plain language, no jargon, one-click actions
- **Wizard experience:** Runs the one-line command (with instructions), follows wizard screens, selects "Local" mode to avoid GitHub complexity

### 3.2 Beginner ("Sam")

- **Background:** Marketing professional, some tech exposure, uses GitHub occasionally
- **Goal:** Set up the full workflow with GitHub integration
- **Pain points:** Comfortable with basics but overwhelmed by multiple tools and config steps
- **Needs:** Step-by-step guidance for token creation, API key setup
- **Wizard experience:** Selects "GitHub" mode, follows guided token/provider setup, chooses Cursor for its visual interface

### 3.3 Developer ("Jordan")

- **Background:** Software developer comfortable with CLI
- **Goal:** Quick setup without reading through QUICK-START.md
- **Pain points:** Doesn't want to manually run 15 commands
- **Needs:** Fast, automated setup
- **Wizard experience:** Runs the one-liner, clicks through screens quickly, may skip optional LLM provider step

## 4. User Journeys

### 4.1 Journey: Non-Programmer, Local Mode

```
Alex reads the project README
  -> Sees "Easy Setup" section with one command
  -> Opens Terminal (guided: "Press Cmd+Space, type Terminal, press Enter")
  -> Pastes: curl -sL <url>/setup/setup.sh | bash
  -> Browser opens with wizard
  -> Screen 1: "Welcome! Detected: macOS 14.2" -> clicks "Get Started"
  -> Screen 2: Selects "Work Locally" -> clicks "Next"
  -> Screen 3: Git installs automatically -> clicks "Next"
  -> (Screens 4-6 skipped automatically)
  -> Screen 7: Picks "Cursor" -> clicks "Install" -> clicks "Launch"
  -> Screen 8: Pastes verification question, sees "Product Owner" -> clicks "Everything Works!"
  -> Screen 9: "You're All Set!" -> Opens Cursor and starts describing what they want
```

**Total user actions:** ~8 clicks + 1 paste command

### 4.2 Journey: Beginner, GitHub Mode

```
Sam reads the project README
  -> Pastes the setup command in Terminal
  -> Browser opens with wizard
  -> Screen 1: "Welcome! Detected: Windows 11" -> clicks "Get Started"
  -> Screen 2: Selects "Use GitHub" -> clicks "Next"
  -> Screen 3: Git and gh CLI install via winget -> clicks "Next"
  -> Screen 4: Clicks "Sign In with Browser" -> completes GitHub OAuth in browser -> status shows "Signed in as @sam" -> clicks "Next"
  -> Screen 5: Clicks link to open token page -> follows numbered steps -> pastes token -> clicks "Save Token" -> clicks "Next"
  -> Screen 6: Selects "Desktop" as location -> clicks "Fork & Clone" -> clicks "Next"
  -> Screen 7: Selects "Gemini" -> clicks link to get API key -> pastes key -> clicks "Save Configuration" -> clicks "Next"
  -> Screen 8: Picks "Cursor" -> clicks "Install" -> clicks "Launch"
  -> Screen 9: Verifies, then "You're All Set!"
```

**Total user actions:** ~15 clicks + 2 paste actions

### 4.3 Journey: Developer, GitHub Mode (Fast Path)

```
Jordan pastes the setup command
  -> Screen 1: "Get Started"
  -> Screen 2: "Use GitHub"
  -> Screen 3: git and gh already installed, "Next"
  -> Screen 4: Already signed in, "Next"
  -> Screen 5: Pastes pre-existing token, "Save", "Next"
  -> Screen 6: "Fork & Clone", "Next"
  -> Screen 7: "Skip" (already has provider configured)
  -> Screen 8: Picks "Claude Code", "Install", "Launch"
  -> Screen 9: Done
```

**Total user actions:** ~10 clicks + 1 paste

## 5. Product Features

### 5.1 Feature: One-Command Bootstrap

**Description:** Users start the entire setup with a single paste-able command.

| Platform | Command |
|----------|---------|
| Mac/Linux | `curl -sL <url>/setup/setup.sh \| bash` |
| Windows | `irm <url>/setup/setup.ps1 \| iex` |

**What happens:**
1. Script downloads itself and the project tarball/zip
2. Installs Python 3 if missing
3. Launches the wizard in the browser
4. Cleans up temp files when done

**User prerequisite:** Ability to open Terminal (Mac/Linux) or PowerShell (Windows) and paste a command.

### 5.2 Feature: Dual Workflow Modes

**Description:** Users choose between GitHub-integrated or fully-local workflow.

| Mode | Screens Shown | Git Required | GitHub Account Required | Internet After Setup |
|------|--------------|-------------|------------------------|---------------------|
| GitHub | All 9 | Yes | Yes | Yes (for PRs, reviews) |
| Local | 5 of 9 | No | No | No |

**Skip logic:** Local mode automatically skips screens 3 (GitHub Account), 4 (Token), 5 (Fork/Clone), and 6 (LLM Provider).

### 5.3 Feature: Guided GitHub Setup

**Description:** Step-by-step visual guidance for GitHub account creation, sign-in, and token generation.

**Sub-features:**
- Account detection via `gh auth status`
- Browser-based OAuth sign-in via `gh auth login --web`
- Direct link to github.com/signup for new accounts
- Clickable link to token settings page
- Numbered instructions with exact button names and scope checkboxes
- Paste-and-save token field

### 5.4 Feature: Guided LLM Provider Setup

**Description:** Per-provider instructions for obtaining API keys, with clickable links to each provider's console.

**Supported providers:**

| Provider | Cost | API Key Page | Special Requirements |
|----------|------|-------------|---------------------|
| GitHub Copilot | FREE | N/A (no key needed) | Copilot Enterprise for automated reviews |
| Google Gemini | $ | makersuite.google.com/app/apikey | Google account |
| OpenAI | $$ | platform.openai.com/api-keys | OpenAI account |
| Anthropic | $$$ | console.anthropic.com | Anthropic account |
| Azure OpenAI | $$$ | portal.azure.com | Azure subscription + endpoint URL |
| Cohere | $ | dashboard.cohere.com | Cohere account |
| Mistral | $ | console.mistral.ai | Mistral account |

### 5.5 Feature: AI Tool Installation and Launch

**Description:** One-click install and launch for supported AI development tools.

| Tool | Type | Install Method (macOS) | Instruction File |
|------|------|----------------------|-----------------|
| Cursor | GUI IDE | `brew install --cask cursor` | `.cursorrules` |
| Windsurf | GUI IDE | `brew install --cask windsurf` | `.windsurfrules` |
| Claude Code | CLI | `npm install -g @anthropic-ai/claude-code` | `CLAUDE.md` |
| VS Code + Continue | GUI IDE + Extension | `brew install --cask visual-studio-code` | `.continuerules` |
| VS Code + Copilot | GUI IDE + Extension | `brew install --cask visual-studio-code` | `.github/copilot-instructions.md` |
| Aider | CLI | `pip3 install aider-chat` | `.aider.conf.yml` |

**Post-install:** Tool is launched pointed at the project directory, where it automatically picks up its instruction file.

### 5.6 Feature: Verification and Fallback

**Description:** Three-layer approach to confirm the AI tool is connected to the workflow.

| Layer | What It Does |
|-------|-------------|
| 1. Precondition | Wizard ensures instruction file exists at expected path |
| 2. Verification prompt | User pastes "What is the first agent role you adopt for any task?" — expected: "Product Owner" |
| 3. Fallback prompt | If verification fails, user pastes a per-tool prompt that explicitly tells the AI to read its instruction file |

## 6. Platform and Environment Support

### 6.1 Operating Systems

| OS | Minimum Version | Package Manager | Entry Script |
|----|----------------|----------------|-------------|
| macOS | 12 (Monterey) | Homebrew (auto-installed) | `setup.sh` |
| Ubuntu | 20.04 LTS | apt | `setup.sh` |
| Fedora | 36 | dnf | `setup.sh` |
| Arch Linux | Rolling | pacman | `setup.sh` |
| openSUSE | Leap 15 | zypper | `setup.sh` |
| Windows | 10 (1809+) | winget / choco | `setup.ps1` |

### 6.2 Browser Support

The wizard UI uses standard HTML5, CSS3, and ES6 JavaScript. No frameworks or transpilation. Compatible with:
- Chrome/Chromium 80+
- Firefox 78+
- Safari 14+
- Edge 80+

### 6.3 Runtime Dependencies

| Dependency | Required At | Auto-Installed By |
|-----------|------------|------------------|
| Python 3 | Wizard launch | `setup.sh` / `setup.ps1` |
| curl or wget | Tarball download (Mac/Linux) | Pre-installed on all supported OS |
| PowerShell 5+ | Zip download (Windows) | Pre-installed on Windows 10+ |

**No pip packages required.** The wizard uses only the Python 3 standard library.

## 7. User Interface Specification

### 7.1 Layout

- Max width: 680px, centered
- Background: light gray (`#f8fafc`)
- Cards: white with subtle shadow and border
- Font: System font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`)
- Responsive: works down to 320px width

### 7.2 Progress Indicator

Segmented horizontal bar at top of wizard. Each segment represents one screen:
- **Gray:** Not yet reached
- **Blue:** Current screen
- **Green:** Completed screen

### 7.3 Screen Template

Each screen follows this structure:
1. **Title** (h2)
2. **Description** (muted text, 1-2 sentences)
3. **Content area** (varies per screen: radio groups, status lists, input fields, tool grids)
4. **Button row** (Back on left, Next on right; Next disabled until step is complete)

### 7.4 Interactive Components

| Component | Usage |
|-----------|-------|
| Radio options | Workflow mode, LLM provider selection (clickable cards with radio buttons) |
| Status items | Prerequisite check (icon + label + version + action button) |
| Tool grid | AI tool selection (2-column grid of clickable cards) |
| Copy box | Verification/fallback prompts (dark box with text + Copy button) |
| Instructions | Step-by-step guides (numbered list with links and code highlights) |
| Alerts | Feedback messages (info blue, success green, warning amber, danger red) |
| Input fields | Token input, API key input, path input, project name input |

## 8. Data Flow

### 8.1 Token and API Key Handling

```
User pastes token in wizard UI (browser)
  -> JavaScript sends POST /api/github/token {"token": "ghp_..."}
  -> Python saves to shell profile (~/.bashrc or ~/.zshrc) or Windows user env
  -> Python runs: echo "token" | gh auth login --with-token
  -> Response: {"success": true}
```

Tokens and API keys:
- Are stored **only on the user's local machine**
- Are transmitted only over `127.0.0.1` (localhost, never over the network)
- Are saved to the user's shell profile (Mac/Linux) or user environment variables (Windows)
- Are optionally saved as GitHub repository secrets (via `gh secret set`)

### 8.2 Fork and Clone Flow

```
User clicks "Fork & Clone" in wizard UI
  -> POST /api/github/fork-clone {"path": "/Users/me/Desktop", "project_name": "my-project"}
  -> Python runs: gh repo fork meenusinha/SoftwareTeam --clone=false
  -> Python runs: gh repo clone SoftwareTeam "/Users/me/Desktop/my-project" -- --branch template/agentic-workflow-gui
  -> Response: {"success": true, "project_path": "/Users/me/Desktop/my-project"}
```

### 8.3 Local Copy Flow

```
User clicks "Copy Project Files" in wizard UI
  -> POST /api/local/copy {"path": "/Users/me/Desktop", "project_name": "my-project"}
  -> Python runs: shutil.copytree(source, dest, ignore='.git')
  -> Source = WIZARD_REPO_PATH env var (set by setup.sh, points to extracted tarball)
  -> Response: {"success": true, "project_path": "/Users/me/Desktop/my-project"}
```

## 9. Constraints and Limitations

| Constraint | Description |
|-----------|-------------|
| No native folder picker | Browser security prevents accessing a native OS folder picker from a web page. Users select from suggested paths or type a custom path. |
| Cannot verify AI tool loaded instructions | No AI tool exposes an API to confirm it read its config file. Mitigated by the verification prompt approach. |
| Sudo on Linux | Package installation requires sudo. If the user doesn't have sudo access, auto-install fails and manual instructions are shown. |
| curl pipe to bash | The entry point uses `curl | bash`, which some security-conscious users may distrust. They can download and inspect the script first. |
| Python on Windows | Python is not pre-installed on Windows. The setup script installs it via winget or downloads the installer directly. |
| Single AI tool | The wizard installs and configures one AI tool at a time. Users can re-run the wizard to set up additional tools. |

## 10. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Homebrew installation fails (macOS) | Cannot install git, gh, or tools | Low | Provide manual install links; xcode-select as git fallback |
| User doesn't have sudo (Linux) | Package installation fails | Medium | Show clear error message with manual instructions |
| GitHub OAuth flow fails | Cannot sign in | Low | Allow manual token paste as alternative |
| API key page UI changes | Screenshots/instructions become outdated | Medium | Use text-only instructions (no screenshots); link directly to key page |
| Python version incompatibility | Wizard doesn't start | Low | Require Python 3.7+; use only stable standard library modules |
| winget not available (older Windows) | Cannot auto-install tools | Medium | Fallback to direct installer downloads or chocolatey |

## 11. Release Plan

### 11.1 Version 1.0 (Current)

- All 9 wizard screens functional
- Mac, Linux, and Windows support
- GitHub and Local workflow modes
- 5 AI tools, 7 LLM providers
- Entry scripts (`setup.sh`, `setup.ps1`)

### 11.2 Future Versions

| Version | Features |
|---------|----------|
| 1.1 | Workflow file updates (Product Owner as first agent, IT Agent prerequisite role removed) |
| 1.2 | GitHub Codespaces integration (`.devcontainer/` config, "Open in Codespaces" button) |
| 1.3 | Native executables (.dmg, .exe) for true double-click setup |
| 2.0 | Hosted web version (no local setup required) |

## 12. Acceptance Criteria

| Criteria | Test |
|----------|------|
| Non-programmer can complete setup | User with no terminal experience completes wizard in under 10 minutes |
| Works on macOS | setup.sh runs on macOS 12+, wizard opens in Safari/Chrome |
| Works on Ubuntu | setup.sh runs on Ubuntu 20.04+, wizard opens in Firefox/Chrome |
| Works on Windows | setup.ps1 runs on Windows 10+, wizard opens in Edge/Chrome |
| GitHub mode works end-to-end | Token saved, repo forked, cloned, tool launched at project |
| Local mode works end-to-end | Files copied, tool launched at project, no GitHub operations |
| Verification flow works | Verification prompt produces expected answer in at least one AI tool |
| Server shuts down cleanly | Closing wizard or clicking "Close" stops the Python server |
