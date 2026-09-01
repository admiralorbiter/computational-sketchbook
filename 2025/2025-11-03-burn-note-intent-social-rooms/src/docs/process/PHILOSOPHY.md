# Development Philosophy & Principles

**Purpose:** Guide AI agents and developers on the "why" behind decisions, not just the "what".

---

## Core Principles

### 1. Privacy-First Mindset (Even in MVP)
- **Even though MVP uses plaintext:** Always think about the migration path to E2E
- **Don't store intents:** Never persist raw user intents; they stay client-side
- **Minimize metadata:** Only collect what's absolutely necessary
- **Short retention:** Design for ephemerality; default to short TTLs
- **Document privacy implications:** Every feature should note privacy impact

### 2. Anonymous by Design
- **No stable identifiers:** Session masks are ephemeral per room
- **Burn Session is real:** Users can truly leave without trace
- **Operator-blind where possible:** Server sees minimal, even in MVP
- **Future-proof for E2E:** Structure code so E2E migration is straightforward

### 3. Fast, Clear, Simple
- **Performance matters:** Join latency is a core feature (≤2s P50)
- **Clear error messages:** Users need to understand what went wrong
- **Progressive disclosure:** Simple entry, power features appear when needed
- **No over-engineering:** MVP means MVP - don't build for scale we don't have yet

### 4. Safety & Civility
- **Safety is non-negotiable:** Reporting, moderation, slow-mode are core features
- **Design for abuse prevention:** Assume bad actors will try to game the system
- **Civility surfaces:** Make it easy to be kind, hard to be harmful
- **Transparency:** Users should understand safety measures

---

## Code Quality Principles

### Simplicity Over Cleverness
- **Readable > Clever:** Code is read more than written
- **Explicit > Implicit:** Make dependencies and side effects clear
- **Fail fast:** Validate early, return clear errors
- **No magic:** If it's not obvious, document it

### Rust-Specific
- **Use the type system:** Let the compiler catch errors
- **Prefer composition:** Build small, testable pieces
- **Error handling:** Use `Result` and `Option` explicitly; don't panic in production paths
- **Async clarity:** Make async boundaries clear; document why things are async

### Testing Philosophy
- **Test behavior, not implementation:** Test what users/callers care about
- **Unit tests for logic:** Core domain logic should be well-tested
- **Integration tests for APIs:** Test the happy path + key error cases
- **Performance tests for critical paths:** Join flow, message fan-out

---

## Decision-Making Framework

### When to Ask vs. Decide

**Ask (create issue, get approval):**
- Breaking API changes (beyond MVP contracts)
- New dependencies (especially large ones)
- Architecture changes (new services, major refactors)
- Privacy/security trade-offs
- Features outside MVP scope

**Decide (make the call, document in ADR if significant):**
- Implementation details within defined contracts
- Code organization and structure
- Error message wording (within guidelines)
- Testing approach
- Performance optimizations
- Documentation improvements

**Document (ADR required):**
- Architectural decisions that constrain future choices
- Technology choices (e.g., database, message queue)
- API design decisions beyond contracts
- Security/privacy trade-offs

---

## Documentation Standards

### What to Document
- **Why, not just what:** Explain decisions and trade-offs
- **API behavior:** What happens in edge cases? What are the error codes?
- **Privacy implications:** How does this affect user privacy?
- **Performance characteristics:** Is this on the critical path?

### What NOT to Document
- **Obvious code:** If the code is self-explanatory, don't add noise
- **Implementation details that change:** Focus on contracts and behavior
- **Duplicate information:** Link to existing docs, don't repeat

### Documentation Format
- **Context first:** Why does this exist?
- **Then decisions:** What choices were made?
- **Finally checklist:** What needs to be done?

---

## Error Handling Philosophy

### User-Facing Errors
- **Be helpful:** "Room is full" > "Error 409"
- **Suggest alternatives:** "Room is full. Try: [alternatives]"
- **Don't blame users:** "Couldn't connect" > "Your connection failed"

### Internal Errors
- **Log with context:** Include correlation IDs, request IDs
- **Don't expose internals:** Don't leak stack traces to users
- **Fail gracefully:** Partial failures should degrade, not crash

### Error Codes
- **Use standard HTTP codes:** 400/401/403/404/409/422/429/500
- **Be consistent:** Same error type = same code
- **Document edge cases:** What happens if X fails during Y?

---

## Security Mindset

### Assume the Worst
- **Users will try to abuse:** Rate limits, validation, moderation
- **Attacks will happen:** Design defensively
- **Servers can be compromised:** Even in MVP, minimize what's exposed

### Defense in Depth
- **Multiple layers:** Rate limits + validation + moderation
- **Fail secure:** If unsure, block rather than allow
- **Audit logs:** Track suspicious patterns (even if not actionable yet)

### Privacy by Design
- **Minimize collection:** Don't store what you don't need
- **Short retention:** Default to ephemeral, extend only when needed
- **Clear boundaries:** What stays client-side? What goes to server?

---

## Performance Principles

### Critical Paths
- **Join flow:** Must be fast (≤2s P50)
- **Message send:** Should feel instant (optimistic UI)
- **Message pull:** Should be responsive (long-poll, not frequent polling)

### Optimization Strategy
- **Measure first:** Don't optimize without data
- **Profile, don't guess:** Use tools to find bottlenecks
- **Cache wisely:** Client-side caching for Atlas, room state
- **Batch operations:** Group database writes when possible

### Scalability (Future)
- **Design for scale:** Even if MVP doesn't need it, don't make it impossible
- **Horizontal scaling:** Stateless services, shardable data
- **Async where possible:** Don't block on I/O

---

## Testing Philosophy

### What to Test
- **Happy paths:** Core user flows work
- **Error cases:** Graceful failure handling
- **Edge cases:** Boundary conditions, empty states
- **Security:** Input validation, rate limits, authorization

### What NOT to Test (Yet)
- **UI polish:** MVP focuses on functionality
- **Performance:** Separate performance tests, not in unit tests
- **Integration with external services:** Mock for MVP

### Test Quality
- **Fast tests:** Unit tests should be fast
- **Deterministic:** No flaky tests
- **Clear failures:** Test names should explain what failed

---

## Code Review Checklist (For Agents)

When submitting code, ensure:
- [ ] Privacy implications considered
- [ ] Error handling is clear and helpful
- [ ] Tests cover happy path + key error cases
- [ ] Documentation updated if API/behavior changed
- [ ] Follows Rust conventions (fmt, clippy)
- [ ] Performance impact considered (if on critical path)
- [ ] Security implications reviewed (rate limits, validation)

---

## Migration Path Thinking

Even in MVP, structure code for:
- **E2E migration:** Separate encryption logic from business logic
- **Scale:** Don't assume single server forever
- **Privacy upgrades:** OHTTP, blind tokens, TEE enclaves

---

## Questions to Ask Yourself

Before implementing:
- "Does this expose more data than necessary?"
- "Can this fail gracefully?"
- "Is this fast enough for the critical path?"
- "Will this be hard to migrate to E2E?"
- "What if a bad actor tries to abuse this?"
- "Is this documented clearly enough?"

---

## Remember

- **MVP means MVP:** Ship fast, but don't cut corners on privacy/safety
- **Users are real people:** Even anonymous users deserve respect
- **Code is communication:** Write for the next agent (or yourself in 6 months)
- **Privacy is a feature:** Not an afterthought

