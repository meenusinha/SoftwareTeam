# Automated Multi-Agent Peer Review System

**Document**: Automated Multi-Agent Peer Review
**Project**: BigProjPOC
**Owner**: IT Agent
**Date**: 2026-01-20
**Version**: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Review Flow](#review-flow)
4. [Agent Roles and Checklists](#agent-roles-and-checklists)
5. [Setup Requirements](#setup-requirements)
6. [Approval Thresholds](#approval-thresholds)
7. [Review Iteration Cycle](#review-iteration-cycle)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## 1. Overview

The **Automated Multi-Agent Peer Review System** uses LLM APIs (OpenAI, Anthropic, Gemini, Azure, Cohere, or Mistral) to automatically review pull requests as different agent roles in a single sequential workflow.

### Key Features

✅ **Fully Automated**: No manual review needed - agents review automatically
✅ **Sequential Reviews**: Product Owner → Architect → Tester (or Developer) review one after another
✅ **Intelligent Feedback**: Each agent applies their expertise and detailed checklist
✅ **Inline Comments**: Issues appear directly on specific lines in "Files changed" tab
✅ **Approval Tracking**: Automatically tracks approvals and marks PR when threshold met
✅ **Iteration Support**: Reviewers re-review after Developer pushes changes
✅ **Single Session**: All reviews happen in one workflow run

### Benefits

- **Quality Assurance**: Multiple expert perspectives on every PR
- **Consistency**: Same rigorous standards applied every time
- **Speed**: Automated reviews complete in minutes
- **Precision**: Inline comments point to exact lines of code with issues
- **Learning**: Detailed feedback helps improve code quality
- **Transparency**: All review comments visible in PR (Conversation + Files changed tabs)
- **Flexible**: Choose from 6 LLM providers (OpenAI, Anthropic, Gemini, Azure, Cohere, Mistral)

---

## 2. How It Works

### Workflow Triggers

The automated review workflow uses **manual trigger only** (`workflow_dispatch`) to save LLM API costs. It does NOT run automatically when a PR is created or updated.

**To trigger the review:**
1. Go to the **Actions** tab in your GitHub repository
2. Click **"Automated Multi-Agent Peer Review"** in the left sidebar
3. Click the **"Run workflow"** button (top right)
4. Enter the **PR number** in the input field
5. Click the green **"Run workflow"** button to start
6. Wait 1-3 minutes for reviews to appear as PR comments

### Sequential Review Process

```
User triggers "Run workflow" from Actions tab (enters PR number)
    ↓
Extract Agent Type (from branch name)
    ↓
Determine Required Reviewers
    ↓
[For Each Reviewer Agent in Sequence]:
    ↓
  Load PR Details (diff, files, description)
    ↓
  Construct Review Prompt (agent-specific)
    ↓
  Call Claude API (as that agent role)
    ↓
  Parse Review Response
    ↓
  Post Review Comment on PR
    ↓
[Next Reviewer]
    ↓
Check Approval Count
    ↓
If 2+ Approvals: Mark PR as "peer-review:approved"
If Changes Requested: Mark PR as "peer-review:changes-requested"
    ↓
Done
```

### Agent Selection

Based on PR branch name `agent/{agent}-{project}-{sessionID}`:

| PR Author | Automated Reviewers |
|-----------|---------------------|
| Developer | Product Owner, Architect, Tester |
| Architect | Product Owner, Developer |
| Tester | Product Owner, Developer |
| IT | Product Owner, Architect |
| Product Owner | Architect, Developer, Tester |

---

## 3. Review Flow

### Phase 1: Initial Review (After PR Created)

1. **Developer** creates PR from `agent/developer-rtdcs-pbCFa`
2. **User triggers** the review workflow from the Actions tab (enter PR number)
3. **Product Owner Agent** reviews:
   - Fetches PR diff and files
   - Calls LLM API with Product Owner prompt and checklist
   - LLM analyzes code for standards, patterns, documentation
   - Posts review comment: "✅ APPROVED" or "🔴 CHANGES REQUESTED"
4. **Architect Agent** reviews:
   - Calls LLM API with Architect prompt and checklist
   - LLM checks design adherence, SOLID principles, interfaces
   - Posts review comment with decision
5. **Tester Agent** reviews:
   - Calls LLM API with Tester prompt and checklist
   - LLM evaluates testability, coverage, quality gates
   - Posts review comment with decision
6. **Approval Check**:
   - Count approvals (✅ APPROVED markers in comments)
   - If ≥ 2 approvals: Add labels `peer-review:approved`, `ready-for-user-review`
   - If changes requested: Add label `peer-review:changes-requested`

### Phase 2: Iteration (After Changes)

1. **Developer** addresses feedback and pushes new commits
2. **User re-triggers** the review workflow from the Actions tab (same PR number)
3. **All reviewers re-review** the updated code (sequential again)
4. **Approval re-check**: Count fresh approvals
5. **Repeat** until PR is approved or closed

---

## 4. Agent Roles and Checklists

Each agent has a specific role, expertise, and checklist that the LLM API uses for review.

### 4.1 Product Owner Agent

**Role**: Senior Technical Leader
**Expertise**: OO Architecture, Design Patterns, Code Quality Standards
**Focus**: Overall quality, standards compliance, design patterns, documentation

**Checklist**:
1. Code follows project standards and conventions
2. Design patterns are correctly applied (Strategy, Singleton, Command)
3. SOLID principles are followed
4. Documentation is complete and up-to-date
5. Commit messages are clear
6. PR description explains what, why, how
7. Overall quality meets requirements
8. No architectural anti-patterns

### 4.2 Architect Agent

**Role**: System Architect and Design Lead
**Expertise**: Software Architecture, Design Patterns (GoF), SOLID, Interface Design
**Focus**: Design adherence, SOLID principles, architecture quality

**Checklist**:
1. Implementation follows EDS specifications exactly
2. Interfaces are correctly implemented
3. Design patterns are appropriate and correct
4. SOLID principles: SRP, OCP, LSP, ISP, DIP
5. Component boundaries are clear, low coupling, high cohesion
6. Architecture is maintainable and extensible
7. Platform support (Linux, macOS) is correct
8. No architectural violations

### 4.3 Tester Agent

**Role**: Quality Assurance and Testing Specialist
**Expertise**: Testing Frameworks, Test Design, Quality Gates
**Focus**: Testability, test coverage, quality gates

**Checklist**:
1. Code is structured for testability
2. Unit tests present for all new/modified code
3. Test coverage adequate (>80% target)
4. Tests follow AAA pattern
5. Edge cases and error paths tested
6. Tests are clear, independent, repeatable, fast
7. Integration points properly tested
8. Quality gates met

### 4.4 Developer Agent (when reviewer)

**Role**: Software Developer and Implementation Specialist
**Expertise**: OOP, Clean Code, TDD, Best Practices
**Focus**: Code quality, implementation correctness, no code smells

**Checklist**:
1. Code is clean, readable, maintainable
2. Naming is clear and descriptive
3. Functions are small and focused (<50 lines)
4. No code duplication (DRY)
5. Logic is correct and efficient
6. Error handling is comprehensive
7. Resource cleanup is proper (RAII)
8. No code smells (long methods, deep nesting, magic numbers)
9. Best practices: const-correctness, smart pointers, thread safety
10. Memory management is safe

---

## 5. Setup Requirements

### 5.1 Repository Secrets

**Required**:
- `ANTHROPIC_API_KEY`: Your Anthropic/Claude API key
  - Obtain from: https://console.anthropic.com/
  - Add to: Repository Settings → Secrets and variables → Actions → New repository secret
  - Name: `ANTHROPIC_API_KEY`
  - Value: `sk-ant-...`

**Automatic**:
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions (no setup needed)

### 5.2 GitHub Actions Permissions

Ensure GitHub Actions has write permissions:

1. Go to: Repository Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select: "Read and write permissions"
4. Check: "Allow GitHub Actions to create and approve pull requests"
5. Save

### 5.3 Install Workflow Files

```bash
# Workflows already in .github/workflows/
# - pr-review-assignment.yml (labels and checklist comment)
# - automated-peer-review.yml (automated reviews)

# Review script already in .github/scripts/
# - automated-review.js (orchestrates reviews)
# - providers/*.js (LLM provider modules)
# - package.json (dependencies)
```

### 5.4 First-Time Setup

After merging this PR:

1. **Add LLM_PROVIDER and LLM_API_KEY secrets** (see 5.1 above)
2. **Verify GitHub Actions permissions** (see 5.2 above)
3. **Test with a sample PR**:
   ```bash
   # Create a test PR from a agent/developer-test-xxxxx branch
   # Watch workflow run in Actions tab
   # Check PR comments for agent reviews
   ```

---

## 6. Approval Thresholds

### Current Configuration

- **Required Approvals**: 2 (configurable in workflow)
- **Approval Triggers**: When 2+ agents post "✅ APPROVED"
- **Labels Added**: `peer-review:approved`, `ready-for-user-review`
- **Awaiting Labels**: Removed when approved

### Decision Logic

```javascript
if (approvals >= 2 && changesRequested === 0) {
  // Mark as peer-review approved
  // Add "ready-for-user-review" label
  // Remove "awaiting-*-review" labels
  // Post approval summary comment
} else if (changesRequested > 0) {
  // Add "peer-review:changes-requested" label
  // Developer needs to fix and push
} else {
  // Still waiting for more approvals
}
```

### Examples

**Scenario 1**: All 3 reviewers approve
- Approvals: 3/2 ✅
- Result: **APPROVED**, ready for user review

**Scenario 2**: 2 approve, 1 requests changes
- Approvals: 2/2
- Changes Requested: 1
- Result: **CHANGES REQUESTED**, Developer must fix

**Scenario 3**: Only 1 approves so far
- Approvals: 1/2
- Result: **WAITING**, need 1 more approval

---

## 7. Review Iteration Cycle

### Iteration Example

**Round 1**:
1. Developer creates PR
2. Product Owner: 🔴 CHANGES REQUESTED (naming issues)
3. Architect: 🔴 CHANGES REQUESTED (SOLID violation)
4. Tester: ✅ APPROVED (tests are good)
5. **Result**: Changes requested (2 agents requested changes)

**Developer Actions**:
- Fixes naming issues
- Refactors to follow SOLID principles
- Commits: `git commit -m "Fix: Apply SOLID principles and improve naming"`
- Pushes: `git push`

**Round 2** (user re-triggers workflow from Actions tab):
1. Product Owner: ✅ APPROVED (naming fixed)
2. Architect: ✅ APPROVED (SOLID principles now correct)
3. Tester: ✅ APPROVED (tests still good)
4. **Result**: 3/2 approvals → **APPROVED** ✅

**User Review**:
- User sees PR with 3 agent approvals
- User reviews and merges

---

## 8. Examples

### 8.1 Where to Find Reviews

Reviews appear in **two locations**:

1. **Conversation Tab**: Overall summary and decision
   - Agent's overall assessment
   - List of positive aspects
   - Final decision (APPROVED or CHANGES REQUESTED)

2. **Files Changed Tab**: Inline comments on specific lines ⭐ **NEW**
   - Click "Files changed" tab
   - Scroll to files with issues
   - See comments directly on problematic lines
   - Each comment shows severity and recommendation

### 8.2 Example Review Comment (Product Owner)

**In Conversation Tab**:
```markdown
## 🤖 **Product Owner Agent Review**

### Summary
This PR implements BigModuleA (ThermalMonitor) with good adherence to design patterns and standards. The Singleton pattern for SharedMemoryManager and Strategy pattern for temperature patterns are correctly applied. However, there are some documentation gaps and a few minor convention issues.

### Positive Aspects
- Correct application of Singleton and Strategy patterns
- Clean code structure with good separation of concerns
- Comprehensive unit tests included

### Decision
🔴 **CHANGES REQUESTED** - This PR requires changes before approval.

**3 inline comment(s)** posted on specific lines in the "Files changed" tab.
```

**In Files Changed Tab** (inline comments on specific lines):
```
src/ThermalMonitor.cpp:45
┌─────────────────────────────────────────────
│ 🤖 Product Owner Agent
│
│ **[Severity: Major]** Missing error handling
│
│ The shared memory initialization lacks error handling.
│ If shm_open fails, the program will crash.
│
│ Recommendation: Add proper error checking and
│ return a status code or throw an exception.
└─────────────────────────────────────────────
  - File: src/int/impl/Logger.cpp:45
  - Problem: Variable `ts` should be `timestamp` for clarity
  - Recommendation: Rename to `timestamp` for better readability

### Positive Aspects
- Strategy pattern correctly implemented for temperature patterns
- Singleton pattern properly used for SharedMemoryManager
- SOLID principles well-applied
- Clear commit messages
- Good code organization

### Decision
🔴 **CHANGES REQUESTED** - This PR requires changes before approval.

---

*Automated review by Product Owner Agent | Agent expertise: overall quality, standards compliance, design patterns, documentation, project alignment*
```

### 8.2 Example Approval Summary

After 2+ approvals:

```markdown
## ✅ Peer Review Approved

**3/2** required approvals obtained!

✨ This PR has passed all peer reviews and is **ready for user review and merge**.

---
*Automated peer review by Product Owner, Architect, and Tester agents*
```

---

## 9. Troubleshooting

### Issue: No Reviews After PR Creation

**Symptoms**: PR created but no automated reviews appear

**Most Likely Cause**: The workflow is **manual trigger only** — it does NOT run automatically.

**Solution**:
1. Go to the **Actions** tab in your GitHub repository
2. Click **"Automated Multi-Agent Peer Review"** in the left sidebar
3. Click **"Run workflow"**, enter the PR number, and click the green button
4. Wait 1-3 minutes for reviews to appear

**Other Possible Causes**:
1. Branch name doesn't match pattern `{llm-name}/{agent}-{project}-{sessionID}`
2. GitHub Actions disabled in repository settings
3. `LLM_API_KEY` secret not configured

### Issue: API Key Error

**Symptoms**: Workflow fails with "ANTHROPIC_API_KEY environment variable is required"

**Solution**:
1. Add `ANTHROPIC_API_KEY` secret to repository:
   - Settings → Secrets and variables → Actions → New repository secret
2. Ensure secret name is exactly `ANTHROPIC_API_KEY`
3. Re-run workflow

### Issue: Reviews Not Posting

**Symptoms**: Workflow runs but no review comments appear on PR

**Possible Causes**:
1. GitHub token permissions insufficient
2. Script error parsing PR details
3. LLM API rate limit hit

**Solutions**:
- Check workflow permissions (read and write needed)
- Check Actions logs for errors
- Wait a few minutes if rate limited

### Issue: Wrong Number of Reviewers

**Symptoms**: Expected 3 reviewers but only 2 reviewed

**Cause**: Review assignment rules based on branch pattern

**Solution**: Verify branch name matches pattern and agent type is correct

### Issue: Approval Not Marked

**Symptoms**: 2+ agents approved but PR not marked as approved

**Possible Causes**:
1. Some reviews still have "CHANGES REQUESTED"
2. Review comments don't contain exact approval markers
3. Label creation failed

**Solutions**:
- Check that changes requested count is 0
- Verify review comments contain "✅ **APPROVED**" exactly
- Manually add labels if needed

---

## Appendix A: LLM Provider Configuration

### Supported Providers

| Provider | Model | Best For | Cost |
|----------|-------|----------|------|
| OpenAI | GPT-4o | General purpose | $$ |
| Anthropic | Claude Sonnet 4 | Code review | $$$ |
| Gemini | Gemini Pro | Fast responses | $ |
| Azure | GPT-4 | Enterprise | $$$ |
| Cohere | Command R Plus | Efficiency | $ |
| Mistral | Mistral Large | Open-source | $ |

### Modular Architecture

The system uses a modular provider architecture:
- Each provider in separate file: `.github/scripts/providers/{provider}.js`
- Dynamic loading based on `LLM_PROVIDER` environment variable
- Standardized interface: `callLLM(prompt, agentType)` returns review text
- Easy to add new providers without modifying main script

### Switching Providers

To switch providers, just update GitHub Secrets:
1. Settings → Secrets → Actions
2. Update `LLM_PROVIDER` to new provider name
3. Update `LLM_API_KEY` to new provider's key
4. (Optional) Add provider-specific secrets like `AZURE_OPENAI_ENDPOINT`

No code changes required!

### Model Configuration

Models vary by provider:
- **OpenAI**: `gpt-4o`
- **Anthropic**: `claude-sonnet-4-20250514`
- **Gemini**: `gemini-pro`
- **Azure**: `gpt-4`
- **Cohere**: `command-r-plus`
- **Mistral**: `mistral-large-latest`

**Common Settings**:
- **Max Tokens**: 4096
- **Temperature**: 0.2 (lower for consistent reviews)

### Cost Considerations

**Per Review**:
- Input: ~2000-5000 tokens (PR details + prompt)
- Output: ~500-2000 tokens (review comment)
- Cost: ~$0.01-$0.05 per review

**Per PR** (3 reviewers):
- Total: ~$0.03-$0.15 per PR

**Monthly** (assuming 50 PRs/month):
- Total: ~$1.50-$7.50/month

*Note: Costs are approximate and depend on PR size and LLM provider pricing*

---

## Appendix B: Workflow Files

### File Structure

```
.github/
├── workflows/
│   ├── pr-review-assignment.yml     # Adds labels and checklist comment
│   └── automated-peer-review.yml    # Automated reviews (this system)
└── scripts/
    ├── automated-review.js          # Review script
    └── package.json                 # Dependencies
```

### Execution Flow (Both Manually Triggered)

1. **pr-review-assignment.yml** (optional, run first):
   - Trigger: Actions tab > "PR Review Assignment (Manual)" > Run workflow > Enter PR number
   - Adds labels
   - Posts checklist comment for reference

2. **automated-peer-review.yml** (main review workflow):
   - Trigger: Actions tab > "Automated Multi-Agent Peer Review" > Run workflow > Enter PR number
   - Calls LLM API for each reviewer
   - Posts review comments
   - Tracks approvals
   - Marks PR when approved

---

## Document Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | IT Agent | Initial automated multi-agent review documentation |

---

**End of Automated Multi-Agent Peer Review Documentation**
