"""
rewrite_nlp.py — Applies house style + adds result tables to 2.4_nlp.ipynb
"""
import json
import copy
import uuid
from pathlib import Path

NB_PATH = Path("Descriptive/2_bluesky/2.4_nlp.ipynb")

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

# ── Helper ──────────────────────────────────────────────────────────────────────
def cell_by_id(cells, cid):
    for i, c in enumerate(cells):
        if c.get("id") == cid:
            return i, c
    return None, None

def make_code_cell(source_str, cell_id=None):
    if cell_id is None:
        cell_id = uuid.uuid4().hex[:8]
    lines = source_str.split("\n")
    src = []
    for j, line in enumerate(lines):
        src.append(line + ("\n" if j < len(lines) - 1 else ""))
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": src,
    }

def set_source(cell, source_str):
    lines = source_str.split("\n")
    src = []
    for j, line in enumerate(lines):
        src.append(line + ("\n" if j < len(lines) - 1 else ""))
    cell["source"] = src
    cell["outputs"] = []
    cell["execution_count"] = None

cells = nb["cells"]

# ══════════════════════════════════════════════════════════════════════════════
# 1. Setup cell — add FIGURES_DIR, TABLES_DIR, render_table_png
# ══════════════════════════════════════════════════════════════════════════════
idx, cell = cell_by_id(cells, "c4de48a0")
new_setup = '''import os
import sys
import time
import re
import string
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Navigate to project root so Data/ paths resolve correctly
PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), "../.."))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

# House style
from house_style import *
apply_style()

# Output dirs
FIGURES_DIR = Path(PROJECT_ROOT) / "latex_template" / "figures" / "bluesky"
TABLES_DIR  = FIGURES_DIR / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# LDA
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from sklearn.feature_extraction.text import CountVectorizer

# NLTK
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download("punkt",     quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
from wordcloud import WordCloud


def render_table_png(df, out_path, title=None, dpi=150):
    """Save a DataFrame as a styled PNG table (financials macro style)."""
    import matplotlib as mpl
    n_rows, n_cols = df.shape
    col_strs = [str(c) for c in df.columns]
    char_widths = []
    for j, col in enumerate(df.columns):
        max_data = df[col].astype(str).str.len().max() if len(df) > 0 else 0
        char_widths.append(max(len(str(col)), int(max_data)) + 2)
    total_chars = sum(char_widths)
    col_widths  = [w / total_chars for w in char_widths]

    fig_w = max(8, min(16, total_chars * 0.12))
    fig_h = max(2, 0.5 + n_rows * 0.42)
    fig = plt.figure(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor(BG_DARK)

    ax = fig.add_axes([0.01, 0.04, 0.98, 0.88])
    ax.set_facecolor(BG_DARK)
    ax.axis("off")

    cell_text  = df.astype(str).values.tolist()
    col_labels = list(df.columns)

    tbl = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        colWidths=col_widths,
        loc="center",
        cellLoc="left",
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1.0, 2.0)

    header_color = "#1c2d3e"
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(SPINE_COLOR)
        cell.set_linewidth(0.6)
        if row == 0:
            cell.set_facecolor(header_color)
            cell.get_text().set_color(TEXT_PRIMARY)
            cell.get_text().set_fontweight("bold")
            cell.get_text().set_fontsize(12)
        else:
            cell.set_facecolor(BG_PANEL if row % 2 == 0 else BG_DARK)
            cell.get_text().set_color(TEXT_PRIMARY)

    if title:
        fig.text(0.5, 0.97, title, ha="center", va="top",
                 color=TEXT_PRIMARY, fontsize=12, fontweight="bold")

    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor=BG_DARK, edgecolor="none")
    plt.close(fig)


print(f"Working directory: {os.getcwd()}")
print("Libraries imported successfully!")
print(f"Figures dir: {FIGURES_DIR}")
print(f"Tables dir:  {TABLES_DIR}")'''

set_source(cell, new_setup)

# ══════════════════════════════════════════════════════════════════════════════
# 2. After preprocessing (d04508d5) — insert preprocessing summary table cell
# ══════════════════════════════════════════════════════════════════════════════
idx_pre, _ = cell_by_id(cells, "d04508d5")
preprocess_table_src = '''# Preprocessing summary table
preprocess_summary = pd.DataFrame({
    "Step": [
        "Source column",
        "Tokenisation",
        "Filter: alphabetic only",
        "Filter: length > 2 chars",
        "Stopwords",
        "BERTopic: URL removal",
        "Documents (LDA)",
        "Documents (BERTopic)",
    ],
    "Detail": [
        "text_clean (already lowercased & normalised in 2.2)",
        "NLTK word_tokenize",
        "Keeps only [a-z]+ tokens",
        "Removes 1-2 char tokens",
        "NLTK English stopwords (no extra domain stops applied)",
        "Regex strip http/https/www + email addresses",
        f"{len(df_lda):,}",
        f"{len(df_bertopic):,}",
    ],
})
render_table_png(
    preprocess_summary,
    TABLES_DIR / "nlp_preprocessing.png",
    title="LDA Preprocessing Pipeline",
)
print("Saved nlp_preprocessing.png")
display(preprocess_summary)'''

cells.insert(idx_pre + 1, make_code_cell(preprocess_table_src, "nlp-prep-tbl"))

# ══════════════════════════════════════════════════════════════════════════════
# 3. Dictionary cell (403a3836) — keep existing code, then insert dict table after
# ══════════════════════════════════════════════════════════════════════════════
idx_dict, cell_dict = cell_by_id(cells, "403a3836")

dict_table_src = '''# Dictionary statistics table
top_terms  = sorted(dictionary.dfs.items(), key=lambda x: x[1], reverse=True)[:15]
top_terms_df = pd.DataFrame([
    {"Term": dictionary[tid], "Doc frequency": freq, "Token ID": tid}
    for tid, freq in top_terms
])

dict_stats = pd.DataFrame({
    "Metric": [
        "Raw vocabulary size",
        "After filter_extremes (no_below=5, no_above=0.5)",
        "Total documents in corpus",
        "Filter: min doc frequency",
        "Filter: max doc frequency",
    ],
    "Value": [
        "30,019",
        f"{len(dictionary):,}",
        f"{len(corpus):,}",
        "5 documents",
        "50% of documents",
    ],
})
render_table_png(
    dict_stats,
    TABLES_DIR / "nlp_dictionary.png",
    title="LDA Dictionary Statistics",
)
print("Saved nlp_dictionary.png")

render_table_png(
    top_terms_df,
    TABLES_DIR / "nlp_top_terms.png",
    title="Top 15 Most Frequent Terms (after filtering)",
)
print("Saved nlp_top_terms.png")
display(dict_stats)
display(top_terms_df)'''

cells.insert(idx_dict + 1, make_code_cell(dict_table_src, "nlp-dict-tbl"))

# ══════════════════════════════════════════════════════════════════════════════
# 4. Coherence plot cell (c4f5a740) — add save + grid style + axes spines
# ══════════════════════════════════════════════════════════════════════════════
idx_coh, cell_coh = cell_by_id(cells, "c4f5a740")
new_coh_plot = '''fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.patch.set_facecolor(BG_DARK)
fig.suptitle("LDA Model Selection: Coherence & AIC", color=TEXT_PRIMARY,
             fontsize=14, fontweight="bold")

for ax, scores, ylabel, title, color in [
    (ax1, coherence_scores_lda, "Coherence Score (u_mass)", "Coherence vs Number of Topics", TM_DEEP_BLUE),
    (ax2, aic_scores_lda,       "AIC",                      "AIC vs Number of Topics",       TM_CRIMSON),
]:
    style_ax(ax, xlabel="Number of Topics", ylabel=ylabel, title=title)
    ax.plot(list(topic_range), scores, marker="o", color=color, linewidth=2, markersize=7)
    best_val = max(scores) if "Coherence" in ylabel else min(scores)
    ax.axhline(best_val, color=REPUBLICAN, lw=1.5, ls="--",
               label=f\'{"Max" if "Coherence" in ylabel else "Min"}: {best_val:.2f}\')
    place_legends_bottom(ax, main_ncol=1, main_y=0.02, event_y=-0.15)

plt.tight_layout(rect=[0, 0.08, 1, 0.96])
fig.savefig(FIGURES_DIR / "nlp_1_coherence.png", dpi=150, bbox_inches="tight",
            facecolor=BG_DARK, edgecolor="none")
plt.show()

optimal_topics_lda = list(topic_range)[np.argmax(coherence_scores_lda)]
print(f"\\nOptimal number of topics (coherence): {optimal_topics_lda}")
print(f"  Coherence: {max(coherence_scores_lda):.4f}")
print(f"  AIC at optimal: {aic_scores_lda[list(topic_range).index(optimal_topics_lda)]:.2f}")'''

set_source(cell_coh, new_coh_plot)

# Insert coherence sweep table after the plot cell
idx_coh2, _ = cell_by_id(cells, "c4f5a740")
coh_table_src = '''# Coherence sweep results table
sweep_df = pd.DataFrame({
    "# Topics": list(topic_range),
    "Coherence (u_mass)": [f"{s:.4f}" for s in coherence_scores_lda],
    "AIC": [f"{s:,.0f}" for s in aic_scores_lda],
    "Selected": ["*" if i == optimal_topics_lda - list(topic_range)[0] else "" for i in range(len(list(topic_range)))],
})
render_table_png(
    sweep_df,
    TABLES_DIR / "nlp_coherence_sweep.png",
    title="LDA Coherence & AIC Sweep Results",
)
print("Saved nlp_coherence_sweep.png")
display(sweep_df)'''

cells.insert(idx_coh2 + 1, make_code_cell(coh_table_src, "nlp-coh-tbl"))

# ══════════════════════════════════════════════════════════════════════════════
# 5. Train model cell (799c88ed) — add model summary table after training
# ══════════════════════════════════════════════════════════════════════════════
idx_train, cell_train = cell_by_id(cells, "799c88ed")
new_train = '''print(f"Training final LDA model with {optimal_topics_lda} topics...")

lda_train_start = time.time()
lda_model = LdaModel(
    corpus=corpus, id2word=dictionary,
    num_topics=optimal_topics_lda, random_state=42,
    passes=15, iterations=400,
    alpha="auto", eta="auto", per_word_topics=True
)
lda_train_time = time.time() - lda_train_start
print(f"LDA trained in {lda_train_time:.1f}s")

cm_final = CoherenceModel(model=lda_model, texts=tokenized_docs,
                          dictionary=dictionary, coherence="u_mass")
coherence_lda_final = cm_final.get_coherence()
print(f"Final LDA Coherence (u_mass): {coherence_lda_final:.4f}")

# Model summary table
model_summary = pd.DataFrame({
    "Parameter": [
        "Number of topics",
        "Passes",
        "Iterations",
        "Alpha",
        "Eta",
        "Dictionary size",
        "Corpus size",
        "Training time (s)",
        "Final coherence (u_mass)",
    ],
    "Value": [
        str(optimal_topics_lda),
        "15",
        "400",
        "auto",
        "auto",
        f"{len(dictionary):,}",
        f"{len(corpus):,}",
        f"{lda_train_time:.1f}",
        f"{coherence_lda_final:.4f}",
    ],
})
render_table_png(
    model_summary,
    TABLES_DIR / "nlp_model_summary.png",
    title="Final LDA Model Configuration",
)
print("Saved nlp_model_summary.png")
display(model_summary)'''

set_source(cell_train, new_train)

# ══════════════════════════════════════════════════════════════════════════════
# 6. Topic words cell (0be20bd3) — add topic words table
# ══════════════════════════════════════════════════════════════════════════════
idx_words, cell_words = cell_by_id(cells, "0be20bd3")
new_words = '''lda_topics = []
rows = []
for i in range(lda_model.num_topics):
    word_weights = lda_model.show_topic(i, topn=10)
    words = [w for w, _ in word_weights]
    lda_topics.append(words)
    rows.append({
        "Topic": f"Topic {i}",
        "Top 10 words": ", ".join(words),
        "Top weight": f"{word_weights[0][1]:.3f}",
    })
    print(f"LDA Topic {i}: {chr(44).join(words)}")

topic_words_df = pd.DataFrame(rows)
render_table_png(
    topic_words_df,
    TABLES_DIR / "nlp_topic_words.png",
    title="LDA Topic Keywords (Top 10 Words per Topic)",
)
print("Saved nlp_topic_words.png")
display(topic_words_df)'''

set_source(cell_words, new_words)

# ══════════════════════════════════════════════════════════════════════════════
# 7. Wordclouds cell (81704b61) — save figure
# ══════════════════════════════════════════════════════════════════════════════
idx_wc, cell_wc = cell_by_id(cells, "81704b61")
new_wc = '''n_topics_lda = lda_model.num_topics
n_cols = 2
n_rows = (n_topics_lda + 1) // 2

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 5 * n_rows))
fig.patch.set_facecolor(BG_DARK)
axes = axes.flatten()

for topic_id in range(n_topics_lda):
    topic_data   = lda_model.show_topic(topic_id, topn=30)
    word_weights = {word: weight for word, weight in topic_data}

    wc = WordCloud(
        width=800, height=400,
        background_color=BG_PANEL,
        color_func=wordcloud_color_func(topic_id=topic_id, seed=42, n_shades=9),
        max_words=30,
        prefer_horizontal=0.9
    ).generate_from_frequencies(word_weights)

    ax = axes[topic_id]
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_facecolor(BG_DARK)
    ax.set_title(f"Topic {topic_id}: {lda_topics[topic_id][0]} / {lda_topics[topic_id][1]}",
                 color=TEXT_PRIMARY, fontweight="bold", fontsize=11, pad=8)

for i in range(n_topics_lda, len(axes)):
    axes[i].set_visible(False)

fig.suptitle("LDA Topics — Bluesky US Election 2024",
             color=TEXT_PRIMARY, fontsize=14, fontweight="bold")
plt.tight_layout()
fig.savefig(FIGURES_DIR / "nlp_2_wordclouds.png", dpi=150, bbox_inches="tight",
            facecolor=BG_DARK, edgecolor="none")
print("Saved nlp_2_wordclouds.png")
plt.show()'''

set_source(cell_wc, new_wc)

# ══════════════════════════════════════════════════════════════════════════════
# 8. Topics over time cell (dd4f567b) — save figure
# ══════════════════════════════════════════════════════════════════════════════
idx_time, cell_time = cell_by_id(cells, "dd4f567b")
new_time = '''# Assign dominant LDA topic to each post
def get_dominant_topic_lda(ldamodel, corpus):
    dominant = []
    for doc in corpus:
        dist = ldamodel.get_document_topics(doc)
        dominant.append(sorted(dist, key=lambda x: x[1], reverse=True)[0][0] if dist else -1)
    return dominant

df_lda["lda_topic"] = get_dominant_topic_lda(lda_model, corpus)

topic_labels = {
    i: " / ".join([w for w, _ in lda_model.show_topic(i, topn=3)])
    for i in range(lda_model.num_topics)
}

daily_topic_counts = (
    df_lda.groupby(["timestamp", "lda_topic"])
    .size()
    .reset_index(name="post_count")
)
daily_totals = df_lda.groupby("timestamp").size().reset_index(name="total")
daily_topic_counts = daily_topic_counts.merge(daily_totals, on="timestamp")
daily_topic_counts["share"] = daily_topic_counts["post_count"] / daily_topic_counts["total"] * 100

topic_share_pivot = (
    daily_topic_counts
    .pivot(index="timestamp", columns="lda_topic", values="share")
    .fillna(0)
)
topic_share_pivot.index = pd.to_datetime(topic_share_pivot.index)
topic_share_pivot = topic_share_pivot.sort_index()

fig, ax = plt.subplots(figsize=(18, 6))
fig.patch.set_facecolor(BG_DARK)
style_ax(ax, ylabel="Share of posts (%)",
         title="LDA Topic Prominence Over Time — Bluesky US Election 2024\\n(7-day rolling mean, % of daily posts)")

for topic_id in topic_share_pivot.columns:
    smooth = topic_share_pivot[topic_id].rolling(7, center=True, min_periods=3).mean()
    ax.plot(
        topic_share_pivot.index, smooth,
        label=f"Topic {topic_id}: {topic_labels[topic_id]}",
        linewidth=2, color=TOPIC_MODEL_COLORS[int(topic_id) % len(TOPIC_MODEL_COLORS)]
    )

add_events(ax)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=40)

event_handles = event_legend_handles(EVENTS)
place_legends_bottom(
    ax,
    event_handles=event_handles,
    main_ncol=2, event_ncol=4,
    main_y=0.20, event_y=0.03,
    main_title="Topics", event_title="Key Events",
)
plt.tight_layout(rect=[0, 0.28, 1, 1])
fig.savefig(FIGURES_DIR / "nlp_3_topics_time.png", dpi=150, bbox_inches="tight",
            facecolor=BG_DARK, edgecolor="none")
print("Saved nlp_3_topics_time.png")
plt.show()'''

set_source(cell_time, new_time)

# ══════════════════════════════════════════════════════════════════════════════
# 9. Buzz group cell (e840446e) — save figure + add buzz table after
# ══════════════════════════════════════════════════════════════════════════════
idx_buzz, cell_buzz = cell_by_id(cells, "e840446e")
new_buzz = '''lda_buzz     = df_lda.groupby(["candidate", "lda_topic"]).size().unstack(fill_value=0)
lda_buzz_pct = lda_buzz.div(lda_buzz.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor(BG_DARK)
style_ax(ax, ylabel="% of posts",
         title="LDA Topic Distribution per Buzz Group")

bottom = np.zeros(len(lda_buzz_pct))
for i, col in enumerate(lda_buzz_pct.columns):
    ax.bar(
        lda_buzz_pct.index,
        lda_buzz_pct[col],
        bottom=bottom,
        label=f"Topic {col}: {topic_labels[col]}",
        color=TOPIC_MODEL_COLORS[i % len(TOPIC_MODEL_COLORS)],
        edgecolor="none",
        alpha=0.9,
    )
    bottom += lda_buzz_pct[col].values

place_legends_bottom(ax, main_ncol=2, main_y=0.02, event_y=-0.15)
plt.tight_layout(rect=[0, 0.18, 1, 1])
fig.savefig(FIGURES_DIR / "nlp_4_topics_buzzgroup.png", dpi=150, bbox_inches="tight",
            facecolor=BG_DARK, edgecolor="none")
print("Saved nlp_4_topics_buzzgroup.png")
plt.show()'''

set_source(cell_buzz, new_buzz)

# Insert buzz table after
idx_buzz2, _ = cell_by_id(cells, "e840446e")
buzz_table_src = '''# Topic distribution per buzz group — table
buzz_table = lda_buzz_pct.copy().round(1)
buzz_table.columns = [f"Topic {c} (%)" for c in buzz_table.columns]
buzz_table.index.name = "Buzz Group"
buzz_table = buzz_table.reset_index()
render_table_png(
    buzz_table,
    TABLES_DIR / "nlp_topic_buzzgroup.png",
    title="LDA Topic Distribution per Buzz Group (%)",
)
print("Saved nlp_topic_buzzgroup.png")
display(buzz_table)'''

cells.insert(idx_buzz2 + 1, make_code_cell(buzz_table_src, "nlp-buzz-tbl"))

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Done! Notebook rewritten successfully.")
