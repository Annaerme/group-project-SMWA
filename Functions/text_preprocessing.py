# text_processing.py

import re
import pandas as pd
from nltk.corpus import stopwords

def clean_text(text: str, stop_words: set = None) -> str:
    """
    Clean a single text string.

    Steps: lowercase → strip URLs/mentions/hashtags →
           keep letters only → collapse spaces → remove stopwords.

    Parameters
    ----------
    text      : Raw input string.
    stop_words: Set of stopwords to remove. Defaults to NLTK English.
    """
    if pd.isna(text):
        return ''

    if stop_words is None:
        stop_words = set(stopwords.words('english'))

    text = str(text).lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)        # URLs
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)               # mentions
    text = re.sub(r'#([A-Za-z0-9_]+)', r'\1', text)          # hashtags
    text = re.sub(r'[^a-z\s]', ' ', text)                    # non-letters
    text = re.sub(r'\s+', ' ', text).strip()                  # whitespace

    tokens = [w for w in text.split() if w not in stop_words]
    return ' '.join(tokens)


def apply_text_cleaning(
    df: pd.DataFrame,
    text_col: str = 'title',
    output_col: str = 'text_clean',
    extra_stopwords: set = None,
    reset_index: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Apply clean_text to a DataFrame and add word count columns.

    Parameters
    ----------
    df              : Input DataFrame.
    text_col        : Column to clean (default: 'title').
    output_col      : Name of the cleaned text column (default: 'text_clean').
    extra_stopwords : Optional extra words to remove on top of NLTK English.
    reset_index     : Reset index after cleaning (default: True).
    verbose         : Print a short summary if True.

    Returns
    -------
    DataFrame with new columns: `output_col`, 'words', 'word_count'.
    """
    df = df.copy()

    stop_words = set(stopwords.words('english'))
    if extra_stopwords:
        stop_words |= set(extra_stopwords)

    df[output_col]  = df[text_col].apply(lambda t: clean_text(t, stop_words))
    df['words']      = df[output_col].str.split()
    df['word_count'] = df['words'].str.len()

    if reset_index:
        df = df.reset_index(drop=True)

    if verbose:
        print(f"✓ Cleaned '{text_col}' → '{output_col}'")
        print(f"  Rows       : {len(df):,}")
        print(f"  Avg words  : {df['word_count'].mean():.1f}")
        print(f"  Empty texts: {(df['word_count'] == 0).sum():,}")
        print()
        print(df[[output_col, 'word_count']].head(3))

    return df