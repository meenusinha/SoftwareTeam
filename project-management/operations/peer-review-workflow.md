# Peer Review Workflow

**Document**: Automated Peer Review Workflow
**Project**: BigProjPOC
**Owner**: IT Agent
**Date**: 2026-01-20
**Version**: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Peer Review Philosophy](#peer-review-philosophy)
3. [Review Assignment Rules](#review-assignment-rules)
4. [Automated Workflow](#automated-workflow)
5. [Review Process](#review-process)
6. [Review Checklist](#review-checklist)
7. [GitHub Labels](#github-labels)
8. [Troubleshooting](#troubleshooting)

---

## 1. Overview

The BigProjPOC project uses an **automated peer review workflow** to ensure quality and knowledge sharing across all agent contributions. Every pull request is automatically assigned to the appropriate peer reviewers based on the originating agent.

### Key Benefits

- **Quality Assurance**: Multiple expert eyes review each change
- **Knowledge Sharing**: All agents stay informed about project evolution
- **Design Validation**: Architect ensures design adherence
- **Implementation Quality**: Developer ensures code quality
- **Test Coverage**: Tester ensures testability and quality gates
- **Process Oversight**: Product Owner ensures overall project alignment

### Automation Components

1. **GitHub Actions Workflow**: `.github/workflows/pr-review-assignment.yml`
   - Automatically detects agent type from branch name
   - Assigns appropriate peer reviewers
   - Adds labels for tracking
   - Creates review request comment with checklist

2. **CODEOWNERS File**: `.github/CODEOWNERS`
   - Documents code ownership by agent
   - Serves as reference for manual review assignments
   - Defines responsibility boundaries

3. **GitHub Labels**: Applied automatically to track review status
   - `peer-review:{agent}` - Identifies PR origin
   - `awaiting-{agent}-review` - Tracks pending reviews

---

## 2. Peer Review Philosophy

### Quality Before Speed

Every PR goes through rigorous peer review **before** user review. This ensures:
- **Design Adherence**: Changes follow architecture specifications
- **Code Quality**: Implementation meets project standards
- **Testability**: Code is properly tested and testable
- **Maintainability**: Changes are sustainable long-term

### Agent Collaboration

Agents review each other's work:
- **Product Owner**: Ensures overall quality and project alignment
- **Architect**: Validates design patterns, SOLID principles, specifications
- **Developer**: Reviews implementation quality, code cleanliness, unit tests
- **Tester**: Ensures testability, coverage, and quality gates
- **IT**: Reviews infrastructure, build system, CI/CD changes

### Two-Phase Review

1. **Phase 1 - Peer Review**: Agents review each other (2-3 approvals required)
2. **Phase 2 - User Review**: After peer approval, user reviews and merges

**Critical**: User review happens **only after** peer approvals are obtained.

---

## 3. Review Assignment Rules

### Branch Naming Convention

All agent work uses the pattern: `agent/{agent}-{project}-{sessionID}`

Examples:
- `agent/developer-rtdcs-pbCFa` (Developer Agent working on RTDCS)
- `agent/architect-rtdcs-pbCFa` (Architect Agent working on RTDCS)
- `agent/tester-rtdcs-Xy1Z9` (Tester Agent working on RTDCS)

### Automatic Review Assignment

| PR Author | Required Reviewers | Minimum Approvals |
|-----------|-------------------|-------------------|
| **Developer** | Product Owner, Architect, Tester | 3 |
| **Architect** | Product Owner, Developer | 2 |
| **Tester** | Product Owner, Developer | 2 |
| **IT** | Product Owner, Architect | 2 |
| **Product Owner** | Architect, Developer, Tester | 3 |

### Rationale

- **Developer PRs** (implementation): Need architectural validation (Architect), quality oversight (Product Owner), and testability review (Tester)
- **Architect PRs** (design): Need implementation feasibility check (Developer) and orchestration approval (Product Owner)
- **Tester PRs** (QA): Need code review (Developer) and process approval (Product Owner)
- **IT PRs** (infrastructure): Need architectural alignment (Architect) and oversight (Product Owner)
- **Product Owner PRs** (coordination): Need technical validation from all technical leads

---

## 4. Automated Workflow

### Workflow Triggers

Both peer review workflows use **manual trigger only** (`workflow_dispatch`) to save LLM API costs. They do NOT run automatically when a PR is created.

**To trigger the review workflows:**

1. Go to the **Actions** tab in your GitHub repository
2. In the left sidebar, select the workflow you want to run:
   - **"PR Review Assignment (Manual)"** — adds labels and posts review checklist comment
   - **"Automated Multi-Agent Peer Review"** — runs LLM-powered code reviews
3. Click the **"Run workflow"** button (top right)
4. Enter the **PR number** in the input field
5. Click the green **"Run workflow"** button to start

**Recommended order**: Run "PR Review Assignment" first (adds labels/checklist), then "Automated Multi-Agent Peer Review" (runs the actual reviews).

### Workflow Steps

```
User clicks "Run workflow" in Actions tab
    ↓
Enter PR Number
    ↓
Detect Agent Type (from branch name)
    ↓
Lookup Review Rules (based on agent type)
    ↓
Add Labels (peer-review:{agent}, awaiting-{agent}-review)
    ↓
Create Review Request Comment (with checklist)
    ↓
Run LLM-powered reviews (sequential)
    ↓
Check Approval Count
    ↓
2+ Approvals? → Mark as "peer-review:approved" + "ready-for-user-review"
    ↓
Ready for User Review & Merge
```

### Workflow Output

For each PR, the workflow:
1. **Adds Labels**:
   - `peer-review:developer` (or architect, tester, it, product-owner)
   - `awaiting-product-owner-review`
   - `awaiting-architect-review`
   - `awaiting-tester-review` (etc.)

2. **Creates Comment** with:
   - List of required reviewers
   - Review policy explanation
   - Complete review checklist for each reviewer
   - PR metadata (branch, project, session ID)

3. **GitHub Step Summary**: Confirmation that reviewers were assigned

---

## 5. Review Process

### For PR Authors (Agents)

1. **Complete Work** in your dedicated git worktree
2. **Commit Changes** with clear, descriptive messages
3. **Push to Remote**: `git push -u origin agent/{agent}-{project}-{sessionID}`
4. **Create Pull Request** to task master branch
5. **Guide the user to trigger the review**: Tell them to go to the **Actions** tab, click **"Automated Multi-Agent Peer Review"**, click **"Run workflow"**, enter the PR number, and click the green button
6. **Address Feedback**: Respond to review comments, make requested changes
7. **Request Re-review**: After addressing feedback, ask user to re-trigger the workflow
8. **Await All Approvals**: Wait for all required reviewers to approve
9. **User Review**: Only after peer approvals, user reviews and merges

### For Reviewers (Agents)

1. **Receive Notification**: GitHub notifies you of review request
2. **Review the PR**:
   - Read the PR description and linked issues
   - Review all changed files
   - Check commits for clarity
   - Use the review checklist appropriate to your role
3. **Test Locally** (if applicable):
   - Check out the branch
   - Build the code
   - Run tests
   - Verify functionality
4. **Provide Feedback**:
   - **Approve**: If all checks pass
   - **Request Changes**: If issues found, provide clear, actionable feedback
   - **Comment**: For non-blocking suggestions
5. **Follow Up**: Re-review after author addresses feedback

### Review Timelines

- **Critical PRs** (blocking work): Review within 4 hours
- **Standard PRs**: Review within 24 hours
- **Documentation PRs**: Review within 48 hours

---

## 6. Review Checklist

### Product Owner Review Checklist

**Overall Quality**:
- [ ] Code follows project standards and conventions
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains what, why, and how
- [ ] Documentation is updated (AI-WORKFLOW.md, README, etc.)

**Design and Architecture**:
- [ ] Design patterns are correctly applied
- [ ] SOLID principles are followed
- [ ] Changes align with project architecture
- [ ] No architectural anti-patterns introduced

**Process Compliance**:
- [ ] Work completed in dedicated worktree
- [ ] Branch naming follows convention
- [ ] Appropriate scope (not too large, not too small)
- [ ] All required files included (no missing pieces)

**Quality Gates**:
- [ ] All tests pass (if applicable)
- [ ] No regressions introduced
- [ ] Performance is acceptable
- [ ] Security considerations addressed

---

### Architect Review Checklist

**Design Adherence**:
- [ ] Implementation follows EDS specifications
- [ ] Interfaces are correctly implemented
- [ ] API contracts match Thrift definitions
- [ ] Shared memory usage follows specification

**Design Patterns**:
- [ ] Appropriate patterns selected (Strategy, Singleton, Command, etc.)
- [ ] Patterns are correctly implemented
- [ ] No pattern misuse or over-engineering
- [ ] Design is extensible and maintainable

**SOLID Principles**:
- [ ] **S**ingle Responsibility: Each class has one purpose
- [ ] **O**pen/Closed: Extensible without modification
- [ ] **L**iskov Substitution: Interfaces are properly used
- [ ] **I**nterface Segregation: Interfaces are focused and minimal
- [ ] **D**ependency Inversion: Depends on abstractions, not concretions

**Architecture Quality**:
- [ ] Component boundaries are clear
- [ ] Coupling is low, cohesion is high
- [ ] Abstraction levels are appropriate
- [ ] No architectural violations

**Platform Support**:
- [ ] Code works on Linux (Ubuntu 20.04+)
- [ ] Code works on macOS (11.0+)
- [ ] Platform-specific code is properly isolated
- [ ] Build system handles platform differences

---

### Developer Review Checklist

**Code Quality**:
- [ ] Code is clean, readable, and maintainable
- [ ] Naming is clear and descriptive
- [ ] Functions are small and focused
- [ ] No code duplication (DRY principle)

**Implementation Quality**:
- [ ] Logic is correct and efficient
- [ ] Edge cases are handled
- [ ] Error handling is comprehensive
- [ ] Resource cleanup is proper (RAII, destructors)

**Code Smells** (should be absent):
- [ ] No long methods (>50 lines)
- [ ] No large classes (>500 lines)
- [ ] No deeply nested conditionals (>3 levels)
- [ ] No magic numbers or hard-coded strings
- [ ] No commented-out code
- [ ] No unnecessary complexity

**Best Practices**:
- [ ] const-correctness is maintained
- [ ] Memory management is safe (smart pointers)
- [ ] Thread safety is ensured (mutexes where needed)
- [ ] No global variables (except constants)

**Testing**:
- [ ] Unit tests are present for all new code
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Test coverage is >80%
- [ ] Tests are clear and maintainable

---

### Tester Review Checklist

**Testability**:
- [ ] Code is structured for testing
- [ ] Dependencies are injectable (for mocking)
- [ ] No tightly coupled components
- [ ] Test points are well-defined

**Test Coverage**:
- [ ] Unit tests cover all public methods
- [ ] Edge cases are tested
- [ ] Error paths are tested
- [ ] Happy path and sad path both covered

**Test Quality**:
- [ ] Tests are clear and well-named
- [ ] Tests are independent (no test interdependencies)
- [ ] Tests are repeatable (deterministic)
- [ ] Tests are fast (<1 second per test)

**Quality Gates**:
- [ ] All tests pass (unit, component, integration)
- [ ] No test failures or skips
- [ ] Code coverage meets threshold (>80%)
- [ ] Performance benchmarks pass (if applicable)

**Integration Testing**:
- [ ] Integration points are properly tested
- [ ] IPC mechanisms work correctly (shared memory, Thrift RPC)
- [ ] Multi-module communication is verified
- [ ] Error scenarios are tested

**Documentation**:
- [ ] Test plans are updated (if needed)
- [ ] Bug reports reference tests
- [ ] Test documentation is clear

---

## 7. GitHub Labels

### Peer Review Labels

| Label | Description | Applied When |
|-------|-------------|--------------|
| `peer-review:developer` | PR from Developer Agent | Developer creates PR |
| `peer-review:architect` | PR from Architect Agent | Architect creates PR |
| `peer-review:tester` | PR from Tester Agent | Tester creates PR |
| `peer-review:it` | PR from IT Agent | IT creates PR |
| `peer-review:product-owner` | PR from Product Owner Agent | Product Owner creates PR |

### Review Status Labels

| Label | Description | Applied When |
|-------|-------------|--------------|
| `awaiting-product-owner-review` | Waiting for Product Owner review | Product Owner is assigned as reviewer |
| `awaiting-architect-review` | Waiting for Architect review | Architect is assigned as reviewer |
| `awaiting-developer-review` | Waiting for Developer review | Developer is assigned as reviewer |
| `awaiting-tester-review` | Waiting for Tester review | Tester is assigned as reviewer |

### Creating Labels

Labels should be created in the GitHub repository:

1. Go to repository → **Issues** → **Labels**
2. Click **New label**
3. Add labels with these configurations:

**Peer Review Labels**:
- Name: `peer-review:developer`, Color: `#0E8A16` (green)
- Name: `peer-review:architect`, Color: `#1D76DB` (blue)
- Name: `peer-review:tester`, Color: `#FBCA04` (yellow)
- Name: `peer-review:it`, Color: `#D93F0B` (orange)
- Name: `peer-review:product-owner`, Color: `#5319E7` (purple)

**Review Status Labels**:
- Name: `awaiting-product-owner-review`, Color: `#EDEDED` (gray)
- Name: `awaiting-architect-review`, Color: `#EDEDED` (gray)
- Name: `awaiting-developer-review`, Color: `#EDEDED` (gray)
- Name: `awaiting-tester-review`, Color: `#EDEDED` (gray)

---

## 8. Troubleshooting

### Reviews Not Appearing After PR Creation

**Symptom**: PR created but no automated review comments appear

**Most Likely Cause**: The review workflows are **manual trigger only** — they do NOT run automatically when a PR is created.

**Solution**:
1. Go to the **Actions** tab in your GitHub repository
2. Click **"Automated Multi-Agent Peer Review"** in the left sidebar
3. Click **"Run workflow"**, enter the PR number, and click the green button
4. Wait 1-3 minutes for reviews to appear as PR comments

**Other Possible Causes**:
1. Branch name doesn't match pattern `{llm-name}/{agent}-{project}-{sessionID}`
2. GitHub Actions are disabled in repository settings
3. `LLM_API_KEY` repository secret is not configured

### Reviewers Not Assigned

**Symptom**: Labels and comment created, but reviewers not assigned

**Explanation**: GitHub does not support auto-assigning reviewers via Actions when using GITHUB_TOKEN. Reviewers are notified via the comment instead.

**Workaround**:
1. Use the comment to know who should review
2. Manually request reviews if needed
3. Reviewers can navigate to PR and submit reviews

### Labels Not Applied

**Symptom**: Comment created but labels missing

**Possible Cause**: Labels don't exist in the repository

**Solution**:
1. Create labels manually (see section 7)
2. Re-run workflow: Comment `/rerun` on PR (if configured)
3. Manually add labels

### Wrong Agent Detected

**Symptom**: Wrong reviewers assigned (e.g., Developer PR assigned Tester reviewers)

**Possible Cause**: Branch name pattern is incorrect

**Solution**:
1. Check branch name: `git branch --show-current`
2. Ensure format is `agent/{agent}-{project}-{sessionID}`
3. Agent must be: developer, architect, tester, it, or product-owner
4. Recreate branch with correct name if needed

### Workflow Permission Errors

**Symptom**: Workflow fails with permission denied errors

**Possible Cause**: GITHUB_TOKEN lacks permissions

**Solution**:
1. Verify workflow has `pull-requests: write` and `issues: write` permissions
2. Check repository settings: Settings → Actions → General → Workflow permissions
3. Ensure "Read and write permissions" is enabled

---

## Appendix: Example Workflow Execution

### Scenario: Developer Creates PR for BigModuleA Implementation

1. **Developer completes work** in `/home/user/worktree-developer`
2. **Developer commits and pushes**: `git push -u origin agent/developer-rtdcs-pbCFa`
3. **Developer creates PR** via GitHub API or web interface:
   - Title: "BigModuleA: Implement ThermalMonitor with Unit Tests"
   - Base: `master`
   - Head: `agent/developer-rtdcs-pbCFa`

4. **User triggers the review workflow** from the Actions tab:
   - Goes to Actions > "Automated Multi-Agent Peer Review" > "Run workflow"
   - Enters PR number and clicks the green button
   - Workflow detects agent type: `developer`
   - Applies labels: `peer-review:developer`, `awaiting-architect-review`, `awaiting-tester-review`
   - Runs LLM-powered reviews sequentially

5. **Review comments posted on PR** (Architect, Tester)

6. **Architect reviews first**:
   - Checks design adherence to `rtdcs-modulea-eds.md`
   - Validates Strategy pattern for temperature patterns
   - Validates Singleton pattern for SharedMemoryManager
   - Verifies SOLID principles
   - **Approves**: ✅

7. **Product Owner reviews**:
   - Checks overall code quality
   - Validates commit messages
   - Ensures documentation is updated
   - **Approves**: ✅

8. **Tester reviews**:
   - Checks unit test coverage (>80%)
   - Validates testability
   - Runs tests locally
   - **Approves**: ✅

9. **All peer approvals obtained** (3/3)

10. **User reviews** and **merges** PR

11. **Worktree cleaned up** by Product Owner

---

## Document Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-20 | IT Agent | Initial peer review workflow documentation |

---

**End of Peer Review Workflow Documentation**
