# Mistakes & Fixes

What went wrong and how it was fixed, organized by agent. Maximum 10 entries per agent — consolidate similar entries into broader rules when the limit is reached.

**Format**: Each entry has a date, what went wrong, and the fix.

---

## IT Agent

### 2026-02-16
**Mistake**: PR creation failed with "could not determine repo" error.
**Fix**: Always run `gh repo set-default OWNER/REPO` before creating PRs. The setup wizard now does this automatically after fork-clone, but verify with `gh repo set-default --view`.

### 2026-02-16
**Mistake**: Fork didn't have the template branch, causing clone to fail.
**Fix**: Use 3-strategy approach: direct clone → sync fork + retry → clone original + fix remotes.

### 2026-03-08
**Mistake**: Used `npm --prefix` with a relative path and npm resolved to a duplicated path, causing ENOENT for package.json.
**Fix**: Run `npm install` from the module root with `cd` to ensure correct workspace resolution.

### 2026-03-08
**Mistake**: Terminal got stuck in a dangling quote after a command, causing `dquote>` prompts and blocking subsequent commands.
**Fix**: Use a fresh background terminal session for the next command (or close the quote with a standalone `"`), then continue in the clean session.

### 2026-03-08
**Mistake**: Committed IT setup changes on the task branch instead of the IT agent branch.
**Fix**: Create the IT agent branch from the current commit and push that branch; avoid pushing the task branch directly.
---

## Product Owner

### 2026-03-08
**Mistake**: Attempted to push agent branch without an upstream tracking branch.
**Fix**: Push with `git push --set-upstream origin <branch>` to set the upstream.

---

## Cost Analyst

<!-- No entries yet -->

---

## Architect

<!-- No entries yet -->

---

## Developer

### 2026-03-08
**Mistake**: Test file accidentally included a patch marker line, breaking the test runner.
**Fix**: Remove the stray marker and re-run tests.

---

## Tester

<!-- No entries yet -->


---

## All Agents
**Mistake**: Ran through all 9 workflow steps without asking user for handover approval between steps, despite no 'skip-confirmation user preference' being set.
**Fix**: Always stop after each step's deliverables (code and documentation with files created in respective filepath location) and output the handover question. Do not generate the next agent's output in the same response.
