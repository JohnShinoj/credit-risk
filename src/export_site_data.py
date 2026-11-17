"""Exports the website's data and figures from the notebooks' saved outputs.

Run after the notebooks (01-12) have been executed:
    .venv/Scripts/python.exe src/export_site_data.py

Writes:
  docs/data/*.json  - test-set applicants with their PDs and suggested rates, all validation scores,
                      final test results, chosen settings and cutoffs, data summary
  docs/figures/*.png - figures from reports/figures/ and selected notebook figures
Nothing is retrained: every number comes from files the notebooks saved.
"""
import base64
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, REPORTS, NB = ROOT / "data" / "processed", ROOT / "reports", ROOT / "notebooks"
OUT = ROOT / "docs"
(OUT / "data").mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(parents=True, exist_ok=True)

SETTINGS = ["Reference (rate + grade)", "Pipeline A (grade)", "Pipeline B (newcomer)"]
SHORT = {"Reference (rate + grade)": "ref", "Pipeline A (grade)": "A", "Pipeline B (newcomer)": "B"}


def write(name, obj):
    path = OUT / "data" / f"{name}.json"
    path.write_text(json.dumps(obj, separators=(",", ":"), default=lambda v: None if pd.isna(v) else v))
    print(f"docs/data/{name}.json  ({path.stat().st_size / 1024:.0f} KB)")


def records(df):
    return json.loads(df.replace({np.nan: None}).to_json(orient="records"))


# ---------- 1. test-set applicants (for the cutoff and applicant explorers) ----------
test = pd.read_csv(DATA / "test.csv")
tp = pd.read_csv(DATA / "test_predictions.csv")
assert len(test) == len(tp)
cols = {"age": "person_age", "income": "person_income", "home": "person_home_ownership",
        "emp": "person_emp_length", "intent": "loan_intent", "grade": "loan_grade", "amount": "loan_amnt",
        "rate": "loan_int_rate", "lti": "loan_percent_income", "pastdef": "cb_person_default_on_file",
        "hist": "cb_person_cred_hist_length", "defaulted": "loan_status"}
app = pd.DataFrame({k: test[v] for k, v in cols.items()})
for s in SETTINGS:
    app[f"pd_{SHORT[s]}"] = tp[f"PD {s}"].round(4)
app["rate_A"] = tp["suggested rate Pipeline A (grade)"].round(2)
app["rate_B"] = tp["suggested rate Pipeline B (newcomer)"].round(2)
write("applicants", {"fields": list(app.columns),
                     "rows": json.loads(app.replace({np.nan: None}).to_json(orient="values"))})

# ---------- 2. chosen models, cutoffs and headline results ----------
ref_sum = pd.read_csv(REPORTS / "pd_summary.csv", index_col=0)
ref_key = next(k for k in ref_sum.index if k.startswith("Random Forest"))
pdA = json.loads((REPORTS / "graded_pd_choice.json").read_text())
pdB = json.loads((REPORTS / "applicant_pd_choice.json").read_text())
rateA = json.loads((REPORTS / "rate_model_with_grade_choice.json").read_text())
rateB = json.loads((REPORTS / "rate_model_choice.json").read_text())
rf_ref = json.loads((REPORTS / "random_forest_choice.json").read_text())["Random Forest"]
write("choices", {
    "ref": {"model": "Random Forest", "params": rf_ref["params"], "calibration": ref_sum.loc[ref_key, "PD method"],
            "cutoff": float(ref_sum.loc[ref_key, "best PD cutoff"]), "notebook": "05 (model), 04 (PD)"},
    "A": {"model": pdA["model"], "params": pdA["params"], "calibration": pdA["calibration"], "cutoff": pdA["pd_cutoff"],
          "notebook": "08", "rate_model": rateA["model"], "rate_inputs": rateA["inputs"], "rate_params": rateA["rf_params"],
          "rate_notebook": "09"},
    "B": {"model": pdB["model"], "params": pdB["params"], "calibration": pdB["calibration"], "cutoff": pdB["pd_cutoff"],
          "notebook": "06", "rate_model": rateB["model"], "rate_inputs": rateB["inputs"], "rate_params": rateB["rf_params"],
          "rate_notebook": "07"},
})
write("headline_test", records(pd.read_csv(REPORTS / "final_test_headline.csv").rename(columns={"Unnamed: 0": "metric"})))
write("headline_validation", records(pd.read_csv(REPORTS / "headline_validation.csv").rename(columns={"Unnamed: 0": "metric"})))
write("test_pd", records(pd.read_csv(REPORTS / "final_test_pd.csv")))
write("test_rate", records(pd.read_csv(REPORTS / "final_test_rate.csv")))
write("test_errors_by_segment", records(pd.read_csv(REPORTS / "final_test_errors_by_segment.csv")))

# ---------- 3. validation scores of every model ----------
write("validation_classification", records(pd.read_csv(REPORTS / "all_classification_scores.csv")))
write("validation_rate", records(pd.read_csv(REPORTS / "all_rate_scores.csv")))

# ---------- 4. data summary ----------
train = pd.read_csv(DATA / "train.csv")
full = pd.concat([train, test], ignore_index=True)
write("data_summary", {
    "raw_rows": 32581, "clean_rows": len(full), "train_rows": len(train), "test_rows": len(test),
    "default_rate": round(full["loan_status"].mean(), 4),
    "missing": {c: int(full[c].isna().sum()) for c in ["person_emp_length", "loan_int_rate"]},
    "grades": records(full.groupby("loan_grade").agg(loans=("loan_status", "size"), default_rate=("loan_status", "mean"),
                                                     mean_rate=("loan_int_rate", "mean")).round(4).reset_index()),
})

# ---------- 5. figures ----------
for png in (REPORTS / "figures").glob("*.png"):
    shutil.copy(png, OUT / "figures" / png.name)
    print(f"docs/figures/{png.name}")


def from_notebook(nb_name, source_snippet, out_name, image_index=0):
    """Save the n-th image output of the first notebook cell whose source contains source_snippet."""
    nb = json.loads((NB / nb_name).read_text(encoding="utf-8"))
    for cell in nb["cells"]:
        if cell["cell_type"] == "code" and source_snippet in "".join(cell["source"]):
            images = [o["data"]["image/png"] for o in cell.get("outputs", []) if "data" in o and "image/png" in o["data"]]
            (OUT / "figures" / f"{out_name}.png").write_bytes(base64.b64decode(images[image_index]))
            print(f"docs/figures/{out_name}.png  (from {nb_name})")
            return
    raise ValueError(f"no cell with {source_snippet!r} in {nb_name}")


from_notebook("02_probability_of_default.ipynb", "thresholds = np.round", "logreg_cutoff_curve")
from_notebook("03_decision_trees.ipynb", "depth_rows = []", "tree_depth_curve")
from_notebook("03_decision_trees.ipynb", "plot_tree(", "tree_depth3", 0)
from_notebook("03_decision_trees.ipynb", "plot_tree(", "tree_importance", 1)
from_notebook("05_random_forest.ipynb", "n_trees = [", "forest_tree_count")
from_notebook("05_random_forest.ipynb", "permutation_importance(pipe", "forest_permutation_importance")
from_notebook("06_applicant_only_models.ipynb", "Preview: interest rate vs", "newcomer_rate_vs_pd")
from_notebook("10_results_summary.ipynb", 'for ax, metric in zip(axes, ["F1", "Brier"])', "validation_f1_brier")
from_notebook("10_results_summary.ipynb", "RATE_ORDER", "validation_rate_r2")
from_notebook("11_final_test.ipynb", "fig, axes = plt.subplots(1, 4", "test_confusion_reliability")
from_notebook("11_final_test.ipynb", "band_rows = []", "test_rate_scatter")
print("done")
