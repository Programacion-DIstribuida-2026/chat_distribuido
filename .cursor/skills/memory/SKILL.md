---
name: memory
description: Sync architecture-snapshot.md with MCP memory service and recall project knowledge semantically. Use when starting a new session, after completing a feature, or to search project context efficiently. Triggers: 'memory sync', 'memory recall', 'memory update', 'sync architecture', 'search project knowledge', 'what components are installed'.
---

# Memory Skill

> **Invoke as:** `/memory sync`, `/memory recall "query"`, `/memory update`

## Preflight Check

Before running any subcommand, verify the memory service is running:

```
retrieve_memory({ query: "test", n_results: 1 })
```

If this fails, tell the user: "Memory service is unavailable. Run `pip install mcp-memory-service` and ensure the `memory` binary is in PATH (check `.cursor/mcp.json`)."

---

## `/memory sync` — Snapshot → MCP

Parses `architecture-snapshot.md` into individual entries and stores each in MCP memory. Run this after scaffolding a new project or after `/memory update`.

### Steps

1. Read `package.json` — get `name` field as `<project-name>`
2. Read `.cursor/memory/architecture-snapshot.md`
3. For each section, parse into individual entries and call `store_memory`:

**Installed shadcn/ui Components** (one memory for the full list):
```
store_memory({
  content: "Installed shadcn/ui components: button, card, input, label, spinner",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:ui", "category:components"]
  }
})
```

**DB Schema** (one memory per table row):
```
store_memory({
  content: "DB table: profiles — columns: id (uuid PK), email (text unique), createdAt, updatedAt",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:database", "category:schema", "table:profiles"]
  }
})
```

**Existing Features** (one memory per feature row):
```
store_memory({
  content: "Feature: auth — path: src/features/auth/ — Login/logout, cookie-based sessions via Supabase",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:features", "category:feature", "feature:auth"]
  }
})
```

**Canonical Pattern References** (one memory per pattern row):
```
store_memory({
  content: "Canonical pattern: Server Action — file: src/features/todos/actions/todos.action.ts",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:patterns", "category:pattern", "pattern:server-action"]
  }
})
```

**Key Rules** (one memory per bullet):
```
store_memory({
  content: "Rule: Runtime queries use Supabase client only — Drizzle is schema/migrations only",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:rules", "category:rule"]
  }
})
```

**Shared Utilities** (one memory per utility row):
```
store_memory({
  content: "Utility: formFieldText(formData, key) — location: src/shared/lib/form-utils.ts — Safe FormData text extraction, avoids no-base-to-string lint error",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:shared", "category:utility"]
  }
})
```

**Strict Rules Reference** (one memory per `###` sub-heading group):
```
store_memory({
  content: "TypeScript strict rules: noUncheckedIndexedAccess (guard arr[i]), exactOptionalPropertyTypes (omit key instead of undefined), noImplicitReturns (explicit return in all branches), noUnusedLocals/noUnusedParameters (prefix unused with _), useUnknownInCatchVariables (narrow with instanceof Error)",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:rules", "category:lint-rule", "subcategory:typescript"]
  }
})
```

4. After all entries are stored, call:
```
trigger_consolidation({ time_horizon: "daily", immediate: true })
```

5. Report: "Stored N memories for project `<project-name>`. Consolidation triggered."

---

## `/memory recall "query"` — Semantic Search

Use to find project context without reading the full snapshot.

### Steps

1. Read `package.json` — get `<project-name>`
2. Call broad semantic search:
```
retrieve_memory({ query: "<user-query>", n_results: 10 })
```
3. If results are too broad, narrow with tags:
```
search_memory({
  query: "<user-query>",
  tags: ["project:<project-name>"],
  limit: 5,
  min_score: 0.6
})
```
4. Present results as a summary. If no results found, tell the user to run `/memory sync` first.

---

## `/memory update` — MCP → Snapshot

Merges new entries (tagged `status:pending-snapshot`) back into `architecture-snapshot.md`. Run after agents store new knowledge via `store_memory`.

### Steps

1. Read `package.json` — get `<project-name>`
2. Search for pending entries:
```
search_memory({
  query: "new pending architecture update",
  tags: ["project:<project-name>", "status:pending-snapshot"],
  limit: 50
})
```
3. For each result, determine the target section from the `domain` and `category` tags:
   - `domain:ui` → "Installed shadcn/ui Components"
   - `domain:database` → "DB Schema"
   - `domain:features` → "Existing Features"
   - `domain:patterns` → "Canonical Pattern References"
   - `domain:rules` + `category:rule` → "Key Rules"
   - `domain:shared` → "Shared Utilities"
4. Read `.cursor/memory/architecture-snapshot.md` and merge new entries into the correct sections
5. Write the updated snapshot
6. Re-store each processed memory WITHOUT the `status:pending-snapshot` tag:
```
store_memory({
  content: "<same content>",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:...", "category:..."]
    // pending-snapshot tag removed
  }
})
```
7. Call `trigger_consolidation({ time_horizon: "daily", immediate: true })`
8. Report: "Merged N entries into architecture-snapshot.md."

---

## Tag Schema Reference

All memories must include `type: "architecture"` and `project:<project-name>`. Use lowercase with hyphens for multi-word values.

| Snapshot Section | Required Tags | Optional Tags |
|---|---|---|
| shadcn Components | `domain:ui`, `category:components` | — |
| DB Schema | `domain:database`, `category:schema` | `table:<name>` |
| Existing Features | `domain:features`, `category:feature` | `feature:<name>` |
| Canonical Patterns | `domain:patterns`, `category:pattern` | `pattern:<type>` |
| Key Rules | `domain:rules`, `category:rule` | — |
| Shared Utilities | `domain:shared`, `category:utility` | — |
| Strict Rules (TS) | `domain:rules`, `category:lint-rule` | `subcategory:typescript` |
| Strict Rules (ESLint) | `domain:rules`, `category:lint-rule` | `subcategory:eslint` |

When storing **new** architecture knowledge (e.g., after `/build-feature`), add `status:pending-snapshot` so `/memory update` can sync it back.

---

## Guardrails

- NEVER store secrets, API keys, `.env` values, or credentials in memory
- ALWAYS scope memories with `project:<project-name>` to prevent cross-project pollution
- ALWAYS use `type: "architecture"` for snapshot-derived memories
- Keep individual memory content under 300 words for effective semantic retrieval
- The snapshot file (`.cursor/memory/architecture-snapshot.md`) is the source of truth — MCP memory is a search index
- If the memory service is unavailable, agents fall back to reading the snapshot file directly
