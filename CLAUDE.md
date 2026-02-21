# Workflow Guide

**This file is your WORKFLOW GUIDE.** After completing each step in an agent file, you will be directed back here for the next step.

CRITICAL: For ANY user task, follow these steps IN ORDER. Do NOT skip steps.

**BEFORE ANY STEP**: Read `ai-assistants/memory.md` first. User preferences stored in memory override all instructions below — even those marked MANDATORY. If the user has expressed a preference about handover behavior, PR creation, or any other workflow aspect, follow the preference instead of the default instruction.

---

## Git Workflow

All work in this project is organized using Git branches at two levels:

1. **Task level:** When the user gives you new work — whether it is building a new project, adding a feature, fixing a bug, or any other request — a task branch `master_{task_name}` is created from the `template/agentic-workflow-gui` branch in the user's forked repository. This task branch is the single destination for all work related to that request.

2. **Agent level:** As each agent (Architect, Developer, Tester, etc.) works on their part of the task, they create their own branch from the task branch. When an agent completes their work, their branch is merged back into the task branch — either directly or through a pull request if the user requests a review.

### How branches work

```
template/agentic-workflow-gui                            ← template branch (never modified directly)
  └── master_{task_name}                                 ← task branch (one per user request)
        ├── claude/architect-{task_name}-{sessionID}     ← Architect's work → merges back to task branch
        ├── claude/developer-{task_name}-{sessionID}     ← Developer's work → merges back to task branch
        └── claude/tester-{task_name}-{sessionID}        ← Tester's work → merges back to task branch
```

### Branch naming

- **Template branch:** `template/agentic-workflow-gui`
- **Task branch:** `master_{task_name}` (e.g., `master_login-page`)
- **Agent branch:** `claude/{agent}-{task_name}-{sessionID}` (e.g., `claude/developer-login-page-abc123`)

### Rules

- Every new user request gets a new task branch created from `template/agentic-workflow-gui`
- All agent branches are created from the task branch, not from the template branch
- All pull requests target the task branch `master_{task_name}`, never main or master
- Iterations, fixes, and improvements related to the same user request all stay within the same task branch

### Creating a Task Branch (Product Owner does this at Step 2)

```bash
git checkout template/agentic-workflow-gui
git checkout -b master_{task_name}
git push -u origin master_{task_name}
```

### Creating an Agent Branch

```bash
git checkout master_{task_name}
git checkout -b claude/{agent}-{task_name}-{sessionID}
```

### Creating a PR

```bash
gh pr create --base master_{task_name} \
  --head claude/{agent}-{task_name}-{sessionID} \
  --title "[Agent Name] Work description" \
  --body "## Summary
[What was accomplished]

## Ready for
[Next Step Name]"
```

### If PR Creation Fails

1. `gh auth status` — check authentication
2. `gh repo set-default OWNER/REPO` — set repository context
3. `git remote -v` — verify remotes point to your fork

---

## Step 1: IT Agent — Verify Tools

Read `ai-assistants/agents/it-agent.md`, go to "Step 1: Verify Tools".
Verify that git and gh CLI are installed and authenticated.
Complete the BEFORE HANDING OFF checklist in that file, then come back here for Step 2.

---

## Step 2: Product Owner — Requirements

Read `ai-assistants/agents/product-owner-agent.md`, go to "Step 2: Requirements".
Clarify requirements with the user and create a user story.
Complete the BEFORE HANDING OFF checklist in that file, then come back here for Step 3.

---

## Step 3: Cost Analyst — Cost Estimate

Read `ai-assistants/agents/cost-analyst-agent.md`, go to "Step 3: Cost Estimate".
Estimate total task cost and warn the user if expensive.
Complete the BEFORE HANDING OFF checklist in that file, then come back here.

**MANDATORY before moving on:**
1. Report the cost estimate to the user
2. If the user approves, continue to Step 4
3. If the user wants to adjust scope, go back to Step 2

---

## Step 4: Architect — Design

Read `ai-assistants/agents/architect-agent.md`, go to "Step 4: Design".
Create the technical design and choose the tech stack.
Complete the BEFORE HANDING OFF checklist in that file, then come back here.

**MANDATORY before moving on** (check `ai-assistants/memory/user-preferences.md` for overrides):
1. Commit and push your work
2. Check user preferences for handover behavior. If no preference exists:
   Ask the user: "Would you like me to create a PR for review, or continue to Step 5?"
   Wait for the user's response — do NOT skip this step
3. If user wants a PR: create it using `gh pr create --base master_{task_name}`

---

## Step 5: IT Agent — Project Setup

Read `ai-assistants/agents/it-agent.md`, go to "Step 5: Project Setup".
Install project dependencies and create build/test/run scripts.
Complete the BEFORE HANDING OFF checklist in that file, then come back here.

**MANDATORY before moving on** (check `ai-assistants/memory/user-preferences.md` for overrides):
1. Commit and push your work
2. Check user preferences for handover behavior. If no preference exists:
   Ask the user: "Would you like me to create a PR for review, or continue to Step 6?"
   Wait for the user's response — do NOT skip this step
3. If user wants a PR: create it using `gh pr create --base master_{task_name}`

---

## Step 6: Developer — Implementation

Read `ai-assistants/agents/developer-agent.md`, go to "Step 6: Implementation".
Implement the feature according to Architect's design.
Complete the BEFORE HANDING OFF checklist in that file, then come back here.

**MANDATORY before moving on** (check `ai-assistants/memory/user-preferences.md` for overrides):
1. Commit and push your work
2. Provide the one-line command to run the app:
   - Mac/Linux: `bash scripts/run.sh`
   - Windows: `scripts\run.ps1`
3. Check user preferences for handover behavior. If no preference exists:
   Ask the user: "Would you like me to create a PR for review, or continue to Step 7?"
   Wait for the user's response — do NOT skip this step
4. If user wants a PR: create it using `gh pr create --base master_{task_name}`

---

## Step 7: Tester — Validation

Read `ai-assistants/agents/tester-agent.md`, go to "Step 7: Validation".
Validate the implementation with tests.
Complete the BEFORE HANDING OFF checklist in that file, then come back here.

**MANDATORY before moving on** (check `ai-assistants/memory/user-preferences.md` for overrides):
1. Commit and push your work
2. Provide the one-line command to run the tests:
   - Mac/Linux: `bash scripts/test.sh`
   - Windows: `scripts\test.ps1`
3. Check user preferences for handover behavior. If no preference exists:
   Ask the user: "Would you like me to create a PR for review, or continue to Step 8?"
   Wait for the user's response — do NOT skip this step
4. If user wants a PR: create it using `gh pr create --base master_{task_name}`

---

## Step 8: IT Agent — Release

Read `ai-assistants/agents/it-agent.md`, go to "Step 8: Release".
Build release artifacts.
Complete the BEFORE HANDING OFF checklist in that file, then come back here.

**MANDATORY before moving on** (check `ai-assistants/memory/user-preferences.md` for overrides):
1. Commit and push your work
2. Check user preferences for handover behavior. If no preference exists:
   Ask the user: "Would you like me to create a PR for review, or continue to Step 9?"
   Wait for the user's response — do NOT skip this step
3. If user wants a PR: create it using `gh pr create --base master_{task_name}`

---

## Step 9: Product Owner — Acceptance

Read `ai-assistants/agents/product-owner-agent.md`, go to "Step 9: Acceptance".
Review the completed work and present to the user.

**MANDATORY:**
1. Provide the run command and test command to the user
2. Ask the user to review and accept the work

---

## Prompting Claude Code for Agent Roles

- "Act as the IT Agent (follow ai-assistants/agents/it-agent.md) and verify tools are installed"
- "Act as the Product Owner (follow ai-assistants/agents/product-owner-agent.md) and create a user story for [feature]"
- "Act as the Cost Analyst (follow ai-assistants/agents/cost-analyst-agent.md) and estimate the cost for this task"
- "Act as the Architect (follow ai-assistants/agents/architect-agent.md) and design the technical solution"
- "Act as the Developer (follow ai-assistants/agents/developer-agent.md) and implement [feature]"
- "Act as the Tester (follow ai-assistants/agents/tester-agent.md) and validate the implementation"

---

## Updating Memory

After completing any step, update memory if any of these happened:
- **User expressed a preference** → save to `ai-assistants/memory/user-preferences.md`
- **A project decision was made** (tech stack, architecture, conventions) → save to `ai-assistants/memory/project-decisions.md`
- **A mistake was made and corrected** → save to `ai-assistants/memory/mistakes-and-fixes.md` under the appropriate agent section
