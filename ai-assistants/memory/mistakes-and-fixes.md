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
---

## Product Owner

<!-- No entries yet -->

---

## Cost Analyst

<!-- No entries yet -->

---

## Architect

<!-- No entries yet -->

---

## Developer

<!-- No entries yet -->

---

## Tester

<!-- No entries yet -->
