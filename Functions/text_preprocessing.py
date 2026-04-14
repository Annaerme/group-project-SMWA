
import re
import pandas as pd
from nltk.corpus import stopwords


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_url_slug(token: str) -> bool:
    """
    Detect random-looking URL fragment tokens (e.g. 'aascfgwids').
    Called AFTER punctuation stripping so tokens are already clean letters only.
    """
    if len(token) < 8:
        return False
    vowels = sum(1 for c in token if c in 'aeiou')
    vowel_ratio = vowels / len(token)
    has_digit = any(c.isdigit() for c in token)
    return vowel_ratio < 0.25 or (has_digit and len(token) >= 10)


def remove_urls(text: str) -> str:
    """
    Remove full URLs and short-domain URL patterns BEFORE punctuation stripping.

    Handles:
      - https://... / http://...
      - www....
      - short domains like apple.news/AASCFgwiDS_q
    """
    if not isinstance(text, str):
        return text
    text = re.sub(r'https?://\S+', '', text)        # full https / http URLs
    text = re.sub(r'www\.\S+', '', text)             # www. URLs
    text = re.sub(r'\b\w+\.\w+/\S+', '', text)      # short domains (apple.news/xxx)
    return re.sub(r'\s+', ' ', text).strip()


# ── Core cleaning function ────────────────────────────────────────────────────

def clean_text(text: str, stop_words: set = None) -> str:
    """
    Clean a single text string.

    Pipeline:
        1. Lowercase
        2. Remove URLs (full + short domain)
        3. Backup URL pass (safety net)
        4. Remove @mentions
        5. Strip # from hashtags (keep the word)
        6. Remove non-letter characters
        7. Collapse whitespace
        8. Tokenise → filter stopwords + short tokens + URL slugs

    Parameters
    ----------
    text       : Raw input string.
    stop_words : Set of stopwords to remove. Defaults to NLTK English.
    """
    if pd.isna(text):
        return ''

    if stop_words is None:
        stop_words = set(stopwords.words('english'))

    text = str(text).lower()                                   # 1. lowercase
    text = remove_urls(text)                                   # 2. remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)         # 3. backup URL pass
    text = re.sub(r'@[A-Za-z0-9_]+', '', text)                # 4. mentions
    text = re.sub(r'#([A-Za-z0-9_]+)', r'\1', text)           # 5. hashtags
    text = re.sub(r'[^a-z\s]', ' ', text)                     # 6. non-letters
    text = re.sub(r'\s+', ' ', text).strip()                   # 7. whitespace

    # 8. filter tokens — stopwords + length + URL slug check (must be last)
    tokens = [
        w for w in text.split()
        if w not in stop_words
        and len(w) >= 3
        and not _is_url_slug(w)
    ]
    return ' '.join(tokens)


# ── DataFrame-level function ──────────────────────────────────────────────────

def apply_text_cleaning(
    df: pd.DataFrame,
    text_col: str = 'text',
    output_col: str = 'text_clean',
    extra_stopwords: set = None,
    reset_index: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Apply clean_text to a DataFrame column and add word count columns.

    Parameters
    ----------
    df              : Input DataFrame.
    text_col        : Column to clean (default: 'text').
    output_col      : Name for the cleaned text column (default: 'text_clean').
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

    df[output_col]   = df[text_col].apply(lambda t: clean_text(t, stop_words))
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
    