# Calculation Logic

## Percentages
- **Assignment %** = (earned / possible) × 100
- **Weighted average** = sum(assignment% × weight) / sum(weights)
- Round displayed values to 2 decimals

## Grade scale (default)
- A: 90–100, B: 80–89, C: 70–79, D: 60–69, F: < 60

## Categories
- Compute category averages and apply category weights to overall grade
- Handle missing categories by 0% or redistribute (document chosen rule)

## “What do I need?”
Given a **target grade** and the **remaining weight**, solve for the required average on remaining work.  
If unattainable, clearly indicate that and offer scenario comparisons.

## Edge cases
- Division by zero (no assignments or possible=0): show friendly message
- Missing weights: fall back to simple average or prompt user to set weights
