# Dev Setup and Workflow

## 1. Development Stack

- Rust toolchain
- Cargo
- macroquad
- rust-analyzer in the IDE of choice
- Git

Optional but recommended:
- `cargo fmt`
- `cargo clippy`
- `cargo test`
- optional simple task runner or shell aliases

## 2. Working Style

This project should be developed in a highly iterative way:

- small slice
- runnable state
- verify behavior
- add tool support
- only then expand

Do not let the main branch drift into a non-runnable state for long.

## 3. Suggested Repo Layout

```text
.
├── README.md
├── docs/
├── assets/
├── src/
├── tests/
└── Cargo.toml
```

## 4. Coding Practices

### Prefer plain, explicit code
This project benefits from readability more than abstraction cleverness.

### Keep sim code pure where possible
The more the core math stays separate from input and rendering, the easier it is to test.

### Minimize hidden state
State transitions and stage activations should be easy to inspect.

### Log important events
If an action matters to the player, it probably matters to the debug log too.

## 5. Branching / Checkpoint Advice

Reasonable checkpoints:
- foundation running
- flight toy works
- data-driven parts work
- builder works
- orbit works
- mission loop works

Each checkpoint should compile, run, and pass smoke checks.

## 6. Recommended Daily Loop

1. pick one narrow task
2. implement it in the smallest useful way
3. run and test it manually
4. add or improve debug visibility if needed
5. commit once the state is stable

## 7. Definition of Done for a Feature

A feature is done when:
- it is runnable
- it is understandable in the UI
- it has at least basic test coverage or a smoke test path
- it does not obviously break a core flow
- it includes enough debug output to troubleshoot later

## 8. Style Guidance for a Solo Project

- prefer consistency over perfection
- document assumptions near the code when math gets tricky
- avoid premature engine-like abstractions
- keep data files easy to inspect manually

## 9. Suggested Early Commands

Typical cycle:

```bash
cargo run
cargo test
cargo fmt
cargo clippy
```

## 10. Documentation Maintenance

Keep the docs alive by updating them when:
- scope changes
- physics simplifications change
- major systems are added or removed
- a roadmap phase is completed

The roadmap and open questions docs should be the most frequently updated.
