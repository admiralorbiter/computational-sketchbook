# Test Status & Testing Guidelines

**Purpose:** Document what tests exist, what needs testing, and important testing guidelines for agents.

---

## ⚠️ IMPORTANT: DO NOT RUN `cargo test`

**Agents should NEVER run `cargo test` during development.**

### Why?
- Tests can get stuck or hang in certain environments
- Tests are verified to exist and be properly structured instead
- Manual verification is done by users/humans, not agents

### What to do instead:
1. **Verify tests exist** - Check that `#[cfg(test)]` modules exist in repository files
2. **Verify test structure** - Ensure tests follow the expected patterns (setup, assertions, cleanup)
3. **Verify test coverage** - Check that all public functions have corresponding tests
4. **Document test status** - Update this file if new tests are added or test coverage changes

---

## Current Test Coverage

### ✅ Storage Layer (`crates/storage/src/`)

#### RoomRepository (`crates/storage/src/rooms.rs`)
- ✅ `test_create_room` - Verifies room creation with valid input
- ✅ `test_get_room` - Verifies room retrieval by ID
- ✅ `test_get_nonexistent_room` - Verifies None returned for non-existent room
- ✅ `test_list_rooms` - Verifies listing multiple rooms

**Coverage:** All public methods (`create_room`, `get_room`, `list_rooms`) have tests

#### MessageRepository (`crates/storage/src/messages.rs`)
- ✅ `test_create_message` - Verifies message creation
- ✅ `test_get_messages` - Verifies message retrieval with multiple messages
- ✅ `test_get_messages_with_limit` - Verifies pagination limit works
- ✅ `test_get_messages_with_after` - Verifies pagination with `after` parameter

**Coverage:** All public methods (`create_message`, `get_messages`, `get_recent_messages`) have tests

#### SessionRepository (`crates/storage/src/sessions.rs`)
- ✅ `test_create_session` - Verifies session creation
- ✅ `test_get_session` - Verifies session retrieval by ID
- ✅ `test_get_nonexistent_session` - Verifies None returned for non-existent session
- ✅ `test_get_session_by_mask` - Verifies session retrieval by room_id and mask
- ✅ `test_delete_session` - Verifies session deletion
- ✅ `test_expire_sessions` - Verifies expired session cleanup (if exists)

**Coverage:** All public methods have tests

### ❌ API Handlers (`apps/web/src/handlers/`)
**Status:** No unit tests yet (integration tests planned for future)

### ❌ Domain Models (`crates/core/src/`)
**Status:** Validation logic is tested indirectly through repository tests. Unit tests for validation logic could be added.

---

## Test Patterns

### Repository Test Pattern
All repository tests follow this pattern:
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    // Helper to run async tests
    fn run_async_test<F>(f: F) where F: std::future::Future<Output = ()> {
        tokio::runtime::Runtime::new().unwrap().block_on(f);
    }
    
    // Setup in-memory SQLite database
    async fn setup_test_db() -> SqlitePool {
        // ... schema initialization
    }
    
    #[test]
    fn test_<function_name>() {
        run_async_test(async {
            let pool = setup_test_db().await;
            // ... test logic
        });
    }
}
```

### What Tests Verify
1. **Happy paths** - Core functionality works as expected
2. **Edge cases** - None values, empty inputs, boundary conditions
3. **Error cases** - Invalid input handling (where applicable)
4. **Data integrity** - Created data matches retrieved data

---

## What Needs Testing (Future)

### High Priority
- [ ] API handler integration tests (`apps/web/src/handlers/`)
  - Test happy paths for all endpoints
  - Test error responses (400, 404, 500)
  - Test input validation

### Medium Priority
- [ ] Domain model validation tests (`crates/core/src/`)
  - Test `Message::validate()` with various inputs
  - Test `Room::validate()` with various inputs
  - Test `UserSession` creation and expiration logic

### Low Priority
- [ ] Performance tests for message pagination
- [ ] Load tests for concurrent room joins
- [ ] Database migration tests

---

## Testing Guidelines for Agents

### When Adding New Code

1. **Repository methods** → MUST add unit tests
   - Follow existing test patterns
   - Test happy path + edge cases
   - Use in-memory SQLite for isolation

2. **API handlers** → SHOULD add integration tests
   - Test HTTP status codes
   - Test response shapes
   - Test error handling

3. **Domain logic** → SHOULD add unit tests
   - Test validation logic
   - Test business rules
   - Test error conditions

### When Verifying Tests (Agents)

1. **Check that tests exist** - Look for `#[cfg(test)]` modules
2. **Check test structure** - Ensure tests follow patterns
3. **Check coverage** - All public functions should have tests
4. **DO NOT run tests** - Just verify they exist and are structured correctly

### Test Quality Checklist

When reviewing tests (not running them), verify:
- [ ] Test names clearly describe what they test
- [ ] Tests are isolated (use in-memory DB, no shared state)
- [ ] Tests cover happy path + edge cases
- [ ] Tests use proper setup/teardown patterns
- [ ] Assertions are clear and meaningful

---

## Manual Testing (For Users/Humans)

When manually testing the application:

### API Endpoints
- `GET /v1/rooms` - List all rooms
- `POST /v1/rooms/:id/join` - Join a room
- `GET /v1/messages?room_id=...` - Get messages
- `POST /v1/messages` - Create a message

### Test Scenarios
1. Create and retrieve rooms
2. Join room and create session
3. Send messages and verify they appear
4. Test pagination (limit, after parameters)
5. Test error cases (invalid room_id, empty body, etc.)

### Manual Test Commands
```bash
# Start server
cargo run -p web

# In another terminal, test endpoints
curl http://localhost:8080/v1/rooms
curl -X POST http://localhost:8080/v1/rooms/<room_id>/join -H "Content-Type: application/json" -d '{"ttl_hours": 24}'
curl "http://localhost:8080/v1/messages?room_id=<room_id>"
```

---

## Notes

- **Test Database:** All repository tests use in-memory SQLite (`sqlite::memory:`) for isolation
- **Async Tests:** Tests use a custom `run_async_test` helper instead of `#[tokio::test]` to avoid conflicts with the `core` crate name
- **Schema Setup:** Each test sets up its own database schema from `schema.sql`
- **No Mocks:** Tests use real SQLite database (in-memory) for realistic testing

---

## Last Updated
2025-11-04 - Initial test status documentation
