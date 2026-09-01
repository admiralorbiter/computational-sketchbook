# Contributing Guide

## Branch workflow
- Create a feature branch per task (e.g., `feature/add-edit-form`).
- Open pull requests early and keep them small.
- Request review from teammates; merge only after approval.

## Commit style
Use clear, present-tense messages:
```
feat(grade-calc): add weighted average function
fix(timer): correct DST boundary calculation
docs(ui): update responsive breakpoints
```

## Code review checklist
- Single-responsibility functions
- Clear names and comments (JSDoc on public functions)
- Input validation and error handling
- No console.log left behind; no dead code
- Accessibility considerations (labels, focus, color contrast)

See [Code Standards](CODE_STANDARDS.md).
