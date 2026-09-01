# Agent Guidelines & Best Practices

**Purpose:** Quick reference for AI agents working on this codebase.

---

## Quick Start Checklist

When starting work on this codebase:
1. ✅ Read `docs/work/AGENT_CONTEXT.md` for project overview
2. ✅ Check `docs/work/SPRINT_STATUS.md` for current state
3. ✅ **Read `docs/process/PHILOSOPHY.md`** - Understand the "why" behind decisions
4. ✅ **Read this guide (`docs/process/AGENT_GUIDELINES.md`)** - Understand the "how"
5. ✅ Read relevant API contracts in `docs/api/`
6. ✅ Check ADRs in `docs/adr/` for major decisions
7. ✅ Understand MVP constraints (plaintext, internal-only)

---

## Code Style & Conventions

### Rust
- Run `cargo fmt` before committing
- Run `cargo clippy --workspace -- -D warnings` and fix issues
- Use `Result<T, E>` for fallible operations
- Prefer `Option<T>` over `null`/`None` checks
- Use meaningful error types, not just `String`

### File Organization
- Domain logic in `crates/core`
- Storage logic in `crates/storage`
- API handlers in `apps/web/src/handlers/` (to be created)
- Shared types in `crates/core/src/types.rs` (to be created)

### Naming
- Use descriptive names: `room_id` not `rid`
- Async functions: suffix with `_async` if ambiguous
- Handlers: `handle_<resource>_<action>` (e.g., `handle_room_join`)

---

## Implementation Priorities

### Must Have (MVP)
- ✅ Room join/message send/pull
- ✅ Whisper handshake and messaging
- ✅ Rate limiting (token-based)
- ✅ Reporting flow
- ✅ Basic moderation actions

### Should Have (MVP)
- Room highlights
- Alternates panel (UX)
- Read-only 60s mode
- Slow-mode enforcement

### Nice to Have (Post-MVP)
- E2E encryption
- OHTTP relays
- Advanced matching features

---

## Common Patterns

### Error Handling
```rust
// Good: Specific error type
enum RoomError {
    NotFound,
    Full,
    RateLimited,
}

// Handler pattern
async fn handle_room_join(
    Path(room_id): Path<String>,
) -> Result<Json<JoinResponse>, ApiError> {
    // ...
}
```

### API Responses
- Use consistent response shapes (see `docs/api/standards.md`)
- Include correlation IDs for debugging
- Return appropriate HTTP status codes

### Logging
- Use structured logging (`tracing`)
- Don't log message bodies or intents
- Include correlation IDs for request tracing

---

## Testing Requirements

### ⚠️ CRITICAL: DO NOT RUN `cargo test`

**Agents must NEVER run `cargo test` during development.**

**Why?** Tests can hang or get stuck in automated environments. Instead, verify that:
1. Tests exist (look for `#[cfg(test)]` modules)
2. Tests follow proper patterns (see `docs/testing/TEST_STATUS.md`)
3. All public functions have corresponding tests

**See:** `docs/testing/TEST_STATUS.md` for full testing guidelines and current test coverage.

### Unit Tests
- Test core domain logic
- Test error cases
- Test edge cases (empty, null, boundaries)
- **Verification:** Check that `#[cfg(test)]` modules exist and follow patterns

### Integration Tests
- Test API endpoints (happy path + key errors)
- Test authentication/authorization
- Test rate limiting
- **Status:** Not yet implemented (see `docs/testing/TEST_STATUS.md`)

### What NOT to Test (Yet)
- UI rendering
- Performance (separate perf tests)
- Full E2E flows (MVP doesn't have E2E)

### When Adding Tests
- Follow existing patterns (see repository test examples)
- Use in-memory SQLite for repository tests
- DO NOT run tests to verify - just ensure they exist and are structured correctly

---

## Documentation Requirements

### When to Update Docs
- ✅ Adding new API endpoint → update `docs/api/`
- ✅ Changing behavior → update relevant spec
- ✅ Making architectural decision → create ADR
- ✅ Adding new feature → update PRD if scope change

### When NOT to Update Docs
- ❌ Internal refactoring (no behavior change)
- ❌ Bug fixes (unless behavior correction)
- ❌ Performance optimizations (unless API changes)

---

## Security Checklist

Before submitting code that handles user input:
- [ ] Input validation (size, format, content)
- [ ] Rate limiting considered
- [ ] Privacy implications documented
- [ ] No sensitive data in logs
- [ ] Error messages don't leak internals
- [ ] Authorization checks (if applicable)

---

## Privacy Checklist

Before storing or logging data:
- [ ] Is this data necessary?
- [ ] What's the retention policy?
- [ ] Can this identify users across sessions?
- [ ] Is this documented in privacy policy?
- [ ] Migration path to E2E considered?

---

## Performance Checklist

For code on critical paths (join, send, pull):
- [ ] Is this fast enough? (Profile if unsure)
- [ ] Are there unnecessary allocations?
- [ ] Are database queries efficient?
- [ ] Is there caching where appropriate?
- [ ] Are async operations properly awaited?

---

## Handoff Checklist

When handing off work:
- [ ] Update `docs/work/SPRINT_STATUS.md`
- [ ] Fill out `docs/work/HANDOFF_TEMPLATE.md`
- [ ] Add entry to `docs/work/CHANGELOG.md` if significant
- [ ] Document any new patterns or gotchas
- [ ] Note any blockers or questions

---

## Decision-Making Guide

### Can I decide this myself?
- ✅ Implementation details within contracts
- ✅ Code structure and organization
- ✅ Test approach
- ✅ Error message wording
- ✅ Documentation improvements

### Should I ask first?
- ❌ Breaking API changes
- ❌ New major dependencies
- ❌ Architecture changes
- ❌ Privacy/security trade-offs
- ❌ Features outside MVP scope

### Should I create an ADR?
- ✅ Architectural decisions
- ✅ Technology choices
- ✅ API design beyond contracts
- ✅ Security/privacy trade-offs

---

## Common Mistakes to Avoid

1. **Running `cargo test`** - ⚠️ NEVER run `cargo test` - verify tests exist instead
2. **Storing intents** - Never persist raw user intents
3. **Logging sensitive data** - Don't log message bodies
4. **Hardcoding** - Use config for limits, timeouts, etc.
5. **Ignoring errors** - Handle all error cases explicitly
6. **Over-engineering** - MVP means MVP; ship fast
7. **Forgetting privacy** - Always consider privacy implications
8. **Breaking changes** - Don't break existing contracts
9. **Missing tests** - Core logic needs tests (but don't run them!)

---

## Getting Unstuck

If blocked or unsure:
1. Check `docs/work/SPRINT_STATUS.md` for context
2. Review relevant ADRs in `docs/adr/`
3. Check API contracts in `docs/api/`
4. Review `docs/process/PHILOSOPHY.md` for principles
5. Look at existing code for patterns
6. Create an issue/ADR if decision needed

---

## Questions Format

When asking questions, include:
- What you're trying to accomplish
- What you've tried
- What the constraint/blocker is
- Relevant code/docs you've reviewed

---

## Remember

- **Privacy-first:** Even in MVP, think about E2E migration
- **Fast & clear:** Performance and UX matter
- **Safe by default:** Design for abuse prevention
- **Document decisions:** Future agents need context
- **Ship fast:** MVP means MVP, but don't cut corners on safety

