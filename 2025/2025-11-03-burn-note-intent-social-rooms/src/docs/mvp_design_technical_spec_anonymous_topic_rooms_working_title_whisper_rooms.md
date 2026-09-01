# MVP Design & Technical Spec — Anonymous Topic Rooms (Working title: WhisperRooms)

**Owner:** Jonathan Lane (product) · **Drafted by:** ChatGPT · **Date:** Nov 3, 2025 · **Version:** 0.1 (MVP)

---

## 1) Problem & Vision
People want to talk about *exactly* what’s on their mind—sometimes niche, sometimes sensitive—without building a profile or revealing identity. Current forums force category browsing and persistent handles. DMs and group chats either aren’t discoverable or aren’t anonymous.

**Vision:** A one‑line intent box (“I’m currently interested in …”) that drops you into a live, relevant room with **session‑only pseudonyms**, **end‑to‑end encrypted** conversations, and lightweight discovery that doesn’t expose you—or your intent—to the operator.

**North Star:** “Say it once → find your people → leave no trail.”

---

## 2) In‑Scope (MVP)
1) **Anonymous entry** via one‑line intent; no account required.
2) **Black‑box matching** to a suitable room using on‑device embeddings + a public Room Atlas.
3) **Rooms** (live chat + short posts) with highlights for quick catch‑up.
4) **Whispers** (ephemeral opt‑in 1:1 DMs) between room members.
5) **Session pseudonyms** (per room, per session) with Burn Session.
6) **E2E encryption:**
   - Rooms: MLS (Messaging Layer Security)
   - Whispers: Signal‑style (X3DH + Double Ratchet)
7) **Operator‑blind networking:** OHTTP/relay for joins; server stores ciphertext only.
8) **Safety:** client‑side safety scoring, reports, slow‑mode, rate limits on ciphertext envelopes.
9) **Sensitive‑topic gating:** disclaimers and curated resources (e.g., for health topics).
10) **Basic moderation workflow** compatible with E2E via consented report uploads.
11) **Anonymous rate limiting:** blind‑signed tokens (Privacy Pass‑style).

**Out of scope (MVP):** PIR‑based catalog fetch, creator tools, fediverse bridges, paid rooms, recommendation digests, ad system.

---

## 3) Personas & Primary Use Cases
- **Nora (22, anime/games):** Types “Demon Hunters lore”. Wants real‑time chat + recs, zero profile, safe spoiler tags.
- **Chris (34, kidney transplant):** Types “post‑transplant intimacy questions”. Needs anonymity, vetted resources, option to whisper for sensitive Qs.
- **Devon (28, curious lurker):** Types “learn about lucid dreaming”. Wants read‑only highlights and low‑friction entry.

**Acceptance criteria (MVP):**
- 90% P50 time from submit‑intent → inside room < **2.0s**; P95 < **4.0s** on LTE.
- Users can participate without creating an account and without exposing IP to the app server.
- Operator cannot view plaintext messages or intents; server holds only ciphertext + minimal metadata.

---

## 4) UX Overview
**Entry:**
- Homepage: single input — *“I’m currently interested in …”*; optional toggle: “Include sensitive/health topics.”
- On submit: subtle spinner; lands in **Room**.

**Room:**
- Header: Room title; “Why you’re here” hint (derived locally); safety meter; Burn Session.
- Tabs: **Live** (chat) · **Posts** (threaded) · **Highlights** (curated) · **Resources** (curated links)
- Composer: shows mask (e.g., *opal‑wren‑41*); spoiler & content warning tags.
- Member row: whisper buttons appear on hover; consented start.

**Whisper:**
- Ephemeral by default; local delete ripple to both sides on request; optional timed expiry (24h default).

**Leave:**
- Burn Session wipes local keys, clears mask; server sees membership removal only.

---

## 5) Functional Requirements
### 5.1 Matching (Black‑Box Discovery)
- **On‑device intent processing:**
  - Normalize intent (strip PII, expand acronyms) and embed (384–768d).
  - No raw intent leaves device.
- **Room Atlas (public, hourly):** Compact dataset with for each room: centroid vector, activity score, civility score, language, last‑updated.
- **Local ranking:**
  - Candidate set via top‑K cosine to centroids.
  - Score = relevance (cosine) + activity + civility + freshness – duplication penalty.
  - MMR diversification to avoid near‑duplicates.
- **Safety gating:** Sensitive intents bias to rooms with vetted resources and active moderation.
- **Join:** Client obtains join token via OHTTP/relay; server receives join request without client IP and without the user’s intent.

### 5.2 Rooms & Messaging
- **Group chat:** MLS (TreeKEM) for forward secrecy and efficient membership changes.
- **Posts:** Short‑form threads; replies reference a post id; all content E2E.
- **Highlights:** Locally computed candidates + moderator‑curated entries; stored server‑side as encrypted records signed by a curator key.
- **History:** New members decrypt from their join epoch onward by default; past epochs may be selectively shared by members.

### 5.3 Whispers (1:1 DMs)
- **Key agreement:** X3DH; session ratcheting: Double Ratchet.
- **Defaults:** Expire after 24h (configurable by both); media allowed with size caps.

### 5.4 Identity & Sessions
- **Masks:** Per room, per session pseudonyms bound to per‑session signing keys.
- **Burn Session:** Removes local keys/mapping; server only invalidates membership and throttles residual envelopes.
- **Optional attestation:** Users can earn higher rate limits via privacy‑preserving attestation (email/phone proof or device attestation) that never displays to others.

### 5.5 Safety & Moderation
- **Client‑side signals:** On‑device model outputs safety scores (toxicity, self‑harm risk). Only scores (not text) are sent.
- **Reports:** User consents to upload reported ciphertext + their local plaintext for review in a **moderation enclave** (TEE) or by trusted moderators under NDA.
- **Rate limits:** Enforced on signed ciphertext envelopes (per session). Slow‑mode for heated rooms.
- **Sensitive‑topic gates:** Prominent disclaimers; link to vetted resources; stricter per‑minute message caps.

### 5.6 Anonymous Rate Limiting
- **Blind‑signed tokens:** Wallet of unlinkable tokens earned via PoW, small purchase, or attestation. Server validates tokens without linking across uses.

### 5.7 Telemetry & Metrics (Privacy‑Preserving)
- **Secure aggregation:** Product metrics (retention, match satisfaction) computed from aggregated, noise‑added counters; no device‑level event logs.
- **Feedback prompt:** After ~90s in room, local “Was this a good match?” thumbs. Only aggregate counts via SecAgg.

---

## 6) Non‑Functional Requirements
- **Security:** No plaintext user content or intents on server; keys never leave clients except prekeys for join bootstrap.
- **Performance:** See acceptance criteria; on‑device embed < 60ms P50 on mid‑tier Android; Room Atlas payload < 25 MB, delta‑updated hourly.
- **Availability:** 99.9% monthly for join/messaging; graceful degradation if OHTTP relay is down (fallback to secondary relay).
- **Scalability:** 100k concurrent room members across shards in MVP; path to multi‑million via horizontal sharding.
- **Accessibility:** WCAG 2.1 AA; keyboard navigation; screen reader labels.
- **Localization:** UI strings structured for i18n; language detection for room sharding.

---

## 7) Architecture
**Client (Web, iOS, Android)**
- Intent normalization + embedding
- Local ranking vs Room Atlas
- MLS client; Double Ratchet for whispers
- Safety model (on‑device); token wallet; Burn Session

**Edge/Relay**
- OHTTP or dedicated relay to strip client IPs; rate limiting at edge by token bucket (tokens = blind‑signed)

**App Server (cannot read content)**
- Room directory (metadata only; no plaintext)
- MLS assistance: key packages, group membership orchestration
- Ciphertext envelope store (append‑only)
- Token verification; envelope‑level rate limits; slow‑mode
- Atlas builder job (batch) — see below

**Moderation Enclave (optional in MVP, recommended)**
- Attested TEE for consented report review; outputs decision (ban, redact, no action)

**Storage**
- Object store for encrypted media; log store for ciphertext envelopes; KV for room metadata; short‑lived cache for join state

**Batch/Analytics**
- Atlas builder (hourly): recompute centroids, activity, civility from encrypted streams using privacy‑preserving aggregates and client‑contributed signals
- Secure aggregation pipeline for metrics

---

## 8) Data Model (Conceptual — encrypted at rest)
- **Room**: id, language, centroid vector, activity score, civility score, policy flags, last‑updated
- **Membership (ephemeral)**: room id, session public keys (signature + encryption), join time bucket
- **Message Envelope (ciphertext)**: room id, sender session id (pseudonymous), send time bucket, size, type (text/media), ratelimit hash, signature
- **Highlight (ciphertext)**: room id, curated reference, curator signature
- **Whisper Session**: recipient public bundle id, session state hash (no plaintext), expiry timestamp
- **Token**: blind signature proof; spend record w/ coarse time bucket

**Never stored:** raw intents, plaintext messages, stable user identifiers, IPs (beyond minimal rolling window at relay, <72h, if enabled).

---

## 9) Cryptography (Operational Summary)
- **Rooms (MLS):** TreeKEM for group key derivation. New epoch on join/leave. Server relays Welcome/Commit messages only.
- **Whispers:** X3DH identity/prekeys → Double Ratchet for message secrecy and PFS.
- **Key storage:** Local secure enclave/Keychain/Keystore; backup disabled by default. Optional local passcode to lock.
- **Anonymous tokens:** VOPRF‑based Privacy Pass; issuer separate from verifier (can be the relay to further unlink).
- **Networking privacy:** OHTTP relays all join and message POSTs; app server never sees client IP or UA.

---

## 10) Room Atlas (Discovery Data)
- **Contents per room:**
  - `centroid`: quantized vector (int8)
  - `activity`: decayed msg/sec
  - `civility`: 0–1 score from reports, retention, client safety signals
  - `language`: ISO tag
  - `freshness`: last active bucket
- **Generation cadence:** hourly; delta‑encoded updates
- **Delivery:** CDN; integrity via signed manifest; client verifies signature before use
- **Privacy:** built from aggregates; no user‑level events or plaintext samples

---

## 11) Matching Logic (Descriptive)
1) Client embeds normalized intent locally.
2) Client downloads/verifies Atlas; selects top‑K centroids by cosine.
3) Compute final rank: relevance + activity + civility + freshness; apply MMR for diversity.
4) Present best room; auto‑join in 1 tap.
5) If room health below threshold, suggest second‑best.

Cold start:
- Seed a small set of starter rooms with curated highlights
- Allow ephemeral “ghost rooms” to form; promote if activity/civility cross thresholds

Split/Merge:
- Track intra‑room topical variance from local LDA/topic hints and activity; auto‑suggest split/merge during off‑peak windows

---

## 12) APIs (Name‑level, no payload examples)
**Client ↔ Relay/App Server**
- `POST /v1/intent/join` (via OHTTP): request join to a room with a blind‑signed token
- `POST /v1/rooms/{id}/mls/commit` : submit MLS commit/envelope
- `GET /v1/rooms/{id}/mls/state` : fetch MLS epoch updates/key packages
- `POST /v1/messages` : send ciphertext envelope (room or whisper)
- `GET /v1/messages` : pull ciphertext envelopes (long‑poll or WebSocket)
- `GET /v1/atlas` : fetch signed Room Atlas manifest + shards
- `POST /v1/report` : submit consented report package for moderation
- `POST /v1/tokens/spend` : spend blind‑signed token for rate‑limited actions

**Admin/Moderation (backoffice)**
- `POST /v1/mod/decision` : apply moderation decision to envelopes (ban/redact/slow‑mode)
- `GET /v1/transparency` : public stats (aggregated)

---

## 13) Safety & Moderation Workflow
1) **Proactive:** client blocks send if local model flags disallowed content and room policy requires; user can appeal.
2) **Reactive reports:** reporter consents to share plaintext; moderation enclave decrypts and renders for review.
3) **Outcomes:** redact message (tombstone), shadow‑limit session, slow‑mode room, ban session keys. No deanonymization.
4) **Transparency:** publish counts by category quarterly; document false‑positive review loop.

---

## 14) Abuse Prevention & Anti‑Spam
- Blind‑token budgets per device/day; cost increases with abuse signals.
- Per‑session signing keys; revocation lists for hot abuse; circuit‑breakers on envelope volume.
- Content‑free throttles: message size caps; media type whitelist; per‑minute limits.
- Invite‑only or moderated subrooms for repeatedly targeted topics.

---

## 15) Observability (Privacy‑Preserving)
- Health: queue depth, envelope throughput, join latency, relay error rates.
- Product: match satisfaction (SecAgg), 1‑day retention, median time‑to‑first‑reply.
- Security: MLS epoch churn rates, moderation response SLAs, token spend anomalies.

---

## 16) Deployment & Infra
- **Relay/OHTTP:** globally distributed edge; stateless; autoscale.
- **App Server:** containerized microservices (directory, messaging, moderation hook); regional shards by language.
- **Stores:** encrypted object storage; append‑only log for envelopes with lifecycle rules (e.g., 30–90 days for room history unless pinned in highlights).
- **CDN:** serves signed Atlas and static assets.
- **Key Management:** no server‑side user keys; service keys in HSM; TEE attestation for moderation enclave.

---

## 17) Security Review & Threat Model (Summary)
- **Adversaries:** abusive users, passive network observers, malicious relay operator, compromised app server, compromised moderator.
- **Mitigations:** E2E (MLS/DR), OHTTP, blind tokens, TEE for reports, minimal metadata, coarse time bucketing, short retention, signed manifests, integrity checks.
- **Residual risks:** client compromise (malware), social engineering, traffic analysis (timing/size). Provide optional cover traffic for high‑risk rooms.

---

## 18) Testing Plan
- **Crypto correctness:** interoperability suites for MLS and DR; key rotation; membership churn.
- **Load:** 100k concurrent members across 2k rooms; soak tests with message fan‑out patterns.
- **Matching:** offline eval sets; online A/B for ranking weights; guardrails to avoid unsafe rooms for sensitive intents.
- **Privacy:** red‑team to attempt operator‑side deanonymization; confirm no raw intents on server; OHTTP linkage tests.
- **Moderation:** seeded abuse scenarios; report pipeline drills to TTR < 30 minutes for high‑risk categories.
- **Accessibility:** screen reader, keyboard, color‑contrast checks.

---

## 19) Rollout & Feature Flags
- **Phased regions:** start with EN‑only, a handful of time zones.
- **Flags:** OHTTP required, whispers enabled, sensitive‑topic gates, ghost rooms, split/merge automation, moderation enclave.
- **Kill switches:** force slow‑mode globally; block media; freeze new joins; disable whispers.

---

## 20) Open Questions
- Which issuer hosts blind tokens (first‑party vs third‑party)?
- Minimum relay retention window (0 vs 24–72h) for abuse forensics?
- Default history window for rooms (none vs 30/60/90 days) given E2E and "see past stuff"?
- Should health rooms require verified moderators at all times?

---

## 21) Glossary
- **MLS:** IETF standard for group E2E messaging.
- **OHTTP:** Oblivious HTTP—proxying that hides client identity from server.
- **VOPRF:** Verifiable Oblivious Pseudorandom Function—basis for unlinkable tokens.
- **Room Atlas:** Public, signed set of room centroids & health signals for on‑device matching.
- **Ghost Room:** Ephemeral, auto‑created room promoted once healthy.
- **Burn Session:** Client action that wipes local keys and pseudonym mapping.

