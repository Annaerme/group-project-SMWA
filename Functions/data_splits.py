import pandas as pd
from typing import Tuple

def train_val_test_split(
    df: pd.DataFrame,
    date_col: str = 'date',
    train_start: str = '2024-07-05',
    train_end:   str = '2024-10-03',
    val_start:   str = '2024-10-04',
    val_end:     str = '2024-10-20',
    test_start:  str = '2024-10-21',
    test_end:    str = '2024-11-04',
    verbose: bool = True,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Chronological train/validation/test split.

    Features are always based on day t-1, odds predicted on day t.

    Parameters
    ----------
    df         : Input DataFrame containing a date column.
    date_col   : Name of the date column (default: 'date').
    train_start/end, val_start/end, test_start/end : Inclusive date boundaries.
    verbose    : Print split sizes and date ranges if True.

    Returns
    -------
    train_df, val_df, test_df
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    train_df = df[df[date_col].between(train_start, train_end)].copy()
    val_df   = df[df[date_col].between(val_start,   val_end)].copy()
    test_df  = df[df[date_col].between(test_start,  test_end)].copy()

    if verbose:
        for name, split in [("Train", train_df), ("Val  ", val_df), ("Test ", test_df)]:
            print(f"{name}: {len(split):>5} rows  "
                  f"({split[date_col].min().date()} → {split[date_col].max().date()})")

    return train_df, val_df, test_df

# from data_splits import train_val_test_split
# train_df, val_df, test_df = train_val_test_split(df)