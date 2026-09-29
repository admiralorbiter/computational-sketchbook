"""
Builds and executes 01_five_company_pilot.ipynb (Phase 0.6 Refactor).
Incorporates audited duration-aware balance sheets and flow metrics, MultiDiGraph representation,
decomposed debt facilities, springing guaranty legal predicates, reachability by amount_type,
and contract-calibrated transmission functions for the parameterized financial stress prototype.
"""

from pathlib import Path
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

NOTEBOOK_DIR = Path(__file__).resolve().parent.parent / "notebooks"
NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOK_DIR / "01_five_company_pilot.ipynb"

nb = nbf.v4.new_notebook()

cells = []

# Cell 1: Markdown - Header & Thesis
cells.append(nbf.v4.new_markdown_cell("""# AI Infrastructure Financial Network: Phase 0.6 Five-Company Pilot
### *The Bubble Lives in the Joins: Emerging Coordination Failures, Multi-Contract Graphs, and Contract-Calibrated Stress Transmission*

---

## Central Organizing Thesis

The thing that blows up in a financial bubble is often **not hidden data**. It is a **hidden relationship between data that everybody can see**.
* **Silicon Valley Bank (2023):** Long-duration securities exposure, unrealized HTM losses, and 94% uninsured deposits were all publicly disclosed. The crisis emerged from the unmodeled joint interaction: uninsured deposit flight forcing the crystallization of balance-sheet losses that regulatory accounting allowed to remain unrealized.
* **Archegos Capital Management (2021):** Each prime broker knew its individual loan exposure to Archegos. What none possessed was the aggregate graph: identical total-return swaps across multiple counterparties concentrating $160B of exposure on $36B of capital.
* **Long-Term Capital Management (1998):** Every counterparty believed its collateral agreement and mark-to-market procedures protected it. Collectively, they had enabled a massive correlated position.

### The Five Kinds of Opacity in 2020s AI Capital Structures
1. **Perimeter Opacity:** Risk is isolated in Special Purpose Vehicles (SPVs) or project-level subsidiaries rather than the consolidated parent balance sheet (e.g. CoreWeave SPV VIII and Applied Digital ELN project LLCs).
2. **Network Opacity:** Participants see direct counterparty commitments, but none observe the aggregate dependence on identical customers, lenders, or suppliers (e.g. 67% of CoreWeave FY25 recognized revenue tied to Microsoft).
3. **Contract Opacity:** Multi-billion dollar backlogs and lease agreements are announced, but termination remedies, liquidated damages, milestone triggers, and **unconditional springing guarantees** remain buried in Exhibit 10 agreements.
4. **Valuation Opacity:** Collateral (GPU clusters) is marked at historical cost or recent transaction prices, ignoring secondary liquidation value under simultaneous distress.
5. **Temporal Opacity:** Severe cash flow maturity mismatches: 5-year debt facilities funding 15-year lease obligations subject to utility substation lead times.

This notebook establishes **Phase 0.6** of the AI Infrastructure Financial Network across five core companies forming a closed capital, hardware, and lease chain: **NVIDIA (NVDA)**, **Supermicro (SMCI)**, **CoreWeave (CRWV)**, **Applied Digital (APLD)**, and **Oracle (ORCL)**, linked to strategic counterparties **Microsoft (MSFT)**, institutional bondholders, and private credit syndicates.
"""))

# Cell 2: Code - Setup
cells.append(nbf.v4.new_code_cell("""import sys
from pathlib import Path

project_root = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from src.graph import ObligationNetwork
from src.reachability import ContractualReachability
from src.stress import FinancialStressEngine

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", 120)

print("Environment initialized successfully.")
print(f"Project Root: {project_root}")
"""))

# Cell 3: Markdown - Entity Registry
cells.append(nbf.v4.new_markdown_cell("""## 1. Entity Registry & Scope of Pilot

We model the network across four functional tiers:
1. **Accelerated Silicon Supplier:** NVIDIA (`NVDA`)
2. **Server OEM / Integrator:** Supermicro (`SMCI`)
3. **Leveraged Neocloud Operator:** CoreWeave (`CRWV`) & Equipment SPV (`CRWV_SPV_VIII`)
4. **HPC Data Center Developer:** Applied Digital (`APLD`), Polaris Forge 1 SPV (`APLD_ELN_LLC`), and Polaris Forge 2 SPV (`APLD_COMPUTECO2`)
5. **Enterprise Cloud Hyperscaler:** Oracle (`ORCL`) & Anchor Customer Microsoft (`MSFT`)
6. **Capital Providers & Infrastructure:** Private Credit Syndicate (`BLACKSTONE_MAGNETAR_SYN`), Institutional Bondholders, and Polaris Forge 1 Campus (`POLARIS_FORGE_1`)
"""))

# Cell 4: Code - Inspect Entities
cells.append(nbf.v4.new_code_cell("""entities_df = pd.read_parquet(project_root / "data/processed/entities.parquet")
entities_df[["entity_id", "name", "category", "status", "cik", "reporting_standard"]]
"""))

# Cell 5: Markdown - Layer 1
cells.append(nbf.v4.new_markdown_cell("""## 2. Layer 1: Audited Accounting Baselines (Direct SEC XBRL Ingestion)

We query `data.sec.gov` directly via `src/sec_ingest.py`, parsing standardized US-GAAP concepts from Form 10-K and 10-Q periodic filings.
Crucially, our Phase 0.6 pipeline:
* Distinguishes **instant balance sheet facts** from **duration flow facts** (3-month quarterly vs 12-month annual).
* Synthesizes derived Q4 flows where Form 10-K only reports annual numbers (e.g. Microsoft FY26 $331.84B - 9M $241.83B = **$90.01B Q4**; APLD FY26 $611.31M - 9M $352.56M = **$258.75M Q4**).
* Aggregates multi-component funded debt (long-term debt, current portion, convertible notes, credit facilities) reconciling exact totals (APLD $4.98B, CRWV $35.55B, SMCI $8.72B).
"""))

# Cell 6: Code - Pivot Financials
cells.append(nbf.v4.new_code_cell("""financials_df = pd.read_parquet(project_root / "data/processed/financials.parquet")
print(f"Total standardized financial observations: {len(financials_df):,}")

# Instant Balance Sheet Metrics (as of latest balance sheet date)
instant_df = (
    financials_df[financials_df["duration_type"] == "instant"]
    .sort_values(by=["entity_id", "metric", "period_end", "filed_date"])
    .groupby(["entity_id", "metric"])
    .last()
    .reset_index()
)
pivot_inst = instant_df.pivot(index="entity_id", columns="metric", values="value") / 1e9

# Flow Metrics (Quarterly Run-Rate / Annual Flows)
flow_df = (
    financials_df[financials_df["duration_type"].isin(["quarterly", "annual"])]
    .sort_values(by=["entity_id", "metric", "period_end", "filed_date"])
    .groupby(["entity_id", "metric"])
    .last()
    .reset_index()
)
pivot_flow = flow_df.pivot(index="entity_id", columns="metric", values="value") / 1e9

bs_summary = pd.DataFrame({
    "Cash & Equiv ($B)": pivot_inst.get("cash_and_equivalents", 0.0),
    "Total Debt ($B)": pivot_inst.get("total_debt", 0.0),
    "Lease Liabilities ($B)": pivot_inst.get("operating_lease_liabilities", 0.0),
    "PP&E Net ($B)": pivot_inst.get("ppe_net", 0.0),
    "Latest Rev Flow ($B)": pivot_flow.get("revenue", 0.0),
    "Latest OCF Flow ($B)": pivot_flow.get("operating_cash_flow", 0.0)
}).round(2).fillna(0.0)

bs_summary
"""))

# Cell 7: Code - Balance Sheet Comparison Plot
cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(11, 5))
bs_plot = bs_summary[["Cash & Equiv ($B)", "Total Debt ($B)", "Lease Liabilities ($B)"]]
bs_plot.plot(kind="bar", ax=ax, color=["#2ecc71", "#e74c3c", "#f39c12"], width=0.65)
ax.set_title("Audited Balance Sheet Structure ($ Billions) - Latest SEC Periodic Disclosures", fontsize=12, fontweight="bold")
ax.set_ylabel("USD ($ Billions)")
ax.set_xlabel("Entity")
ax.grid(True, linestyle="--", alpha=0.5)
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(project_root / "outputs/figures/fin_bs_structure.png", dpi=300)
plt.show()
"""))

# Cell 8: Markdown - Layer 2
cells.append(nbf.v4.new_markdown_cell("""## 3. Layer 2: The Contractual Obligation Multi-Graph

We model obligations using `nx.MultiDiGraph` with `obligation_id` as the edge key.
This architecture preserves multiple distinct facilities between the same counterparty pair:
* **CoreWeave Indebtedness Decomposed:** DDTL 1.0 ($1.30B), DDTL 2.0 ($3.19B), DDTL 2.1 ($3.00B), DDTL 3.0 ($2.215B), DDTL 5.0 ($1.101B), Senior Notes ($10.029B), Convertibles ($6.588B), OEM Financing ($4.220B), Magnetar Loan ($0.189B), and non-recourse SPV DDTL 4.0 ($8.5B commitment).
* **Applied Digital Debt Segmented:** $2.35B 9.25% Senior Notes (Polaris Forge 1 - fixed rate), $2.15B 6.75% Senior Notes (Polaris Forge 2 - fixed rate), and $476M corporate notes.
* **Microsoft Relationship:** Characterized strictly as `REL-MSFT-CRWV-REVENUE-CONCENTRATION` ($3.438B recognized revenue, 67% concentration of FY25 revenue) with `amount_type = "recognized_revenue"` (NOT an unverified 5-year take-or-pay contract).

Crucially, we **do not compute a naive net exposure** across different obligation types. Instead, exposure is categorized strictly by **`amount_type`**.
"""))

# Cell 9: Code - Exposure by Amount Type
cells.append(nbf.v4.new_code_cell("""net = ObligationNetwork()
exposure_df = net.compute_exposure_by_amount_type()

exposure_table = exposure_df.assign(
    principal_debt_B=lambda df: (df["outgoing_principal_debt_usd"] / 1e9).round(2),
    facility_capacity_B=lambda df: (df["outgoing_facility_capacity_usd"] / 1e9).round(2),
    lease_lifetime_B=lambda df: (df["outgoing_lease_lifetime_usd"] / 1e9).round(2),
    purchase_commitments_B=lambda df: (df["outgoing_purchase_commitments_usd"] / 1e9).round(2),
    contingent_guarantee_B=lambda df: (df["outgoing_contingent_guarantees_usd"] / 1e9).round(2),
    equity_investment_B=lambda df: (df["outgoing_equity_investments_usd"] / 1e9).round(2)
)[["entity_id", "category", "principal_debt_B", "facility_capacity_B", "lease_lifetime_B", "purchase_commitments_B", "contingent_guarantee_B", "equity_investment_B"]]

exposure_table[exposure_table[["principal_debt_B", "facility_capacity_B", "lease_lifetime_B", "purchase_commitments_B", "contingent_guarantee_B", "equity_investment_B"]].sum(axis=1) > 0]
"""))

# Cell 10: Code - Obligations Ledger
cells.append(nbf.v4.new_code_cell("""obl_df = pd.read_parquet(project_root / "data/processed/obligations.parquet")
obl_df[["obligation_id", "from_entity", "to_entity", "obligation_type", "amount", "amount_type", "as_of_date", "term_years", "recourse", "shared_assumptions"]].assign(
    amount_B=lambda df: (df["amount"] / 1e9).round(2)
).drop(columns=["amount"])
"""))

# Cell 11: Code - MultiDiGraph Topology Plot
cells.append(nbf.v4.new_code_cell("""G = net.graph

plt.figure(figsize=(15, 11))
pos = {
    "NVDA": np.array([0.0, 1.0]),
    "SMCI": np.array([-0.7, 0.4]),
    "HARDWARE_SUPPLIERS": np.array([-1.0, 0.9]),
    "CRWV": np.array([0.0, 0.1]),
    "MSFT": np.array([-0.9, -0.3]),
    "BLACKSTONE_MAGNETAR_SYN": np.array([0.8, 0.5]),
    "INSTITUTIONAL_BONDHOLDERS": np.array([0.9, 0.0]),
    "OEM_FINANCING_PARTNERS": np.array([0.7, -0.4]),
    "CRWV_SPV_VIII": np.array([0.2, -0.6]),
    "APLD_ELN_LLC": np.array([0.6, -0.8]),
    "APLD_COMPUTECO2": np.array([0.8, -1.0]),
    "PROJECT_LENDERS": np.array([1.1, -0.85]),
    "POLARIS_FORGE_1": np.array([0.2, -1.0]),
    "APLD": np.array([0.5, -1.1]),
    "ORCL": np.array([-0.4, 0.8])
}

category_colors = {
    "hardware_supplier": "#1f77b4",
    "server_oem": "#ff7f0e",
    "neocloud_operator": "#2ca02c",
    "hyperscaler_anchor": "#9467bd",
    "hyperscaler_cloud": "#8c564b",
    "private_credit_syndicate": "#d62728",
    "capital_markets": "#d62728",
    "hardware_financing": "#e377c2",
    "datacenter_developer": "#e377c2",
    "project_spv": "#7f7f7f",
    "physical_asset_project": "#bcbd22"
}

node_colors = [category_colors.get(G.nodes[n].get("category", ""), "#333333") for n in G.nodes()]
node_sizes = [max(950, len(n) * 230) for n in G.nodes()]

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9, edgecolors="black", linewidths=1.5)
nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold", font_family="sans-serif")

# Draw edges
for u, v, k, d in G.edges(data=True, keys=True):
    amt = d.get("amount", 1e9)
    width = max(1.2, np.log10(amt) - 7.8) * 1.5
    edge_color = "#e74c3c" if "DEBT" in k or "LEASE" in k else ("#9b59b6" if "GUARANTY" in k else "#3498db")
    nx.draw_networkx_edges(
        G, pos, edgelist=[(u, v)], width=width, edge_color=edge_color,
        arrowsize=18, arrowstyle="-|>", connectionstyle="arc3,rad=0.1"
    )

edge_labels = {(u, v): f"${d.get('amount', 0)/1e9:.1f}B" for u, v, k, d in G.edges(data=True, keys=True) if d.get("amount", 0) >= 2e9}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color="#2c3e50")

plt.title("AI Infrastructure Multi-Graph Obligation Network (Phase 0.6)\\n(Edges Represent Distinct Legal Facilities, Leases, Guarantees, and Commitments)", fontsize=13, fontweight="bold")
plt.axis("off")
plt.tight_layout()
plt.savefig(project_root / "outputs/figures/obligation_network_topology.png", dpi=300)
plt.show()
"""))

# Cell 12: Markdown - Unwrapping SPVs
cells.append(nbf.v4.new_markdown_cell("""## 4. Unwrapping Perimeter Opacity: The Springing Guaranty

Notice the literal contractual reality revealed in APLD's Form 10-K (Note 14 & Exhibit 10):
* CoreWeave assigned its direct lease liabilities for Polaris Forge 1 to `CRWV_SPV_VIII` and was formally released from direct lease obligations.
* **HOWEVER**, CoreWeave concurrently executed an **Unconditional Springing Guaranty of Payment and Performance** for the SPV's obligations.
* **The Literal Legal Predicate:** The guaranty is dormant during ordinary operations, but *springs* into an active, direct parent liability upon an SPV colocation payment default or bankruptcy trigger.
* Thus, SPV restructuring did NOT insulate CoreWeave; it introduced a **contingent liquidity cliff** where an operating deficit at the SPV level immediately reactivates parent balance sheet liability for the full $11.0B lease.
"""))

# Cell 13: Code - Unwrap SPVs
cells.append(nbf.v4.new_code_cell("""collapsed_graph = net.unwrap_spv_perimeter()
print(f"Consolidated Economic Network: {collapsed_graph.number_of_nodes()} Nodes | {collapsed_graph.number_of_edges()} Edges")

collapsed_records = []
for u, v, k, d in collapsed_graph.edges(data=True, keys=True):
    collapsed_records.append({
        "from_parent": u,
        "to_parent": v,
        "obligation_key": k,
        "amount_B": round(d.get("amount", 0.0) / 1e9, 2),
        "amount_type": d.get("amount_type"),
        "primary_type": d.get("primary_type"),
        "recourse": d.get("recourse")
    })
pd.DataFrame(collapsed_records).sort_values(by="amount_B", ascending=False)
"""))

# Cell 14: Markdown - Reachability vs Stress
cells.append(nbf.v4.new_markdown_cell("""## 5. Topological Reachability by Amount Type

In Phase 0.6, we eliminate naive cross-category dollar aggregation.
Summing non-fungible quantities ($34.2B purchase commitments + $11.0B lease + $35.5B debt principal) into a single dollar pool produces mathematically flawed ratios.
Instead, our Reachability Engine (`src/reachability.py`) reports dependency footprints **broken down strictly by `amount_type`** alongside edge count reachability:
"""))

# Cell 15: Code - Reachability Analysis
cells.append(nbf.v4.new_code_cell("""reach_engine = ContractualReachability(network=net)
reach_summary = reach_engine.run_standard_footprints()
reach_summary[[
    "scenario_id", "assumptions", "reachable_edges", "edge_reach_pct",
    "debt_principal_reach_pct", "purchase_commit_reach_pct", "lease_value_reach_pct", "revenue_reach_pct"
]]
"""))

# Cell 16: Code - Reachability Bar Chart
cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(11, 5))
reach_plot = reach_summary.sort_values(by="edge_reach_pct", ascending=True)
bars = ax.barh(reach_plot["scenario_id"].str.replace("REACH_", ""), reach_plot["edge_reach_pct"], color="#2c3e50", height=0.55)
ax.set_title("Assumption Dependency Footprint (% of Network Edges Reachable Within 2 Hops)", fontsize=12, fontweight="bold")
ax.set_xlabel("% of Contractual Edges Within Reachability Footprint")
ax.set_xlim(0, 115)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va="center", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.savefig(project_root / "outputs/figures/assumption_reachability_footprint.png", dpi=300)
plt.show()
"""))

# Cell 17: Markdown - Financial Stress Simulation
cells.append(nbf.v4.new_markdown_cell("""## 6. Parameterized Financial Stress Prototype

Using `src/stress.py`, we execute contract-calibrated transmission functions:
$$\text{Shock} \longrightarrow \Delta \text{ Cash Flow} \longrightarrow \text{Borrowing Base / Covenant Breach} \longrightarrow \text{Liquidity Cure} \longrightarrow \text{Next Edge}$$

We test five adversarial scenarios grounded in contractual terms:
1. **Modeled Borrowing Base Contraction (-40% GPU Collateral):**
   Evaluates CoreWeave's drawn DDTLs ($10.8B) against the contract-calibrated **71.42% borrowing base advance rate** (DDTL 5.0 formula), forcing a **$4.32B mandatory debt prepayment**, consuming 78.2% of CoreWeave's cash and triggering a capex freeze.
2. **Anchor Customer Concentration & Springing Guaranty (-30% Microsoft Off-Take):**
   Reduces CoreWeave's recognized annual cash flow by **$1.03B/yr**, causing an SPV colocation lease shortfall that satisfies the legal predicate triggering CoreWeave parent's **Unconditional Springing Guaranty** on the $11.0B lease.
3. **Credit Refinancing Spread Spike (+300 bps):**
   Rigorously isolates floating debt (adding **$324M/yr** cash interest to CRWV DDTLs and $14M to APLD corporate facilities) from fixed debt (APLD $4.5B notes and CRWV $20.8B notes are fixed coupons, experiencing zero immediate cash impact but facing rollover refinancing risk).
4. **Phased Grid Energization Delay (12 Months at Polaris Forge 1):**
   Models the operational reality: ~100 MW operational generates **$183.3M/yr** base rent ongoing, while the unenergized ~300 MW expansion is deferred ($550M rent delayed), leaving APLD to self-fund **$163M** in construction debt carrying costs (consuming only 10.2% of APLD cash).
5. **OEM Purchase Commitment Expected Loss (SMCI 15% Demand Pause):**
   Models Supermicro's $34.2B purchase commitments under US-GAAP NRV write-down (40% loss severity on $5.13B excess allocation), generating a **$2.05B pre-tax loss provision** consuming 27.3% of cash.
"""))

# Cell 18: Code - Execute Financial Stress
cells.append(nbf.v4.new_code_cell("""stress_engine = FinancialStressEngine(network=net)
stress_summary = stress_engine.run_all_stress_scenarios()

stress_display = stress_summary.assign(
    direct_hit_B=lambda df: (df["direct_cash_or_collateral_hit_usd"] / 1e9).round(2)
)[["scenario_name", "shock_parameter", "target_entity", "direct_hit_B", "covenant_or_liquidity_impact", "contagion_mechanism"]]
stress_display
"""))

# Cell 19: Code - Financial Stress Waterfall Plot
cells.append(nbf.v4.new_code_cell("""fig, ax = plt.subplots(figsize=(11, 5))
stress_plot = stress_summary.sort_values(by="direct_cash_or_collateral_hit_usd", ascending=True)
bars = ax.barh(stress_plot["scenario_name"], stress_plot["direct_cash_or_collateral_hit_usd"] / 1e9, color="#c0392b", height=0.55)
ax.set_title("Parameterized Financial Stress Prototype: Direct Cash or Collateral Impact ($ Billions)", fontsize=12, fontweight="bold")
ax.set_xlabel("Direct Cash / Collateral Drain ($ Billions)")

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.1, bar.get_y() + bar.get_height()/2, f"${w:.2f}B", va="center", fontsize=9, fontweight="bold", color="#922b21")

plt.tight_layout()
plt.savefig(project_root / "outputs/figures/financial_stress_waterfall.png", dpi=300)
plt.show()
"""))

# Cell 20: Markdown - Evidence Receipts
cells.append(nbf.v4.new_markdown_cell("""## 7. Verifiable Evidence Ledger (Audit Receipts)

Every contractual assertion in this notebook is backed by an audited SEC EDGAR citation in `data/processed/evidence_claims.parquet`.
Below are the exact verbatim excerpts and accession numbers proving the $11.0B Polaris Forge lease, the $35.551B debt structure, the SPV springing guaranty, the $34.2B SMCI commitments, and the 67% Microsoft concentration.
"""))

# Cell 21: Code - Inspect Evidence
cells.append(nbf.v4.new_code_cell("""claims_df = pd.read_parquet(project_root / "data/processed/evidence_claims.parquet")
claims_df[["claim_id", "entity_id", "filing_type", "filing_date", "section_locator", "exact_quote", "evidence_class"]]
"""))

# Cell 22: Markdown - Synthesis
cells.append(nbf.v4.new_markdown_cell("""## 8. Synthesis & Computational Sketchbook Findings

### What Phase 0.6 Established
1. **The Bubble Lives in the Joins:** On consolidated statements, Applied Digital appears as a standalone host with $1.59B in cash and $4.98B in debt. But through the join at Polaris Forge 1 ($11.0B 15-year lease with CoreWeave), APLD's cash flows are tied to CoreWeave's solvency.
2. **Perimeter Opacity & The Springing Guaranty:** CoreWeave did not simply isolate lease obligations in an SPV; it executed an **Unconditional Springing Guaranty of Payment and Performance**. If SPV VIII defaults on colocation rent, parent liability is reactivated.
3. **Decomposed Debt Realities:** CoreWeave's indebtedness is not a monolithic loan, but $35.551B across DDTLs ($10.8B drawn), senior notes ($10.0B), convertible debt ($6.6B), OEM financing ($4.2B), and Magnetar ($0.19B).
4. **Floating vs. Fixed Insulation:** Applied Digital's $4.50B in project notes and CoreWeave's $20.8B in senior/convertible notes bear fixed coupons, suffering zero immediate cash hit from rate spikes but facing maturity rollover risk.
5. **Modeled Borrowing Base Contraction:** A -40% GPU collateral haircut triggers a **$4.32B mandatory debt prepayment**, consuming 78.2% of CoreWeave's cash and forcing operational capex freezes down the supply chain.

### Next Steps for Phase 1
* Maintain epistemic discipline on the five-company pilot before expanding the universe.
* Incorporate FINRA TRACE secondary bond prices to observe real-time market-implied credit spreads.
* Refine contract-calibrated liquidity transmission functions.
"""))

nb.cells = cells

# Save notebook
with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Wrote unexecuted notebook to {NOTEBOOK_PATH.name}")

# Execute notebook
print("Executing notebook with nbconvert ExecutePreprocessor...")
ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
    nb_to_run = nbf.read(f, as_version=4)

ep.preprocess(nb_to_run, {"metadata": {"path": str(NOTEBOOK_DIR)}})

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb_to_run, f)

print(f"Successfully executed and saved {NOTEBOOK_PATH.name} with live outputs!")
