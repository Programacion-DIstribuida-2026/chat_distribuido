---
name: discover-feature
description: Run the BA+TL requirements discovery process for a new feature. BA asks questions, then collaborates with Technical Lead to produce a combined plan (Functional Tasks + Technical Tasks) in .requirements/<feature-name>-<timestamp>.md. Use this in Conversation 1, then start a new conversation and run /build-feature. Triggers: 'new feature', 'define requirements', 'discover feature', 'I want to build'. NOT for: already-defined features (use /build-feature directly).
user-invocable: true
---

# Discover Feature Skill

> **Invoke as:** `/discover-feature <feature-description>`
> Run in **Agent mode**. After this skill completes, **start a new conversation** before running `/build-feature`.

## IMPORTANT: Token Budget

This conversation is for requirements only. Do NOT start implementation here. When done, start a fresh conversation to keep the implementation context clean.

---

## Process

### Step 1 — Load Existing Features via MCP Memory

1. Read `package.json` → get `<project-name>`
2. Call `search_memory` with `tags: ["project:<project-name>", "domain:features"]` to understand existing features
3. **Fallback**: if memory service is unavailable, read `.cursor/memory/architecture-snapshot.md` → "Existing Features" section

---

### Step 2 — Discovery Questions (BA role)

Ask ALL of the following before writing anything. Cover at minimum questions 1–3 + any relevant ones from 4–8.

1. **Problem & audience** — "What problem does this solve? Who experiences it?"
2. **User flows** — "Walk me through the happy path. What happens on error?"
3. **Edge cases & constraints** — "What are the limits? What should NOT happen?"
4. **Field constraints** — "Length limits, allowed formats, required vs optional fields?"
5. **Volume & scale** — "How many records? Do you need search or pagination?"
6. **File/upload specifics** — (if applicable) "What file types and size limits are allowed?"
7. **Privacy & access** — "Who can see this data? Per-user or shared?"
8. **Relationship to existing features** — (informed by MCP results) "Does this link to existing data?"
9. **Confirm understanding** — Restate what you heard and ask for explicit approval

If the user says "just do it" without answering, document all assumptions in an `## Assumptions` section.

Only after the user confirms your understanding should you proceed to Step 3.

---

### Step 3 — Write Draft Functional Spec (BA role)

```markdown
## Feature: [Feature Name]

### User Story
As a [user type], I want [goal] so that [reason].

### Acceptance Criteria
- [ ] AC1: When [user does X], they see [Y]
- [ ] AC2: When [error condition], user sees [message/state]
- [ ] AC3: [Edge case]: [expected outcome]

### Functional Test Cases
- [ ] TC1 (AC1): User does X → sees Y (happy path)
- [ ] TC2 (AC2): User triggers error → sees error message
- [ ] TC3 (AC3): Edge case behavior
```

**Rules:**
- Acceptance criteria in plain functional language — no code, no implementation details
- Test cases describe what the **user sees**, not system internals
- Every AC maps to at least one test case
- No database tables, API calls, component names, or file paths
- Write requirements in the user's language; IDs (`AC1`, `TC1`) and technical terms stay in English

---

### Step 4 — Technical Lead Complexity Assessment

With the draft spec ready, use the `technical-lead` subagent:

> technical-lead: please review the draft spec above and the codebase, then report back:
> 1. What existing patterns/components/schemas apply to this feature?
> 2. What is the implementation complexity (S/M/L) and why?
> 3. Are there any technical constraints or risks the spec should mention?
> 4. Break down the technical tasks needed, grouped into parallel execution groups (A runs first, B/C can run in parallel after A completes)

**Wait for TL's response. Do not proceed until TL has responded.**

After TL responds: if TL identifies missing requirements (e.g., edge cases not covered), go back to the user with targeted follow-up questions before writing the combined plan.

---

### Step 5 — Produce Combined Plan

Merge BA functional spec + TL technical breakdown into the final plan file.

**Filename**: `.requirements/{feature-name}-{YYYY-MM-DD-HHmm}.md`

```markdown
# Feature: [Feature Name]
> Created: {timestamp} | Status: ready-to-build

## Context
[One paragraph: what problem this solves, who it's for, why now]

## Assumptions
[List any assumptions made when user skipped discovery questions — empty if none]

---

## Functional Task List (BA-owned)

### User Story
As a [user type], I want [goal] so that [reason].

### Acceptance Criteria
- [ ] AC1: ...
- [ ] AC2: ...
- [ ] AC3: ...

### Functional Test Cases
- [ ] TC1 (AC1): ...
- [ ] TC2 (AC2): ...
- [ ] TC3 (AC3): ...

---

## Technical Task List (TL-owned)

### Complexity Assessment
[S/M/L with rationale from TL]

### Parallel Execution Plan

#### Group A — Foundation (runs first, no dependencies)
- [ ] A1: [task — assigned agent: backend/frontend]
- [ ] A2: [task — assigned agent: backend]

#### Group B — Feature Logic (runs after Group A, backend+frontend in parallel)
- [ ] B1: [task — assigned agent: backend]
- [ ] B2: [task — assigned agent: frontend]

#### Group C — Integration & Polish (runs after Group B)
- [ ] C1: [task — assigned agent: test-qa]
- [ ] C2: [task — assigned agent: frontend]

### Review Gate (runs after all groups complete, in parallel)
- [ ] R1: code-reviewer — full diff review
- [ ] R2: security-researcher — auth, RLS, input validation

### Architecture Sync
- [ ] Update `.cursor/memory/architecture-snapshot.md` (new tables, components, features)
- [ ] Run `/memory sync`
```

---

### Step 6 — Store Requirement in MCP Memory

```
store_memory({
  content: "Requirement: <feature-name> — <one-line summary of what the feature does and key ACs>",
  metadata: {
    type: "architecture",
    tags: ["project:<project-name>", "domain:features", "category:requirement", "feature:<feature-name>", "status:pending-snapshot"]
  }
})
```

---

### Step 7 — Hand Off

Tell the user:

> Combined plan written to `.requirements/<feature-name>-<timestamp>.md`.
>
> **Next step**: Start a **fresh conversation** and run:
> ```
> /build-feature @.requirements/<feature-name>-<timestamp>.md
> ```

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| User says "just do it" without answering | Wants to skip discovery | Document all assumptions in `## Assumptions` section |
| MCP memory unavailable | Service not running | Fall back to reading `.cursor/memory/architecture-snapshot.md` directly |
| TL finds missing edge cases | Spec incomplete | Go back to user with targeted follow-up questions |
| Feature overlaps with existing one | Missed relationship check in Step 1 | Re-query MCP with `domain:features`, clarify scope before writing spec |

---

## Guardrails
- Always ask questions before writing — never assume requirements
- Do NOT start any implementation in this conversation
- Do NOT produce Technical Tasks without TL input
- Document all assumptions explicitly if user skips questions
- Hand off to `/build-feature` in a fresh conversation — never chain them in the same conversation
