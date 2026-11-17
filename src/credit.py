"""Shared helpers for the credit-risk notebooks.

Every notebook imports from here so that the data, the 5 CV folds and the preprocessing are
identical everywhere (same as notebook 02). Nothing here touches the test set.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, precision_recall_curve, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
RANDOM_STATE = 42
TARGET = "loan_status"

NUM_COLS = ["person_age", "person_income", "person_emp_length", "loan_amnt",
            "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length"]
CAT_COLS = ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]

# Applicant-only features: what a NEW applicant can provide before the lender has priced the loan
# (no lender-assigned interest rate or grade).
APPLICANT_NUM_COLS = [c for c in NUM_COLS if c != "loan_int_rate"]
APPLICANT_CAT_COLS = [c for c in CAT_COLS if c != "loan_grade"]


def load_train():
    """The 80% training set only (the 20% test set stays locked)."""
    df = pd.read_csv(DATA / "train.csv")
    return df.drop(columns=TARGET), df[TARGET]


def make_cv():
    """The same 5 stratified folds used in notebook 02."""
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


def make_preprocess(num_cols=NUM_COLS, cat_cols=CAT_COLS):
    """Median-impute + scale numeric columns, one-hot encode categorical columns.
    Default = all features (26 after encoding); pass APPLICANT_* for the applicant-only set."""
    return ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                          ("scale", StandardScaler())]), list(num_cols)),
        ("cat", OneHotEncoder(handle_unknown="ignore"), list(cat_cols)),
    ], sparse_threshold=0)   # always dense (gradient boosting needs dense input; values are identical)


def make_pipeline(model, use_smote=False, num_cols=NUM_COLS, cat_cols=CAT_COLS):
    """preprocess -> (SMOTE on the training folds only) -> model."""
    steps = [("prep", make_preprocess(num_cols, cat_cols))]
    if use_smote:
        steps.append(("smote", SMOTE(random_state=RANDOM_STATE)))
    steps.append(("model", model))
    return ImbPipeline(steps)


def f1_curve(score, y):
    """Precision, recall and F1 at EVERY distinct score (the only cutoffs where F1 can change).
    Rule everywhere: predict default if score >= cutoff."""
    precision, recall, thresholds = precision_recall_curve(y, score)
    p, r = precision[:-1], recall[:-1]          # last point (p=1, r=0) has no threshold
    f1 = np.divide(2 * p * r, p + r, out=np.zeros_like(p), where=(p + r) > 0)
    return pd.DataFrame({"precision": p, "recall": r, "f1": f1},
                        index=pd.Index(thresholds, name="cutoff"))


def best_cutoff(score, y):
    """Exact search: the cutoff with the highest F1 over every distinct score."""
    return float(f1_curve(score, y)["f1"].idxmax())


def fold_metrics(score, y, cutoff, X, cv):
    """Per-round metrics (plus mean) from out-of-fold scores at a given cutoff."""
    rows = []
    for k, (_, val_idx) in enumerate(cv.split(X, y), start=1):
        s, yv = score[val_idx], y.iloc[val_idx]
        pred = (s >= cutoff).astype(int)
        rows.append({"round": k, "accuracy": accuracy_score(yv, pred),
                     "precision": precision_score(yv, pred, zero_division=0),
                     "recall": recall_score(yv, pred), "f1": f1_score(yv, pred),
                     "roc_auc": roc_auc_score(yv, s)})
    t = pd.DataFrame(rows).set_index("round")
    t.loc["mean"] = t.mean()
    t.loc["sd"] = t.iloc[:5].std()
    return t


# ---------- probability calibration (same method as notebook 04) ----------
PD_EPS = 1e-3   # keep PDs inside [0.001, 0.999] so log loss stays finite


def as_logit(score, is_probability):
    """Platt scaling works on an unbounded score: use log-odds for models that output probabilities."""
    if is_probability:
        p = np.clip(score, PD_EPS, 1 - PD_EPS)
        return np.log(p / (1 - p))
    return score


def crossfit_calibrate(score, y, X, cv, how):
    """Out-of-fold PDs: the mapping applied to fold k is fitted only on the other folds' scores and labels.
    how = 'Platt (sigmoid)' or 'isotonic'."""
    from sklearn.isotonic import IsotonicRegression
    from sklearn.linear_model import LogisticRegression
    pd_ = np.empty(len(score))
    for tr, va in cv.split(X, y):
        if how == "Platt (sigmoid)":
            m = LogisticRegression(C=1e6).fit(score[tr].reshape(-1, 1), y.iloc[tr])
            pd_[va] = m.predict_proba(score[va].reshape(-1, 1))[:, 1]
        else:
            m = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(score[tr], y.iloc[tr])
            pd_[va] = m.predict(score[va])
    return np.clip(pd_, PD_EPS, 1 - PD_EPS)


def ece(pd_, y, bins=10):
    """Expected calibration error over equal-size bins: average |mean PD - actual default rate|."""
    y = np.asarray(y)
    edges = np.quantile(pd_, np.linspace(0, 1, bins + 1))
    idx = np.clip(np.searchsorted(edges, pd_, side="right") - 1, 0, bins - 1)
    return sum(abs(pd_[idx == b].mean() - y[idx == b].mean()) * (idx == b).mean()
               for b in range(bins) if (idx == b).any())
