# Can't Stop Pairing Heuristics (m1 & m2)

> **Category:** `[SKETCHBOOK EXPERIMENT / HEURISTIC PROBE]`  
> **Date:** 2024-07-13  
> **Origin:** Direct implementation of pairing heuristics from Canakci et al. (~2016)  

---

## 1. Overview

Interactive terminal companion tools designed to assist in real-time Can't Stop play by computing the optimal way to pair 4 rolled dice into 2 column sums.

Derived from the research report *"The Can't Stop Game"* by Burcu Canakci, Sofia Serrano, Olivia Roy, and Dr. Clyde Kruskal (University of Maryland, College Park).

---

## 2. Included Tools

### `m1-relative-final-progress.py`
Implements the **Relative Final Progress** heuristic ($m_1$). Given candidate column pairs, it scores each choice by the normalized progress across target columns:

$$\text{Score}(O) = \sum_{c \in O} \frac{\text{progress}(c)}{\text{length}(c)}$$

It picks the pairing maximizing this ratio, favoring short outer columns when progress has already begun or central columns when advancing rapidly.

### `m2-algorithm.py`
Implements the **Stuck-Penalty** heuristic ($m_2$). In addition to relative progress, it tracks opponent marker locations. If a candidate column currently holds an opponent permanent tile, it scales the score by the probability of escaping/passing the opponent.

---

## 3. Usage & Interactive CLI Format

Both scripts run as interactive REPLs:

```bash
python m1-relative-final-progress.py
# or
python m2-algorithm.py
```

### Input Conventions:
1. **Board State:** Enter 11 integers representing marker advancement in columns 2 through 12.
   ```text
   0 0 1 2 0 4 0 1 0 0 0
   ```
2. **Opponent Board State** (`m2` only): Same 11-integer format for the opponent's markers.
3. **Candidate Pairs:** Formatted as comma-separated pairs or two-digit combinations:
   ```text
   8,7 96 410 5
   ```
4. **Turn Decision:** Enter `b` (busted), `s` (stopped and banked progress), or `c` (rolled again and continued).

---

## 4. Algorithmic Audit Notes

1. **Simplicity vs. Complexity ($m_1$ vs $m_2$):** Canakci et al. simulated 1,000 games head-to-head between $m_1$, $m_2$, and $m_3$. They found no statistically significant difference in win rates, but $m_1$ ran twice as fast. Consequently, their advanced Monte Carlo rollout engine used $m_1$ exclusively.
2. **2-Dice vs. 4-Dice Probabilities in `m2`:** The implementation in `m2-algorithm.py` defines `probabilities` using standard 2-dice distribution tables (`7: 6/36 = 16.7%`). However, in Can't Stop, 4 dice are rolled and grouped, making the true probability of forming a 7 equal to $64.3\%$.
3. **Stuck Multiplier:** The script multiplies score by `(1 - p_stuck)`, penalizing columns that have a higher chance of rolling the matching number, whereas the paper describes scaling by the probability of successfully moving off the tile.

---

## 5. Cross-Repository Links

- **Theoretical Synthesis & Academic Citations:** See Big Brain Time at `research/cant-stop-computational-heuristics.md`.
- **Precursor Repository:** `admiralorbiter/cant_stop_research` (2022-2023).
- **Subsequent Web Coach:** `computational-sketchbook/2025/2025-08-10-cant-stop-coach/`.
