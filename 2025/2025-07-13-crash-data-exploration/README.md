# Traffic Crash Data Exploration — Rapid DOT Crash Analytics (July 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / VOLUMETRIC SCAFFOLDING ARTIFACT]`  
> **Date:** July 13, 2025 (~75 minute sprint)  
> **Stack:** Python 3, Pandas, NumPy, Matplotlib, Seaborn  

---

## 1. What Was the Idea?
A rapid exploratory probe examining a Department of Transportation (DOT) crash-data snapshot dated July 12, 2025, breaking down temporal patterns, severity, environmental conditions, and Kansas City geographic subsets, alongside an exploratory forecast for the remainder of 2025.

---

## 2. What Was Actually Built?
Despite the repository's historical title (`ML_Playground`), the project contained **no machine learning models** (no scikit-learn, PyTorch, or XGBoost dependencies). It generated over 150 KB of descriptive analytical classes across ~75 minutes:
- `crash_exploration.py`: Broad descriptive metrics (fatalities, injuries, vehicle counts, weather conditions, lighting, and time-of-day distributions).
- `kansas_city_analysis.py`: Regional subsetting and comparative metrics for the Kansas City metropolitan area.
- `quick_2025_prediction.py`: A 3-heuristic exploratory forecast:
  1. Fraction-of-year elapsed linear extrapolation: $\text{count} \times \frac{365}{\text{days elapsed}}$
  2. Recent monthly seasonal additions: $\text{count} + \text{avg remaining monthly counts (2020--2024)}$
  3. Recent 5-year annual average comparison.
  4. Final projection selected via $\max(\text{seasonal\_prediction}, \text{recent\_yearly\_avg})$.

---

## 3. Archaeological Significance & Epistemic Warning: Volumetric Scaffolding

> [!NOTE]
> **Exploratory, Non-Authoritative Findings:**  
> The generated analyses and forecasts should be treated as disposable exploratory scaffolding rather than vetted statistical research.

### Identified Methodological Defects:
1. **Geographic Conflation (Kansas City Filter):** The filtering query flagged records where either the crash city OR `CRASH_CARRIER_CITY` matched `"KANSAS CITY"` or `"KC"`. This conflated the motor carrier's corporate registration address with the actual physical crash site.
2. **Unreproducible Exposure Clock:** The forecasting script evaluated elapsed days via `datetime.now()` rather than anchoring to the fixed cutoff date of the underlying snapshot (July 12, 2025), causing reruns on later dates to yield shifting exposure windows.
3. **Biased Heuristic Selection:** Taking the maximum of two estimates systematically biased the final projection upward without statistical justification.

---

## 4. The Methodological Lesson: The Volumetric Scaffolding Phenomenon

This experiment illustrates a defining characteristic of the AI-accelerated era:
- **Code Volume $\neq$ Intellectual Depth:** AI copilots can generate massive, multi-panel plotting classes, dashboards, and complex analytical breakdowns within an hour.
- **Contrast with `mo_data_analysis`:** While `mo_data_analysis` showed that AI can make flawed modeling look miraculously successful ($R^2 \approx 0.99$), `ML_Playground` shows that AI can make a casual 1-hour data curiosity look like a massive enterprise analytical system simply through volumetric boilerplate generation.
