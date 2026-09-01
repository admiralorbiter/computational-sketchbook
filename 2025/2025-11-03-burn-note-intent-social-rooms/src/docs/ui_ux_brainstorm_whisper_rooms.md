# UI / UX Brainstorm — WhisperRooms

**Purpose:** Explore product/UI patterns, matching improvements, and experience design to make anonymous topic rooms intuitive, safe, and addictively useful.

**Date:** Nov 3, 2025 · **Owner:** Jonathan Lane · **Version:** Ideation v0.1

---

## 1) Design Principles
- **Searchless by default:** One line in → right room out. Reduce categorization overhead.
- **Privacy-first:** Users should feel safe at a glance; anonymity is visible and controllable.
- **Fast start, graceful depth:** Simple entry, but power tools appear as needed.
- **Kindness surfaces:** Nudge toward civility; celebrate helpfulness, not clout.
- **Local-first:** Make the client feel smart—ranking, summaries, and safety hints run on-device.

---

## 2) Core Mental Model
- You carry a **temporary mask** and a **topic impulse**.
- The system drops you into a **living room** of people with the same impulse.
- You can **whisper**, **post**, **react**, and **burn** the session with one tap.

---

## 3) Entry & Onboarding
**Intent box** (home): placeholder examples switch every few seconds:
- “I’m currently interested in … *Demon Hunters lore*”
- “… *post‑transplant intimacy questions*”
- “… *beginner 3D printing tips*”

**Accessories:**
- Toggle: **“Include sensitive topics”** (with a short tooltip and link to resources).
- Language auto-detect + a subtle chip to change.
- Voice input; immediate tokenization feedback (quietly shows extracted entities *locally*).
- **Preview card** appears after typing ≥ 10 chars: top room title, 2 recent highlights, room vibe (calm/active).
- **Safe start** option: join as **read-only for 60s**, then auto-unlock posting.

**Empty state:** screenshot-like mock showing how live chat and posts differ; a single “Try ‘Ask a specific question’” button inserts a scaffold.

---

## 4) Matching UX & Making It Better
**Visible but private cues:**
- “You’re here because your intent matched *{3 concepts}*.” (computed locally from atlas)
- **Fit meter** (0–3 dots) with small copy: “We can try a different room.”

**Controls to improve matching:**
- **Room switcher:** One‑tap to “Show alternatives” (2–3 diverse options via MMR).
- **Feedback chips:** *Too broad*, *Wrong vibe*, *Off-topic*, *Sensitive content* → feeds a **local** preference vector and aggregate (secure) metrics.
- **Vibe slider** (experiment): *chill ↔ debatey* influences the civility/activity weight mix.
- **Negative keywords** (advanced): easy chip list the user can remove later.
- **Session memory** (local only): repeat join for similar intents prefers rooms you engaged in, for 7 days.

**Algorithmic experiments:**
- **Pairwise preference learning** from “A vs B” quick picks during alternates view.
- **Contextual bandits**: try slightly riskier adjacent rooms for 10% of sessions to learn.
- **Warm-start facets**: mini taxonomy to disambiguate (e.g., “Demon Hunters → anime / games / myth”).

---

## 5) Room Experience
**Layout:**
- Header: room title, **Why you’re here** hint, **safety meter**, **Burn** button.
- Tabs: **Live** (fast scroll chat) · **Posts** (threaded Q&A) · **Highlights** (digest) · **Resources** (curated links)

**Composer:**
- Mask chip (e.g., *opal‑wren‑41*) with **Switch mask** menu.
- Content warnings & spoiler tags; quick templates: *Question*, *Experience*, *Advice*, *Vent*.
- Attachment types: image, voice note (auto-transcribed on device), poll.

**Highlights:**
- Auto-compiled locally + curator‑pinned; “Skim last 24h” button.

**Thread ergonomics:**
- Convert a fast chat message into a post **after the fact** (“Make this a post”).
- “Summarize thread so far” (local summary over cached plaintext before send).

**Whispers (1:1):**
- **Ask to Whisper** handshake; expiry defaults to 24h.
- Private safety meter shows when both have rate‑limit headroom (reduces spam fear).

**Exit & Recovery:**
- Burn Session → confirm with a single, plain sentence; “Copy room shard link before leaving?” option.

---

## 6) Navigation & Discovery
- **Adjacent rooms** strip at the bottom: 3 related topics; hover shows preview.
- **Back to impulse**: stores the last typed intent locally; re‑enter to tweak and re‑match.
- **Saved topics (local only)**: pinned intents that never leave the device.
- **Moment rooms:** time‑boxed events (watch party, Q&A hour) that vanish; RSVP with an anonymous reminder.

---

## 7) Anonymity & Consent Cues
- **Mask presentation:** geometric avatar + two-word codename; never display join time precisely (bucketed).
- **Mask tools:** Flip mask, mute, block; “hide my last 10 messages” (local redact request propagates a tombstone if allowed).
- **Privacy debugger:** quick panel showing exactly what the server can see (envelope size, time bucket, room id).
- **Panic gestures:** press‑and‑hold on header to burn + exit.

---

## 8) Safety, Moderation & Sensitive Topics
- **Room charters:** short, humane rules shown on first post.
- **Client‑side guardrails:** health/legal rooms show “not professional advice” banner; required checkbox for certain content types.
- **Reporting flow:** single tap on message → “Include my plaintext so mods can help” (default on for severe categories).
- **Slow‑mode** visibly indicated; countdown shows when you can post again.
- **Safety meter:** small always-visible indicator (auto‑mod present / high report rate / calm).

---

## 9) Accessibility & Inclusivity
- **WCAG AA** color/contrast; large tap targets; clear focus outlines.
- **Screen reader names** for masks and buttons; structured landmarks.
- **Localization** of idioms; RTL support; profanity filters aligned to locale.
- **Cognitive load**: short sentences, chunky spacing, progressive disclosure.

---

## 10) Performance & Micro‑interactions
- First paint quick: skeleton room while keys negotiate.
- Message send: optimistic bubble that locks once ciphertext is acknowledged.
- Pinned **“Connection status”** unobtrusive indicator; never block typing on network hiccups.

---

## 11) Retention & Delight (non-creepy)
- **Topic seeds** on home informed by what’s trending globally (no personal history unless local).
- **Weekly “New to this?” guides** surfaced in Highlights for popular topics.
- **Gentle trophies**: post gets “thanks” → your **mask** (not you) earns a small token visible only in that room.

---

## 12) Growth Loops (Privacy‑preserving)
- **Intent links**: share a link that pre-fills the intent text without exposing the room members.
- **Room shard invites**: doors open to a specific shard with no roster.
- **Creator moments**: let community members schedule a one‑hour themed session (with consented mod presence).

---

## 13) Privacy‑Preserving Signals for Matching
- **Thumbs + fit reason** → aggregated via secure aggregation only.
- **Dwell time** measured locally; only bucketed averages sent.
- **Reply depth** and **time‑to‑first‑reply** as room health (aggregated).
- **Negative encounters**: mutes/blocks contribute to civility score without identity.

---

## 14) Feature Backlog (Now / Next / Later)
**Now (MVP)**
- Intent box → local match → join
- Live chat + Posts + Highlights
- Masking + Burn Session
- Whispers (handshake + expiry)
- Basic reporting + slow‑mode

**Next**
- Room previews + alternates
- Vibe slider + negative keywords
- Moment rooms + RSVP reminders
- Thread → Post conversion; local summary

**Later**
- PIR/TEE‑backed private retrieval for atlas shards
- Advanced sensitive‑topic prompts and vetted expert office hours
- Optional cover traffic for high‑risk rooms

---

## 15) Edge Cases & Error States
- **Room full**: Queue with ETA and “nearby rooms” suggestions.
- **Relay down**: fallback relay and clear banner; read‑only mode still works for cached highlights.
- **Key sync issues**: automated re‑join with a fresh mask; show clear status.
- **Media blocked**: preview policy explains why; suggest text alternative.

---

## 16) Experiment Ideas
- **Two‑card chooser** on entry to disambiguate ambiguous intents.
- **Ask a better question** nudge that converts vague posts into structured prompts.
- **Civility badge** for rooms maintaining high health; temporary slow‑mode lift as a reward.
- **Read‑only personalities**: surfaces for lurkers (polls, emoji‑only reactions).

---

## 17) Research Plan (Rapid)
- **Five‑user test** (two sensitive‑topic testers, three hobbyists).
- Success if: time‑to‑first‑reply < 2m, 70% report feeling “safe”, >60% say the room felt on‑topic.
- Follow‑ups: perception of anonymity, comprehension of safety meter, ease of burning session.

---

## 18) Open Questions
- Should sensitive rooms require a live mod or just heightened slow‑mode?
- How aggressively should we auto‑split growing rooms vs rely on community input?
- What’s the default history window that balances “see past stuff” with ephemerality?

---

## 19) Success Metrics (Aggregated, Privacy‑preserving)
- **Match Fit**: % “good fit” thumbs aggregated per room.
- **First Response Speed**: median mins to first reply.
- **Healthy Retention**: % who return to *any* room within 7 days (local prompt can ask to rejoin).
- **Civility Index**: weighted mix of reports, mutes/blocks, reply depth, churn.

