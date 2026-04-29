# Security Audit Steps

### 1. Dependency Audit
```bash
pnpm audit
```
Categorize findings by: Critical / High / Medium / Low

### 2. Secret Scan
Search for hardcoded secrets:
```bash
grep -r "sk_" src/ --include="*.ts"
grep -r "apiKey\s*=" src/ --include="*.ts"
grep -r "password\s*=" src/ --include="*.ts"
```
Check `.env.example` has no real values.

### 3. RLS Verification
For each table in `src/shared/db/*.schema.ts`:
- Confirm RLS is enabled in Supabase dashboard
- Confirm explicit policies exist

### 4. Auth Coverage
- Verify `proxy.ts` protects all non-public routes
- Check every `route.ts` in protected features has auth check
- Verify `app/(protected)/layout.tsx` has server-side auth check

### 5. Input Validation
- Every `route.ts` has Zod schema validation
- Every `.action.ts` has Zod schema validation

### 6. XSS Check
```bash
grep -r "dangerouslySetInnerHTML" src/ --include="*.tsx"
```

### 7. Security Headers
Verify in `next.config.ts`:
- `Content-Security-Policy`
- `Strict-Transport-Security`
- `X-Frame-Options`
