---
name: create-api-route
description: Create a new Next.js API route with Zod validation, auth check, and TDD tests. Use when adding API endpoints to a feature. Triggers: 'create API route', 'add endpoint', 'new route handler', 'API endpoint'. NOT for: Server Actions (those go in features/*/actions/).
---

# Create API Route Skill

## Process

### 1. Define Schema
```typescript
const requestSchema = z.object({ /* fields */ });
const responseSchema = z.object({ /* fields */ });
type RequestBody = z.infer<typeof requestSchema>;
```

### 2. Write Test First (TDD)
```typescript
describe("POST /api/my-route", () => {
  it("returns 400 on invalid input", async () => { ... });
  it("returns 401 when unauthenticated", async () => { ... });
  it("returns 200 with valid input", async () => { ... });
});
```

Run test — must FAIL (RED).

### 3. Implement Route
```typescript
// Determine runtime:
// - AI routes: export const runtime = "edge"
// - DB routes: no export (Node.js default)

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return Response.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json() as unknown;
  const parsed = requestSchema.safeParse(body);
  if (!parsed.success) return Response.json({ error: "Invalid input" }, { status: 400 });

  // business logic...

  return Response.json(result);
}
```

### 4. Verify
```bash
pnpm test:unit
pnpm lint
pnpm typecheck
```

## Checklist
- [ ] Zod schema for request/response
- [ ] Auth check (unless public endpoint)
- [ ] Input validation
- [ ] Correct runtime (`edge` for AI, `nodejs` default for DB)
- [ ] Tests written BEFORE implementation
- [ ] ≥95% statement/function/line coverage, ≥90% branch coverage
