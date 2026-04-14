"""
buzz_labeler.py
────────────────────────────────────────────────────────────────────────────────
Political buzz labeler for cleaned text data.

Loads a cleaned CSV/parquet, checks the 'title_clean' column for Trump/Harris
keywords, and adds a 'candidate' column (TrumpBuzz / HarrisBuzz / ElectionBuzz).

Works for Bluesky, Twitter/X, Reddit, or any text dataset that has been
pre-processed with apply_text_cleaning().

Run directly
------------
    python buzz_labeler.py

    -> reads  INPUT_PATH  (set below)
    -> writes OUTPUT_PATH (set below)

Import
------
    from buzz_labeler import add_buzz_labels, BuzzConfig
    df = add_buzz_labels(df, text_col='title_clean')
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


# ══════════════════════════════════════════════════════════════════════════════
# ── CONFIGURE HERE ────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

INPUT_PATH  = "../../Data/2_Silver/your_dataset_clean.csv"   # <- change this
OUTPUT_PATH = "../../Data/2_Silver/your_dataset_labeled.csv" # <- change this
TEXT_COL    = "title_clean"   # column that contains the cleaned text


# ══════════════════════════════════════════════════════════════════════════════
# ── CONFIG DATACLASS ──────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BuzzConfig:
    """
    Configuration for the buzz labeler.

    Parameters
    ----------
    labels : list of dicts, each with:
        - "label"    : str        -- name of the buzz category
        - "keywords" : list[str]  -- words to search for (case-insensitive)
    neutral_label : str
        Label used when no category wins (or it's a tie).
    text_col : str
        Default text column (can be overridden in add_buzz_labels).
    whole_word : bool
        If True, only match whole words (e.g. "gop" won't match "gopnik").
    min_score_gap : int
        Minimum difference in keyword hits before declaring a winner.
        Set to 0 to always pick a winner even on a 1-0 score.
    output_col : str
        Name of the new column added to the DataFrame.
    verbose : bool
        Print a short distribution summary after labeling.
    """
    labels: list[dict[str, Any]] = field(default_factory=list)
    neutral_label: str = "ElectionBuzz"
    text_col: str = "title_clean"
    whole_word: bool = True
    min_score_gap: int = 1
    output_col: str = "candidate"
    verbose: bool = True


# ══════════════════════════════════════════════════════════════════════════════
# ── DEFAULT TRUMP / HARRIS 2024 KEYWORDS ──────────────────────────════════════
#
#  Based on the original TRUMP_QUERIES / HARRIS_QUERIES hashtag sets, converted
#  to plain words for use on cleaned text (no #, lowercase, no punctuation).
#  Multi-word phrases are included as joined slugs (e.g. "trumpvance") because
#  apply_text_cleaning() strips punctuation and collapses whitespace.
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = BuzzConfig(
    labels=[
        {
            "label": "TrumpBuzz",
            "keywords": [
                # ── Candidate & running mate ───────────────────────────────
                "trump", "trump2024", "trumpvance", "votetump",
                "trumprally", "trumpdebate", "donaldtrump",
                "vance", "jdvance", "vance2024", "vancevp",
                # ── Party & movement ──────────────────────────────────────
                "republican", "republicans", "gop",
                "rnc", "rnc2024", "republicanconvention",
                "maga", "maga2024", "magacountry",
                "americafirst",
                "makeamericagreatagain",
                # ── Policy / ideological signals ──────────────────────────
                "project2025",
                "stopthesteal",
                "deepstate",
                "saveamerica",
                "trumptrain",
                "ultramaga",
                "patriot", "patriots",
                "conservative", "conservatives",
                "rightwing",
                "letsgobrandon",
                "draintheswamp",
                # ── Media / figures associated with Trump ──────────────────
                "hannity", "tucker", "foxnews", "breitbart",
                "maralago", "truthsocial",
            ],
        },
        {
            "label": "HarrisBuzz",
            "keywords": [
                # ── Candidate & running mate ───────────────────────────────
                "harris", "kamala", "kamalaharris",
                "harris2024", "kamalaharris2024", "kamala2024",
                "voteharris", "votekamala",
                "harriswalz",
                "walz", "timwalz", "walz2024", "walzvp",
                # ── Party & movement ──────────────────────────────────────
                "democrat", "democrats", "democratic",
                "dnc", "dnc2024",
                "demconvention", "democraticconvention",
                "voteblue", "bluewave",
                "winwithkamala",
                "wearenotgoingback",
                # ── Policy / ideological signals ──────────────────────────
                "prochoice", "abortionrights",
                "reproductivefreedom", "reproductiveright",
                "roevwade",
                "progressive", "progressives",
                "leftwing",
                "liberal", "liberals",
                "healthcare", "medicare", "medicaid",
                "climatechange", "greennewdeal",
                "guncontrol", "gunreform",
                "racialjustice", "socialjustice",
                "blacklivesmatter", "blm",
                # ── Media / figures associated with Harris ─────────────────
                "obama", "michelleobama", "barackobama",
                "biden", "joebiden",
                "msnbc",
            ],
        },
    ],
    neutral_label="ElectionBuzz",
)


# ══════════════════════════════════════════════════════════════════════════════
# ── CORE LABELING LOGIC ───────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def _build_pattern(keywords: list[str], whole_word: bool) -> re.Pattern:
    """Compile a single regex pattern from a list of keywords."""
    escaped = [re.escape(k) for k in keywords]
    joined  = "|".join(escaped)
    if whole_word:
        return re.compile(rf"\b(?:{joined})\b", re.IGNORECASE)
    return re.compile(rf"(?:{joined})", re.IGNORECASE)


def _label_row(text: str, patterns: list[tuple[str, re.Pattern]],
               neutral_label: str, min_score_gap: int) -> str:
    """Score one text string against all patterns and return the winning label."""
    text = str(text) if pd.notna(text) else ""

    scores = {label: len(pattern.findall(text)) for label, pattern in patterns}
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    if len(ranked) < 2:
        top_label, top_score = ranked[0]
        return top_label if top_score > 0 else neutral_label

    top_label,  top_score  = ranked[0]
    _,          next_score = ranked[1]

    if top_score == 0:
        return neutral_label
    if (top_score - next_score) < min_score_gap:
        return neutral_label

    return top_label


# ══════════════════════════════════════════════════════════════════════════════
# ── PUBLIC API ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def add_buzz_labels(
    df: pd.DataFrame,
    text_col: str | None = None,
    config: BuzzConfig | None = None,
    output_col: str | None = None,
) -> pd.DataFrame:
    """
    Add a 'candidate' column to a DataFrame by matching keywords in text_col.

    Parameters
    ----------
    df         : Input DataFrame (not modified in place).
    text_col   : Column containing cleaned text. Overrides config.text_col.
    config     : BuzzConfig instance. Defaults to DEFAULT_CONFIG (Trump/Harris).
    output_col : Name for the new column. Overrides config.output_col.

    Returns
    -------
    DataFrame with the new candidate column appended.
    """
    cfg        = config or DEFAULT_CONFIG
    text_col   = text_col   or cfg.text_col
    output_col = output_col or cfg.output_col

    if text_col not in df.columns:
        raise ValueError(f"Column '{text_col}' not found. Available: {list(df.columns)}")
    if not cfg.labels:
        raise ValueError("BuzzConfig.labels is empty — define at least one label.")

    # Pre-compile all patterns once
    patterns = [
        (entry["label"], _build_pattern(entry["keywords"], cfg.whole_word))
        for entry in cfg.labels
    ]

    df = df.copy()
    df[output_col] = df[text_col].apply(
        lambda t: _label_row(t, patterns, cfg.neutral_label, cfg.min_score_gap)
    )

    if cfg.verbose:
        print(f"✓ Buzz labels added -> '{output_col}'")
        print(f"  Rows     : {len(df):,}")
        vc = df[output_col].value_counts()
        for label, count in vc.items():
            print(f"  {label:<20}: {count:,}  ({count/len(df)*100:.1f}%)")
        print()

    return df


def remap_labels(df: pd.DataFrame, remap: dict[str, str],
                 col: str = "candidate") -> pd.DataFrame:
    """Replace old label names with new ones (migration helper)."""
    df = df.copy()
    df[col] = df[col].replace(remap)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# ── MAIN — run directly to label a file ───────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    input_path  = Path(INPUT_PATH)
    output_path = Path(OUTPUT_PATH)

    # ── Load ──────────────────────────────────────────────────────────────────
    print(f"Loading: {input_path}")
    if input_path.suffix == ".parquet":
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)
    print(f"  {len(df):,} rows loaded\n")

    # ── Label on cleaned text column ──────────────────────────────────────────
    df = add_buzz_labels(df, text_col=TEXT_COL)

    # ── Preview ───────────────────────────────────────────────────────────────
    print("Sample output:")
    print(df[[TEXT_COL, "candidate"]].head(10).to_string(index=False))
    print()

    # ── Save ──────────────────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix == ".parquet":
        df.to_parquet(output_path, index=False)
    else:
        df.to_csv(output_path, index=False)
    print(f"✓ Saved to: {output_path}")