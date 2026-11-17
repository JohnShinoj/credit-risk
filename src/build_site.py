"""Builds the 8 HTML pages of the project website (shared header, menu and footer).

Usage (from the repository root):  python src/build_site.py docs
The pages read their data and figures from docs/data and docs/figures, written by src/export_site_data.py.
All text and numbers on the pages are in this file; every number comes from the notebooks' saved outputs.
"""
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "docs")
REPO = "https://github.com/JohnShinoj/credit-risk"
NBLINK = REPO + "/blob/main/notebooks/"
PLOTLY = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>'

PAGES = [("index.html", "Overview"), ("data.html", "Data"), ("method.html", "Method"),
         ("evaluation.html", "Evaluation"), ("results.html", "Results"), ("explore.html", "Explore"),
         ("analysis.html", "Result analysis"), ("limitations.html", "Limitations & reproduce")]


def repo(path, label=None):
    kind = "tree" if path.endswith("/") or "." not in path.split("/")[-1] else "blob"
    return f'<a href="{REPO}/{kind}/main/{path.rstrip('/')}" target="_blank" rel="noopener">{label or path}</a>'


def nb(name, label=None):
    return f'<a href="{NBLINK}{name}" target="_blank" rel="noopener">{label or name}</a>'


def page(fname, title, body, scripts=""):
    i = [p[0] for p in PAGES].index(fname)
    if fname in ("method.html", "evaluation.html", "results.html", "explore.html", "analysis.html"):
        # key to the three settings, right after the page's lead paragraph
        body = body.replace("</p>", "</p>" + SETTINGS_KEY, 1)
    nav = "".join(f'<a href="{f}"{" class=active" if f == fname else ""}>{t}</a>' for f, t in PAGES)
    prev_ = f'<a href="{PAGES[i-1][0]}">← {PAGES[i-1][1]}</a>' if i > 0 else "<span></span>"
    next_ = f'<a href="{PAGES[i+1][0]}">{PAGES[i+1][1]} →</a>' if i < len(PAGES) - 1 else "<span></span>"
    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Risk-Based Lending</title>
<meta name="description" content="ES 335 project: predicting loan default and estimating interest rates for three lending settings.">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="site"><div class="inner">
<a class="brand" href="index.html">Risk-Based Lending &amp; Interest Rate Estimation<small>ES 335 · John Shinoj (25110151)</small></a>
<nav class="tabs">{nav}</nav></div></header>
<main>
{body}
<div class="pager">{prev_}{next_}</div>
</main>
<footer>Code, notebooks and full results: <a href="{REPO}" target="_blank" rel="noopener">{REPO}</a>.
Every number on this site is produced by the notebooks in that repository.</footer>
{scripts}
</body></html>
"""
    (OUT / fname).write_text(html, encoding="utf-8")
    print("wrote", OUT / fname)


SETTINGS_KEY = """<div class="note"><b>The three settings compared on this site</b> (they differ only in what is known when the
decision is made):<br>
<span class="tag ref">Reference</span> a loan that is <b>already priced</b>: the applicant's grade and the interest rate are both known.<br>
<span class="tag A">Pipeline A</span> a <b>graded applicant</b>: the applicant has a grade (A–G, a credit-history rating like a credit score), the interest rate is not set yet.<br>
<span class="tag B">Pipeline B</span> a <b>newcomer</b>: no grade and no rate, only what the applicant tells us.<br>
<a href="index.html#why-three">Why we compare all three →</a></div>"""


def fig(name, caption, width=None):
    w = f' style="max-width:{width}px"' if width else ""
    return f'<figure><img src="figures/{name}.png" alt="{caption}" loading="lazy"{w}><figcaption>{caption}</figcaption></figure>'


SETTINGS_TABLE = f"""
<div class="table-wrap"><table>
<tr><th>Setting</th><th>Who it is for</th><th>Known when the decision is made</th><th>Predicts</th><th>Notebooks</th></tr>
<tr><td><span class="tag ref">Reference</span></td><td>A loan that is already priced (e.g. monitoring existing loans)</td><td>applicant details + <b>grade</b> + <b>interest rate</b></td><td>probability of default only (the rate is already set)</td><td>{nb("02_probability_of_default.ipynb", "02")}, {nb("03_decision_trees.ipynb", "03")}, {nb("05_random_forest.ipynb", "05")}, {nb("04_probability_of_default.ipynb", "04")}</td></tr>
<tr><td><span class="tag A">Pipeline A</span> graded applicant</td><td>An applicant who already has a grade A–G (a credit-history rating), rate not yet decided</td><td>applicant details + <b>grade</b></td><td>probability of default → approve/decline → interest rate</td><td>{nb("08_graded_applicant_models.ipynb", "08")} (default), {nb("09_interest_rate_with_grade.ipynb", "09")} (rate)</td></tr>
<tr><td><span class="tag B">Pipeline B</span> newcomer</td><td>A brand-new applicant with no grade and no rate</td><td>applicant details only</td><td>probability of default → approve/decline → interest rate</td><td>{nb("06_applicant_only_models.ipynb", "06")} (default), {nb("07_interest_rate_regression.ipynb", "07")} (rate)</td></tr>
</table></div>
<p style="font-size:14px;color:var(--muted)">All three are evaluated together on the test set in {nb("11_final_test.ipynb", "notebook 11")};
{nb("10_results_summary.ipynb", "notebook 10")} collects every validation result.</p>"""

# =====================================================================================
page("index.html", "Overview", f"""
<h1>Who will default, and what interest rate should they pay?</h1>
<p class="lead">Predicting loan default and suggesting a risk-based interest rate, and measuring how much the answer depends on
what the lender already knows about the applicant.</p>

<div class="card">
<h3 style="margin-top:0">The two research questions</h3>
<ol>
<li><b>Default:</b> given what is known about a loan applicant, how likely are they to default? We predict a calibrated
<b>probability of default (PD)</b> for every applicant and decline those above a cutoff.</li>
<li><b>Interest rate:</b> for applicants who are approved, what interest rate fits their risk?</li>
</ol>
<p style="margin-bottom:0"><b>Unit:</b> one row = one loan applicant (one loan). <b>Targets:</b> <code>loan_status</code>
(1 = defaulted, 0 = repaid) and <code>loan_int_rate</code> (% per year).</p>
</div>

<div class="card">
<h3 style="margin-top:0">How a decision is made</h3>
<p class="src">Source: {nb("11_final_test.ipynb")} (decisions on the test set); cutoff search: {repo("src/credit.py")} (<code>best_cutoff</code>)</p>
<pre style="background:#f7f7f5;border:1px solid var(--line);border-radius:8px;padding:10px;overflow-x:auto;font-size:13px;margin:6px 0 10px">
applicant ──► model ──► probability of default (PD), e.g. 0.12
                              │
              PD ≥ cutoff ?  ─┤── yes ──► DECLINE (no rate offered)
                              │
                              └── no ───► APPROVE ──► rate model ──► suggested interest rate, e.g. 11.4%</pre>
<ul style="margin-bottom:0">
<li><b>Probability of default (PD):</b> a calibrated probability from a Random Forest: among applicants given PD 0.30, about 30%
actually default.</li>
<li><b>Approve / decline:</b> decline when PD is at or above the <b>cutoff</b>. Each setting's cutoff was chosen on the training
set as the one with the highest F1, then frozen: <span class="tag ref">Reference</span> 0.378, <span class="tag A">Pipeline A</span>
0.367, <span class="tag B">Pipeline B</span> 0.388. On the test set this approves about 83% of applicants.</li>
<li><b>Interest rate:</b> only approved applicants get a suggested rate (Pipelines A and B; in the Reference the rate is already set).
The rate model is a <b>Random Forest regressor</b> trained on past loans and the rates actually charged. It suggests the rate that
<b>similar past borrowers paid</b>: in <span class="tag A">Pipeline A</span> it uses the grade + applicant details, in
<span class="tag B">Pipeline B</span> the PD + applicant details (no grade). It learns from <b>all</b> past loans with a
recorded rate, not only approved ones; the cutoff decides only <i>whether</i> a rate is offered. So it reproduces the lender's
past pricing; it does not calculate a break-even or profit-maximising rate.</li>
<li>You can move the cutoff yourself and browse individual decisions on the <a href="explore.html">Explore</a> tab.</li>
</ul>
</div>

<div class="card">
<h3 style="margin-top:0">What is a loan grade?</h3>
<p>Every applicant has a <b>risk grade from A (safest) to G (riskiest)</b>. The grade is a <b>combined evaluation of the
applicant's credit history</b> (for example past defaults and repayment record), summarised in one letter, much like a
credit score such as <b>CIBIL</b> in India or FICO in the US. The grade then largely decides the interest rate
(averages we calculated from the dataset's 29,315 cleaned loans that have a recorded rate):</p>
<div class="table-wrap"><table>
<tr><th>Grade</th><th class="num">A</th><th class="num">B</th><th class="num">C</th><th class="num">D</th><th class="num">E</th><th class="num">F</th><th class="num">G</th></tr>
<tr><td>Average interest rate (calculated by us from the data)</td><td class="num">7.3%</td><td class="num">11.0%</td><td class="num">13.5%</td><td class="num">15.4%</td><td class="num">17.0%</td><td class="num">18.6%</td><td class="num">20.3%</td></tr>
<tr><td>Share who defaulted (calculated by us from the data)</td><td class="num">10%</td><td class="num">16%</td><td class="num">21%</td><td class="num">59%</td><td class="num">65%</td><td class="num">70%</td><td class="num">98%</td></tr>
</table></div>
<p style="margin-bottom:0">Because it packs the whole credit history into one value, the grade is the most informative single
input for the interest rate and adds a lot to default prediction. Like a credit score, we treat it as <b>universal and available
when someone applies</b>. The dataset does not document how the grade was produced, so this is an assumption. Someone with no
credit history yet (a newcomer) has no grade, which is the situation of Pipeline B.</p>
</div>

<h2>Three settings: what is known at decision time?</h2>
<p>The dataset contains each loan's <b>grade</b> (A–G) and <b>interest rate</b>. The rate is set by the lender and the grade
exists only once the applicant has a credit history, so a model may only use them if they would really be known when the
prediction is made. That is why we built three settings:</p>
{SETTINGS_TABLE}

<h2 id="why-three">Why compare all three?</h2>
<p class="src">Source: pipelines in {nb("06_applicant_only_models.ipynb", "nb 06")}–{nb("09_interest_rate_with_grade.ipynb", "09")}; two-stage grade model: {nb("07_interest_rate_regression.ipynb")}</p>
<p>A lender meets applicants at different stages, and what is known about them differs. Each pipeline answers the question
for one stage, and each has a clear role:</p>
<div class="table-wrap"><table>
<tr><th>Pipeline</th><th>Role in this project</th></tr>
<tr><td><span class="tag A">Pipeline A</span> graded applicant</td><td><b>Main pipeline for pricing.</b> Grade + details → PD → approve/decline →
interest rate. This assumes the grade is <b>universal and available when someone applies</b>, like a credit score (e.g. CIBIL)
that any lender can look up, rather than a rating only this lender assigns after its own assessment.
The dataset does not say how the grade was produced, so this is an assumption.</td></tr>
<tr><td><span class="tag B">Pipeline B</span> newcomer</td><td><b>Fallback</b> for applicants without a grade (for example no credit history yet).
It also shows how much the grade is worth: without it, default prediction and pricing are much weaker. To see whether
we could get a higher score, we also tried predicting the grade first from the applicant's details and then the rate (a two-stage
model). It did not increase the score (rate R² 0.303 vs 0.305 without it): the grade was guessed correctly only 49% of the time.</td></tr>
<tr><td><span class="tag ref">Reference</span> already-priced loan</td><td><b>Upper bound and model selection.</b> With grade and rate both known it shows the best
this data allows (e.g. for checking loans already on the books), and it is where all the models were first compared.</td></tr>
</table></div>
<p>Why keep them separate rather than build one model:</p>
<div class="card">
<ol style="margin:0">
<li><b>A model may only use what is known when the decision is made.</b> The interest rate is decided by the
lender, and a grade exists only for applicants with a credit history. Using them for an applicant who has no grade or has not
been priced yet would be cheating (information leakage), and the
results would look better than any real system could achieve. Each setting uses only what is truly available at its moment
in the lending process.</li>
<li><b>Each setting is a real situation a lender faces.</b> <span class="tag ref">Reference</span> checking the risk of loans
already on the books; <span class="tag A">Pipeline A</span> pricing an applicant who has been graded; <span class="tag B">Pipeline B</span>
deciding on a brand-new applicant (the situation of our interactive tools and of a real application form).</li>
<li><b>Predicting the rate must not use the rate.</b> The interest-rate models are part of Pipelines A and B only, and their
probability-of-default inputs come from models that never saw the rate; otherwise the answer would be hidden in the input.</li>
<li><b>The gap between the settings is itself a finding.</b> Comparing them measures how much the grade and the rate are
worth: Reference vs A shows what the interest rate adds once the grade is known (almost nothing); A vs B shows what the grade
adds (a lot: default F1 0.84 → 0.70, rate R² 0.91 → 0.31). Note that Pipeline A's rate accuracy (R² 0.91) reflects how
<i>this</i> lender priced its loans from its grade; another lender may follow the grade less closely.</li>
<li><b>The Reference setting is the upper bound.</b> With everything known it shows the best performance this data allows, and
it is where all the models were first compared before the choice was confirmed in A and B.</li>
</ol>
</div>

<h2>Headline results (final test set, used once)</h2>
<p class="src">Source: {nb("11_final_test.ipynb")}; table: {repo("reports/final_test_headline.csv")}</p>
<div class="grid three">
<div class="card kpi"><span class="tag ref">Reference</span><div class="v">0.838</div><div class="l">default F1 (Random Forest)<br>Brier 0.052 · ROC-AUC 0.942</div></div>
<div class="card kpi"><span class="tag A">Pipeline A</span><div class="v">0.837 · R² 0.907</div><div class="l">default F1 · interest-rate R²<br>rate error ±0.99 pp</div></div>
<div class="card kpi"><span class="tag B">Pipeline B</span><div class="v">0.699 · R² 0.305</div><div class="l">default F1 · interest-rate R²<br>rate error ±2.70 pp</div></div>
</div>
<div class="card">
<h3 style="margin-top:0">How to read these numbers</h3>
<ul style="margin-bottom:0">
<li><b>F1</b> (default, 0 to 1, higher is better): how well the model catches defaulters <i>without</i> wrongly declining good
customers. It balances <i>precision</i> (of those declined, the share who really default) and <i>recall</i> (of all defaulters,
the share caught).</li>
<li><b>Brier score</b> (default, 0 to 1, lower is better): how accurate the predicted probability of default is, the average of
(predicted probability − what happened)², where what happened is 1 for a default and 0 for repaid. A PD of 0.9 for someone who
defaults is a small error (0.01); a PD of 0.1 for them is a large one (0.81). Guessing the average default rate (0.219) for
everyone scores 0.171.</li>
<li><b>R²</b> (interest rate, 0 to 1, higher is better): the share of the differences in interest rates between borrowers that the
model explains. R² = 0.9 means 90% is explained; R² = 0 is no better than giving everyone the average rate.</li>
<li><b>± pp</b> (interest rate): the typical error of the suggested rate (RMSE) in percentage points, e.g. ±2.70 pp means a
suggestion of 11% is typically off by about 2.7 points.</li>
<li><b>ROC-AUC</b> (default, 0.5 to 1): how well risky applicants are ranked above safe ones; 0.5 is random.</li>
</ul>
</div>
<div class="note good"><b>Main finding.</b> The grade, a one-letter summary of the applicant's credit history, carries almost all the useful information. Knowing only the grade
(Pipeline A) predicts default as well as knowing grade and rate together, and explains 91% of the variation in rates. For a
newcomer without a grade (Pipeline B), default prediction drops to F1 0.70 and only 30% of rate variation can be explained:
the limit is the information available, not the choice of model.</div>
<p>Baselines for comparison: predicting "everyone repays" gives F1 = 0 (accuracy 78%); guessing the average default rate for
everyone gives Brier 0.171; guessing the average interest rate gives an error of ±3.24 pp (R² = 0).</p>

<h2>How to read this site</h2>
<div class="table-wrap"><table>
<tr><th>Tab</th><th>What you will find</th></tr>
<tr><td><a href="data.html">Data</a></td><td>Source, what a row is, variables, cleaning and quality issues</td></tr>
<tr><td><a href="method.html">Method</a></td><td>Preprocessing and why, the leak-free pipeline, baseline and models compared</td></tr>
<tr><td><a href="evaluation.html">Evaluation</a></td><td>Train/test split, cross-validation, cutoff tuning, calibration, the metrics and why</td></tr>
<tr><td><a href="results.html">Results</a></td><td>Validation and test results, an interactive comparison of every model, the World Bank check</td></tr>
<tr><td><a href="explore.html">Explore</a></td><td><b>Interactive:</b> move the decision cutoff on the test set; browse real test applicants and the models' decisions</td></tr>
<tr><td><a href="analysis.html">Result analysis</a></td><td>Why each result happens, in plain words, with the evidence</td></tr>
<tr><td><a href="limitations.html">Limitations &amp; reproduce</a></td><td>What the results do not show, how to rerun everything, AI-use disclosure, citations</td></tr>
</table></div>
<div class="card">
<h3 style="margin-top:0">Check everything in the repository</h3>
<p>This site summarises the work; the repository <a href="{REPO}" target="_blank" rel="noopener">{REPO}</a> lets you check it.
Main parts:</p>
<ul style="margin-bottom:0">
<li>{repo("README.md")}: setup and run steps, data access, AI-use disclosure, citations</li>
<li>{repo("notebooks/")}: the 13 notebooks, run in order, with all outputs saved</li>
<li>{repo("src/credit.py")}: the exact preprocessing, the 5 cross-validation folds, the cutoff search and calibration used everywhere</li>
<li>{nb("01_clean_split.ipynb")}: cleaning and the exact train/test split (saved once, seed 42)</li>
<li>{repo("reports/")}: every chosen setting (JSON) and every result table (CSV), including all extra experiments</li>
<li>{repo("src/build_site.py")} and {repo("src/export_site_data.py")}: build this website from the saved results</li>
</ul>
</div>
""")

# =====================================================================================
page("data.html", "Data", f"""
<h1>Data</h1>
<p class="lead">A public credit-risk dataset of 32,581 loan applicants, cleaned to 32,409 and split once into training and test sets.</p>

<div class="card">
<p><b>Source:</b> <i>Credit Risk Dataset</i> by laotse, Kaggle
(<a href="https://www.kaggle.com/datasets/laotse/credit-risk-dataset" target="_blank" rel="noopener">kaggle.com/datasets/laotse/credit-risk-dataset</a>),
downloaded with <code>kagglehub</code> in {nb("01_clean_split.ipynb")}. Public data; no personal identifiers.</p>
<p><b>One row</b> = one loan applicant and their loan. <b>Size:</b> 32,581 rows × 12 columns.
<b>Not documented:</b> the country and the loan dates. The structure (grades A–G, MORTGAGE/RENT/OWN/OTHER, a $35,000 loan cap)
matches US marketplace lending, so amounts are read as US dollars.</p>
<p style="margin-bottom:0"><b>Also used:</b> US prime lending rate and inflation from the World Bank Open Data API
({nb("12_macro_check.ipynb")}), to check whether the interest rates are realistic.</p>
</div>

<h2>Variables</h2>
<p class="src">Source: {nb("01_clean_split.ipynb")}</p>
<div class="table-wrap"><table>
<tr><th>Variable</th><th>Meaning</th><th>Type</th><th>Used in</th></tr>
<tr><td><code>person_age</code></td><td>applicant's age (years)</td><td>numeric</td><td>all</td></tr>
<tr><td><code>person_income</code></td><td>annual income</td><td>numeric</td><td>all</td></tr>
<tr><td><code>person_home_ownership</code></td><td>RENT / MORTGAGE / OWN / OTHER</td><td>category</td><td>all</td></tr>
<tr><td><code>person_emp_length</code></td><td>years employed (887 missing after cleaning)</td><td>numeric</td><td>all</td></tr>
<tr><td><code>loan_intent</code></td><td>purpose: education, medical, venture, personal, debt consolidation, home improvement</td><td>category</td><td>all</td></tr>
<tr><td><code>loan_amnt</code></td><td>loan amount</td><td>numeric</td><td>all</td></tr>
<tr><td><code>loan_percent_income</code></td><td>loan amount ÷ income (loan-to-income)</td><td>numeric</td><td>all</td></tr>
<tr><td><code>cb_person_default_on_file</code></td><td>a past default on the credit-bureau file (Y/N)</td><td>category</td><td>all</td></tr>
<tr><td><code>cb_person_cred_hist_length</code></td><td>length of credit history (years)</td><td>numeric</td><td>all</td></tr>
<tr><td><code>loan_grade</code></td><td>risk grade A (best) … G (worst): a one-letter rating of the applicant's credit history</td><td>category</td><td>Reference, A; target of the grade classifier in B</td></tr>
<tr><td><code>loan_int_rate</code></td><td>interest rate charged (%), 3,094 missing after cleaning</td><td>numeric</td><td>input in Reference; <b>target</b> of the rate models</td></tr>
<tr><td><code>loan_status</code></td><td>1 = defaulted, 0 = repaid</td><td>binary</td><td><b>target</b> of the default models; never an input</td></tr>
</table></div>

<h2>Quality checks and cleaning</h2>
<p class="src">Source: {nb("01_clean_split.ipynb")} (Section 1: cleaning)</p>
<div class="table-wrap"><table>
<tr><th>Step</th><th class="num">Rows left</th><th>Reason</th></tr>
<tr><td>Raw data</td><td class="num">32,581</td><td></td></tr>
<tr><td>Remove exact duplicates</td><td class="num">32,416</td><td>165 repeated rows; a copy in both train and test would inflate test scores</td></tr>
<tr><td>Remove age &gt; 100</td><td class="num">32,411</td><td>impossible ages (up to 144)</td></tr>
<tr><td>Remove impossible employment length</td><td class="num">32,409</td><td>&gt; 60 years, or longer than age − 14 (e.g. 123 years for a 22-year-old)</td></tr>
</table></div>
<div class="note"><b>Missing values were not filled in here.</b> Employment length (887) and interest rate (3,094) are filled with the
median <i>inside each cross-validation fold</i>, learned from training rows only (see <a href="method.html">Method</a>), so the test
set never influences them. Rows without a rate cannot be used to train or test the rate models (nothing to learn from).</div>

<h2>Class balance and the train/test split</h2>
<p class="src">Source: {nb("01_clean_split.ipynb")} (split); folds: {repo("src/credit.py")} (<code>make_cv</code>)</p>
<div class="grid two">
<div class="card"><p><b>21.9% of applicants defaulted</b> (78.1% repaid). This is a moderate imbalance: a model that predicts
"everyone repays" is 78% accurate but useless, which is why accuracy is not our main metric.</p></div>
<div class="card"><p><b>Stratified 80/20 split</b> (random seed 42): <b>25,927 training</b> and <b>6,482 test</b> applicants, both
21.9% defaulters. The test set was saved once and not opened until the final evaluation.</p></div>
</div>

<h2>Loans by grade (calculated from the data, not predicted)</h2>
<p>Calculated by us from the data: the 29,315 cleaned loans (training + test) that have a recorded interest rate
(printed in {nb("12_macro_check.ipynb")}, Step 2).</p>
<div class="table-wrap"><table>
<tr><th>Grade</th><th class="num">Loans</th><th class="num">Share of loans</th><th class="num">Average rate</th><th class="num">Default rate</th></tr>
<tr><td>A</td><td class="num">9,712</td><td class="num">33.1%</td><td class="num">7.3%</td><td class="num">10.0%</td></tr>
<tr><td>B</td><td class="num">9,335</td><td class="num">31.8%</td><td class="num">11.0%</td><td class="num">16.3%</td></tr>
<tr><td>C</td><td class="num">5,807</td><td class="num">19.8%</td><td class="num">13.5%</td><td class="num">20.8%</td></tr>
<tr><td>D</td><td class="num">3,308</td><td class="num">11.3%</td><td class="num">15.4%</td><td class="num">59.5%</td></tr>
<tr><td>E</td><td class="num">880</td><td class="num">3.0%</td><td class="num">17.0%</td><td class="num">64.9%</td></tr>
<tr><td>F</td><td class="num">214</td><td class="num">0.7%</td><td class="num">18.6%</td><td class="num">70.1%</td></tr>
<tr><td>G</td><td class="num">59</td><td class="num">0.2%</td><td class="num">20.3%</td><td class="num">98.3%</td></tr>
</table></div>
<p>Rates rise steadily with the grade. The default rates jump sharply from C to D and reach 98% in grade G, which is extreme for
real lending; we come back to this in <a href="analysis.html">Result analysis</a> and <a href="limitations.html">Limitations</a>.</p>
""")

# =====================================================================================
page("method.html", "Method", f"""
<h1>Method</h1>
<p class="lead">How the data is prepared, why, and which models were compared, for default prediction and for interest-rate prediction.</p>

<h2>Preprocessing, and why</h2>
<p class="src">Source: {repo("src/credit.py")} (<code>make_preprocess</code>, <code>make_pipeline</code>)</p>
<div class="table-wrap"><table>
<tr><th>Step</th><th>Applied to</th><th>Why</th></tr>
<tr><td>Median imputation</td><td>employment length, interest rate (where it is an input)</td><td>fills gaps without being pulled by extreme values (income and loan amounts are right-skewed)</td></tr>
<tr><td>Standardisation (mean 0, SD 1)</td><td>numeric columns</td><td>puts income (thousands) and age (tens) on the same scale, which logistic regression and SVMs need; harmless for trees</td></tr>
<tr><td>One-hot encoding</td><td>home ownership, loan intent, past default, grade</td><td>turns categories into 0/1 columns without inventing a false order (e.g. "OWN = 2 × RENT")</td></tr>
<tr><td>SMOTE (optional)</td><td>training folds only</td><td>creates synthetic defaulters to rebalance the classes; compared with and without (see below)</td></tr>
</table></div>

<div class="note good"><b>Leak-free by construction.</b> Every step that learns from data (the medians, the means and SDs, the
categories, SMOTE) sits inside a scikit-learn / imbalanced-learn <code>Pipeline</code>. In every cross-validation round it is
learned from the four training folds only and then applied to the validation fold; at the end it is learned from the training
set only and applied to the test set. SMOTE is applied <i>only</i> when fitting, never to a validation or test fold, so those
always keep the real 22% default rate.</div>

<pre style="background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;overflow-x:auto;font-size:13px">
one cross-validation round (repeated 5 times, each fold used once for validation)

  4 training folds ── impute → scale → one-hot ──(SMOTE)──► fit model
                          │ learned statistics
                          ▼
  1 validation fold ── impute → scale → one-hot ──────────► predict → score (F1 / RMSE)</pre>

<h2>Where each pipeline is in the code</h2>
<div class="table-wrap"><table>
<tr><th>Setting</th><th>Default models (classification + PD)</th><th>Interest-rate models (regression)</th></tr>
<tr><td><span class="tag ref">Reference</span> rate + grade</td><td>{nb("02_probability_of_default.ipynb", "02")} logistic regression, SMOTE, linear and RBF SVM ·
{nb("03_decision_trees.ipynb", "03")} decision tree · {nb("05_random_forest.ipynb", "05")} Random Forest ·
{nb("04_probability_of_default.ipynb", "04")} calibrated PD for every model</td><td>none (rate already known)</td></tr>
<tr><td><span class="tag A">Pipeline A</span> grade</td><td>{nb("08_graded_applicant_models.ipynb", "08")} all five model types, re-tuned, calibrated PD</td>
<td>{nb("09_interest_rate_with_grade.ipynb", "09")} linear, Ridge, Lasso, Random Forest, gradient boosting</td></tr>
<tr><td><span class="tag B">Pipeline B</span> newcomer</td><td>{nb("06_applicant_only_models.ipynb", "06")} all five model types, re-tuned, calibrated PD</td>
<td>{nb("07_interest_rate_regression.ipynb", "07")} linear, Ridge, Lasso, Random Forest, gradient boosting, two-stage grade model</td></tr>
<tr><td>All three</td><td colspan="2">{nb("01_clean_split.ipynb", "01")} cleaning and split ·
{nb("10_results_summary.ipynb", "10")} all validation results · {nb("11_final_test.ipynb", "11")} final test set ·
{nb("12_macro_check.ipynb", "12")} World Bank check · shared code in <code>src/credit.py</code></td></tr>
</table></div>

<h2>Models for default (classification)</h2>
<p class="src">Source: {nb("02_probability_of_default.ipynb", "nb 02")}, {nb("03_decision_trees.ipynb", "03")}, {nb("05_random_forest.ipynb", "05")}, {nb("06_applicant_only_models.ipynb", "06")}, {nb("08_graded_applicant_models.ipynb", "08")}; all scores: {repo("reports/all_classification_scores.csv")}</p>
<p>The same five model types were compared in <b>all three settings</b> (Reference: notebooks 02, 03, 05; Pipeline A: notebook 08;
Pipeline B: notebook 06), each re-tuned for its own inputs.</p>
<div class="table-wrap"><table>
<tr><th>Model</th><th>Role</th><th>Why it fits</th><th>Tuned</th></tr>
<tr><td>Logistic regression</td><td><b>baseline</b></td><td>simple, interpretable, gives probabilities; a straight-line (linear) boundary</td><td>C (regularisation) in Pipelines A and B; default C in Reference</td></tr>
<tr><td>Soft-margin linear SVM</td><td>extra</td><td>widest-margin straight boundary; shows the maximal-margin idea and its limits</td><td>C</td></tr>
<tr><td>SVM with RBF kernel</td><td>candidate</td><td>curved boundaries, captures interactions between features</td><td>C, γ (grid on an 8,000-row subset; the top 2 confirmed on all rows in Reference, the winner scored on all rows in A and B)</td></tr>
<tr><td>Decision tree</td><td>extra</td><td>yes/no rules (thresholds), readable</td><td>depth, leaf size, criterion</td></tr>
<tr><td>Random Forest</td><td>candidate</td><td>averages 300 trees on bootstrap samples with random features per split, which cuts the variance of single trees</td><td>depth, leaf size, max_features, criterion (randomized search)</td></tr>
</table></div>
<p>Logistic regression and the SVMs were run <b>with and without SMOTE</b>. Trees and forests were run without it, because
SMOTE never improved F1 for any model once the decision cutoff was tuned (see <a href="analysis.html">Result analysis</a>).</p>

<h3>From score to probability of default</h3>
<p>A good PD must mean what it says: among applicants given PD 0.30, about 30% should default. Each model's scores were turned
into PDs with three methods: the model's own probability, <b>Platt scaling</b> (an S-shaped curve) and <b>isotonic regression</b>
(a flexible increasing step function). The mapping is fitted by <b>cross-fitting</b>: the mapping applied to a fold never sees
that fold's outcomes. The version with the lowest Brier score was kept ({nb("04_probability_of_default.ipynb")},
{nb("06_applicant_only_models.ipynb")}, {nb("08_graded_applicant_models.ipynb")}).</p>

<h2>Models for the interest rate (regression)</h2>
<p class="src">Source: {nb("07_interest_rate_regression.ipynb", "nb 07")} (Pipeline B), {nb("09_interest_rate_with_grade.ipynb", "nb 09")} (Pipeline A); all scores: {repo("reports/all_rate_scores.csv")}</p>
<div class="table-wrap"><table>
<tr><th>Model</th><th>Role</th><th>Tuned</th></tr>
<tr><td>Predict the average rate</td><td>floor: anything useful must beat it</td><td>-</td></tr>
<tr><td>Linear regression</td><td><b>baseline</b></td><td>-</td></tr>
<tr><td>Ridge, Lasso</td><td>candidates (shrink coefficients; Lasso can drop inputs)</td><td>α</td></tr>
<tr><td>Random Forest regressor</td><td>candidate (non-linear)</td><td>depth, leaf size, max_features</td></tr>
<tr><td>Gradient boosting regressor</td><td>added to try to improve R²</td><td>learning rate, trees, leaves, L2</td></tr>
<tr><td>Two-stage: predict the grade, then the rate</td><td>Pipeline B only (a newcomer has no grade); tried to see whether it
could raise the R². Stage 1, a Random Forest
classifier predicts the grade (A–G) from the applicant's details and PD; stage 2, the rate models use those grade probabilities
as extra inputs. Out-of-fold, so no leakage. Result: R² 0.303 vs 0.305 without it.</td><td>stage 1: 300 trees, leaf size 5</td></tr>
</table></div>

<h2>What each setting may use</h2>
<p class="src">Source: input lists in {repo("src/credit.py")} (<code>NUM_COLS</code>, <code>APPLICANT_NUM_COLS</code>, ...)</p>
<div class="table-wrap"><table>
<tr><th>Setting</th><th>Default-model inputs</th><th>Rate-model inputs</th></tr>
<tr><td><span class="tag ref">Reference</span></td><td>details + grade + rate</td><td>none (rate known)</td></tr>
<tr><td><span class="tag A">Pipeline A</span></td><td>details + grade (no rate)</td><td>grade + details (+ PD tried; it added nothing)</td></tr>
<tr><td><span class="tag B">Pipeline B</span></td><td>details only</td><td>details + newcomer PD (no grade)</td></tr>
</table></div>
<div class="note warn"><b>Why the rate is never an input when predicting the rate.</b> A PD model that used the interest rate,
fed into a model that predicts the interest rate, would leak the answer. So Pipelines A and B use PD models that never see the
rate, and the PD used to train the rate model is <b>out-of-fold</b> (each applicant's PD came from a model that did not train on
them), so it behaves like a real newcomer's PD.</div>
""")

# =====================================================================================
page("evaluation.html", "Evaluation", f"""
<h1>Evaluation design</h1>
<p class="lead">All choices were made on the training set with cross-validation; the test set was used exactly once, at the end.</p>

<h2>Split, cross-validation and the test set</h2>
<p class="src">Source: {nb("01_clean_split.ipynb")} (split); {repo("src/credit.py")} (<code>make_cv</code>); {nb("11_final_test.ipynb")} (test)</p>
<pre style="background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px;overflow-x:auto;font-size:13px">
32,409 applicants
├── TEST 20% (6,482) ───────────── locked; used once, in notebook 11, after every choice was frozen
└── TRAIN 80% (25,927)
     ├── 5-fold stratified cross-validation (same folds for every model)
     │     → choose hyperparameters (mean validation F1 or RMSE)
     │     → choose the decision cutoff (out-of-fold predictions)
     │     → choose the PD calibration (lowest Brier score)
     │     → compare models and choose one per setting
     └── refit the chosen models on all 25,927 → predict the test set once</pre>
<ul>
<li><b>Stratified</b> split and folds: every fold keeps the 21.9% default rate, so scores differ because of the model, not luck.</li>
<li><b>5 folds:</b> every training applicant is used for validation exactly once; models are judged by the <b>mean</b> over the 5 rounds, never the best round.</li>
<li><b>Tuning is separate from testing:</b> the test set played no part in any choice. Its scores are reported with a bootstrap 95% interval.</li>
</ul>

<h2>Choosing the decision cutoff</h2>
<p class="src">Source: {repo("src/credit.py")} (<code>f1_curve</code>, <code>best_cutoff</code>); worked example in {nb("02_probability_of_default.ipynb")}</p>
<p>A model says "default" when its PD is at or above a <b>cutoff</b>. The default 0.5 is not best when only 22% default. We
tried <b>every distinct out-of-fold score</b> as the cutoff (an exact search, ~25,000 candidates) and kept the one with the highest F1,
then checked it beat 0.5 in each fold. The chosen cutoffs are about 0.37–0.39 on the calibrated PD scale.
You can move the cutoff yourself on the <a href="explore.html">Explore</a> tab.</p>
{fig("logreg_cutoff_curve", "Logistic regression (notebook 02): precision, recall and F1 against the cutoff. Without SMOTE the best cutoff is 0.33; with SMOTE, 0.67, because SMOTE inflates the scores. After tuning both reach the same F1.")}

<h2>Metrics, and why each was chosen</h2>
<div class="table-wrap"><table>
<tr><th>Metric</th><th>What it measures</th><th>Why we use it</th></tr>
<tr><td><b>F1</b> (main)</td><td>balance of precision and recall for defaulters</td><td>rewards catching defaulters (protects the lender) without wrongly declining good customers; "everyone repays" scores 0</td></tr>
<tr><td>Precision</td><td>of applicants flagged, the share who really default</td><td>cost of declining good customers</td></tr>
<tr><td>Recall</td><td>of real defaulters, the share flagged</td><td>cost of lending to people who will not repay</td></tr>
<tr><td>ROC-AUC</td><td>how well risky applicants are ranked above safe ones, at any cutoff</td><td>separates ranking quality from the choice of cutoff</td></tr>
<tr><td><b>Brier score</b></td><td>mean of (PD − outcome)²</td><td>accuracy of the probability itself, needed because the PD is shown to users and drives pricing (guessing 0.219 for everyone gives 0.171)</td></tr>
<tr><td>ECE, mean PD</td><td>average gap between predicted PD and actual default rate</td><td>checks calibration: does PD 0.3 really mean 30%?</td></tr>
<tr><td><b>RMSE</b> (rates)</td><td>typical error of the suggested rate, in percentage points</td><td>in the units a borrower cares about</td></tr>
<tr><td><b>R²</b> (rates)</td><td>share of the variation in rates explained</td><td>comparable across pipelines (0 = no better than the average rate)</td></tr>
<tr><td>Accuracy</td><td>share of correct predictions</td><td>reported only next to its 78% "everyone repays" baseline; misleading on its own</td></tr>
</table></div>
<div class="note"><b>Details in the repository.</b> The split: {nb("01_clean_split.ipynb")}. The folds, the exact cutoff search and
the calibration: {repo("src/credit.py")} (<code>make_cv</code>, <code>best_cutoff</code>, <code>crossfit_calibrate</code>).
Calibration of every model: {nb("04_probability_of_default.ipynb")}, {nb("06_applicant_only_models.ipynb")},
{nb("08_graded_applicant_models.ipynb")}. The one-time test: {nb("11_final_test.ipynb")}.</div>
""")

# =====================================================================================
page("results.html", "Results", f"""
<h1>Results</h1>
<p class="lead">The chosen model in every setting is a Random Forest, for default and for the interest rate. Every section below
can be read on its own: what it shows, how to read it, and what it tells us.</p>

<h2>Final test set (6,482 applicants, used once)</h2>
<p><b>What this is.</b> All choices (models, hyperparameters, cutoffs, calibration) were made with 5-fold cross-validation on the
training set (<i>validation</i>). Only then was each setting's chosen model run <b>once</b> on the 20% test set: 6,482 applicants
the models had never seen. This is the honest estimate of how the system would do on new applicants.</p>
<div class="table-wrap"><table>
<tr><th></th><th><span class="tag ref">Reference</span><br>rate + grade</th><th><span class="tag A">Pipeline A</span><br>grade</th><th><span class="tag B">Pipeline B</span><br>newcomer</th></tr>
<tr><td>PD model (chosen on validation)</td><td>Random Forest, isotonic</td><td>Random Forest, isotonic</td><td>Random Forest, Platt</td></tr>
<tr><td>PD cutoff (frozen)</td><td class="num">0.378</td><td class="num">0.367</td><td class="num">0.388</td></tr>
<tr><td><b>F1 test</b> (95% interval)</td><td class="num"><b>0.838</b> (0.823–0.853)</td><td class="num"><b>0.837</b> (0.821–0.852)</td><td class="num"><b>0.699</b> (0.677–0.719)</td></tr>
<tr><td>F1 validation</td><td class="num">0.829</td><td class="num">0.827</td><td class="num">0.691</td></tr>
<tr><td>Precision / recall</td><td class="num">0.953 / 0.748</td><td class="num">0.956 / 0.743</td><td class="num">0.820 / 0.609</td></tr>
<tr><td>ROC-AUC</td><td class="num">0.942</td><td class="num">0.939</td><td class="num">0.892</td></tr>
<tr><td><b>Brier</b> test (validation)</td><td class="num">0.052 (0.056)</td><td class="num">0.053 (0.056)</td><td class="num">0.086 (0.088)</td></tr>
<tr><td>ECE (calibration error)</td><td class="num">0.005</td><td class="num">0.007</td><td class="num">0.013</td></tr>
<tr><td>Applicants approved</td><td class="num">82.8%</td><td class="num">83.0%</td><td class="num">83.7%</td></tr>
<tr><td>Rate model</td><td>-</td><td>RF regressor on grade + details</td><td>RF regressor on PD + details</td></tr>
<tr><td><b>Rate R²</b> test (validation)</td><td>-</td><td class="num"><b>0.907</b> (0.905)</td><td class="num"><b>0.305</b> (0.305)</td></tr>
<tr><td>Rate error (RMSE)</td><td>-</td><td class="num">±0.99 pp</td><td class="num">±2.70 pp</td></tr>
</table></div>
<div class="card">
<p style="margin-top:0"><b>How to read the rows.</b></p>
<ul>
<li><b>PD model and cutoff:</b> the Random Forest gives each applicant a calibrated probability of default (PD); isotonic and
Platt are the two calibration methods. Applicants with PD at or above the cutoff are declined.</li>
<li><b>F1, precision, recall</b> (0 to 1, higher is better) judge the approve/decline decision: recall = share of defaulters
caught, precision = share of declined applicants who really defaulted, F1 combines both.</li>
<li><b>ROC-AUC</b> (0.5 = random, 1 = perfect): how well risky applicants are ranked above safe ones, whatever the cutoff.</li>
<li><b>Brier and ECE</b> (lower is better) judge the probabilities themselves: Brier = average of (PD − outcome)²; ECE = average
gap between predicted PD and the actual default rate.</li>
<li><b>Rate R² and RMSE</b> judge the suggested interest rate: R² = share of rate differences explained; RMSE = typical error in
percentage points (pp).</li>
</ul>
<p style="margin-bottom:0"><b>What it shows.</b> (1) The Reference and Pipeline A are practically equal: once the grade is known,
also knowing the rate adds nothing. (2) Pipeline B, without the grade, is clearly weaker for both default and rate. (3) Test
scores are close to validation scores (e.g. F1 0.837 vs 0.827), so the choices made on validation were not overfitted.</p>
</div>

<p>Full tables: {repo("reports/final_test_headline.csv")}, {repo("reports/final_test_pd.csv")}, {repo("reports/final_test_rate.csv")}, {repo("reports/final_test_errors_by_segment.csv")}; code: {nb("11_final_test.ipynb")}. The confusion-matrix counts below are recomputed in {nb("13_website_checks.ipynb")}.</p>

<h3>Baselines: what if we used no model?</h3>
<p class="src">Source: {nb("11_final_test.ipynb")}</p>
<p>A score only means something next to the simplest possible answer. Each baseline below uses no information about the
applicant at all:</p>
<div class="table-wrap"><table>
<tr><th>Baseline</th><th>Result</th><th>Why</th><th>Our models</th></tr>
<tr><td>Say "everyone repays"</td><td class="num">accuracy 0.781, F1 0</td><td>78.1% of test applicants repaid, so this is "right"
78% of the time, but it catches <b>no</b> defaulter. This is why we use F1, not accuracy.</td><td class="num">F1 0.70–0.84</td></tr>
<tr><td>Give everyone PD 0.219 (the average default rate)</td><td class="num">Brier 0.171</td><td>Every repayer is off by 0.219,
every defaulter by 0.781: 0.219 × 0.781 = 0.171.</td><td class="num">Brier 0.052–0.086</td></tr>
<tr><td>Give everyone the average rate</td><td class="num">RMSE 3.24 pp, R² 0</td><td>This is just the natural spread of rates.</td>
<td class="num">±0.99 pp (A), ±2.70 pp (B)</td></tr>
</table></div>
<p><b>What it tells us:</b> every pipeline is far better than guessing. Even Pipeline B's Brier score is half the baseline's.</p>

<h3>95% intervals: is the gap between A and B real?</h3>
<p class="src">Source: {nb("11_final_test.ipynb")} (<code>bootstrap_ci</code>, 1,000 resamples)</p>
<p>The test set is one sample of 6,482 applicants; another sample would give slightly different scores. To measure this we used
a <b>bootstrap</b>: draw 6,482 applicants from the test set <i>with replacement</i> (some appear twice, some not at all),
recompute F1, and repeat 1,000 times. The middle 95% of those values is the interval: the range in which the score would
plausibly fall for a different sample.</p>
<p><b>What it tells us:</b> Pipeline A's lowest plausible F1 (0.821) is well above Pipeline B's highest (0.719), so <b>the
intervals do not overlap and the gap is real, not luck</b>: the grade really helps. The Reference (0.823–0.853) and A overlap almost
completely, so knowing the rate on top of the grade adds nothing measurable.</p>

<h3>Confusion matrices and reliability diagram</h3>
<p class="src">Source: {nb("11_final_test.ipynb")}; counts recomputed in {nb("13_website_checks.ipynb")}</p>
{fig("test_confusion_reliability", "Test set: confusion matrices at the frozen cutoffs (left three) and the reliability diagram (right).")}
<p><b>How to read a confusion matrix.</b> It counts the four possible outcomes of the approve/decline decision. Rows are what
actually happened, columns are the model's decision at its frozen cutoff; "% of row" is the share of that actual group.</p>
<div class="table-wrap"><table>
<tr><th></th><th>predicted repay (approve)</th><th>predicted default (decline)</th></tr>
<tr><td><b>repaid</b></td><td>correct: good customer approved</td><td>error: good customer wrongly declined (lost business)</td></tr>
<tr><td><b>defaulted</b></td><td>error: defaulter approved (lost money)</td><td>correct: defaulter declined</td></tr>
</table></div>
<p>The same numbers, turned into rates:</p>
<div class="table-wrap"><table>
<tr><th>Test set (1,418 defaulters, 5,064 repaid)</th><th><span class="tag ref">Reference</span></th><th><span class="tag A">Pipeline A</span></th><th><span class="tag B">Pipeline B</span></th></tr>
<tr><td>Defaulters caught (recall)</td><td class="num">1,060 / 1,418 = 74.8%</td><td class="num">1,054 / 1,418 = 74.3%</td><td class="num">864 / 1,418 = 60.9%</td></tr>
<tr><td>Declined who really defaulted (precision)</td><td class="num">1,060 / 1,112 = 95.3%</td><td class="num">1,054 / 1,102 = 95.6%</td><td class="num">864 / 1,054 = 82.0%</td></tr>
<tr><td>Good customers wrongly declined</td><td class="num">52 (1.0%)</td><td class="num">48 (0.9%)</td><td class="num">190 (3.8%)</td></tr>
<tr><td>Defaulters approved</td><td class="num">358</td><td class="num">364</td><td class="num">554</td></tr>
<tr><td><b>Default rate among approved</b> (21.9% with no model)</td><td class="num">358 / 5,370 = 6.7%</td><td class="num">364 / 5,380 = 6.8%</td><td class="num">554 / 5,428 = 10.2%</td></tr>
</table></div>
<p><b>What it tells us:</b></p>
<ul>
<li>All three decline a similar number (about 17%), so about 83% are approved.</li>
<li>With the grade, 96% of declines are real defaulters, and the default rate among approved applicants falls from 21.9% to 6.8%.</li>
<li>Without the grade (Pipeline B), the model wrongly declines <b>four times as many good customers</b> (190 vs 48) and approves
about 190 more defaulters, because without the credit history it cannot tell them apart as well.</li>
<li>The missed defaulters are mostly applicants who look safe (homeowners, small loans, high income): see
<a href="analysis.html">Result analysis</a>, finding 5.</li>
</ul>
<p><b>How to read the reliability diagram.</b> It checks whether a PD can be taken at face value: when the model says "30%",
do about 30% of those people default? The test applicants are sorted by predicted PD and split into 10 equal groups (about 650
each). Each dot is one group: x = its average predicted PD, y = the share who actually defaulted. On the dotted diagonal,
predicted = actual.</p>
<p><b>What it tells us:</b> all three pipelines lie on the diagonal; the <b>ECE</b> (average distance from the diagonal, weighted
by group size) is only 0.005 / 0.007 / 0.013, so a PD can be read as a real probability. Most dots sit below 0.25 or near 0.9: the
forests are confident about most applicants. Pipeline B has a dot at 0.45, a group it is unsure about (and indeed 47% of them
defaulted).</p>
<div class="note"><b>Calibrated is not the same as accurate.</b> A good PD needs two things:
<ul style="margin:6px 0">
<li><b>Calibration (honesty):</b> the numbers mean what they say. Among applicants given PD 0.30, about 30% really default.
The reliability diagram checks this.</li>
<li><b>Sharpness (decisiveness):</b> the PDs are pushed away from the average (0.22) towards 0 or 1, so the model clearly
separates safe applicants (e.g. PD 0.02) from risky ones (e.g. PD 0.95) instead of giving many people an unsure middle value.</li>
</ul>
A model can be honest without being sharp: giving <i>everyone</i> PD 0.22 is perfectly calibrated (22% of everyone defaults),
but useless, because it cannot tell anyone apart. Pipeline B's probabilities are as honest as A's (both lie on the diagonal),
but they are less sharp: more applicants get uncertain middle PDs (like the group at 0.45). That is why B's F1 is lower and its
Brier score is higher: the Brier score rewards both calibration and sharpness.</div>

<h2>Every model compared (validation, interactive)</h2>
<p><b>What this is.</b> Before the final test, every model was scored with 5-fold cross-validation on the training set, in each
of the three settings. This chart is how the final model was chosen; the test set was not used. Pick a task (default or
interest rate) and a metric; each model has one bar per setting, coloured by setting.</p>
<div class="controls">
<span class="seg" id="task"><button data-v="clf" class="on">Default (8 classifiers)</button><button data-v="rate">Interest rate (5 regressors)</button></span>
<label>Metric <select id="metric"></select></label>
</div>
<div id="cmpChart" class="chart"></div>
<div class="table-wrap" id="cmpTable"></div>
<p>Full tables: {repo("reports/all_classification_scores.csv")}, {repo("reports/all_rate_scores.csv")}; summary notebook: {nb("10_results_summary.ipynb")}.</p>
<div class="note"><b>What it tells us.</b> In every setting the ranking is the same: <b>Random Forest &gt; decision tree &gt;
RBF SVM &gt; linear models</b>, so the choice of the Random Forest does not depend on what is known about the applicant. SMOTE
never improves F1. For rates, all five regressors are within 0.02 R² of each other in each pipeline: the information available
matters far more than the choice of regressor.</div>

<h2>Interest rates on the test set</h2>
<p class="src">Source: {nb("11_final_test.ipynb")}; table: {repo("reports/final_test_rate.csv")}</p>
{fig("test_rate_scatter", "Predicted vs actual rate on the test set, one dot per applicant.")}
<p><b>How to read it.</b> Each dot is one test applicant: x = the rate they were actually charged, y = the rate our model
suggests. A perfect model would put every dot on the dotted diagonal.</p>
<p><b>What it tells us:</b></p>
<ul>
<li><span class="tag A">Pipeline A</span> follows the diagonal in steps, one step per grade: within a grade the suggestion is
almost constant, because the grade decides most of the rate. Typical error ±0.99 pp.</li>
<li><span class="tag B">Pipeline B</span> suggests rates in two flat bands (about 10% and about 14.5%), mainly split by whether
the applicant has a past default. It cannot reach very low or very high rates: newcomers charged 6% and 20% get similar
suggestions. Typical error ±2.70 pp.</li>
</ul>

<h2>Do the rates look real? (World Bank check)</h2>
<div class="card">
<p><b>Benchmark (the baseline rate).</b> The interest rate that banks charge their <i>safest</i> customers at a given time; it
moves with the economy (when the central bank raises rates, every loan gets more expensive). We use the <b>US prime lending
rate</b> from the World Bank API. The data has no loan dates, so we use its average over the years that fit the data:
<b>3.86%</b>.</p>
<p><b>Premium.</b> The extra a borrower pays <i>on top of</i> the benchmark for their own risk:
<b>premium = interest rate − benchmark</b>. Example: a 7.3% loan when the benchmark is 3.86% has a premium of
7.3 − 3.86 ≈ <b>3.4 percentage points (pp)</b>.</p>
<p style="margin-bottom:0"><b>"Above the benchmark"</b> means the premium is positive: the borrower pays more than the safest
customers. In real risk-based lending every borrower should be above the benchmark, and riskier borrowers further above it.
Comparing premiums instead of raw rates removes the effect of the economy, so only the pricing of risk is left.
Details in {nb("12_macro_check.ipynb")}.</p>
</div>
{fig("macro_context", "Solid lines: US prime rate and inflation from the World Bank. Dashed lines: each grade's average interest rate, calculated by us from the dataset (actual rates charged, not predictions). Green years are plausible for these loans.")}
<p><b>How to read it.</b> Solid lines are the US economy by year (World Bank); dashed lines are each grade's average rate in our
data, which has no dates, so they are flat. The green line is the benchmark we use (3.86%).</p>
<p><b>What it tells us:</b> in 2000–01 and 2005–07 the prime rate was above the cheapest loans in the data, which is implausible
(no lender charges its customers less than its safest rate), so those years are excluded. In the other (green) years every grade
sits above the benchmark, and riskier grades further above it, as in real risk-based lending.</p>
<div class="grid two">
{fig("pipelineA_premium_vs_actual", "Pipeline A: suggested vs actual premium per grade (approved test applicants).")}
{fig("pipelineB_premium_vs_actual", "Pipeline B: suggested vs actual premium per PD band (approved test applicants).")}
</div>
<p><b>How to read these box plots.</b> Only approved test applicants with a recorded rate are shown. For each group, grey is
the premium actually charged and colour is the premium our model suggests. The line in a box is the median, the box holds the
middle 50% of applicants and the whiskers most of the rest. A perfect model would make each coloured box look like its grey
neighbour. Left (Pipeline A): groups are grades. Right (Pipeline B, no grade): groups are five equal-size bands of newcomer PD,
from safest (1) to riskiest (5).</p>
<p><b>What they tell us:</b></p>
<ul>
<li><span class="tag A">Pipeline A</span>: the medians match in every grade, and premiums climb from about +3.5 pp (A) to
about +15 pp (F). The suggested boxes are narrower: within a grade the model gives nearly the same premium to everyone, while
real premiums still vary. There is no grade G because almost all grade G applicants are declined (PD above the cutoff).</li>
<li><span class="tag B">Pipeline B</span>: actual premiums are spread very widely (about +2 to +16 pp) in every PD band, while
the suggestions stay between about +5 and +8 pp. On average per band the suggestion is right (+6 to +8 pp), slightly too low in
the riskiest band; for individuals it can be far off, because the lender priced by grade, which a newcomer does not have.</li>
<li>Actual premiums rise only from about +6 to +8 pp across the five PD bands, but from +3.5 to +15 pp across grades: the
grade explains the pricing far better than the newcomer's PD (R² 0.91 vs 0.31).</li>
</ul>
""", PLOTLY + '\n<script src="assets/results.js"></script>')

# =====================================================================================
page("explore.html", "Explore", f"""
<h1>Explore the results</h1>
<p class="lead">Two interactive tools on the <b>test set</b> (6,482 applicants the models never saw). Nothing is retrained:
these are the frozen models' saved predictions.</p>

<div class="card">
<b>Models used here</b>
<ul style="margin-bottom:0">
<li><span class="tag ref">Reference</span> Random Forest on details + grade + rate, isotonic-calibrated PD ({nb("05_random_forest.ipynb", "nb 05")}, {nb("04_probability_of_default.ipynb", "04")})</li>
<li><span class="tag A">Pipeline A</span> Random Forest on details + grade, isotonic-calibrated PD ({nb("08_graded_applicant_models.ipynb", "nb 08")}); rate: Random Forest regressor on grade + details ({nb("09_interest_rate_with_grade.ipynb", "nb 09")})</li>
<li><span class="tag B">Pipeline B</span> Random Forest on details only, Platt-calibrated PD ({nb("06_applicant_only_models.ipynb", "nb 06")}); rate: Random Forest regressor on PD + details ({nb("07_interest_rate_regression.ipynb", "nb 07")})</li>
</ul></div>

<h2>1. Move the decision cutoff</h2>
<p class="src">Source: test-set PDs from {nb("11_final_test.ipynb")}, exported by {repo("src/export_site_data.py")}</p>
<p>An applicant is declined when their PD is at or above the cutoff. Lower it to catch more defaulters (but decline more good
customers); raise it for the opposite. The dashed line marks the cutoff chosen on the training set.</p>
<div class="controls">
<span class="seg" id="cutSetting"><button data-v="ref">Reference</button><button data-v="A" class="on">Pipeline A</button><button data-v="B">Pipeline B</button></span>
<label>Cutoff <input type="range" id="cut" min="0.02" max="0.98" step="0.01"> <b id="cutVal"></b></label>
<button class="btn" id="cutReset">Reset to chosen cutoff</button>
</div>
<div class="grid two">
<div>
<div class="cm" id="cm"></div>
<div class="metrics" id="cutMetrics"></div>
</div>
<div id="cutChart" class="chart"></div>
</div>
<p id="cutStory" class="note"></p>

<h2>2. Browse real test applicants</h2>
<p class="src">Source: test-set predictions from {nb("11_final_test.ipynb")}, exported by {repo("src/export_site_data.py")}</p>
<p>Filter, then click an applicant to see what each model decided, the suggested rates, and what really happened.</p>
<div class="controls">
<label>Show <select id="fType">
<option value="all">all applicants</option>
<option value="missed">defaulters the chosen pipeline approved (missed)</option>
<option value="falsealarm">good customers the pipeline declined</option>
<option value="caught">defaulters the pipeline caught</option>
<option value="disagree">A and B disagree</option>
</select></label>
<label>Pipeline for decisions <select id="fPipe"><option value="A">Pipeline A</option><option value="B">Pipeline B</option><option value="ref">Reference</option></select></label>
<label>Home <select id="fHome"><option value="">any</option><option>RENT</option><option>MORTGAGE</option><option>OWN</option><option>OTHER</option></select></label>
<label>Grade <select id="fGrade"><option value="">any</option><option>A</option><option>B</option><option>C</option><option>D</option><option>E</option><option>F</option><option>G</option></select></label>
<label>Loan / income <select id="fLti"><option value="">any</option><option value="0-0.1">≤ 10%</option><option value="0.1-0.2">10–20%</option><option value="0.2-0.3">20–30%</option><option value="0.3-1">&gt; 30%</option></select></label>
<button class="btn" id="fRandom">Random applicant</button>
</div>
<p id="fCount" style="color:var(--muted);font-size:14px"></p>
<div class="grid two">
<div class="applist" id="appList"></div>
<div id="appCard" class="card" style="margin:0"></div>
</div>
""", '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>\n<script src="assets/explore.js"></script>')

# =====================================================================================
def why(title, saw, reason, proof, takeaway, extra=""):
    return f"""<div class="card"><h3 style="margin-top:0">{title}</h3><div class="why">
<div class="row"><b>What we saw</b><div>{saw}</div></div>
<div class="row"><b>Why</b><div>{reason}</div></div>
<div class="row"><b>Proof</b><div>{proof}</div></div>
<div class="row"><b>In short</b><div><b>{takeaway}</b></div></div></div>{extra}</div>"""


TERMS = """<div class="note"><b>Terms used on this page.</b>
<b>PD</b> = probability of default (0 to 1). <b>F1</b> (0 to 1, higher is better) = how well defaulters are caught without
wrongly declining good customers; it combines <b>recall</b> (share of defaulters caught) and <b>precision</b> (share of declined
applicants who really default). <b>Brier score</b> (lower is better) = how close the PDs are to what happened.
<b>R²</b> (0 to 1, higher is better) = share of the differences in interest rates that a model explains; <b>pp</b> = percentage
points. <b>Validation</b> = 5-fold cross-validation on the training set; <b>test</b> = the 20% hold-out used once at the end.</div>"""

page("analysis.html", "Result analysis", "<h1>Result analysis: why the results look like this</h1>"
     "<p class=\"lead\">Seven findings. Each card can be read on its own: what we saw, why it happens, the evidence from our "
     "notebooks, and a one-line takeaway. Simple counts and shares quoted here are recomputed in "
     + nb("13_website_checks.ipynb") + ".</p>"
     + TERMS
     + why("1. The grade (a summary of the credit history) carries most of the information",
           "We ran three settings on the same test applicants. <span class=\"tag A\">Pipeline A</span>, which knows the grade but not the interest rate, predicts default as well as the <span class=\"tag ref\">Reference</span>, which knows both: F1 0.837 vs 0.838, Brier 0.053 vs 0.052. Its rate model explains 91% of the differences in rates (R² 0.907). <span class=\"tag B\">Pipeline B</span>, a newcomer with neither, does clearly worse: F1 0.699, Brier 0.086, rate R² 0.305.",
           """The grade (A best … G worst) is a <b>combined evaluation of the applicant's credit history</b>, summarised in one letter, much like a credit score such as CIBIL. The applicant details hold only two simple history facts (past default yes/no and length of credit history) next to facts about the applicant <i>today</i> (age, income, loan size, home ownership); the grade sums up the whole history. The lender sets the interest rate mainly from the grade, so once the grade is known, the rate adds nothing new.
<br><br><b>What this means for Pipeline B.</b> A newcomer has no grade, so the models lose this summary. They can still see today's risk (for example a large loan relative to income), which is why F1 is still 0.70, but the PDs are less sharp (higher Brier) and the rates much rougher (±2.7 pp instead of ±1.0 pp), because the lender's pricing follows the grade and the details cannot rebuild it. Since a grade, like a credit score, is normally universal and available when someone applies, Pipeline A is our main pricing pipeline and Pipeline B the fallback for applicants without a credit history.""",
           f"The grade alone predicts the interest rate with R² 0.903 ({nb('09_interest_rate_with_grade.ipynb', 'nb 09')}). Grades A and B contain <b>no</b> applicant with a past default, while C–G contain about 50%, so the grade clearly reflects the credit history. Guessing the grade from the details is right only 49% of the time ({nb('07_interest_rate_regression.ipynb', 'nb 07')}). In the Random Forest's permutation importance (below), grade is the 4th most important input and the rate only the 6th.",
           "If the grade is available, use it: it makes both the approve/decline decision and the price accurate. Without it the models still work, but less precisely.",
           fig("forest_permutation_importance", "Random Forest (Reference setting): how much ROC-AUC drops when each input is shuffled; a bigger drop means a more important input. Loan-to-income, home ownership and income matter most; grade is 4th, the rate 6th.", 620))
     + why("2. Trees and forests beat straight-line models",
           "In cross-validation on the training set (Reference setting), the tree models clearly beat the straight-line (linear) models at predicting default: Random Forest F1 0.830 and a single decision tree 0.813, against about 0.68 for logistic regression and the linear SVM.",
           "Default risk here follows yes/no rules that <b>combine</b> features, for example \"renting <b>and</b> borrowing more than about 31% of income\". A linear model gives each feature its own fixed weight and adds them up, so it cannot express \"only when both are true\". A tree asks a sequence of yes/no questions, so it captures such combinations directly.",
           f"In a depth-3 tree (below, {nb('03_decision_trees.ipynb', 'nb 03')}), applicants who rent and borrow more than ~31% of their income (7.2% of all applicants) <b>all</b> defaulted. The best linear model still misclassifies about 13% of training applicants whatever its margin setting C ({nb('02_probability_of_default.ipynb', 'nb 02')}, Step 5). Model scores: {nb('05_random_forest.ipynb', 'nb 05')}, {nb('10_results_summary.ipynb', 'nb 10')}.",
           "Default in this data depends on combinations of conditions, which trees capture and straight lines cannot.",
           fig("tree_depth3", "Depth-3 decision tree on the training set. Each box is a yes/no question; numeric thresholds are on the standardised scale (1.26 ≈ loan above 31% of income). Bottom-right leaf: renters with a high loan-to-income, 100% default."))
     + why("3. A forest of trees beats a single tree",
           "In cross-validation, one fully grown decision tree scores F1 0.746. Averaging 300 trees, each trained on a different random resample of the training data (<b>bagging</b>), raises this to 0.824. A <b>Random Forest</b>, which in addition lets each split choose only among a random subset of features, does best (0.830).",
           "A single deep tree memorises its training data (training F1 = 1.0), so it makes many confident mistakes on new applicants (overfitting). Trees trained on different random samples make <i>different</i> mistakes, and averaging them cancels much of the error. Restricting each split to a random subset of features makes the trees even more different from each other, so even more errors cancel.",
           "Average correlation between the trees' predictions (lower = trees disagree more = more errors cancel): 0.64 with all features (bagging), 0.57 with random feature subsets (Random Forest). Validation F1 rises with the number of trees and levels off after about 100 (below); adding trees never makes it worse.",
           "Many different trees averaged are more reliable than one tree; this is why the Random Forest was chosen in every setting.",
           fig("forest_tree_count", "Validation and out-of-bag F1 against the number of trees: rises, then plateaus. More trees never overfit.", 700))
     + why("4. SMOTE (synthetic defaulters) did not help",
           "Only 22% of applicants default. SMOTE creates synthetic defaulters so the training data becomes 50/50. With logistic regression at the standard cutoff, it raised recall (0.56 → 0.77) but lowered precision (0.77 → 0.55), so F1 stayed at 0.645. Once the cutoff was tuned for each, F1 was 0.676 with SMOTE and 0.674 without: essentially equal.",
           "Training on a 50/50 world makes the model give higher scores to <i>everyone</i>. That moves the decision line, which is exactly what lowering the cutoff does. It does not teach the model anything new about <i>who</i> defaults, so once the cutoff is tuned the two give the same result.",
           f"Logistic regression with and without SMOTE ranks applicants almost identically (rank correlation 99.5%); only the F1-best cutoff moves, from 0.36 (no SMOTE) to 0.67 (SMOTE) ({nb('13_website_checks.ipynb', 'nb 13')}). The same pattern held for the linear and RBF SVMs: SMOTE changed precision and recall but never raised F1 once the cutoff was tuned.",
           "Tuning the cutoff does the same job as SMOTE, more simply; the final Random Forests use no SMOTE.")
     + why("5. The models miss defaulters who look safe",
           "On the test set the models approve some applicants who later default. <span class=\"tag A\">Pipeline A</span> misses 26% of the 1,418 defaulters and <span class=\"tag B\">Pipeline B</span> 39%. These misses are very uneven: they pile up among applicants who look safe on paper.",
           "The models catch risk that is visible in the data, such as a large loan relative to income or renting. Defaulters with comfortable-looking profiles probably defaulted for reasons the data does not record, such as losing a job or an illness after the loan was given, so no model could see it coming.",
           """Share of test-set defaulters in each group that were missed (approved):<div class="table-wrap"><table><tr><th>Test-set defaulters who were</th><th class="num">missed by A</th><th class="num">missed by B</th></tr>
<tr><td>homeowners with a mortgage</td><td class="num">53%</td><td class="num">71%</td></tr>
<tr><td>borrowing ≤ 10% of income</td><td class="num">49%</td><td class="num">75%</td></tr>
<tr><td>in the highest-income quarter</td><td class="num">34%</td><td class="num">78%</td></tr>
<tr><td>borrowing &gt; 30% of income</td><td class="num">4%</td><td class="num">5%</td></tr></table></div>
Try it: on the <a href="explore.html">Explore</a> tab choose "defaulters the chosen pipeline approved".""",
           "The models catch risk that shows in the numbers; defaults caused by events the data does not record cannot be predicted.")
     + why("6. A newcomer's interest rate can only be guessed roughly (R² ≈ 0.3)",
           "For a newcomer (<span class=\"tag B\">Pipeline B</span>, no grade), every rate model explains only about 30% of the differences in interest rates (R² ≈ 0.30; typical error ±2.7 pp). With the grade (<span class=\"tag A\">Pipeline A</span>) it is 91% (±1.0 pp). R² = 1 would mean every rate is predicted exactly; R² = 0 means no better than giving everyone the average rate.",
           "The lender sets the rate mainly from the grade, and the grade summarises the full credit history, of which the applicant details contain only two simple facts. Two newcomers with the same age, income and loan can have very different grades because of their past, so from their details alone the rate can only be guessed roughly: right on average, but several points off for individuals.",
           f"""<ul style="margin:0;padding-left:18px">
<li><b>Same ceiling for every model.</b> Six very different methods (linear, Ridge, Lasso, Random Forest, gradient boosting, two-stage) all stop at R² ≈ 0.30. When every model hits the same wall, the limit is the information, not the model ({nb('07_interest_rate_regression.ipynb', 'nb 07')}).</li>
<li><b>Guessing the grade first does not help.</b> The two-stage model predicts the grade, then the rate. The grade is right only 49% of the time and E, F or G is <b>never</b> predicted: those grades are rare (≈ 4% of loans) and their applicants look like A–C applicants (median income $58–71k vs $53–58k; same median age 26; 47% have income, loan size and loan-to-income all within the normal A–C range).</li>
<li><b>Pulled towards the middle.</b> On the test set, newcomers actually charged under 8% get suggestions about 3.1 pp too high; those charged over 17% about 5.5 pp too low.</li>
<li><b>World Bank check.</b> Premium = rate minus the US prime rate. Per PD band the average suggested premium matches the actual one (+6 to +8 pp), but real premiums within a band spread about 3× more than the suggestions (see the box plots on the <a href="results.html">Results</a> tab).</li></ul>""",
           "Without the credit-history grade, no model can price a newcomer precisely; Pipeline B's rate is a rough starting point, which is why Pipeline A is the main pricing pipeline.",
           fig("newcomer_rate_vs_pd", "Each dot is one approved applicant: the rate actually charged against their newcomer PD. The rate rises with PD, but at any PD the spread is wide.", 760))
     + why("7. The data's pricing looks real, but its default rates look extreme",
           "Two things in the data do not fit together. The interest rates look like real lending: they rise steadily from grade A to G. But the default rates are extreme: 21.9% of all loans and 98% of grade G loans defaulted.",
           "A lender who charges about 20% interest to a group where 98% default loses almost the whole loan on nearly everyone; no real lender could keep doing that. Real data is also messy, while this data contains rules with no exceptions at all. Both suggest the dataset is partly simulated, or describes an unusually risky group of borrowers.",
           f"""<ul style="margin:0;padding-left:18px">
<li><b>Pricing looks real.</b> World Bank check: the <b>premium</b> (interest rate minus the US prime rate, i.e. what a borrower pays above the rate for the safest customers) rises steadily from +3.5 pp (grade A) to +16.4 pp (grade G), as in real risk-based lending.</li>
<li><b>Defaults look extreme.</b> Default rates by grade (calculated from the data, not predicted; 29,315 cleaned loans with a recorded rate): A 10%, B 16%, C 21%, then D 59%, E 65%, F 70%, G 98%.</li>
<li><b>Rules without exceptions.</b> Every applicant who rents and borrows over ~31% of income defaulted (about 1,870 people); grades A and B contain <b>no</b> applicant with a past default, while C–G contain about 50%.</li></ul>Sources: {nb('12_macro_check.ipynb', 'nb 12')} (World Bank premiums), {nb('13_website_checks.ipynb', 'nb 13')} (default rates, rule counts).""",
           "The pricing is realistic, but the default pattern is too clean and too extreme to be typical; our high scores may not carry over to real lending data.",
           fig("premium_by_grade_data", "Premium over the US benchmark by grade (boxes, calculated from the data) and each grade's actual default rate (red line).", 760))
     + """<div class="note warn"><b>What this means for the conclusions.</b> Clean, rule-like data is easy for tree models to learn,
so these scores may be higher than the same models would reach on real lending data. The results describe this dataset.</div>""")

# =====================================================================================
def lim(title, issue, effect, handled):
    return f"""<div class="card"><h3 style="margin-top:0">{title}</h3><div class="why">
<div class="row"><b>The issue</b><div>{issue}</div></div>
<div class="row"><b>Effect</b><div>{effect}</div></div>
<div class="row"><b>What we did</b><div>{handled}</div></div></div></div>"""


LIMITS = (
    lim("1. No loan dates",
        "The dataset does not say <i>when</i> each loan was given. Interest rates depend strongly on the economy at the time: when the central bank raises its rate, every loan becomes more expensive.",
        "We cannot study how risk or pricing changed over time, and we cannot match each loan to the economy at the moment it was issued, as the proposal originally planned. A random train/test split also cannot test whether a model trained on older loans works on newer ones.",
        "We used the World Bank data as a <b>plausibility check</b> instead: we kept only the years in which the US prime rate was below the cheapest loans in the data, and used the average prime rate over those years (3.86%) as one fixed benchmark. With dates, each loan could be compared with the benchmark of its own year, and the split could be made by time.")
    + lim("2. How the grade is produced is not documented",
        "The dataset gives each loan a grade A–G but does not say who assigned it or how. We treat it as a universal credit-history rating, available when someone applies, like a credit score such as CIBIL.",
        "<span class=\"tag A\">Pipeline A</span>, our main pricing pipeline, depends on this assumption. If the grade is instead assigned by this lender only after its own assessment, Pipeline A can only be used after that step, and <span class=\"tag B\">Pipeline B</span> is the realistic setting for brand-new applicants. Pipeline A's high rate accuracy (R² 0.91) also reflects how closely <i>this</i> lender priced from its own grade; for another lender it may be lower.",
        "We built and reported all three settings, so the results are available under either reading: Pipeline A if the grade is known at application, Pipeline B if it is not. The assumption is stated wherever Pipeline A is described.")
    + lim("3. Country not documented",
        "The dataset does not say which country the loans come from. We assume the United States from its structure (dollar amounts, a $35,000 loan cap, and grades and home-ownership categories as used by US lenders).",
        "The World Bank comparison uses US interest rates. If the loans came from another country, the benchmark (3.86%) and therefore all premiums would be different. The default and rate models themselves do not depend on the country.",
        "The assumption is stated on the Data and Results tabs, and the World Bank part is presented only as a plausibility check, not as a result the models depend on.")
    + lim("4. Possibly partly simulated data",
        "Real lending data is messy, but this data contains rules with <b>no exceptions</b>: every applicant who rents and borrows more than about 31% of income defaulted (about 1,870 people), and grades A and B contain no applicant with a past default. Default rates are also extreme: 22% overall and 98% in grade G (calculated from the data).",
        "Clean, rule-like patterns are easy for tree models to learn, so our scores (for example F1 0.84) may be <b>higher than the same models would reach on real loans</b>. No real lender could keep lending at about 20% interest to a group where 98% default, so the defaults may not reflect real behaviour.",
        "We report this openly (Result analysis, finding 7) and describe the results as results on this dataset, not on lending in general. Testing on a second, real dataset would show how much the scores drop.")
    + lim("5. Only approved loans (selection bias)",
        "The data contains only loans that were actually granted. Applicants the lender rejected never appear, so we never see whether they would have repaid.",
        "The models learn from an already-filtered group. When used on <i>all</i> applicants, including the kind the lender used to reject, their PDs may be too low, because such people are rare in the training data. This is a known problem in credit scoring (reject inference).",
        "Nothing can fix this with this data. It would need records of rejected applicants, or methods that estimate how they would have behaved.")
    + lim("6. One dataset only",
        "All models were trained and tested on one lender's data. The test set comes from the same data, only a different 20% of it.",
        "The test result shows how the models do on <i>new applicants of this lender</i>. How they would do for other lenders, countries or time periods is untested.",
        "We looked for a second dataset to check against (for example Lending Club), but key inputs such as age are missing there, so the same models could not be applied.")
    + lim("7. Information ceiling for newcomers",
        "Without the grade, the only credit-history facts left are past default (yes/no) and length of credit history. The lender set rates mainly from the grade.",
        "<span class=\"tag B\">Pipeline B</span> can predict a newcomer's rate only to about ±2.7 pp (R² 0.31), and its default decisions are weaker (F1 0.70 vs 0.84). Six different rate models all stopped at the same R² ≈ 0.30, so a better model would not help: the information is missing.",
        "We tried predicting the grade first (two-stage model); it did not help (R² 0.303 vs 0.305). Pipeline B is therefore presented as a rough fallback, with Pipeline A as the main pricing pipeline.")
    + lim("8. The rate model copies past pricing, and the cutoff ignores money",
        "The rate model is trained on the rates this lender actually charged. The approve/decline cutoff is chosen to maximise F1.",
        "The suggested rate is what <i>similar borrowers paid in the past</i>, not a break-even or profit-maximising rate. F1 treats a missed defaulter (the lender loses most of the loan) and a wrongly declined good customer (the lender loses only the interest) as equally bad. A cutoff based on money would probably be <b>stricter</b> than ours (0.37–0.39): to break even on a borrower with a 37% chance of default, the rate would need to be roughly 35–60%, far above the 23% maximum in the data.",
        "We state this as a limitation. With the loss per default and the lender's funding cost, the cutoff could instead be chosen to maximise expected profit, and a rate could be calculated from the PD.")
    + lim("9. Method details",
        "Three shortcuts in how the models were built: (a) SMOTE was applied after one-hot encoding, so its synthetic applicants can have \"in-between\" categories (for example 0.4 renter); (b) the RBF SVM in Pipelines A and B was tuned on an 8,000-row subset, not the full training set; (c) the forest searches tried 15 random combinations, not every combination.",
        "(a) The synthetic defaulters are slightly unrealistic. (b) and (c) The chosen settings may not be the very best possible.",
        "(a) SMOTENC, which handles categories properly, would be the cleaner choice; SMOTE never improved F1 here and the final models do not use it, so this does not affect the final results. (b) The subset result was confirmed on the full training set in the Reference setting. (c) A full search might find slightly better settings, but the Random Forest was already the best model in every setting.")
    + lim("10. Correlation, not causation",
        "The models learn which kinds of applicants defaulted in the past. They do not learn what <i>causes</i> default.",
        "The PD cannot be used to answer \"what if\" questions. For example, a lower interest rate would not make a risky applicant safer in these models, even though in reality a lower repayment might reduce default. Likewise, telling an applicant to change one input would not necessarily change their real risk.",
        "We use the models only for prediction (who is likely to default, what similar borrowers paid) and do not draw causal conclusions.")
)

page("limitations.html", "Limitations & reproduce", f"""
<h1>Limitations, reproduction, AI use and citations</h1>

<h2>Limitations</h2>
<p>Each limitation below explains the issue, its effect on our results, and what we did about it (or what would fix it).</p>
{LIMITS}

<h2>Reproduce</h2>
<p>Everything on this site can be recreated from the repository:
<a href="{REPO}" target="_blank" rel="noopener">{REPO}</a>. The README has the same steps.</p>

<h3>1. Set up Python</h3>
<p>Python 3.13 (tested with 3.13.11 on Windows; other systems should work). Create a virtual environment, install the exact
package versions in <code>requirements.txt</code>, and register the environment as a Jupyter kernel:</p>
<pre style="background:#f7f7f5;border:1px solid var(--line);border-radius:8px;padding:10px;overflow-x:auto;font-size:13px">python -m venv .venv
.venv\\Scripts\\activate            (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m ipykernel install --user --name ml-project-venv --display-name "ML project (.venv 3.13)"</pre>
<p>Select the kernel <b>"ML project (.venv 3.13)"</b> in Jupyter or VS Code. Pinned versions matter: a different scikit-learn
version can give slightly different numbers.</p>

<h3>2. Get the data</h3>
<ul>
<li><b>Loan data:</b> notebook 01 downloads the public Kaggle <i>Credit Risk Dataset</i> automatically with
<code>kagglehub</code>. If it asks for credentials, create a free Kaggle account and an API token (Kaggle → Settings → API), or
download <code>credit_risk_dataset.csv</code> by hand and point notebook 01 to it.</li>
<li><b>World Bank data:</b> notebook 12 downloads it from the public World Bank API (no key needed) and saves a copy, so it only
downloads once.</li>
<li>The data is <b>not stored in the repository</b> (it is recreated by the notebooks). The repository contains no private data,
passwords or API keys.</li>
</ul>

<h3>3. Run the notebooks in order</h3>
<p>Run each notebook from top to bottom. Later notebooks read files saved by earlier ones (the train/test split, the chosen
settings in <code>reports/</code>), so the order matters. Times are for a 12-core laptop on mains power.</p>
<div class="table-wrap"><table>
<tr><th>Order</th><th>Notebook</th><th>What it does</th><th>Time</th></tr>
<tr><td>1</td><td>{nb("01_clean_split.ipynb")}</td><td>download, cleaning (172 rows removed), stratified 80/20 train/test split, saved once</td><td>&lt; 1 min</td></tr>
<tr><td>2</td><td>{nb("02_probability_of_default.ipynb")}</td><td>Reference: logistic regression, SMOTE, cutoff tuning, linear and RBF SVM with C/γ grid search</td><td>~35 min</td></tr>
<tr><td>3</td><td>{nb("03_decision_trees.ipynb")}</td><td>Reference: decision tree (depth curve, tuning, readable tree)</td><td>~1 min</td></tr>
<tr><td>4</td><td>{nb("05_random_forest.ipynb")}</td><td>Reference: bagging vs Random Forest, tuning, importance</td><td>~10 min</td></tr>
<tr><td>5</td><td>{nb("04_probability_of_default.ipynb")}</td><td>Reference: calibrated PD for every model (<b>needs 03 and 05 first</b>)</td><td>~5 min</td></tr>
<tr><td>6</td><td>{nb("06_applicant_only_models.ipynb")}</td><td>Pipeline B: every model without rate and grade, calibrated PD</td><td>~15 min</td></tr>
<tr><td>7</td><td>{nb("07_interest_rate_regression.ipynb")}</td><td>Pipeline B: interest-rate models, gradient boosting, two-stage grade model</td><td>~5 min</td></tr>
<tr><td>8</td><td>{nb("08_graded_applicant_models.ipynb")}</td><td>Pipeline A: every model with grade but no rate, calibrated PD</td><td>~45 min</td></tr>
<tr><td>9</td><td>{nb("09_interest_rate_with_grade.ipynb")}</td><td>Pipeline A: interest-rate models with grade</td><td>~7 min</td></tr>
<tr><td>10</td><td>{nb("10_results_summary.ipynb")}</td><td>all validation results in one place</td><td>~1 min</td></tr>
<tr><td>11</td><td>{nb("11_final_test.ipynb")}</td><td><b>final test set, used once</b>; error analysis; saves per-applicant test predictions</td><td>~1 min</td></tr>
<tr><td>12</td><td>{nb("12_macro_check.ipynb")}</td><td>World Bank check of the interest rates; website figures</td><td>~1 min</td></tr>
<tr><td>13</td><td>{nb("13_website_checks.ipynb")}</td><td>recomputes the simple counts and shares quoted on this website (no new models)</td><td>&lt; 1 min</td></tr>
</table></div>

<h3>4. Rebuild the website</h3>
<p>Run <code>python src/export_site_data.py</code>. It reads the notebooks' saved results and writes the website's data files
(<code>docs/data/</code>) and figures (<code>docs/figures/</code>). Then run <code>python src/build_site.py docs</code>, which
writes the eight HTML pages. To view the site locally:
<code>python -m http.server 8765 --directory docs</code>, then open <code>http://localhost:8765</code>.</p>

<h3>Why the results come out the same every time</h3>
<ul>
<li><b>Fixed randomness:</b> every random step (the split, the folds, SMOTE, the forests, the bootstrap) uses seed 42.</li>
<li><b>One split, saved:</b> the train/test split is made once in notebook 01 and saved; every later notebook reads the same files.</li>
<li><b>Same folds everywhere:</b> every model uses the same 5 cross-validation folds (<code>src/credit.make_cv</code>), so models
are compared on exactly the same data.</li>
<li><b>No leakage:</b> all learned preprocessing (filling gaps, scaling, encoding, SMOTE) sits inside the model pipeline, so it is
learned from the training folds only.</li>
<li><b>Choices saved, test used once:</b> every choice is made with cross-validation and saved in <code>reports/</code>; notebook 11
is the only notebook that opens the test set.</li>
</ul>

<h2>AI-use disclosure</h2>
<div class="card">
<p><b>Tool used:</b> Claude (Anthropic), model Claude Opus 5.5, through the Claude Code desktop app, 7–17 November 2026.</p>
<p><b>What I did myself.</b> Chose the topic and wrote the research questions and project proposal (data plan, baseline and candidate
methods, evaluation plan). Made the design decisions during the project: working step by step; the three settings (rate + grade
known, grade known, newcomer); which models and hyperparameters to tune; keeping the decision tree as a final-model candidate;
excluding the grade from newcomer pricing; trimming the tree and forest experiments; deferring SMOTENC; the World Bank check.
Reviewed every step's code and results, ran the notebooks, asked questions until I understood each method (cross-validation, SMOTE,
cutoff tuning, calibration, Brier score, bagging, regression metrics), and approved each change before it was made.</p>
<p><b>What the AI assistant did.</b> Wrote most of the Python code in the notebooks and in <code>src/</code> following my instructions
and approvals; explained the theory behind each method and proposed options that I chose between; ran the notebooks to check they
worked and found and fixed errors (for example a leakage risk when using PD as an input to the rate model, and a conclusion about
Pipeline B that the data contradicted); drafted the text of this website and the README, which I reviewed and edited.</p>
<p style="margin-bottom:0"><b>How I checked it.</b> Every number on this site comes from the notebooks in the repository and can be
reproduced by running them. The test set was used once, after all choices were frozen (notebook 11). All conclusions, and any
errors, are my responsibility.</p>
</div>

<h2>Citations</h2>
<ul>
<li>laotse. <i>Credit Risk Dataset</i>. Kaggle. https://www.kaggle.com/datasets/laotse/credit-risk-dataset</li>
<li>World Bank Open Data API: indicators FR.INR.LEND (lending interest rate) and FP.CPI.TOTL.ZG (inflation), United States. https://data.worldbank.org</li>
<li>Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. <i>JMLR</i> 12, 2825–2830.</li>
<li>Lemaître, G., Nogueira, F., Aridas, C. (2017). Imbalanced-learn. <i>JMLR</i> 18(17), 1–5.</li>
<li>Chawla, N. V. et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique. <i>JAIR</i> 16, 321–357.</li>
<li>Breiman, L. (2001). Random Forests. <i>Machine Learning</i> 45, 5–32.</li>
<li>Cortes, C., Vapnik, V. (1995). Support-vector networks. <i>Machine Learning</i> 20, 273–297.</li>
<li>Platt, J. (1999). Probabilistic outputs for support vector machines. <i>Advances in Large Margin Classifiers</i>.</li>
<li>Zadrozny, B., Elkan, C. (2002). Transforming classifier scores into accurate multiclass probability estimates. <i>KDD</i>.</li>
<li>Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. <i>Monthly Weather Review</i> 78(1).</li>
<li>Bergstra, J., Bengio, Y. (2012). Random search for hyper-parameter optimization. <i>JMLR</i> 13, 281–305.</li>
<li>Lipton, Z. C., Elkan, C., Narayanaswamy, B. (2014). Optimal thresholding of classifiers to maximize F1. <i>ECML PKDD</i>.</li>
<li>James, G., Witten, D., Hastie, T., Tibshirani, R. <i>An Introduction to Statistical Learning</i>. Springer.</li>
<li>Software: pandas, NumPy, Matplotlib, Seaborn, Jupyter, requests, kagglehub, Plotly.js (website charts).</li>
<li>AI assistance: Claude (Anthropic); see the AI-use disclosure above.</li>
</ul>
""")
