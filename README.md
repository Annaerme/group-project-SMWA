# Social Media & Web Analytics — 2024 US Presidential Election

> Can social media signals, search trends, financial markets, and online betting odds predict the outcome of a presidential election?

This project analyses the **2024 US presidential election** (July 5 – November 4, 2024) by collecting and cross-referencing data from seven distinct sources. It moves from raw data collection through descriptive analysis to predictive modelling, with every notebook sharing a unified visual identity via [`house_style.py`](#house-style).

A high-level map of every notebook is available in [`project_overview.ipynb`](project_overview.ipynb).

---

## Table of Contents

- [Project Structure](#project-structure)
- [Data Sources](#data-sources)
- [Data Retrieval](#data-retrieval)
- [Descriptive Analysis](#descriptive-analysis)
- [Predictive Modelling](#predictive-modelling)
- [House Style](#house-style)
- [Setup & Installation](#setup--installation)

---

## Project Structure

```
.
├── data_retrieval/          # One notebook per data source — API calls & raw saves
├── Data/
│   ├── 1_Bronze/            # Raw data as retrieved (CSV, Parquet)
│   ├── 2_Silver/            # Cleaned & enriched data
│   └── 3_Gold/              # Model-ready feature tables
├── Descriptive/             # EDA, NLP, sentiment, cross-source analysis
│   ├── 0_polymarket/
│   ├── 1_reddit/
│   ├── 2_bluesky/
│   ├── 3_newspapers/
│   ├── 4_financials/
│   ├── 5_google_trends/
│   ├── 6_polls/
│   ├── 7_cross_source/
│   └── 8_events/
├── Predictive/              # Feature engineering → models → SHAP analysis
│   ├── 1_feature_engineering/
│   ├── 2_preprocessing/
│   ├── 3_models/
│   └── 4_model_analysis/
├── house_style.py           # Shared colour palette, style helpers, event markers
├── project_overview.ipynb   # Auto-generated index of all notebooks
├── update_tocs.py           # Script: regenerates TOCs & project_overview.ipynb
└── requirements.txt
```

---

## Data Sources

| # | Source | Bronze folder | Coverage |
|---|--------|---------------|----------|
| 0 | **Polymarket** | `Polymarket/` | Daily Trump/Harris win probabilities |
| 1 | **Reddit** | `Reddit/` | Posts from political subreddits |
| 2 | **Bluesky** | `Bluesky/` | Posts mentioning candidates |
| 3 | **Newspapers** (MediaCloud) | `Newspapers/` | Daily article counts & text |
| 4 | **Financials** | `Financials/` | S&P 500, VIX daily closes |
| 5 | **Google Trends** | `google_trends/` | Daily search interest for `trump`, `kamala`, `vance`, `walz`, `election 2024`; interest by US state |
| 6 | **Polls** | `Polls/` | Wikipedia polling averages |

---

## Data Retrieval

Each notebook in `data_retrieval/` handles one source end-to-end: authentication, pagination, rate-limit handling, and saving to `Data/1_Bronze/`.

| Notebook | Source |
|----------|--------|
| [`0_polymarket.ipynb`](data_retrieval/0_polymarket.ipynb) | Polymarket prediction market API |
| [`1_reddit.ipynb`](data_retrieval/1_reddit.ipynb) | Reddit PRAW API |
| [`2_bluesky.ipynb`](data_retrieval/2_bluesky.ipynb) | Bluesky `atproto` API |
| [`3_media_cloud.ipynb`](data_retrieval/3_media_cloud.ipynb) | MediaCloud news API |
| [`4_financials.ipynb`](data_retrieval/4_financials.ipynb) | `yfinance` / `pandas-datareader` |
| [`5_google_trends.ipynb`](data_retrieval/5_google_trends.ipynb) | `pytrends` — two overlapping windows stitched together |
| [`6_polls.ipynb`](data_retrieval/6_polls.ipynb) | Wikipedia polling table scrape |

---

## Descriptive Analysis

### Per-source notebooks

Each source follows the same five-notebook pattern where applicable:

| Suffix | Focus |
|--------|-------|
| `1_eda` | Distributions, time series, coverage |
| `2_network_analysis` | Retweet / mention graphs |
| `3_textual_analysis` | Word frequencies, topic modelling |
| `4_nlp` | NER, keyword extraction, embeddings |
| `5_sentiment_analysis` | VADER + NRC emotion profiles |

#### 0 · Polymarket
[`0.1_eda`](Descriptive/0_polymarket/0.1_eda.ipynb) — Win-probability time series, volatility, and event-driven spikes.

#### 1 · Reddit
[`1.1_eda`](Descriptive/1_reddit/1.1_eda.ipynb) · [`1.2_network_analysis`](Descriptive/1_reddit/1.2_network_analysis.ipynb) · [`1.3_textual_analysis`](Descriptive/1_reddit/1.3_textual_analysis.ipynb) · [`1.4_nlp`](Descriptive/1_reddit/1.4_nlp.ipynb) · [`1.5_sentiment_analysis`](Descriptive/1_reddit/1.5_sentiment_analysis.ipynb)

#### 2 · Bluesky
[`2.1_eda`](Descriptive/2_bluesky/2.1_eda.ipynb) · [`2.2_network_analysis`](Descriptive/2_bluesky/2.2_network_analysis.ipynb) · [`2.3_textual_analysis`](Descriptive/2_bluesky/2.3_textual_analysis.ipynb) · [`2.4_nlp`](Descriptive/2_bluesky/2.4_nlp.ipynb) · [`2.5_sentiment_analysis`](Descriptive/2_bluesky/2.5_sentiment_analysis.ipynb)

#### 3 · Newspapers
[`3.1_eda`](Descriptive/3_newspapers/3.1_eda.ipynb) · [`3.2_network_analysis`](Descriptive/3_newspapers/3.2_network_analysis.ipynb) · [`3.3_textual_analysis`](Descriptive/3_newspapers/3.3_textual_analysis.ipynb) · [`3.4_nlp`](Descriptive/3_newspapers/3.4_nlp.ipynb) · [`3.5_sentiment_analysis`](Descriptive/3_newspapers/3.5_sentiment_analysis.ipynb)

#### 4 · Financials
[`4.1_eda`](Descriptive/4_financials/4.1_eda.ipynb) — S&P 500 and VIX behaviour relative to campaign events.

#### 5 · Google Trends
[`5.1_eda`](Descriptive/5_google_trends/5.1_eda.ipynb) — National keyword trends, Polymarket overlap, related queries.  
[`5.2_state_analysis`](Descriptive/5_google_trends/5.2_state_analysis.ipynb) — State-level search gap ranking, swing-state focus, VP home-state effects, animated choropleth.

#### 6 · Polls
[`6.1_eda`](Descriptive/6_polls/6.1_eda.ipynb) — Polling averages, margin trends, comparison with prediction markets.

### Cross-source analysis (`7_cross_source/`)

These notebooks bring all sources together on a shared daily timeline (July 5 – November 4 2024).

| Notebook | Focus |
|----------|-------|
| [`7.1_cross_source_overview`](Descriptive/7_cross_source/7.1_cross_source_overview.ipynb) | Pearson correlation heatmap across all features; key-event timeline |
| [`7.2_media_attention`](Descriptive/7_cross_source/7.2_media_attention.ipynb) | Media coverage vs. Polymarket odds; Google Trends vs. odds |
| [`7.3_sentiment_emotions`](Descriptive/7_cross_source/7.3_sentiment_emotions.ipynb) | Sentiment divergence vs. odds; NRC emotion profiles per platform |
| [`7.4_polls_coverage`](Descriptive/7_cross_source/7.4_polls_coverage.ipynb) | Polling margins vs. media coverage |
| [`7.5_general_insights`](Descriptive/7_cross_source/7.5_general_insights.ipynb) | Multi-panel attention overview; social buzz (Reddit + Bluesky); Polymarket composites |

### Event studies (`8_events/`)

Deep-dives into four major campaign moments.

| Notebook | Event |
|----------|-------|
| [`8.1_trump_era`](Descriptive/8_events/8.1_trump_era.ipynb) | Trump's overall campaign arc |
| [`8.2_biden_out_harris_in`](Descriptive/8_events/8.2_biden_out_harris_in.ipynb) | Biden withdrawal & Harris nomination |
| [`8.3_debate_&_trump_assassination_2.0`](Descriptive/8_events/8.3_debate_&_trump_assassination_2.0.ipynb) | Debate night & second assassination attempt |
| [`8.4_musk_mingles`](Descriptive/8_events/8.4_musk_mingles%20copy.ipynb) | Elon Musk's involvement and its measurable impact |

---

## Predictive Modelling

The goal is to predict **Polymarket win probability** (next-day) from lagged social media, sentiment, search, and financial features.

| Notebook | Content |
|----------|---------|
| [`1_feature_engineering`](Predictive/1_feature_engineering/feature_engineering.ipynb) | Rolling windows, lag construction, normalisation |
| [`2_preprocessing`](Predictive/2_preprocessing/preprocessing.ipynb) | Train/validation/test splits, scaling |
| `3_models/Basic/` | Single-source baselines: lag-only, social media, web search, traditional media, financial |
| `3_models/combo/` | Combined models: lag + SMWA; lag + SMWA + traditional media |
| [`3_models/full/full`](Predictive/3_models/full/full.ipynb) | Full-feature model |
| [`4_model_analysis/1_model_analysis`](Predictive/4_model_analysis/1_model_analysis.ipynb) | Performance comparison across all models |
| [`4_model_analysis/2_interpretation_shap`](Predictive/4_model_analysis/2_interpretation_shap.ipynb) | SHAP feature importance & summary plots |

---

## House Style

All notebooks import a shared style module that ensures every figure is immediately recognisable as part of this project.

```python
import sys, importlib
sys.path.insert(0, '../..')   # adjust depth as needed
import house_style as _hs
importlib.reload(_hs)
from house_style import *
apply_style()
```

### Colour conventions

| Constant | Hex | Use |
|----------|-----|-----|
| `REPUBLICAN` | `#e6524d` | Trump / Republican signal |
| `DEMOCRAT` | `#207dff` | Harris / Democrat signal |
| `NEUTRAL` | `#77787A` | Neutral / misc |
| `BLUESKY_BLUE` | `#1185fe` | Bluesky platform series |
| `REDDIT_ORG` | `#e85a28` | Reddit platform series |
| `C_SP500` | `#4a90e2` | S&P 500 |
| `C_VIX` | `#e69c1e` | VIX volatility |
| `C_FEAR / C_ANGER / C_TRUST / …` | — | NRC emotion series |

All figures use a **dark background** (`BG_DARK = #0f171f`) with a slightly lighter panel layer (`BG_PANEL = #16232e`).

### Key helpers

| Function / constant | Purpose |
|---------------------|---------|
| `apply_style()` | Sets matplotlib `rcParams` project-wide |
| `styled_fig(...)` | Creates a pre-styled `(fig, ax)` pair |
| `style_ax(ax, ...)` | Applies axis finishing (grid, ticks, title) |
| `EVENTS` | List of `(label, date, color)` tuples for the 10 key campaign events |
| `add_events(ax)` | Draws dashed vertical event lines on any axis |
| `event_legend_handles()` | Returns legend handles for `EVENTS` |
| `fmt_xaxis(ax)` | Applies `%b %d` date formatting with bi-weekly ticks |
| `wordcloud_palette(...)` | Generates themed colour gradients for word clouds |

### Updating tables of contents

Run from the project root after editing notebooks to regenerate all in-notebook TOCs and rebuild `project_overview.ipynb`:

```bash
python update_tocs.py
```

---

## Setup & Installation

```bash
# Clone the repository
git clone https://github.com/Annaerme/group-project-SMWA.git
cd group-project-SMWA

# Create and activate a virtual environment (conda example)
conda create -n SMWA2026 python=3.11
conda activate SMWA2026

# Install all dependencies
pip install -r requirements.txt

# Optional: download spaCy model
python -m spacy download en_core_web_sm
```

> **Data note:** Raw and processed data files are **not** committed to the repository. Run the notebooks in `data_retrieval/` in order (0 → 6) to populate `Data/1_Bronze/`, then run the cleaning/NLP cells in each `Descriptive/` source folder to populate `Data/2_Silver/`.
