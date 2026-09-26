# Gate 1 — Grandview C-4 RWL / Kauffman Funding Lifecycle

## Status

**PARTIALLY RESOLVED — no defensible post-grant date yet.**

Gate 1 establishes a much stronger direct funding chronology but does **not** identify a verified closeout date. The project must continue to treat the grant lifecycle as an empirical variable.

## Findings

### 1. Grandview entered RWL through a funded design-and-plan phase in 2019

Kauffman program documentation places Grandview in Cohort 1 and describes the cohort as receiving grants in summer 2019 for a Real World Learning Design and Plan year before implementation in 2020-21. The March 2021 district snapshot likewise places Grandview in the 2019-20 Design + Plan phase followed by pilot and implementation years.

**Known:** direct/catalytic Kauffman funding existed at entry.

**Unknown:** Grandview-specific 2019 award amount and grant instrument.

### 2. At least $420,000 in direct Kauffman payments appears in tax years 2021-2024

An IRS-derived aggregation of Kauffman Form 990-PF grant records reports **$420,000** paid to Consolidated School District No. 4 in **three funded tax years** between 2021 and 2024.

This figure does **not** include the summer 2019 design grant because the aggregation begins with tax year 2021.

### 3. The 2023 continuation payment is directly verified

Kauffman's TY2023 Form 990-PF lists:

- recipient: **Consolidated School District No. 4**
- address: **13015 10th Street, Grandview, MO 64030**
- amount: **$135,000**
- grant ID: **202307-14162**
- purpose: continued implementation of a district-wide Real World Learning strategic plan intended to increase graduates leaving high school ready for learning work and life in the Kansas City region.

This is primary evidence that Grandview was still receiving direct Kauffman RWL implementation funding in tax year 2023.

### 4. A second $135,000 payment is reported for 2024

An IRS-derived Kauffman grant listing reports the same recipient amount grant ID and purpose in 2024.

This is strong evidence of continuation into 2024 but is currently classified **medium-high confidence** because the exact TY2024 grant row has not yet been independently archived from the foundation's primary filing.

### 5. The remaining $150,000 Kauffman payment is not yet assigned to an exact year

The IRS-derived aggregate reports $420,000 across three funded years from 2021-2024.

Known 2023 + 2024 payments:

```text
$135,000 + $135,000 = $270,000
$420,000 - $270,000 = $150,000
```

Therefore a third **$150,000** Kauffman payment exists in the 2021-2024 aggregate and must fall in **2021 or 2022** if the aggregate is accurate.

Do **not** yet assign:
- exact tax year,
- grant ID,
- RWL purpose,
- award period.

Those require the individual Kauffman filing row or district acceptance record.

### 6. PREP-KC also transferred funds directly to Grandview

PREP-KC Schedule I data reports:

| PREP-KC fiscal year | Grandview payment |
| --- | ---: |
| FY2023 | $67,282 |
| FY2024 | $50,400 |

PREP-KC's work with Grandview on Market Value Assets and the South KC micro-region is separately documented. However the public Schedule I index does not surface the purpose of these two payments.

**Rule:** keep these as an intermediary funding stream with `adjacent_unresolved` RWL linkage until the MOU or Schedule I purpose is recovered.

### 7. By 2024 the pathway ecosystem had meaningful non-Kauffman capital

On September 13 2024 KCNSC announced NNSA-supported investments that included:

- **$125,000 to the Grandview Educational Foundation** for Grandview's Advanced Manufacturing Pathway and lab including dual college credit;
- **$75,000 to PREP-KC** for a dual-credit pilot;
- **$50,000 to Great Jobs KC** for advanced-manufacturing training in which Grandview C-4 participates.

These amounts are **not evidence that Kauffman was replaced**. They are evidence that RWL-aligned operational capacity was attracting other capital by 2024.

## Funding picture currently supported

```text
Summer 2019
  Kauffman-funded Cohort 1 Design + Plan grant
  amount unresolved
        |
        v
2020-21
  Pilot / implementation begins
        |
        v
2021 or 2022
  $150,000 Kauffman payment inferred from IRS aggregate
  exact year + purpose unresolved
        |
        v
2023
  $135,000 Kauffman direct RWL continuation payment
  grant 202307-14162
  + $67,282 PREP-KC -> Grandview payment
        |
        v
2024
  $135,000 Kauffman continuation payment reported
  same grant 202307-14162
  + $50,400 PREP-KC -> Grandview payment
  + $125,000 KCNSC/NNSA -> Grandview Educational Foundation
        |
        v
2025-26
  RWL activities and organizational capacity visibly continue
  current RWL site still describes network districts as receiving support
  NO verified Grandview-specific Kauffman transaction or closeout date yet
```

## What we can and cannot claim

### Supported

- Grandview's RWL participation was grant-supported from its Cohort 1 design phase.
- Grandview received direct Kauffman RWL continuation funding in 2023.
- Public IRS-derived evidence supports continued direct Kauffman funding in 2024.
- Kauffman grant records for 2021-2024 total $420,000 across three funded tax years.
- PREP-KC separately transferred funds directly to Grandview in FY2023 and FY2024.
- Other RWL-aligned capital was flowing into Grandview's advanced-manufacturing pathway by 2024.

### Not supported yet

- A specific **final Kauffman year** for Grandview.
- Any claim that 2025 or 2026 is **post-grant**.
- A claim that PREP-KC's FY2023/FY2024 district payments were Kauffman pass-through dollars.
- A claim that KCNSC/NNSA funding replaced Kauffman funding.
- A district fund/account code for the Kauffman receipts.
- A local-dollar backfill amount.

## Remaining Gate 1 evidence targets

1. **2019 award instrument / board acceptance**
   - amount
   - grant ID
   - award term
   - restrictions
   - district match

2. **2021 or 2022 Kauffman grant row**
   - resolve the inferred $150,000 payment to an exact tax year and purpose

3. **2024 primary Kauffman filing row**
   - independently archive the $135,000 payment currently supported by an IRS-derived secondary listing

4. **Grandview accounting treatment**
   - corrected DESE district code is **048074**
   - pull ASBR / district ledger records using 048074
   - search local revenue and grant account descriptions for Kauffman / RWL / PREP-KC

5. **PREP-KC MOU / grant purpose**
   - determine whether FY2023 $67,282 and FY2024 $50,400 were restricted to RWL/MVA work or broader partnership activity

6. **2025-2026 direct support**
   - no reliable transaction has yet been located
   - current network language cannot substitute for an award record

## Gate decision

**Gate 1 remains open but narrowed.**

The start and continuation of the Kauffman funding relationship are now well established. The remaining identification problem is the **right-hand edge** of the treatment: when direct Kauffman support actually ended or materially changed.

Until that is resolved the longitudinal study should use:

`grant_status_at_event = unknown_or_current_support_unverified`

rather than `post_grant`.
