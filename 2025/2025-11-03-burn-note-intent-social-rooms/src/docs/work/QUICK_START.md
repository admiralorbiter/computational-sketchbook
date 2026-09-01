# Quick Start for AI Agents

**5-minute onboarding checklist** - Get productive fast

---

## Step 1: Read These (5 min)
1. **`docs/work/AGENT_CONTEXT.md`** - Project overview
2. **`docs/process/PHILOSOPHY.md`** - Core principles (skim the key sections)
3. **`docs/work/SPRINT_STATUS.md`** - What's happening now

---

## Step 2: Understand Your Task
- What sprint are you working on?
- What specific task/feature?
- Check `docs/work/SPRINT_STATUS.md` for context

---

## Step 3: Find Relevant Docs
- **API work?** → `docs/api/` (contracts defined)
- **New feature?** → `docs/product/` (PRD, UX specs)
- **Architecture?** → `docs/architecture/` (HLD, sequences)
- **Decision needed?** → `docs/adr/` (existing decisions)

---

## Step 4: Check Constraints
- **Privacy:** MVP uses plaintext (internal-only). See `docs/security/privacy_mvp_caveats.md`
- **Performance:** Join ≤2s P50. See `docs/observability/metrics.md`
- **API:** Follow `docs/api/standards.md`
- **No E2E yet:** Document migration path, don't implement

---

## Step 5: Start Working
- Follow `docs/process/AGENT_GUIDELINES.md` for patterns
- Update `docs/work/SPRINT_STATUS.md` as you progress
- Create handoff doc when done: `docs/work/HANDOFF_TEMPLATE.md`

---

## Common Questions

**"What should I implement?"**
→ Check `docs/work/SPRINT_STATUS.md` → "Next Up" section

**"How should I structure this?"**
→ `docs/process/AGENT_GUIDELINES.md` → Code Style & Conventions

**"Can I make this decision?"**
→ `docs/process/PHILOSOPHY.md` → Decision-Making Framework

**"What's the API contract?"**
→ `docs/api/` (relevant endpoint doc)

**"Is this a privacy concern?"**
→ `docs/process/PHILOSOPHY.md` → Privacy-First Mindset

**"What tests do I need?"**
→ `docs/testing/TEST_STATUS.md` → Testing guidelines (⚠️ DO NOT run cargo test)

---

## Remember
- **Privacy-first:** Even in MVP, think E2E migration
- **Fast & safe:** Performance + safety are core features
- **Document decisions:** Future agents need context
- **MVP means MVP:** Ship fast, but don't cut safety corners

---

## Need More Help?
- Full guide: `docs/process/AGENT_GUIDELINES.md`
- Philosophy: `docs/process/PHILOSOPHY.md`
- Context: `docs/work/AGENT_CONTEXT.md`

