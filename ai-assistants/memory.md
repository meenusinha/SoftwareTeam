# Agent Memory

This is the shared memory system for all agents across all providers. It persists across sessions and tool switches.

**Every agent MUST read this file before starting any step.**

---

## Override Hierarchy

When instructions conflict, follow this priority order:

1. **User Preferences** (highest priority — always override everything else)
2. **Provider file instructions** (default behavior when no user preference exists)
3. **Agent file instructions** (role-specific defaults)

If a user has expressed a preference (stored in [`memory/user-preferences.md`](./memory/user-preferences.md)), that preference takes priority over any instruction in the provider or agent files — even instructions marked as MANDATORY. Mandatory instructions define the **default** behavior; user preferences define **overrides**. 

---

  ## Standing Rule: Handover Confirmation

  Before handing off to the next agent, ALWAYS check [`memory/user-preferences.md`](./memory/user-preferences.md).
  - If a "skip handover confirmation" preference exists → hand over directly
  - If no such preference exists → STOP and ask the user the mandatory handover question ("Would you like me to create a PR for review, or should I hand over to next Agent"?).
  A single "yes" or "hand over" or "continue" or similar response does NOT create a preference.
  Only an entry in user-preferences.md does.

---

## Memory Files

| File | Purpose | When to Read | When to Write |
|------|---------|-------------|---------------|
| [`user-preferences.md`](./memory/user-preferences.md) | Behavioral overrides from the user | Before every step | When the user expresses a preference |
| [`project-decisions.md`](./memory/project-decisions.md) | Tech stack, architecture, conventions | Before design/implementation steps | When a project decision is made |
| [`mistakes-and-fixes.md`](./memory/mistakes-and-fixes.md) | What went wrong and how it was fixed | Before every step (your section) | When a mistake is corrected |

---

## Rules

### Reading
- Always read [`user-preferences.md`](./memory/user-preferences.md) before starting any step
- Read [`project-decisions.md`](./memory/project-decisions.md) before Steps 4, 5, 6, 7 (design, setup, implementation, testing)
- Read your agent section in [`mistakes-and-fixes.md`](./memory/mistakes-and-fixes.md) before starting your step

### Writing
- **User preferences**: When the user says something like "don't ask me about X", "always do Y", "I prefer Z" — save it immediately. Never delay writing a user preference.
- **Project decisions**: When a decision is made about tech stack, architecture, conventions, testing approach — save it. Other agents will need it.
- **Mistakes & fixes**: When something goes wrong and you fix it, document what happened and how you fixed it. Keep entries concise.

### Consolidation
- [`user-preferences.md`](./memory/user-preferences.md): No limit. Never delete entries — only the user can remove preferences.
- [`project-decisions.md`](./memory/project-decisions.md): No limit. Update existing entries when decisions change.
- [`mistakes-and-fixes.md`](./memory/mistakes-and-fixes.md): Maximum 10 entries per agent. When you hit the limit, consolidate similar entries into broader rules before adding new ones.

### MANDATORY Provider-Agnostic
- Never use tool-specific language in memory files (no "Cursor", "Claude", "Copilot", etc.)
- Write entries so any agent from any provider can understand them
