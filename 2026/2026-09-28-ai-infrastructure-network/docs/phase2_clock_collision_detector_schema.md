# Phase 2.4 Clock-Collision Detector: Unified Schema & Tri-Project Synthesis

**Document ID:** SPEC-PHASE2-CLOCK-COLLISION-DETECTOR  
**Status:** Certified Architecture Specification & Cross-Project Schema  
**Date:** October 1, 2026  
**Projects Synthesized:**  
1. **Polaris Forge 1 (PF1):** $3.94B Dual-Silo 144A Fixed Notes (Ellendale, ND) — *Binary Rent Step-Up Archetype*  
2. **Project Jupiter:** ~$18.0B Syndicated Bank Facility & Microgrid (Santa Teresa, NM) — *Multi-State Offtake Carry Archetype*  
3. **IREN Mackenzie:** Up-to-$2.4B Staged GPU Equipment Financing Facility (Mackenzie, BC) — *Staged Equipment Acceptance & Availability Window Cliff Archetype*  

---

## 1. The Clock-Collision Paradigm

Traditional project finance modeling treats default as a single probabilistic event ($P(\text{Default})$), attempting to simulate cash-flow distributions through synthetic Monte Carlo distributions. In hyperscale AI infrastructure, this predictive approach collapses under unobserved contract terms, private credit covenants, and unfiled sponsor recourse exhibits.

The **Infrastructure Stress Observatory** replaces speculative forecasting with a deterministic **Clock-Collision Detector**. Every infrastructure financing is structured around four distinct, interacting clocks:

```
                            [The 4 Interacting Clocks]

         Physical Clocks                           Contract Clocks
   ┌──────────────────────────┐              ┌──────────────────────────┐
   │ • Permitting decisions   │              │ • Lease commencement     │
   │ • Grid interconnections  │              │ • Rent step-up dates     │
   │ • Substation civil works │              │ • Development carry term │
   │ • Equipment logistics    │              │ • Force-majeure disputes │
   │ • Acceptance testing     │              │ • Acceptance deadlines   │
   └────────────┬─────────────┘              └────────────┬─────────────┘
                │                                         │
                └───────────────────┬─────────────────────┘
                                    │
                                    ▼
                ┌───────────────────┴─────────────────────┐
                │   The Clock-Collision Synchronization   │
                │                 Engine                  │
                └───────────────────┬─────────────────────┘
                                    │
                ┌───────────────────┴─────────────────────┐
                │                                         │
   ┌────────────┴─────────────┐              ┌────────────┴─────────────┐
   │ • Fixed coupon dates     │              │ • Completion guarantees  │
   │ • Reserve exhaustion     │              │ • Sponsor liquidity burn │
   │ • Facility availability  │              │ • Emergency equity calls │
   │ • Loan maturity & ext.   │              │ • Revolver exhaustion    │
   └──────────────────────────┘              └──────────────────────────┘
        Financial Clocks                           Support Clocks
```

### The Two Guiding Questions:
1. $$\boxed{\text{Which clock reaches its boundary first?}}$$
2. $$\boxed{\text{What observable public signal tells us that ordering is changing?}}$$

Distress occurs not because a project is inherently unviable, but because an upstream physical or regulatory delay causes a project to **miss a downstream financial or contractual deadline**.

---

## 2. Tri-Project Structural Archetypes

The observatory evaluates three empirically grounded archetypes spanning diverse capital structures and physical dependencies:

```
                    [Comparative Architecture of the Three Archetypes]

   Polaris Forge 1 (`PF1`)           Project Jupiter              IREN Mackenzie
─────────────────────────────   ──────────────────────────   ─────────────────────────────
• Capital Structure:            • Capital Structure:         • Capital Structure:
  $3.94B Dual-Silo 144A Notes     ~$18.0B Syndicated Loan      Up-to-$2.4B Staged Facility
  ($2.35B @ 9.25%, $1.59B @ 7%)   (SOFR + 250 bps, 4-yr term)  (Fixed 9.0%, MFSA + Notes)
• Physical Dependency:          • Physical Dependency:       • Physical Dependency:
  Electric Substation (MDU)       Gas Pipeline ROW (NMSLO)     GPU Delivery & Acceptance
• Contract State Transition:    • Contract State Transition: • Contract State Transition:
  Binary Rent Step-Up             Multi-State Offtake Carry    Staged Draw Eligibility
  $0 Rent -> Operational Rent     Dev Carry -> FM -> Op Rent   Undrawn -> Accepted -> Funded
• Protective Legal Shield:      • Protective Legal Shield:   • Protective Legal Shield:
  Parent Capex Completion         Tenant Force-Majeure         Staged Equipment Condition
  Guarantees (Applied Digital)    Defense (Extends Carry)      (Undrawn Debt Bears No Drag)
• Binding Financial Clock:      • Binding Financial Clock:   • Binding Financial Clock:
  Lumpy Semiannual Coupons        Floating Benchmark Carry;    Hard Dec 31, 2026 Facility
  (Months 6, 12, 18, 24...)       4-Yr Loan Maturity           Availability Window Cliff
```

---

## 3. The 6 Reusable Failure Archetypes (Scenario Library)

Across all three projects, distress manifests through six recurring failure archetypes:

### Scenario 1: Physical Milestone Misses Financial Payment Date
- **Exemplar:** Polaris Forge 1 (Silo 1 & Silo 2).
- **Mechanism:** Civil construction or electric substation interconnection slips past a fixed semiannual coupon payment date (e.g. Month 6, 12, or 18) while debt-service reserves are insufficient.
- **Collision Condition:**
  $$T_{\text{energization}} > T_{\text{coupon}} \quad \text{AND} \quad \text{DSRA}_{\text{cash}} < \text{InterestDue}$$
- **Reconverging Entity:** Project SPV $\to$ Bondholders (direct monetary payment default).

### Scenario 2: Contract Cash-Flow State Step-Down (Force-Majeure Dispute)
- **Exemplar:** Project Jupiter.
- **Mechanism:** Upstream permitting or infrastructure bottleneck prevents commercial operation; the anchor tenant declares force majeure or invokes dispute provisions, refusing to step up to full operational rent and extending lower development-stage carry.
- **Collision Condition:**
  $$T_{\text{permit\_resolution}} > T_{\text{carry\_term}} \quad \text{OR} \quad \text{DevelopmentCarry} < \text{DebtServiceDue}$$
- **Reconverging Entity:** Project SPV $\to$ Syndicated Bank Consortium (loan trading discount at 89–91c).

### Scenario 3: Reserve / Liquidity Exhaustion Before Commercial Operation
- **Exemplar:** Polaris Forge 1 (Silo 2).
- **Mechanism:** Continuous pre-operational delay burns available debt-service reserves and operating cash to zero before commercial revenue arrives.
- **Collision Condition:**
  $$\sum_{t=1}^{T_{\text{commence}}} \text{InterestDue}_t > \text{InitialReserves} + \sum \text{OperatingCashInflows}$$
- **Reconverging Entity:** Project SPV $\to$ Bondholder Workout / Debt Acceleration Boundary (post-shortfall continuation unmodeled).

### Scenario 4: Financing Availability Window Expiration Cliff
- **Exemplar:** IREN Mackenzie.
- **Mechanism:** Hardware delivery, customs clearance, or customer qualification testing delays push equipment acceptance past a hard contractual facility availability deadline (December 31, 2026). Undrawn commitments vanish permanently.
- **Collision Condition:**
  $$T_{\text{acceptance}} > \text{AvailabilityDeadline} \quad \text{AND} \quad \text{HardwareCommitted} > \text{DrawnPrincipal}$$
- **Reconverging Entity:** Project SPV $\to$ Borrower Capital Gap (replacement-funding requirement; unfinanced hardware capex exceeds committed debt capacity).

### Scenario 5: Shared Sponsor / Support Reconvergence
- **Exemplar:** Polaris Forge 1 (Dual Silos).
- **Mechanism:** Multiple legally segregated, bankruptcy-remote project SPVs encounter concurrent cost overruns or delay shortfalls. Contractual completion guarantees reconverge these independent liabilities into an aggregate cash drain on a single parent balance sheet.
- **Collision Condition:**
  $$\sum_{i} \text{CapexDeficit}_i > \text{ParentUnrestrictedCash}$$
- **Reconverging Entity:** Independent Project SPVs $\to$ Single Parent Corporate Entity (Applied Digital).

### Scenario 6: Refinancing / Maturity Collision in Dislocated Markets
- **Exemplar:** Project Jupiter / Polaris Forge 1.
- **Mechanism:** Short- or medium-term construction debt reaches maturity (e.g. 4-year term for Jupiter, 2030/2031 bullets for PF1) while physical delays or legal disputes prevent permanent takeout financing or loan extension.
- **Collision Condition:**
  $$T_{\text{maturity}} \text{ arrives WHILE } \text{SecondaryLoanDiscount} > \text{Threshold} \quad \text{OR} \quad \text{CreditSpread} \gg \text{Target}$$
- **Reconverging Entity:** Borrower SPV $\to$ Debt Restructuring / Syndicate Workout.

---

## 4. The Cross-Project Early-Warning Indicator Catalog

The indicator catalog establishes the empirical core of the observatory, classifying each indicator by **Signal Role** (`EARLY_WARNING`, `CONFIRMATION`, `FINANCIAL_RECOGNITION`, `OUTCOME`) and **Observability** (`PUBLIC`, `COMMERCIAL_DATA`, `PRIVATE_OR_UNAVAILABLE`), while strictly separating **observed historical lead times** from **monitoring windows** and **hypothesized intervals**:

| Indicator ID | Project | Layer | Signal Role | Observability | Leading Indicator Event | Threatened Boundary | Lead-Time Status | Quantified Lead Time | Primary Source / Basis |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: | :--- |
| **`IND-JUP-001`** | Project Jupiter | **`REGULATORY`** | **`EARLY_WARNING`** | **`PUBLIC`** | NMSLO denial order for 0.6-mile pipeline ROW across state trust land | Fuel availability for Bloom microgrid; loan valuation | **`OBSERVED`** | **65 Calendar Days** | July 15, 2026 (NMSLO Order) $\to$ Sept 18, 2026 (loan discount @ 89–91c) |
| **`IND-JUP-002`** | Project Jupiter | **`CONTRACT_LEGAL`** | **`EARLY_WARNING`** | **`PUBLIC`** | Oracle formal force-majeure notice citing pipeline permitting impasse | Step-up from development carry to full operational rent | **`OBSERVED`** | **71 Calendar Days** | July 15, 2026 (NMSLO Order) $\to$ Sept 24, 2026 (Oracle notice) |
| **`IND-JUP-003`** | Project Jupiter | **`EDGAR_FILING`** | **`CONFIRMATION`** | **`PUBLIC`** | Corporate disclosure of permitting impasse or loan valuation discount on EDGAR | Public market awareness of project distress and credit discount | **`RIGHT_CENSORED_OBSERVED`** | **$\ge 77$ Calendar Days** | July 15, 2026 $\to$ Sept 30, 2026 (0 filings on EDGAR by ORCL or OBDC) |
| **`IND-JUP-004`** | Project Jupiter | **`DEBT_MARKET`** | **`FINANCIAL_RECOGNITION`** | **`COMMERCIAL_DATA`** | Project Jupiter syndicated loan trades down to 89–91 cents on the dollar | Secondary market loan valuation; syndication extension willingness | **`OBSERVED`** | **0 Calendar Days** | Sept 18, 2026 baseline mark establishing the 65d early warning lead |
| **`IND-PF1-001`** | Polaris Forge 1 | **`UTILITY_DOCKET`** | **`EARLY_WARNING`** | **`PUBLIC`** | MDU / Otter Tail Power public regulatory filings and interconnection queue studies | Commercial operation date gating Silo 1 / Silo 2 tenant operational rent | **`MONITORING_WINDOW`** | **90–180 Calendar Days** | Standard RTO / utility transmission study revision cycles |
| **`IND-PF1-002`** | Polaris Forge 1 | **`EDGAR_FILING`** | **`CONFIRMATION`** | **`PUBLIC`** | Parent capital raises, convertible notes, ATM equity offerings, or revolver draws | Parent cash capacity to fund completion guarantees across dual silos | **`HYPOTHESIZED_WINDOW`** | **30–90 Calendar Days** | Corporate cash burn rate preceding parent balance sheet exhaustion |
| **`IND-MAC-001`** | IREN Mackenzie | **`PHYSICAL_LOGISTICS`** | **`EARLY_WARNING`** | **`PRIVATE_OR_UNAVAILABLE`** | GPU server shipping manifests, customs clearance, and customer acceptance testing logs | Hard December 31, 2026 facility availability expiration cliff | **`MONITORING_WINDOW`** | **30–60 Calendar Days** | Final hardware delivery and qualification window preceding cliff |
| **`IND-MAC-002`** | IREN Mackenzie | **`EDGAR_FILING`** | **`FINANCIAL_RECOGNITION`** | **`PUBLIC`** | SEC Form 10-Q note detailing drawn vs. undrawn borrowings under MFSA and Notes | Loss of undrawn debt capacity; replacement-funding requirement | **`MONITORING_WINDOW`** | **45–60 Calendar Days** | Q1 FY27 Form 10-Q filing window (quarter ended Sept 30, 2026, filed Nov 2026) |

---

## 5. The Subordinate Boundary Calculator Architecture

The deterministic engine is retained, but strictly subordinated to the observatory. It does not output speculative default probabilities; it calculates **concrete operational thresholds**:

```
[Observable Indicator Alert]
          │
          ▼
[Update Estimated Milestone] ───> [Boundary Calculator] ───> [Actionable Interpretation]
e.g. Expected Acceptance Date     Calculates:                "Expected acceptance Jan 20:
     approaches Dec 31, 2026      AcceptanceSlackDays = -20   availability boundary precedes
                                  (Date boundary collision)   acceptance by 20 days."
```

### Certified Functional Boundaries:
1. **Polaris Forge 1 (Phase 2.1 Frozen):**
   $$T_{\text{payment\_shortfall}} = f\left(\Delta t,\; \text{DSRA\_Tier},\; \text{CouponSchedule}\right)$$
   $$C_{\text{parent\_support}} = f_{\text{pre-shortfall}}\left(\text{CapexBurn},\; \Delta t\right)$$
2. **Project Jupiter (Conditional Mechanism Specification):**
   $$T_{\text{runway}} = f\left(R_{\text{debt-service liquidity}},\; P_{\text{dev carry}},\; P_{\text{FM carry}},\; r_{\text{debt}},\; \Delta t\right)$$
3. **IREN Mackenzie (Minimal Date Boundary Slack Calculator):**
   $$\text{AcceptanceSlackDays} = \text{Dec 31, 2026} - T_{\text{acceptance}}$$
   - $\text{AcceptanceSlackDays} \ge 0$: Equipment accepted prior to cliff (on track).
   - $\text{AcceptanceSlackDays} < 0$: Availability boundary precedes acceptance by $|\text{AcceptanceSlackDays}|$ days.
   - If explicit remaining eligible financing / equipment value is disclosed:
     $$\text{FinancingCapacityAtRisk} = \text{UnacceptedEligibleEquipmentValue} \quad (\text{replacement-funding requirement})$$

---

## 6. The Empirical Scoreboard

The observatory is evaluated across historical natural experiments and prospective monitoring cases using three objective criteria:

1. **Detection Lead Time:**
   $$\Delta t_{\text{lead}} = t_{\text{financial recognition}} - t_{\text{earliest observable indicator}}$$
   - *Benchmark Proven:* Project Jupiter achieved **$\Delta t_{\text{lead}} = 65\text{ days}$** against secondary debt trading discounts and **$\ge 77\text{ days}$** against SEC disclosures.
2. **Boundary Identification:**
   - Did the observatory correctly identify which clock/contractual boundary became binding first?
   - *PF1:* Identified coupon date cliffs strictly dominating delay duration.
   - *Jupiter:* Identified commercial offtake carry dispute rather than binary power loss.
   - *Mackenzie:* Identified December 31, 2026 availability window cliff rather than power energization.
3. **Incremental Information Gain:**
   - Did the cross-layer JOIN reveal critical structural dependencies unrecoverable from financial feeds alone?
   - *The Jupiter Proof:* Joining a local 0.6-mile state land pipeline permit denial $\to$ gas fuel supply $\to$ Bloom microgrid $\to$ Oracle lease contract $\to$ syndicated bank loan yielded 65–71 days of actionable intelligence.
