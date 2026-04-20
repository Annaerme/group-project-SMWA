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

The descriptive phase answers *what happened* across each data source and *how the sources relate to each other*. For a full clickable index see [`project_overview.ipynb`](project_overview.ipynb).

### Per-source analysis (`0_polymarket/` – `6_polls/`)

Each source is explored in its own subfolder. Social media sources (Reddit, Bluesky, Newspapers) follow a consistent five-step pipeline: exploratory data analysis → network analysis → textual analysis → NLP (topic modelling, NER, embeddings) → sentiment analysis with VADER and NRC emotion profiles. Non-text sources (Polymarket, Financials, Google Trends, Polls) focus on time-series EDA, event-driven patterns, and comparisons with prediction market odds. Google Trends also includes a dedicated state-level analysis covering search-gap rankings across all 51 US states and an animated choropleth.

### Cross-source analysis (`7_cross_source/`)

Once each source is understood in isolation, all daily signals are aligned on a shared timeline (July 5 – November 4, 2024) and examined together. This section covers correlation structure across all features, how media attention and search interest track Polymarket odds, how sentiment divergence relates to shifts in electoral expectations, and how polling margins interact with coverage volume. A final general-insights notebook combines social buzz (Reddit + Bluesky), all attention signals, and Polymarket composites into multi-panel overviews.

### Event studies (`8_events/`)

Four pivotal moments are studied in detail — Trump's campaign arc, the Biden withdrawal and Harris nomination, the debate and second assassination attempt, and Elon Musk's involvement — to understand how discrete real-world events propagate across platforms and markets.

---

## Predictive Modelling

The predictive phase uses the features constructed from all seven sources to forecast **next-day Polymarket win probabilities**. Raw signals are first engineered into lagged rolling-window features and normalised, then fed into a structured model comparison. Models are built progressively — starting from a lag-only baseline, adding single source groups (social media, web search, traditional media, financial), then combining them, and finally running a full-feature model. Model performance is compared systematically, and the best-performing model is interpreted with SHAP to identify which signals drive the predictions.

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
