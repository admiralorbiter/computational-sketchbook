# Missouri Data Analysis — AI-Accelerated Data-Science Sketch (April 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / METHODOLOGICAL ARTIFACT]`  
> **Date:** April 6, 2025 (~4 hour sprint)  
> **Stack:** Python 3, Pandas, Scikit-learn, XGBoost, LightGBM, PyTorch, Folium, Matplotlib, Seaborn  

---

## 1. What Was the Idea?
An exploratory data science sprint examining Missouri ZIP Code Tabulation Area (ZCTA) demographic, housing, education, and socioeconomic data (`mo.csv`) to test how rapidly an AI assistant could drive an end-to-end analytical pipeline from data inspection to machine learning modeling and deployment.

---

## 2. What Was Built (The 8-Step Pipeline)?
In under four hours, the workflow progressed through 8 escalating scripts:
1. `step1.py`: Initial data inspection, summary statistics, skewness, missingness, and median imputation.
2. `step2.py`: Univariate distribution plotting, boxplots, and within-domain correlation heatmaps.
3. `step3.py`: Automated variable categorization and bivariate/multivariate OLS regressions.
4. `step4.py`: Geospatial mapping using a hand-coded ZIP prefix lookup dictionary to plot regional coordinates.
5. `step5.py`: Global correlation matrix across all numeric features.
6. `step6.py`: Baseline Machine Learning for Mean Income and Disability Rate (Linear Regression, Random Forest, Gradient Boosting).
7. `step7.py`: Advanced Nonlinear Models & Deep Learning (XGBoost, LightGBM, Multi-Layer Perceptron, Voting Ensemble).
8. `step8.py`: "Production" model serialization (`.pkl`), feature importance analysis, and sample inference.

---

## 3. Archaeological Significance & Epistemic Warning: Target Leakage

> [!CAUTION]
> **Analytically Invalid Final Prediction Model:**  
> The advanced models in `step7.py` and `step8.py` report seemingly miraculous performance ($R^2 \approx 0.9883$). These metrics are an artifact of **severe target leakage** rather than predictive power.

### The Leakage Forensic:
- **Baseline Models (`step6.py`):** Correctly reported that demographic variables alone explained only $\sim 18\%$ of out-of-sample income variance ($R^2 = 0.1795$ for Linear Regression, $R^2 = -0.0028$ for tuned Gradient Boosting).
- **Advanced Feature Engineering (`step7.py`):** Created features directly derived from the target variable `Households Mean income (dollars)`:
  $$\text{Log\_Income} = \log(1 + \text{Households Mean income})$$
  $$\text{Income\_Per\_Capita} = \frac{\text{Households Mean income}}{\text{Households Total}}$$
- **The Result:** The model was handed a mathematical transformation of the exact ground truth it was asked to predict, shooting $R^2$ to $0.9883$.
- **The Serialized Model:** `step8.py` trained this leaked ensemble over the full dataset and generated high-precision sample predictions (predicting $\$75,827$ for a $\$76,285$ row), illustrating how unvalidated models can easily masquerade as working production systems.

---

## 4. The Methodological Lesson: The Inversion of Stopping Rules

This experiment serves as a textbook specimen of early AI-assisted data science:
- **The Velocity Collapse:** When AI makes escalating from descriptive stats to gradient boosting to deep ensembles take 11 minutes, developer friction ceases to constrain technical complexity.
- **The Shift in Scarcity:** The bottleneck is no longer the ability to write machine learning code—it is the **epistemic discipline to verify validity, check causal assumptions, and enforce stopping rules**.
