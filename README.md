# Risk-Based Lending and Interest Rate Estimation

ES 335 course project · John Shinoj (25110151)

**Website:** https://johnshinoj.github.io/credit-risk/
**Repository:** https://github.com/JohnShinoj/credit-risk

## What this project does

1. **Default:** predicts a calibrated **probability of default (PD)** for each loan applicant and declines applicants above a
   cutoff (classification; main metric F1, plus Brier score for the probabilities).
2. **Interest rate:** suggests an interest rate for approved applicants (regression; RMSE and R²).

Because the lender's **grade** and **interest rate** are themselves lender decisions, the project compares three settings that
differ in what is known when the decision is made:

| Setting | Known at decision time | Default model | Rate model |
|---|---|---|---|
| Reference: already-priced loan | details + grade + rate | Random Forest | none (rate known) |
| Pipeline A: graded applicant | details + grade | Random Forest | Random Forest regressor (grade + details) |
| Pipeline B: newcomer | details only | Random Forest | Random Forest regressor (PD + details) |

**Final test-set results** (20% hold-out, used once): default F1 0.838 / 0.837 / 0.699 (Reference / A / B); Brier 0.052 / 0.053 /
0.086; interest-rate R² 0.907 (A) and 0.305 (B). Full results, error analysis and limitations are on the website.

## Repository layout

```
notebooks/      12 Jupyter notebooks, run in order (see below)
src/credit.py   shared code: data loading, the 5 CV folds, preprocessing pipeline, exact cutoff search, calibration
src/export_site_data.py   exports the website's data and figures from the notebooks' saved outputs
reports/        chosen settings (JSON) and result tables (CSV) written by the notebooks; reports/figures/ = figures
docs/           the website (GitHub Pages): HTML pages, assets/, data/ (JSON exported from reports), figures/
data/           NOT in the repository (git-ignored); created by notebook 01 and later notebooks
requirements.txt  exact package versions used
```

## Setup

Python 3.13 (tested with 3.13.11) on Windows; any OS should work.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m ipykernel install --user --name ml-project-venv --display-name "ML project (.venv 3.13)"
```

The notebooks use the kernel **"ML project (.venv 3.13)"**; select it in Jupyter or VS Code.

## Data access

* **Credit Risk Dataset** by laotse on Kaggle: https://www.kaggle.com/datasets/laotse/credit-risk-dataset (public).
  Notebook 01 downloads it automatically with `kagglehub` (`kagglehub.dataset_download("laotse/credit-risk-dataset")`).
  If kagglehub asks for credentials, create a free Kaggle account and an API token (Kaggle → Settings → API), or download
  `credit_risk_dataset.csv` manually and point notebook 01 to it.
* **World Bank Open Data API** (no key needed): notebook 12 downloads US indicators `FR.INR.LEND` (lending interest rate) and
  `FP.CPI.TOTL.ZG` (inflation) with `requests`, and caches them in `data/processed/macro_worldbank_usa.csv`.
* The raw and processed data are not committed. No private data, credentials or API keys are stored in this repository.

## Run order

Run each notebook top to bottom from the `notebooks/` folder (or `jupyter nbconvert --to notebook --execute --inplace <file>`).
Later notebooks read files written by earlier ones. Times are on a 12-core laptop on mains power.

| # | Notebook | What it does | Time |
|---|---|---|---|
| 01 | `01_clean_split.ipynb` | download, cleaning (172 rows removed), stratified 80/20 split → `data/processed/train.csv`, `test.csv` | < 1 min |
| 02 | `02_probability_of_default.ipynb` | Reference: logistic regression, SMOTE, cutoff tuning, linear SVM, RBF SVM with C/γ grid search | ~35 min |
| 03 | `03_decision_trees.ipynb` | Reference: decision tree | ~1 min |
| 05 | `05_random_forest.ipynb` | Reference: bagging vs Random Forest, tuning, importance | ~10 min |
| 04 | `04_probability_of_default.ipynb` | Reference: calibrated PD for every model (**run after 03 and 05**) | ~5 min |
| 06 | `06_applicant_only_models.ipynb` | Pipeline B: all models without rate and grade, calibrated PD | ~15 min |
| 07 | `07_interest_rate_regression.ipynb` | Pipeline B: interest-rate regression (incl. gradient boosting, two-stage grade model) | ~5 min |
| 08 | `08_graded_applicant_models.ipynb` | Pipeline A: all models with grade but no rate, calibrated PD | ~45 min |
| 09 | `09_interest_rate_with_grade.ipynb` | Pipeline A: interest-rate regression with grade | ~7 min |
| 10 | `10_results_summary.ipynb` | all validation results in one place | ~1 min |
| 11 | `11_final_test.ipynb` | **final test set, used once**; error analysis; saves per-applicant test predictions | ~1 min |
| 12 | `12_macro_check.ipynb` | World Bank API check of the interest rates; website figures | ~1 min |

Then rebuild the website data: `python src/export_site_data.py`. To view the site locally:
`python -m http.server 8765 --directory docs` and open http://localhost:8765.

**Reproducibility notes.** All randomness uses seed 42. The train/test split is created once (notebook 01) and saved; every model
uses the same 5 stratified folds (`src/credit.make_cv`). All learned preprocessing (imputation, scaling, encoding, SMOTE) sits
inside scikit-learn / imbalanced-learn pipelines, so it is learned from training folds only. Every choice (hyperparameters, cutoffs,
calibration, models) is made with 5-fold cross-validation on the training set and saved in `reports/`; notebook 11 is the only
notebook that opens the test set.

## AI-use disclosure

**Tool used:** Claude (Anthropic), model Claude Opus 5.5, through the Claude Code desktop app, 7–17 November 2026.

**What I did myself.** Chose the topic and wrote the research questions and project proposal (data plan, baseline and candidate
methods, evaluation plan). Made the design decisions during the project: working step by step; the three settings (rate + grade
known, grade known, newcomer); which models and hyperparameters to tune; keeping the decision tree as a final-model candidate;
excluding the grade from newcomer pricing; trimming the tree and forest experiments; deferring SMOTENC; the World Bank check.
Reviewed every step's code and results, ran the notebooks, asked questions until I understood each method (cross-validation,
SMOTE, cutoff tuning, calibration, Brier score, bagging, regression metrics), and approved each change before it was made.

**What the AI assistant did.** Wrote most of the Python code in the notebooks and in `src/` following my instructions and
approvals; explained the theory behind each method and proposed options that I chose between; ran the notebooks to check they
worked and found and fixed errors (for example a leakage risk when using PD as an input to the rate model, and a conclusion about
Pipeline B that the data contradicted); drafted the text of the website and this README, which I reviewed and edited.

**How I checked it.** Every number on the website comes from the notebooks in this repository and can be reproduced by running
them. The test set was used once, after all choices were frozen (notebook 11). All conclusions, and any errors, are my
responsibility.

## Citations

* laotse. *Credit Risk Dataset*. Kaggle. https://www.kaggle.com/datasets/laotse/credit-risk-dataset
* World Bank Open Data API: FR.INR.LEND, FP.CPI.TOTL.ZG (United States). https://data.worldbank.org
* Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR* 12, 2825–2830.
* Lemaître, G., Nogueira, F., Aridas, C. (2017). Imbalanced-learn. *JMLR* 18(17), 1–5.
* Chawla, N. V. et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. *JAIR* 16, 321–357.
* Breiman, L. (2001). Random Forests. *Machine Learning* 45, 5–32.
* Cortes, C., Vapnik, V. (1995). Support-vector networks. *Machine Learning* 20, 273–297.
* Platt, J. (1999). Probabilistic outputs for support vector machines. *Advances in Large Margin Classifiers*.
* Zadrozny, B., Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. *KDD*.
* Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review* 78(1).
* Bergstra, J., Bengio, Y. (2012). Random search for hyper-parameter optimization. *JMLR* 13, 281–305.
* Lipton, Z. C., Elkan, C., Narayanaswamy, B. (2014). Optimal thresholding of classifiers to maximize F1. *ECML PKDD*.
* James, G., Witten, D., Hastie, T., Tibshirani, R. *An Introduction to Statistical Learning*. Springer.
* Software: pandas, NumPy, SciPy, Matplotlib, Seaborn, Jupyter, requests, kagglehub; Plotly.js for the website's interactive charts.
* AI assistance: Claude (Anthropic); see the AI-use disclosure above.
