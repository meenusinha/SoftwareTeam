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
