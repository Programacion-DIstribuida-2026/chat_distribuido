# Review Checklist

## Code Quality
- Zero `any` types
- Zero comments (excluding test AAA labels: `// Arrange`, `// Act`, `// Assert`)
- Functions ≤ 20 lines
- Files ≤ 200 lines
- No magic numbers/strings
- Proper error handling

## Tests
- Tests written BEFORE implementation (TDD)
- ≥95% statement/function/line coverage on new/changed files
- ≥90% branch coverage (every if/else/ternary/catch)
- Behavior tested, not implementation
- AAA pattern with labeled comments on every test
- Tests NOT weakened (no removed assertions, no loosened matchers, no .skip)
- Edge cases covered: null, empty, boundaries, errors, auth expired

## Architecture
- Correct layer (features → shared only)
- Server Actions for mutations (not TanStack)
- Edge runtime on AI routes

## Security
- Input validation at boundaries
- Auth checks in protected routes
- No exposed secrets

## Performance
- No N+1 query patterns
- No unnecessary re-renders

## Accessibility
- Semantic HTML
- ARIA labels where needed
