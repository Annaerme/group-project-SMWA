# Social Media & Web Analytics — 2024 US Presidential Election

> Can social media signals, news coverage, polling data, and financial markets predict daily movements in election prediction market probabilities?

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
├── Functions/               # Shared Python helpers imported across notebooks
│   ├── buzz_column.py       # Buzz-label assignment logic
│   ├── data_splits.py       # Walk-forward CV split utilities
│   ├── evaluation_metrics.py# Model evaluation helpers
│   └── text_preprocessing.py# Reusable text cleaning functions
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

The campaign window is divided into four narrative eras, each capturing a distinct phase of the race:

| Era | Period | Theme |
|-----|--------|-------|
| **Trump era** | Jul 5 – Jul 20 | Trump leads the race following the first assassination attempt and the JD Vance VP pick |
| **Biden out / Harris in** | Jul 21 – Aug 18 | Biden withdraws, Harris enters, Obama endorses — a sudden reshaping of the field |
| **Debate & second assassination attempt** | Aug 19 – Oct 4 | DNC, the Trump–Harris ABC debate, and the second attempt on Trump's life |
| **Musk mingles** | Oct 5 – Nov 4 | Elon Musk's active campaign involvement, the Vance–Walz debate, and the final stretch |

Within each era the analysis traces how the key events below drove measurable shifts across platforms and prediction markets:

- **Jul 13** — Trump shot at Butler rally
- **Jul 15** — JD Vance announced as VP pick
- **Jul 21** — Biden withdraws from the race
- **Jul 26** — Obama endorses Harris
- **Aug 5** — Harris officially nominated
- **Aug 19** — Democratic National Convention opens
- **Sep 10** — Trump–Harris debate (ABC)
- **Sep 15** — Second assassination attempt on Trump
- **Oct 1** — Vance–Walz VP debate (CBC)
- **Oct 5** — Musk appears at Butler rally with Trump
- **Oct 7** — Musk's America PAC offers $47 per registered swing-state voter
- **Oct 10** — Musk increases petition reward

---

## Predictive Modelling

The predictive phase uses features from all seven sources to forecast the **next-day Polymarket Trump win probability**. The full pipeline runs from raw signals through feature engineering and preprocessing to a structured model comparison and interpretation.

### Feature engineering & preprocessing

All sources are merged into a single daily basetable (`Data/3_Gold/basetable_ultimate.csv`) covering July 5 – November 4, 2024. Features include lagged rolling-window aggregates of post volumes, sentiment scores, NRC emotion profiles, Google Trends indices, poll margins, financial indicators, and time-dimension variables (days to election, days since last major event). Missing values are imputed deterministically — financials are forward-filled (markets are closed on weekends), and pre-event leading NaNs are filled with a fixed prior. Feature selection applies three sequential filters (variance threshold, correlation deduplication, and mutual information) fitted exclusively on the train/validation set to prevent leakage.

### Cross-validation strategy

To respect the time-ordered structure of the data, an **expanding-window walk-forward CV** is used with 3 folds and a 1-day gap between train end and validation start. The final **14-day test set (Oct 22 – Nov 4, 2024)** is held out completely until the final evaluation.

### Models tested

Each feature set is evaluated with the same four model types:

| Model | Notes |
|-------|-------|
| **Ridge Regression** | L2-regularised linear model; alpha tuned per fold via walk-forward CV |
| **Random Forest** | Ensemble of decision trees; captures non-linear interactions |
| **SVM** | RBF-kernel support vector machine; strong on small, noisy datasets |
| **XGBoost** | Gradient-boosted trees; tuned for depth and learning rate |

Models are trained on eight progressively richer feature sets, moving from single-source baselines to full-feature combinations:

| Feature set | Sources included |
|-------------|-----------------|
| Lag-only baseline | Yesterday's Polymarket probability only |
| Social media | Bluesky + Reddit post volumes & sentiment |
| Web search | Google Trends keyword indices |
| Traditional media | Newspaper coverage & NLP features |
| Financial | S&P 500, VIX, oil price |
| Lag + SMWA | Lag + social media + web search |
| Lag + SMWA + traditional media | Above + newspaper features |
| Full | All sources combined |

### Evaluation metrics

Three metrics are reported for every model × feature set combination:

| Metric | Description |
|--------|-------------|
| **Directional Accuracy (DA)** | Fraction of test days where the model correctly predicted the *direction* of next-day movement — the primary operational metric |
| **MAE** | Mean Absolute Error on the raw probability — secondary accuracy metric |
| **R²** | Coefficient of determination; negative for almost all models, which is expected: prediction markets already price in most available information, so daily residuals are near-noise |

A naive baseline (always predict zero change) scores MAE = 0.0162, DA = 0.00, R² = −0.057. The **best model overall is SVM** (DA = 0.571, MAE = 0.0143), correctly predicting the direction of market movement on 8 of the 14 held-out test days.

### Interpretation

Model behaviour is unpacked with four complementary methods:

- **XGBoost gain & Random Forest MDI** — tree-based feature importances as a quick ranking baseline
- **SHAP TreeExplainer (XGBoost)** — exact Shapley values; visualised as beeswarm plots (per-day per-feature contributions), summary bar charts (mean |SHAP|), waterfall plots (single-day decomposition), and dependence plots (non-linear feature effects)
- **SHAP KernelExplainer (SVM)** — sampling-based Shapley values for the black-box best model; compared side-by-side with XGBoost SHAP to identify features that are robustly important across model classes
- **Ridge standardised coefficients** — directly interpretable linear importance scores with direction (sign) indicating whether a feature is associated with an upward or downward move in Trump's predicted probability

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

### Pre-trained models

The NLP notebooks use GloVe word embeddings (100-dimensional vectors trained on Wikipedia + Common Crawl). These are **not** committed to the repository due to file size. Download and place them manually:

1. Download `glove.6B.zip` from [https://nlp.stanford.edu/projects/glove/](https://nlp.stanford.edu/projects/glove/)
2. Extract and place the files under `Pre-trained-models/glove.6B/`:

```
Pre-trained-models/
└── glove.6B/
    ├── glove.6B.50d.txt
    ├── glove.6B.100d.txt   ← used by the notebooks
    ├── glove.6B.200d.txt
    └── glove.6B.300d.txt
```

The notebooks load the embeddings via `GLOVE_PATH = Path('../../Pre-trained-models/glove.6B.100d.txt')`. If the file is not present, the GloVe section is skipped automatically without breaking the rest of the notebook.

> **Data note:** Raw and processed data files are **not** committed to the repository. Run the notebooks in `data_retrieval/` in order (0 → 6) to populate `Data/1_Bronze/`, then run the cleaning/NLP cells in each `Descriptive/` source folder to populate `Data/2_Silver/`.
