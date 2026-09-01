# Runbook — Local Development

## Prereqs
- Rust toolchain (stable)
- Windows PowerShell (repo assumes Windows dev), or any shell

## Commands
- Start API: `cargo run -p web`
- Start API with logs: `$env:RUST_LOG="info,axum=info"; cargo run -p web`
- Open in browser: `start http://localhost:8080/`
- Health: `curl http://localhost:8080/healthz`
- Watch mode: `cargo watch -x "run -p web"`
- Build all: `cargo build --workspace`
- Run CLI: `cargo run -p cli`
- Test: `cargo test --workspace` (⚠️ AGENTS: DO NOT run this - see `docs/testing/TEST_STATUS.md`)
- Format: `cargo fmt --all`
- Lint: `cargo clippy --workspace -- -D warnings`

## Troubleshooting

### Database Connection Issues
- **Problem:** "unable to open database file" (SQLite error code 14) on Windows
- **Solution:** The code uses `SqliteConnectOptions::filename()` which handles Windows paths correctly. If you see this error, check:
  - Database file location: Should be in current working directory (`burn_note.db`)
  - File permissions: Ensure write permissions in the directory
  - File locks: Close any SQLite clients that might have the file open
  - **Note:** The database is created in the directory where you run `cargo run -p web`, not in the project root

### Schema Execution Issues
- **Problem:** "no such table" errors even though database connects
- **Solution:** Check `crates/storage/src/lib.rs` `init()` method logs. The schema execution splits SQL statements by semicolons - ensure all statements are properly formatted and terminated.
- **Debug:** Look for "Executing schema statement" messages in console output to see which statements are running

### Port in Use
- **Problem:** "Address already in use" when starting server
- **Solution:** Change bind address in `apps/web/src/main.rs` or stop the existing process using port 8080

### Missing Components
- **Problem:** Compilation errors about missing Rust components
- **Solution:** Run `rustup component add rustfmt clippy`

### Static Files Not Loading
- **Problem:** HTML/CSS/JS files not loading from `/static/` route
- **Solution:** Ensure `apps/web/static/` directory exists and files are present. The server serves from this directory via `tower-http::ServeDir`.


