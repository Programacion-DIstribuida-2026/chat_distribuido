---
name: build-feature
description: Plan and implement a new feature following TDD — tech-lead planning, backend + frontend in parallel, review gate, and memory sync. Run in a fresh conversation after /discover-feature. Triggers: 'build feature', 'implement feature', 'start building', 'build from requirements'. NOT for: bug fixes, refactors, or API-only routes (use /create-api-route).
---

# Build Feature Skill

> **Invoke as:** `/build-feature @.requirements/<feature-name>-<timestamp>.md`
> Run in **Agent mode** in a **fresh conversation** (not the same one where you ran `/discover-feature`).

## IMPORTANT: Fresh Conversation Required

If this conversation already contains requirements gathering, **start a new conversation** first. Reusing the same context risks hitting the token limit mid-implementation.

If context usage exceeds 60% at any point, stop and tell the user to continue in a new conversation referencing the current step.

---

## Process

### 1. Read the Requirements

Read `.requirements/<feature-name>-<timestamp>.md`. Confirm the file exists and contains both a **Functional Task List** (with acceptance criteria) and a **Technical Task List** (with Parallel Execution Plan groups A/B/C) before proceeding.

- If no spec exists → tell the user to run `/discover-feature <description>` first
- If the file only has functional tasks (old format) → use the `technical-lead` subagent to produce the Technical Task List before continuing

### 2. Load Architecture Context via MCP Memory

Load project context with targeted queries (token-efficient):

1. Read `package.json` to get the project name (`<project-name>`)
2. `search_memory` with `tags: ["project:<project-name>", "domain:ui"]` — installed shadcn/ui components
3. `search_memory` with `tags: ["project:<project-name>", "domain:database"]` — existing schema
4. `search_memory` with `tags: ["project:<project-name>", "domain:features"]` — existing features and paths
5. `search_memory` with `tags: ["project:<project-name>", "domain:patterns"]` — canonical pattern references
6. `search_memory` with `tags: ["project:<project-name>", "domain:rules"]` — active lint/TS rules

**Fallback**: if memory service is unavailable or returns no results, read `.cursor/memory/architecture-snapshot.md` directly.

**Also read `eslint.config.ts` and `tsconfig.json`** to confirm active rules and compiler flags before writing any code.

**Dependency pre-flight:**
```bash
pnpm ls drizzle-orm   # Confirm installed version
pnpm typecheck        # Confirm baseline passes — fix pre-existing errors first
```

### 3. Planning (Tech Lead)

The requirements file already contains a Technical Task List with parallel execution groups produced during `/discover-feature`. The TL should:

1. **Read the Parallel Execution Plan** from the requirements file (Groups A/B/C + Review Gate)
2. **Verify against current codebase state** — confirm referenced patterns, schemas, and components still exist
3. **Identify reuse** from MCP memory:
   - Which canonical patterns to copy
   - Which shadcn components are already installed vs need installing
   - Which shared utilities apply (`formFieldText`, `firstZodIssueMessage`, etc.)
4. **Plan the test structure**:
   - One `describe` block per acceptance criterion
   - Which mocks are needed (`makeSupabaseMock`, HTTP mocks, etc.)
   - Which edge cases map to test cases from the Functional Task List
5. **Present a brief implementation summary to the user** and wait for approval before proceeding to Step 4.

> Summary: execution order (which groups run in parallel), which files will be created/modified, any risks or deviations from the plan.

### 4. Create Feature Structure

```
src/features/<feature-name>/
├── components/
├── actions/
├── queries/
├── hooks/
├── api/
├── lib/
└── __tests__/
```

### 5. Pre-Test Setup

Update `vitest.config.ts` to exclude files that cannot be meaningfully tested in jsdom:
- Drizzle schema file(s) (`src/shared/db/*.schema.ts`)
- Pure type-only files
- Portal/browser-API-dependent UI wrappers (e.g., `src/shared/components/ui/sonner.tsx`)

```typescript
// vitest.config.ts — add to coverage.exclude before writing tests
exclude: [
  "src/shared/db/*.schema.ts",
  "src/shared/components/ui/sonner.tsx",
]
```

### 6. TDD: RED Phase

Write ALL test files first — zero implementation code at this stage:
- `__tests__/<component>.test.tsx` — component tests
- `__tests__/use-<feature>.test.ts` — hook tests (if applicable)
- `__tests__/<action>.action.test.ts` — action tests (see `references/server-action-test-template.md`)
- `__tests__/<feature>.queries.test.ts` — query tests

Import mock helpers from `@/shared/test-utils/supabase-mock` — do not inline mock chains.

**Coverage guidance:** Threshold is 95% statements/functions/lines and 90% branches. Use `/* v8 ignore next */` for genuinely unreachable defensive branches.

**For standard CRUD features**: write tests and implementation per module (queries test+impl → actions test+impl → UI test+impl) instead of strict all-RED-then-all-GREEN.

**BLOCKING GATE — do not proceed until this passes:**
Run `pnpm test:unit` and paste the output. All new tests must **FAIL** (red). If any new test passes without implementation, the test is wrong — fix it before continuing.

### 7. TDD: GREEN Phase

Follow the **Parallel Execution Plan** from the requirements file:

- **Group A**: run first (foundation — schema, shared types, no dependencies)
- **Group B**: launch `backend` and `frontend` subagents **in parallel** after Group A completes
- **Group C**: run after Group B (integration, polish)

Typical assignment:

| backend handles | frontend handles |
|-----------------|-------------------|
| `actions/` | `components/` |
| `queries/` | `page.tsx` |
| `schema.ts` changes | shadcn component installs |
| RLS policies | Loading/empty states |

**Do NOT run intermediate verification between sub-tasks.** Complete all GREEN phase work, then run a single verification pass in Step 9.

**BLOCKING GATE — do not proceed until this passes:**
Run `pnpm test:unit` and paste the output. All tests must **PASS** (green).

### 8. Refactor

Clean up while keeping tests green.

### 9. Verify & Self-Check

Run all three **together** (single pass) and paste output:
```bash
pnpm test:coverage   # Must meet thresholds: 95% statements/functions/lines, 90% branches
pnpm lint            # Must pass with 0 warnings
pnpm typecheck       # Must pass with 0 errors
```

If issues are found, fix **all** of them, then run the full trio again once.

Before moving to the review gate, verify manually:
- [ ] No `any` types: `grep -r ": any" src/features/<feature>/`
- [ ] No `eslint-disable` comments
- [ ] All UI text in Spanish, all `it()`/`describe()` text in English
- [ ] No file over 200 lines
- [ ] No function over 20 lines
- [ ] AAA pattern (`// Arrange`, `// Act`, `// Assert`) in every test
- [ ] `ActionResult` returned from every Server Action mutation
- [ ] Toast feedback (`toast.success` / `toast.error`) for every mutation
- [ ] RLS policies written for every new table

### 10. Review Gate

Run @code-reviewer and @security-researcher **in parallel** on the changed files. Fix any findings before marking the feature complete.

This step is not optional. The feature is not done until both reviewers pass.

> **Note for time-critical work:** if the user explicitly says to skip the review gate, you may proceed — but flag the skipped step so it can be done as a follow-up.

### 11. Update Architecture Snapshot & MCP Memory

Update `.cursor/memory/architecture-snapshot.md`:
- Add new DB tables to the schema table
- Add new shadcn components to the installed list
- Add the new feature to the Existing Features table
- Add any new canonical pattern references that differ from existing ones

Then run `/memory sync` to persist all changes to MCP memory so future sessions load context efficiently.

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| MCP memory returns no results | Memory not synced yet | Run `/memory sync` first, then retry |
| Test passes without implementation (RED fails) | Test asserts on falsy/default values | Ensure the test expects a specific truthy result that only a real implementation can produce |
| `pnpm typecheck` fails on schema file | Schema imported in test without mock | Add the schema file to `coverage.exclude` in `vitest.config.ts` |
| Context exceeds 60% mid-build | Feature too large for one conversation | Stop, note the current step, start a new conversation referencing it |
| `lint-staged` blocks commit | ESLint warnings treated as errors | Fix all warnings; never use `eslint-disable` inline — fix the code |

---

## Guardrails
- NEVER start implementation before the user approves the plan (Step 3)
- NEVER start implementation before the RED gate is confirmed with actual test output
- Coverage threshold: 95% statements/functions/lines, 90% branches
- Follow `features/* → shared/*` dependency direction
- RLS is mandatory for every new table — not a post-step
- Write lint-compliant code from the start — read the Strict Rules Reference before the first line of code
