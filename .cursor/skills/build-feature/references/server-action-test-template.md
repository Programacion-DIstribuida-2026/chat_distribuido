# Server Action Testing Pattern

Test Server Actions by mocking `createClient`, asserting on the returned `ActionResult`, and verifying side effects.

## Setup

```typescript
import { vi, it, expect, describe, beforeEach } from "vitest";
import { createClient } from "@/shared/lib/supabase/server";
import { revalidatePath } from "next/cache";
import { makeChain, makeSupabaseMock } from "@/shared/test-utils/supabase-mock";
import { myAction } from "@/features/example/actions/my.action";

vi.mock("@/shared/lib/supabase/server", () => ({ createClient: vi.fn() }));
vi.mock("next/cache", () => ({ revalidatePath: vi.fn() }));

beforeEach(() => {
  vi.clearAllMocks();
});
```

## Unauthenticated case (required in every action test)

```typescript
it("returns error when user is not authenticated", async () => {
  // Arrange
  const { mockClient } = makeSupabaseMock({ user: null });
  vi.mocked(createClient).mockResolvedValue(mockClient as never);
  const formData = new FormData();

  // Act
  const result = await myAction(formData);

  // Assert
  expect(result).toEqual({ status: "error", message: "No autenticado" });
  expect(revalidatePath).not.toHaveBeenCalled();
});
```

## Happy path (insert example)

```typescript
it("returns success and revalidates on valid input", async () => {
  // Arrange
  const { mockClient, mockFrom } = makeSupabaseMock({ user: { id: "user-1" } });
  vi.mocked(createClient).mockResolvedValue(mockClient as never);
  mockFrom.mockReturnValue(makeChain({ error: null }));
  const formData = new FormData();
  formData.set("title", "My item");

  // Act
  const result = await myAction(formData);

  // Assert
  expect(result).toEqual({ status: "success", message: expect.any(String) });
  expect(revalidatePath).toHaveBeenCalledWith("/");
});
```

## DB error case

```typescript
it("returns error when db insert fails", async () => {
  // Arrange
  const { mockClient, mockFrom } = makeSupabaseMock({ user: { id: "user-1" } });
  vi.mocked(createClient).mockResolvedValue(mockClient as never);
  mockFrom.mockReturnValue(makeChain({ error: { message: "db error" } }));
  const formData = new FormData();
  formData.set("title", "My item");

  // Act
  const result = await myAction(formData);

  // Assert
  expect(result).toEqual({ status: "error", message: expect.any(String) });
  expect(revalidatePath).not.toHaveBeenCalled();
});
```

## Validation error case

```typescript
it("returns error when required field is missing", async () => {
  // Arrange
  const { mockClient } = makeSupabaseMock({ user: { id: "user-1" } });
  vi.mocked(createClient).mockResolvedValue(mockClient as never);
  const formData = new FormData(); // no fields set

  // Act
  const result = await myAction(formData);

  // Assert
  expect(result).toEqual({ status: "error", message: expect.any(String) });
});
```

## Key Rules

- Always import `makeChain` and `makeSupabaseMock` from `@/shared/test-utils/supabase-mock`
- Every action test must cover: unauthenticated, validation error, DB error, happy path
- `mockFrom` returns a chain — each chained method (`.select()`, `.insert()`, etc.) returns the same chain object
- `then` on the chain resolves with the value you pass to `makeChain()`
- Never use `mockReturnThis()` — it does not match Supabase's actual chaining API
