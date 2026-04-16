"""
evaluation_metrics.py
─────────────────────────────────────────────────────────────────────────────
Shared evaluation helpers for all model notebooks.

Import
------
    from Functions.evaluation_metrics import (
        directional_accuracy, compute_metrics, cv_evaluate, final_eval,
        tune_hyperparams,
    )
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


def directional_accuracy(y_true, y_pred):
    """Fraction of predictions with the correct direction (sign)."""
    return float(np.mean(np.sign(y_true) == np.sign(y_pred)))


def compute_metrics(y_true, y_pred):
    """Return MAE, RMSE, Directional Accuracy and R² as a dict."""
    return {
        "MAE"          : mean_absolute_error(y_true, y_pred),
        "RMSE"         : np.sqrt(mean_squared_error(y_true, y_pred)),
        "Dir. Accuracy": directional_accuracy(y_true, y_pred),
        "R2"           : r2_score(y_true, y_pred),
    }


def cv_evaluate(model_factory, folds, X, y, scale=False):
    """
    Walk-forward cross-validation.

    Parameters
    ----------
    model_factory : callable
        Zero-argument callable that returns a fresh (unfitted) model.
    folds : list of (train_idx, val_idx) tuples
        From get_cv_folds() in data_splits.py.
    X : np.ndarray  (n_samples, n_features)
    y : np.ndarray  (n_samples,)
    scale : bool
        If True, fit StandardScaler on train fold, transform both.

    Returns
    -------
    pd.DataFrame with one row per fold + Mean and Std summary rows.
    """
    records = []
    for i, (train_idx, val_idx) in enumerate(folds, 1):
        X_tr, y_tr   = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx],   y[val_idx]
        if scale:
            sc    = StandardScaler()
            X_tr  = sc.fit_transform(X_tr)
            X_val = sc.transform(X_val)
        model = model_factory()
        model.fit(X_tr, y_tr)
        m = compute_metrics(y_val, model.predict(X_val))
        records.append({"Fold": i, **m})
        print(f"  Fold {i}: MAE={m['MAE']:.4f}  RMSE={m['RMSE']:.4f}  "
              f"DA={m['Dir. Accuracy']:.3f}  R2={m['R2']:.4f}")
    agg  = pd.DataFrame(records).set_index("Fold")
    mean = agg.mean().rename("Mean")
    std  = agg.std().rename("Std")
    print(f"  -- Mean --  MAE={mean['MAE']:.4f}  RMSE={mean['RMSE']:.4f}  "
          f"DA={mean['Dir. Accuracy']:.3f}  R2={mean['R2']:.4f}")
    return pd.concat([agg, mean.to_frame().T, std.to_frame().T])


def tune_hyperparams(make_model, param_grid, folds, X, y, scale=False):
    """
    Grid search over param_grid using walk-forward CV folds.

    Parameters
    ----------
    make_model : callable
        Function(**params) -> fresh unfitted sklearn-compatible model.
        Must accept every key in param_grid as a keyword argument.
    param_grid : dict
        {param_name: [values_to_try], ...}
    folds : list of (train_idx, val_idx)
        Walk-forward CV folds from get_cv_folds().
    X : np.ndarray  (n_samples, n_features)
    y : np.ndarray  (n_samples,)
    scale : bool
        If True, fit StandardScaler on train fold only, transform both.

    Returns
    -------
    best_params : dict
        Parameter combination with the lowest mean CV MAE.
    results_df : pd.DataFrame
        All combinations sorted by cv_mae ascending, with cv_mae_std column.
    """
    from itertools import product as iterproduct

    keys   = list(param_grid.keys())
    combos = list(iterproduct(*param_grid.values()))

    records    = []
    best_mae   = float("inf")
    best_params = None  # kept as original Python types from param_grid

    for combo in combos:
        params    = dict(zip(keys, combo))
        fold_maes = []
        for train_idx, val_idx in folds:
            X_tr, y_tr   = X[train_idx], y[train_idx]
            X_val, y_val = X[val_idx],   y[val_idx]
            if scale:
                sc    = StandardScaler()
                X_tr  = sc.fit_transform(X_tr)
                X_val = sc.transform(X_val)
            model = make_model(**params)
            model.fit(X_tr, y_tr)
            fold_maes.append(mean_absolute_error(y_val, model.predict(X_val)))
        mean_mae = float(np.mean(fold_maes))
        if mean_mae < best_mae:
            best_mae    = mean_mae
            best_params = params          # original Python int/float from param_grid
        records.append({
            **params,
            "cv_mae"    : mean_mae,
            "cv_mae_std": float(np.std(fold_maes)),
        })

    results_df = pd.DataFrame(records).sort_values("cv_mae").reset_index(drop=True)
    return best_params, results_df


def final_eval(model_factory, X_tv, y_tv, X_test, y_test, scale=False):
    """
    Train on full train+val set, evaluate on held-out test set.

    Returns
    -------
    model   : fitted model
    y_pred  : test-set predictions
    metrics : dict from compute_metrics()
    """
    if scale:
        sc       = StandardScaler()
        X_tv_s   = sc.fit_transform(X_tv)
        X_test_s = sc.transform(X_test)
    else:
        X_tv_s, X_test_s = X_tv, X_test
    model = model_factory()
    model.fit(X_tv_s, y_tv)
    y_pred = model.predict(X_test_s)
    return model, y_pred, compute_metrics(y_test, y_pred)
