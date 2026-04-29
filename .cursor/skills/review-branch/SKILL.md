---
name: review-branch
description: Review current branch changes against develop — runs full code quality, testing, architecture, and security checklist. Triggers: 'review branch', 'review my changes', 'check branch quality', 'review PR'.
disable-model-invocation: true
---

# Review Branch Skill

## Process

### 1. Get Changes
```bash
git diff develop...HEAD
```
Or for a specific branch:
```bash
git diff develop...<branch-name>
```

### 2. Check Each Changed File
Apply the full checklist from `references/review-checklist.md` — covers code quality, tests, architecture, security, performance, and accessibility.

**You MUST check every changed file individually. Do not summarize or skip files. Show your analysis for each file before moving to the next.**

### 3. Generate Report
```
## Branch Review: <branch-name>

### Changed Files
- [list each file]

### Issues Found
- [file:line]: [issue] → [fix]

### Verdict: PASS / FAIL
```

### 4. Run Automated Checks
```bash
pnpm lint
pnpm typecheck
pnpm test:coverage
```
