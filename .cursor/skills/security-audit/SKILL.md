---
name: security-audit
description: Run a full security audit on the codebase — checks OWASP Top 10, RLS policies, hardcoded secrets, auth coverage, input validation, XSS vectors, and security headers. Triggers: 'security audit', 'audit security', 'check vulnerabilities', 'scan for secrets', 'check RLS'.
disable-model-invocation: true
---

# Security Audit Skill

## Process

**You MUST execute every step below. Do not skip or summarize steps. Show your findings for each step before moving to the next.**

Execute all 7 audit steps from `references/audit-steps.md`:
1. Dependency audit (`pnpm audit`)
2. Secret scan (hardcoded keys)
3. RLS verification (all tables)
4. Auth coverage (routes + actions)
5. Input validation (Zod at boundaries)
6. XSS check (`dangerouslySetInnerHTML`)
7. Security headers (`next.config.ts`)

## Output Format
```
## Security Audit Report

### Critical 🔴
[findings]

### High 🟠
[findings]

### Medium 🟡
[findings]

### Low 🟢
[findings]

### Passed ✅
[clean checks]
```
