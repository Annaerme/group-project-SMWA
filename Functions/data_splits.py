"""
data_splits.py — Single source of truth for cross-validation splits.

All team members MUST import their CV folds from this module rather than
defining their own splits. Using different splits across feature branches
will make results incomparable and may introduce data leakage.

Context
-------
Task    : 1-day-ahead forecasting of Polymarket daily prices for the
          2024 US presidential election.
Data    : ~4 months of daily data (approx. Jul–Nov 2024).
Strategy: Expanding-window (walk-forward) time-series cross-validation,
          with a fixed held-out test set covering the final 14 days.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WALK-FORWARD CROSS-VALIDATION  —  how & why
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Full timeline (≈ 120 days, Jul → Nov 2024)
  ├──────────────────────────────────────────────────┤ TEST (14 days, held-out)
  │◄──────────────── CV region (≈ 106 days) ────────►│

  Each fold EXPANDS the training window — no data is ever discarded:

  Fold 1  ├─── TRAIN (~35 d) ───┤·├── VAL (~21 d) ──┤
  Fold 2  ├───── TRAIN (~56 d) ─────┤·├── VAL (~21 d) ──┤
  Fold 3  ├──────── TRAIN (~77 d) ──────────┤·├ VAL (~14 d) ┤
                                              ^
                                           gap = 1 day

  Legend
  ──────
  TRAIN  rows the model is fitted on
  VAL    rows used to evaluate / tune hyperparameters  (never fitted on)
  ·      gap row(s) — intentionally excluded from both sets
  TEST   completely untouched until final model evaluation

WHY WALK-FORWARD (not standard k-fold)?
────────────────────────────────────────
  Standard k-fold shuffles data randomly, so a validation fold can contain
  dates that are EARLIER than some training dates. For a time series that
  means the model "sees the future" during training — an unrealistic
  advantage that inflates CV scores and leads to poor real-world performance.

  Walk-forward respects the arrow of time: the model is always trained on
  the past and evaluated on what comes next, exactly as it would be used in
  production. Each fold simulates a real deployment scenario.

  We use an EXPANDING (not sliding) window because election prediction
  dynamics accumulate over time — early-campaign data remains informative
  even close to election day. A sliding window would needlessly discard
  that signal.

WHY A GAP OF 1 DAY?
────────────────────
  Our features include rolling averages, lag values and other backward-
  looking aggregations computed at day t from days t-1, t-2, … If the last
  training day were immediately adjacent to the first validation day, a
  feature at the boundary could still "bleed" information across the split
  (e.g. a 3-day rolling mean on the first val day would include training
  rows). The 1-day gap eliminates this edge case and mirrors the real
  prediction task: we observe day t-1, then predict day t.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATA LEAKAGE REMINDERS
----------------------
1. Fit scalers/normalizers ONLY on training data per fold; then transform
   val/test with the fitted scaler — never fit on val or test.
2. Rolling/lag features must use ONLY backward-looking windows (shift >= 1).
   Never let a feature at time t see information from t or later.
3. Do NOT touch the held-out test set until final evaluation. Hyperparameter
   tuning and model selection must be done exclusively on CV folds.
4. If you add any feature that aggregates over the full dataset (e.g. mean
   encoding), recompute it inside each fold's training window only.
5. The gap between train and val exists to prevent leakage from rolling
   features that span the boundary. Do not remove it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a proper DatetimeIndex sorted ascending."""
    df = df.copy()
    if not isinstance(df.index, pd.DatetimeIndex):
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
        else:
            raise ValueError(
                "DataFrame must have a DatetimeIndex or a 'date' column."
            )
    df = df.sort_index()
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_cv_folds(
    df: pd.DataFrame,
    n_splits: int = 3,
    gap: int = 1,
    test_days: int | None = None,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Return expanding-window CV folds as integer positional index pairs.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a DatetimeIndex (or a 'date' column), sorted
        chronologically. Each row represents one calendar day.
    n_splits : int
        Number of CV folds (default 5). Each successive fold adds more
        training data (expanding window).
    gap : int
        Number of rows to skip between the end of the training window and
        the start of the validation window. Set to 1 for 1-day-ahead
        forecasting so the model never sees the day it is predicting.
    test_days : int or None
        If provided, the final `test_days` rows are excluded from CV and
        held out as an untouched test set. CV runs only on the earlier rows.

    Returns
    -------
    list of (train_indices, val_indices)
        Each element is a tuple of 1-D integer arrays containing the
        *positional* (iloc) indices of the training and validation rows.

    Example
    -------
    >>> import pandas as pd, numpy as np
    >>> from Functions.data_splits import get_cv_folds, print_fold_summary
    >>> dates = pd.date_range("2024-07-01", periods=120)
    >>> df = pd.DataFrame({"price": np.random.rand(120)}, index=dates)
    >>> folds = get_cv_folds(df, n_splits=5, gap=1, test_days=14)
    >>> print_fold_summary(df, folds)
    """
    df = _ensure_datetime_index(df)
    n_rows = len(df)

    # Carve off the test set before building CV folds
    if test_days is not None:
        cv_df = df.iloc[: n_rows - test_days]
    else:
        cv_df = df

    tscv = TimeSeriesSplit(n_splits=n_splits, gap=gap)

    folds: List[Tuple[np.ndarray, np.ndarray]] = []
    for train_pos, val_pos in tscv.split(cv_df):
        # tscv returns positional indices into cv_df, which is already a
        # contiguous slice of df, so no offset adjustment is needed when
        # test_days is used — the indices are relative to cv_df, not df.
        folds.append((train_pos, val_pos))

    return folds


def get_test_split(
    df: pd.DataFrame,
    test_days: int = 14,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Return (train_val_indices, test_indices) for the final held-out test set.

    The test boundary is determined solely by `test_days` so that every
    team member evaluates on the same rows regardless of feature choices.

    Parameters
    ----------
    df : pd.DataFrame
        Same DataFrame passed to `get_cv_folds`.
    test_days : int
        Number of final rows reserved as the test set (default 14 ≈ 2 weeks).

    Returns
    -------
    (train_val_indices, test_indices)
        Integer positional arrays suitable for use with df.iloc.

    Example
    -------
    >>> tv_idx, test_idx = get_test_split(df, test_days=14)
    >>> train_val_df = df.iloc[tv_idx]
    >>> test_df      = df.iloc[test_idx]
    """
    df = _ensure_datetime_index(df)
    n_rows = len(df)
    split_point = n_rows - test_days

    train_val_indices = np.arange(split_point)
    test_indices = np.arange(split_point, n_rows)
    return train_val_indices, test_indices


def validate_no_leakage(
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    df: pd.DataFrame,
    gap: int = 1,
) -> None:
    """
    Assert that a (train_idx, val_idx) fold is free of data leakage.

    Checks performed
    ----------------
    1. No index overlap between train and val.
    2. Every training date is strictly before every validation date.
    3. The gap between the last training date and the first validation date
       is at least `gap` calendar days.

    Parameters
    ----------
    train_idx : array-like of int
        Positional indices of training rows.
    val_idx : array-like of int
        Positional indices of validation rows.
    df : pd.DataFrame
        The full DataFrame (DatetimeIndex or 'date' column).
    gap : int
        Minimum required gap in calendar days (default 1).

    Raises
    ------
    AssertionError with a descriptive message if any check fails.
    """
    df = _ensure_datetime_index(df)

    train_idx = np.asarray(train_idx)
    val_idx = np.asarray(val_idx)

    # Check 1: no shared positional indices
    overlap = np.intersect1d(train_idx, val_idx)
    assert len(overlap) == 0, (
        f"LEAKAGE: {len(overlap)} indices appear in both train and val: {overlap[:5]}"
    )

    train_dates = df.index[train_idx]
    val_dates = df.index[val_idx]

    # Check 2: all training dates are strictly earlier than all val dates
    assert train_dates.max() < val_dates.min(), (
        f"LEAKAGE: last train date ({train_dates.max().date()}) is not "
        f"before first val date ({val_dates.min().date()})."
    )

    # Check 3: the calendar gap is large enough
    actual_gap = (val_dates.min() - train_dates.max()).days
    assert actual_gap >= gap, (
        f"LEAKAGE: gap between last train date ({train_dates.max().date()}) "
        f"and first val date ({val_dates.min().date()}) is {actual_gap} day(s), "
        f"but required gap is {gap} day(s)."
    )


def print_fold_summary(
    df: pd.DataFrame,
    folds: List[Tuple[np.ndarray, np.ndarray]],
) -> None:
    """
    Print a human-readable table summarising each CV fold.

    Useful for a quick sanity-check in notebooks to confirm all team members
    are working with the same date boundaries.

    Parameters
    ----------
    df : pd.DataFrame
        The full DataFrame used to generate `folds`.
    folds : list of (train_indices, val_indices)
        As returned by `get_cv_folds`.
    """
    df = _ensure_datetime_index(df)

    header = (
        f"{'Fold':>4}  "
        f"{'Train start':>12}  {'Train end':>12}  {'#Train':>7}  "
        f"{'Val start':>12}  {'Val end':>12}  {'#Val':>6}"
    )
    print(header)
    print("-" * len(header))

    for i, (train_idx, val_idx) in enumerate(folds, start=1):
        train_dates = df.index[train_idx]
        val_dates = df.index[val_idx]
        print(
            f"{i:>4}  "
            f"{str(train_dates.min().date()):>12}  "
            f"{str(train_dates.max().date()):>12}  "
            f"{len(train_idx):>7}  "
            f"{str(val_dates.min().date()):>12}  "
            f"{str(val_dates.max().date()):>12}  "
            f"{len(val_idx):>6}"
        )


# ---------------------------------------------------------------------------
# Legacy helper — kept for backward compatibility
# ---------------------------------------------------------------------------

def train_val_test_split(
    df: pd.DataFrame,
    date_col: str = "date",
    train_start: str = "2024-07-05",
    train_end: str = "2024-10-03",
    val_start: str = "2024-10-04",
    val_end: str = "2024-10-20",
    test_start: str = "2024-10-21",
    test_end: str = "2024-11-04",
    verbose: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Fixed-boundary chronological train/validation/test split (legacy).

    Prefer `get_cv_folds` + `get_test_split` for new work. This function
    is retained so existing notebooks do not break.

    Features are always based on day t-1, odds predicted on day t.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    train_df = df[df[date_col].between(train_start, train_end)].copy()
    val_df = df[df[date_col].between(val_start, val_end)].copy()
    test_df = df[df[date_col].between(test_start, test_end)].copy()

    if verbose:
        for name, split in [("Train", train_df), ("Val  ", val_df), ("Test ", test_df)]:
            print(
                f"{name}: {len(split):>5} rows  "
                f"({split[date_col].min().date()} -> {split[date_col].max().date()})"
            )

    return train_df, val_df, test_df


# ---------------------------------------------------------------------------
# Demo / smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import numpy as np

    # Dummy data covering the full timeline, so we can see how the splits work in practice.
    dates = pd.date_range("2024-07-05", "2024-11-05", freq="D")
    rng = np.random.default_rng(42)
    dummy_df = pd.DataFrame(
        {"price": rng.uniform(0.3, 0.8, size=len(dates))},
        index=dates,
    )

    print("=== Test split ===")
    tv_idx, test_idx = get_test_split(dummy_df, test_days=14)
    print(
        f"Train/val rows : {len(tv_idx)}  "
        f"({dummy_df.index[tv_idx[0]].date()} -> {dummy_df.index[tv_idx[-1]].date()})"
    )
    print(
        f"Test rows      : {len(test_idx)}  "
        f"({dummy_df.index[test_idx[0]].date()} -> {dummy_df.index[test_idx[-1]].date()})"
    )

    print("\n=== CV folds (n_splits=5, gap=1, test_days=14) ===")
    folds = get_cv_folds(dummy_df, n_splits=3, gap=1, test_days=14)
    print_fold_summary(dummy_df, folds)

    print("\n=== Leakage validation (all folds) ===")
    for i, (tr, va) in enumerate(folds, 1):
        validate_no_leakage(tr, va, dummy_df, gap=1)
        print(f"  Fold {i}: OK")
