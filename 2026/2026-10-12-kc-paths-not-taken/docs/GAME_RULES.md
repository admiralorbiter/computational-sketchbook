# KC Pathways — Formal Game Rules & State Transitions

**Specification Version:** 0.1.0  
**Engine Domain:** Pure deterministic state machine (no randomness in Slice 01)  

---

## 1. Mathematical State Machine Formulation

The game state is a 6-tuple:
$$\mathcal{S} = \langle r, a_p, \tau, \mathcal{C}, \mathcal{H}, \sigma \rangle$$

Where:
- $r \in \{1, 2, 3\}$: Current planning round.
- $a_p \in \{0, 1, 2\}$: Action points available in the current round.
- $\tau \in \{\text{reliable}, \text{needs-coordination}\}$: Fixed transportation condition.
- $\mathcal{C} \subseteq \mathcal{A}_{\text{catalog}}$: Set of completed action IDs.
- $\mathcal{H} = [e_1, e_2, \dots, e_k]$: Chronological event history log.
- $\sigma \in \{\text{playing}, \text{finished}\}$: Terminal game status.

### Initial State
$$\mathcal{S}_0(\tau) = \langle 1, 2, \tau, \emptyset, [], \text{playing} \rangle$$

---

## 2. Action Precondition Functions

For each candidate action $\alpha \in \mathcal{A}_{\text{catalog}}$, the feasibility predicate $\text{Available}(\alpha, \mathcal{S})$ holds if and only if all of the following conditions are met:
1. $\sigma = \text{playing}$ (game is active).
2. $\alpha \notin \mathcal{C}$ (action has not been completed previously).
3. $r \ge \alpha.\text{round\_available}$ (round temporal gate is satisfied).
4. $\alpha.\text{requires} \subseteq \mathcal{C}$ (all structural prerequisite actions are completed).
5. If $\alpha.\text{requires\_transport\_investigation} = \text{true}$ and $\tau = \text{needs-coordination}$, then $\text{investigate\_transport} \in \mathcal{C}$.
6. If $\alpha.\text{requires\_transport\_profile} \ne \text{null}$, then $\tau = \alpha.\text{requires\_transport\_profile}$.
7. $a_p \ge \alpha.\text{cost\_ap}$ (player has sufficient AP in the current round).

---

## 3. State Transition Operators

### 3.1. Apply Action: $\text{Execute}(\mathcal{S}, \alpha) \to \mathcal{S}'$
When valid action $\alpha$ is executed:
- $a_p' = a_p - \alpha.\text{cost\_ap}$
- $\mathcal{C}' = \mathcal{C} \cup \{\alpha.\text{id}\}$
- $\mathcal{H}' = \mathcal{H} \mathbin{\Vert} [\text{Event}(r, \alpha.\text{id}, \alpha.\text{title}, a_p')]$
- If $a_p' = 0$ and $r = 3$, check if further actions are possible. If no actions are available, or player explicitly ends round, advance to $\sigma = \text{finished}$.

### 3.2. Advance Round: $\text{NextRound}(\mathcal{S}) \to \mathcal{S}'$
When the player concludes the current round $r$:
- If $r < 3$:
  - $r' = r + 1$
  - $a_p' = 2$ (unspent AP does NOT carry over)
  - $\mathcal{H}' = \mathcal{H} \mathbin{\Vert} [\text{RoundSummary}(r)]$
- If $r = 3$:
  - $\sigma' = \text{finished}$
  - Evaluate terminal outcome.

---

## 4. Terminal Evaluation Function

$$\text{EvaluateOutcome}(\mathcal{S}) = \begin{cases}
\text{health\_start\_prepared} & \text{if } \text{prepare\_health\_start\_inquiry} \in \mathcal{C} \\
\text{postgrad\_plan\_prepared} & \text{if } \text{draft\_postgrad\_plan} \in \mathcal{C} \\
\text{still\_exploring} & \text{otherwise}
\end{cases}$$

Note: If both were completed (impossible under 6 AP budget, but mathematically provable), `health_start_prepared` takes priority.

---

## 5. Counterfactual Analysis & AP Budget Proof

### Budget: 6 AP Maximum (3 rounds $\times$ 2 AP)

#### Path 1: Health Start Academy
- With $\tau = \text{reliable}$:
  1. Round 1: `speak_counselor` (1 AP) + `investigate_health_start` (1 AP) $\implies a_p=0$.
  2. Round 2: `prepare_health_start_inquiry` (2 AP) $\implies a_p=0$. **Plan Complete!**
  3. Round 3: 2 AP free to explore `explore_mcc_health` (1 AP) + `compare_college_options` (1 AP).
  Total AP spent on Health Start: **4 AP**.

- With $\tau = \text{needs-coordination}$:
  1. Round 1: `speak_counselor` (1 AP) + `investigate_health_start` (1 AP) $\implies a_p=0$.
  2. Round 2: `investigate_transport` (1 AP) $\implies a_p=1$. (Player cannot run a 2 AP action with 1 AP remaining, so 1 AP is lost or must be spent on MCC if available).
     - Or Round 2: `explore_mcc_health` (1 AP) + `investigate_transport` (1 AP).
  3. Round 3: `prepare_health_start_inquiry` (2 AP). **Plan Complete!**
  Total AP spent on Health Start: **5 AP**.

#### Path 2: Postsecondary MCC Route
1. Round 1: Research actions (e.g. `speak_counselor`, `investigate_health_start`).
2. Round 2: `explore_mcc_health` (1 AP) + `compare_college_options` (1 AP).
3. Round 3: `draft_postgrad_plan` (1 AP) + 1 AP remaining for other tasks.
Total AP spent on MCC: **3 AP**.

#### Mutual Exclusivity of Complete Plans
$$\text{Cost}(\text{Health Start}) + \text{Cost}(\text{MCC Postgrad}) \ge 4 + 3 = 7 \text{ AP} > 6 \text{ AP}$$
Therefore, the player cannot fully complete both terminal pathway inquiries in a single 6-AP playthrough. This mathematical property guarantees authentic decision tradeoffs.
