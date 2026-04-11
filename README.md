# Social Media & Web Analytics — Group Project (2025–2026)

**Ghent University — Faculty of Economics and Business Administration**

## Project Overview

This project analyses the **2024 US Presidential Election** (Trump vs. Harris) using a combination of social media, traditional media, financial markets and opinion polls. The end goal is a **predictive model** that forecasts daily Polymarket win probabilities one day ahead, evaluated with time-series cross-validation.

---

## Research Question

> *Can daily sentiment and activity on social media, combined with financial data, polling numbers and news coverage, reliably predict Polymarket win probabilities for the 2024 US presidential election?*

---

## Project Structure

```
group-project-SMWA/
│
├── A. Lectures/                    # Course material & exercises (do not edit)
│   ├── Lecture 1 Social network analysis/
│   ├── Lecture 2 Text mining/
│   ├── Lecture 3 NLP/
│   ├── Lecture 4 Traditional sentiment analysis/
│   ├── Lecture 5 LLM's for sentiment analysis/
│   ├── Lecture 6 Targeting the user/
│   └── installation_guide/
│
├── Data/                           # Medallion data architecture
│   ├── 1_Bronze/                   # Raw data — never edit manually
│   │   ├── Bluesky/                # bsky_US_2024_raw.csv
│   │   ├── Reddit/                 # Posts & comments per subreddit (.jsonl)
│   │   ├── Newspapers/             # MediaCloud & newspaper articles (.csv)
│   │   ├── Polls/                  # Wikipedia polling data
│   │   ├── Polymarket/             # Daily win probabilities
│   │   └── Financials/             # Macroeconomic & financial market data
│   │
│   ├── 2_Silver/                   # Processed, enriched data
│   │   ├── Bluesky/                # Posts + centrality metrics + figures
│   │   ├── Reddit/
│   │   ├── Newspapers/
│   │   ├── Polls/
│   │   ├── Polymarket/
│   │   ├── Financials/
│   │   └── Google Trends/
│   │
│   └── 3_Gold/                     # Model-ready data
│       ├── basetable.csv           # Central base table (all features, daily)
│       ├── text_raw_daily.csv      # Daily raw texts
│       ├── finbert_news_cache.csv  # FinBERT sentiment cache for news articles
│       └── sbert_features_cache.csv # SBERT semantic embeddings (cache)
│
├── Descriptive/                    # Descriptive analyses per data source
│   ├── house_style.py              # Shared visual style (colours, fonts)
│   ├── Bluesky/
│   │   ├── 1_Data_collection.ipynb
│   │   ├── 2_Network_analysis.ipynb
│   │   ├── 3_Sentiment_analysis.ipynb
│   │   ├── 4_Textual_analysis.ipynb
│   │   └── 5_NLP.ipynb
│   ├── Reddit/
│   │   ├── 1_Data_collection.ipynb
│   │   ├── 1_Preprocessing.ipynb
│   │   ├── 2_Network_analysis.ipynb
│   │   ├── 3_Textual_analysis.ipynb
│   │   ├── 3_Wordclouds.ipynb
│   │   └── 4_Sentiment_analysis.ipynb
│   ├── Newspapers/
│   │   ├── 1_retrieval_newspapers.ipynb
│   │   ├── 2_media_cloud.ipynb
│   │   ├── 3_combining_newspapers_mediacloud.ipynb
│   │   ├── 4_Textual_analysis.ipynb
│   │   ├── 5_NLP.ipynb
│   │   ├── 6_analysis.ipynb
│   │   └── 7_cross_source_analysis.ipynb
│   ├── Polls/
│   │   ├── 1_Data_collection.ipynb
│   │   └── 2_Descriptive_analysis.ipynb
│   ├── Polymarket/
│   │   └── polymarket.ipynb
│   ├── Financials/
│   │   └── 1_Descriptive.ipynb
│   └── Google Trends/
│       ├── 1_Data_collection.ipynb
│       ├── 2_Descriptive_analysis.ipynb
│       └── 3_State_analysis.ipynb
│
├── Predictive/                     # Predictive modelling
│   ├── basetable.ipynb             # Builds Data/3_Gold/basetable.csv
│   ├── text_features.ipynb         # SBERT/FinBERT feature extraction
│   ├── modelA.ipynb                # Model A
│   ├── modelB.ipynb                # Model B
│   ├── 5_Predictive_analysis.ipynb # Combined analysis
│   └── Basic/                      # Baseline models per feature group
│       ├── 1_lag.ipynb             # Autoregressive (lag) features
│       ├── 2_social_media.ipynb    # Social media features
│       ├── 3_web.ipynb             # Google Trends features
│       ├── 4_traditional_media.ipynb # Newspaper features
│       └── 5_financial.ipynb       # Financial features
│
├── Functions/                      # Shared Python utility functions
│   ├── data_splits.py              # Time-series cross-validation (single source of truth)
│   └── text_preprocessing.py       # Text cleaning (NLTK)
│
├── Pre-trained-models/             # Cache for large models (ignored by git)
│
├── Assignment_SMWA_20261.pdf       # Official assignment description
├── Rubric_SMWA.pdf                 # Grading rubric
├── cv_splits.html                  # Visualisation of CV splits
├── timeline.html                   # Project timeline
└── timeline_slide.html             # Timeline (slide deck version)
```

---

## Data Sources

| Source | Period | Content | Location (Bronze) |
|---|---|---|---|
| **Bluesky** | Jul–Nov 2024 | Posts around Trump/Harris/election hashtags | `Data/1_Bronze/Bluesky/` |
| **Reddit** | Jul–Nov 2024 | Posts & comments from 7 political subreddits | `Data/1_Bronze/Reddit/` |
| **Newspapers** | Jul–Nov 2024 | MediaCloud + scraped articles | `Data/1_Bronze/Newspapers/` |
| **Google Trends** | Jul–Nov 2024 | Search interest per candidate / per state | *(Silver)* |
| **Polls** | Jun–Nov 2024 | Trump vs. Harris vote share (Wikipedia) | `Data/1_Bronze/Polls/` |
| **Polymarket** | Jul–Nov 2024 | Daily win probabilities (target variable) | `Data/1_Bronze/Polymarket/` |
| **Financial** | Jul–Nov 2024 | S&P500, oil, VIX, 10-year bond, USD index | `Data/1_Bronze/Financials/market.csv` |
| **Macroeconomic** | Monthly | GDP, unemployment, CPI inflation, consumer sentiment | `Data/1_Bronze/Financials/macros.csv` |

### Reddit Subreddits
`r/conservative`, `r/republican`, `r/trump` · `r/democrats`, `r/liberal` · `r/politics`, `r/worldnews`

---

## Data Architecture (Medallion)

```
Bronze (raw)  →  Silver (processed)  →  Gold (model-ready)
```

- **Bronze**: Unprocessed raw data. Never edit manually.
- **Silver**: Filtered, normalised data with added features (sentiment scores, centrality metrics, figures).
- **Gold**: Daily base table (`basetable.csv`) with all features merged, ready for modelling.

---

## Predictive Model

### Target Variable
`polymarket_trump_prob` — Trump's daily win probability on Polymarket (continuous, 0–1).

### Strategy
**1-day-ahead forecasting** via expanding-window walk-forward cross-validation over ~120 days of data (July–November 2024).

```
Full timeline (≈ 120 days, Jul → Nov 2024)
├──────────────────────────────────────────────────┤ TEST (14 days, held-out)
│◄──────────────── CV region (≈ 106 days) ────────►│

Fold 1  ├─── TRAIN (~35 d) ───┤·├── VAL (~21 d) ──┤
Fold 2  ├───── TRAIN (~56 d) ─────┤·├── VAL (~21 d) ──┤
Fold 3  ├──────── TRAIN (~77 d) ──────────┤·├ VAL (~14 d) ┤
                                            ^
                                         gap = 1 day
```

- **Expanding window**: early campaign data remains informative throughout.
- **Gap of 1 day**: prevents leakage from rolling features across the split boundary.
- **Held-out test set**: the final 14 days are only touched after model selection.

### Feature Groups (in `basetable.csv`)
| Group | Example features |
|---|---|
| Lag | `polymarket_trump_prob_lag1`, `days_to_election` |
| Bluesky | `bsky_post_count`, `bsky_trump_sentiment_avg`, `bsky_reply_ratio` |
| Reddit | Sentiment scores per subreddit, post volumes |
| Newspapers | FinBERT sentiment, daily publication volume |
| Google Trends | Search volume Trump/Harris, state-level data |
| Polls | Trump %, Harris %, polling margin |
| Financial | S&P500, VIX, oil, bond yield, USD |
| Macroeconomic | Unemployment, CPI, GDP, consumer sentiment |

---

## Shared Utility Functions

### `Functions/data_splits.py`
Single source of truth for CV splits — all team members use exactly the same date boundaries.

```python
from Functions.data_splits import get_cv_folds, get_test_split, print_fold_summary, validate_no_leakage

# Test split
tv_idx, test_idx = get_test_split(df, test_days=14)

# CV folds
folds = get_cv_folds(df, n_splits=3, gap=1, test_days=14)
print_fold_summary(df, folds)

# Leakage check
for tr, va in folds:
    validate_no_leakage(tr, va, df, gap=1)
```

### `Functions/text_preprocessing.py`
Text cleaning for use across all notebooks.

```python
from Functions.text_preprocessing import apply_text_cleaning

df = apply_text_cleaning(df, text_col='title', output_col='text_clean')
```

Steps: lowercase → remove URLs/mentions/hashtags → letters only → collapse whitespace → stopword filter (NLTK English).

### `Descriptive/house_style.py`
Shared matplotlib style for consistent visualisations across all notebooks.

```python
import sys; sys.path.insert(0, "..")
from house_style import apply_style, REPUBLICAN, DEMOCRAT, NEUTRAL, styled_fig

apply_style()  # call once at the top of each notebook
```

**Colour palette**:
- Republican (Trump): `#e6524d`
- Democrat (Harris): `#207dff`
- Neutral: `#77787A`

> Note: colours reflect *which hashtag cluster a post came from*, not the author's political stance. A "TrumpBuzz" post was found via a Trump-related hashtag — it may be pro- or anti-Trump.

---

## Data Leakage — Rules

1. Fit scalers/normalizers **only on training data** per fold; then transform val/test with the fitted scaler.
2. Rolling/lag features must use **only backward-looking windows** (shift ≥ 1).
3. **Do not touch** the held-out test set until final evaluation.
4. Mean encodings and global aggregations must be **recomputed inside each fold's training window**.
5. **Never remove** the gap between train and val.

---

## Installation

```bash
# Create environment
conda create -n smwa python=3.11
conda activate smwa

# Install dependencies (see installation guide)
pip install -r "A. Lectures/installation_guide/requirements.txt"
```

See `A. Lectures/installation_guide/Installation_Guide_SMWA26.ipynb` for detailed step-by-step instructions.

---

## Workflow

All work is done **in Jupyter notebooks** (no standalone scripts). This ensures reproducibility for the entire team.

Recommended order for a full reproducible run:

1. Run **descriptive notebooks** per data source (Bronze → Silver)
2. Run `Predictive/basetable.ipynb` (Silver → Gold)
3. Run `Predictive/text_features.ipynb` (build SBERT/FinBERT cache)
4. Run baseline models: `Predictive/Basic/1_lag.ipynb` through `5_financial.ipynb`
5. Run main models: `Predictive/modelA.ipynb`, `Predictive/modelB.ipynb`

---

## Team

Ghent University, 2025–2026 — Social Media and Web Analytics (F000799A)
