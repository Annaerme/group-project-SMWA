"""
check_data.py -- Verify that all required data files are present locally.

Run from any location:
    python data/check_data.py

The script prints a colour-coded status table and exits with code 1 if any
file is missing, so it can also be used in CI / pre-notebook hooks.
"""

import sys, io
# Force UTF-8 output so Unicode box-drawing chars work on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from pathlib import Path

# ── Resolve the data root relative to this script ─────────────────────────────
DATA = Path(__file__).resolve().parent
BRONZE = DATA / "1_bronze"
SILVER = DATA / "2_silver"
GOLD   = DATA / "3_gold"

# ── Expected files ─────────────────────────────────────────────────────────────
# Format: (absolute_path, description, used_by)
#   used_by: short label of the notebook(s) / pipeline stage that reads this file.

EXPECTED = [
    # ── 1_bronze / bluesky ────────────────────────────────────────────────────
    (BRONZE / "bluesky" / "bsky_US_2024_raw.csv",
     "Raw Bluesky posts (US, 2024)",
     "Bluesky notebooks"),

    # ── 1_bronze / financials ─────────────────────────────────────────────────
    (BRONZE / "financials" / "market.csv",
     "Daily market data (S&P 500, VIX, USD index, …)",
     "Cross-source analysis"),

    (BRONZE / "financials" / "macros.csv",
     "Macroeconomic indicators",
     "Financials analysis"),

    # ── 1_bronze / google_trends ──────────────────────────────────────────────
    (BRONZE / "google_trends" / "trends_daily_stitched.csv",
     "Google Trends — daily stitched (trump, kamala, …)",
     "Cross-source analysis (sec. 8)"),

    (BRONZE / "google_trends" / "trump_daily_by_state.csv",
     "Google Trends — Trump interest by US state",
     "Google Trends analysis"),

    # ── 1_bronze / newspapers ─────────────────────────────────────────────────
    (BRONZE / "newspapers" / "newspaper_articles.csv",
     "Raw newspaper articles (scraped)",
     "3.1 combining / NLP pipeline"),

    (BRONZE / "newspapers" / "mediacloud_stories.csv",
     "MediaCloud raw story-level data",
     "3.1 combining"),

    (BRONZE / "newspapers" / "mediacloud_daily.csv",
     "MediaCloud daily aggregates (basetable_v2 reads from Bronze)",
     "basetable_v2"),

    # ── 1_bronze / polls ──────────────────────────────────────────────────────
    (BRONZE / "polls" / "wikipedia_polls.csv",
     "Wikipedia polling averages (Trump vs Harris)",
     "Cross-source analysis"),

    # ── 1_bronze / polymarket ─────────────────────────────────────────────────
    (BRONZE / "polymarket" / "polymarket_win_probabilities.csv",
     "Polymarket daily win probabilities",
     "Cross-source analysis"),

    (BRONZE / "polymarket" / "polymarket_july.csv",
     "Polymarket data — July detail",
     "Polymarket analysis"),

    # ── 1_bronze / reddit ─────────────────────────────────────────────────────
    (BRONZE / "reddit" / "r_conservative_posts.jsonl",
     "Reddit r/conservative — posts",
     "Reddit textual analysis"),

    (BRONZE / "reddit" / "r_conservative_comments.jsonl",
     "Reddit r/conservative — comments",
     "Reddit textual analysis"),

    (BRONZE / "reddit" / "r_politics_posts.jsonl",
     "Reddit r/politics — posts",
     "Reddit textual analysis"),

    (BRONZE / "reddit" / "r_worldnews_posts.jsonl",
     "Reddit r/worldnews — posts",
     "Reddit textual analysis"),

    (BRONZE / "reddit" / "r_democrats_posts.jsonl",
     "Reddit r/democrats — posts",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_trump_posts.jsonl",
     "Reddit r/trump — posts",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_republican_posts.jsonl",
     "Reddit r/republican — posts",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_liberal_posts.jsonl",
     "Reddit r/liberal — posts",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_trump_comments.jsonl",
     "Reddit r/trump — comments",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_republican_comments.jsonl",
     "Reddit r/republican — comments",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_liberal_comments.jsonl",
     "Reddit r/liberal — comments",
     "basetable_v2"),

    (BRONZE / "reddit" / "r_democrats_comments.jsonl",
     "Reddit r/democrats — comments",
     "basetable_v2"),

    # ── 2_silver / bluesky ────────────────────────────────────────────────────
    (SILVER / "bluesky" / "bsky_US_2024_posts.csv",
     "Bluesky processed posts (US, 2024)",
     "basetable_v2"),

    (SILVER / "bluesky" / "bsky_US_2024_centrality.csv",
     "Bluesky network centrality labels",
     "basetable_v2"),

    (SILVER / "bluesky" / "basetable_train.csv",
     "Bluesky basetable — train split",
     "Bluesky modelling"),

    (SILVER / "bluesky" / "basetable_val.csv",
     "Bluesky basetable — validation split",
     "Bluesky modelling"),

    (SILVER / "bluesky" / "basetable_test.csv",
     "Bluesky basetable — test split",
     "Bluesky modelling"),

    # ── 2_silver / newspapers ─────────────────────────────────────────────────
    (SILVER / "newspapers" / "newspaper_articles_combined.csv",
     "Cleaned & combined newspaper articles",
     "3.2 textual analysis / NLP pipeline"),

    (SILVER / "newspapers" / "textual_features_newspapers.csv",
     "Textual features (TF-IDF, readability, …)",
     "3.2 textual analysis"),

    (SILVER / "newspapers" / "nlp_features_newspapers.csv",
     "NLP features (NER shares, NRC emotions, …)",
     "3.3 NLP / cross-source analysis"),

    (SILVER / "newspapers" / "sentiment_features_newspapers.csv",
     "Sentiment features (VADER scores per leaning)",
     "3.4 sentiment / cross-source analysis"),

    (SILVER / "newspapers" / "mediacloud_daily.csv",
     "MediaCloud daily aggregates (coverage volume, media share)",
     "3.1 combining / cross-source analysis"),

    (SILVER / "newspapers" / "mediacloud_features.csv",
     "MediaCloud engineered features",
     "3.1 combining"),

    # ── 3_gold ────────────────────────────────────────────────────────────────
    (GOLD / "basetable.csv",
     "Master basetable (all sources merged)",
     "Predictive modelling"),

    (GOLD / "basetable_v2.csv",
     "Master basetable v2 (updated feature set)",
     "Predictive modelling"),
]

# ── Runner ─────────────────────────────────────────────────────────────────────
def _fmt_size(path: Path) -> str:
    try:
        b = path.stat().st_size
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.0f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"
    except Exception:
        return "?"


def main() -> int:
    # ANSI colours (gracefully degraded on Windows without ANSI support)
    try:
        import colorama
        colorama.init()
        GREEN  = "\033[92m"
        RED    = "\033[91m"
        YELLOW = "\033[93m"
        RESET  = "\033[0m"
        BOLD   = "\033[1m"
    except ImportError:
        GREEN = RED = YELLOW = RESET = BOLD = ""

    present = []
    missing = []

    col_path  = 52
    col_desc  = 46
    col_used  = 30

    header = (
        f"{'Path':<{col_path}}  {'Description':<{col_desc}}  "
        f"{'Used by':<{col_used}}  Size / Status"
    )
    print(f"\n{BOLD}Data file status — {DATA}{RESET}")
    print("─" * len(header))
    print(BOLD + header + RESET)
    print("─" * len(header))

    for path, desc, used_by in EXPECTED:
        rel = str(path.relative_to(DATA))
        if path.exists():
            size = _fmt_size(path)
            status = f"{GREEN}✓  {size}{RESET}"
            present.append(path)
        else:
            status = f"{RED}✗  MISSING{RESET}"
            missing.append(path)

        print(
            f"{rel:<{col_path}}  {desc:<{col_desc}}  "
            f"{used_by:<{col_used}}  {status}"
        )

    print("─" * len(header))
    print(
        f"\n{BOLD}Summary:{RESET}  "
        f"{GREEN}{len(present)} present{RESET}  |  "
        f"{RED}{len(missing)} missing{RESET}\n"
    )

    if missing:
        print(f"{YELLOW}Missing files — download these from SharePoint:{RESET}")
        for p in missing:
            print(f"  • {p.relative_to(DATA)}")
        print()
        return 1

    print(f"{GREEN}All files present. You're good to go.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
