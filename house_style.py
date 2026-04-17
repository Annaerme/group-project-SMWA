"""
house_style.py — Shared visual style for all project notebooks.

Usage (from any notebook in Descriptive/<subfolder>/):
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    # or directly:
    sys.path.insert(0, "..")
    from house_style import *

Then call apply_style() once at the top of each notebook.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import warnings

# ── Colour palette ─────────────────────────────────────────────────────────────
BG_DARK      = "#0f171f"   # figure / axes background
BG_PANEL     = "#16232e"   # slightly lighter panel background
REPUBLICAN   = "#e6524d"   # CandidateA (Trump / Republican)
DEMOCRAT     = "#207dff"   # CandidateB (Harris / Democrat)
ACCENT       = "#243c69"   # secondary accent (borders, highlights)
NEUTRAL      = "#77787A"   # neutral posts / misc elements
BLUESKY_BLUE = "#1185fe"   # platform color for Bluesky volume/series
REDDIT_ORG   = "#e85a28"   # platform color for Reddit volume/series

# ── Signal colours ─────────────────────────────────────────────────────────────
C_VIX    = "#e69c1e"   # oranje        — marktvolatiliteit (VIX)
C_SP500  = "#1a3875"   # donkerblauw   — S&P 500

# ── NRC emotion colours ────────────────────────────────────────────────────────
C_FEAR         = "#8b1a5c"   # bordeaux-paars
C_ANGER        = "#cc2222"   # rood
C_TRUST        = "#27ae60"   # groen
C_DISGUST      = "#1e6b35"   # donkergroen
C_SADNESS      = "#3b82c4"   # blauw
C_JOY          = "#f0c330"   # geel
C_ANTICIPATION = "#f5a0c0"   # babyroze

TEXT_PRIMARY = "#e8eaed"   # main text
TEXT_MUTED   = "#6b8399"   # axis labels, tick labels
GRID_COLOR   = "#1c2d3e"   # subtle grid lines
SPINE_COLOR  = "#1e3048"   # axis spines

# Buzz colour map — use like: BUZZ_COLORS[row["candidate"]]
# Labels reflect *which hashtag cluster the post came from*, NOT the author's political stance.
# A post labelled "TrumpBuzz" was found via a Trump-related hashtag — it may be pro- OR anti-Trump.
BUZZ_COLORS = {
    "TrumpBuzz"   : REPUBLICAN,
    "HarrisBuzz"  : DEMOCRAT,
    "ElectionBuzz": NEUTRAL,
}
CANDIDATE_COLORS = BUZZ_COLORS  # backwards-compatible alias

# General-purpose qualitative palette (8 colours)
PALETTE = [DEMOCRAT, REPUBLICAN, NEUTRAL, ACCENT,
           "#f0a500", "#2ec4b6", "#9b5de5", "#f15bb5"]


# ── Font setup ─────────────────────────────────────────────────────────────────
def _best_available_font(candidates):
    """Return the first font from `candidates` that matplotlib can find."""
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            return font
    return "DejaVu Sans"  # matplotlib built-in fallback

FONT_FAMILY = _best_available_font([
    "Inter", "Helvetica Neue", "Helvetica", "Arial", "Roboto",
    "Source Sans Pro", "Open Sans", "Lato",
])


# ── Core style applicator ──────────────────────────────────────────────────────
def apply_style():
    """
    Apply the project house style globally via matplotlib rcParams.
    Call once at the top of each notebook after imports.
    """
    mpl.rcParams.update({
        # Figure
        "figure.facecolor"      : BG_DARK,
        "figure.edgecolor"      : BG_DARK,
        "figure.dpi"            : 120,
        "figure.titlesize"      : 16,
        "figure.titleweight"    : "bold",

        # Axes
        "axes.facecolor"        : BG_PANEL,
        "axes.edgecolor"        : SPINE_COLOR,
        "axes.labelcolor"       : TEXT_PRIMARY,
        "axes.labelsize"        : 11,
        "axes.labelpad"         : 8,
        "axes.titlesize"        : 13,
        "axes.titleweight"      : "bold",
        "axes.titlecolor"       : TEXT_PRIMARY,
        "axes.titlepad"         : 12,
        "axes.spines.top"       : False,
        "axes.spines.right"     : False,
        "axes.prop_cycle"       : mpl.cycler(color=PALETTE),
        "axes.grid"             : True,
        "axes.axisbelow"        : True,

        # Grid
        "grid.color"            : GRID_COLOR,
        "grid.linewidth"        : 0.8,
        "grid.alpha"            : 1.0,

        # Ticks
        "xtick.color"           : TEXT_MUTED,
        "ytick.color"           : TEXT_MUTED,
        "xtick.labelsize"       : 9,
        "ytick.labelsize"       : 9,
        "xtick.direction"       : "out",
        "ytick.direction"       : "out",
        "xtick.major.pad"       : 6,
        "ytick.major.pad"       : 6,

        # Legend
        "legend.facecolor"      : BG_PANEL,
        "legend.edgecolor"      : SPINE_COLOR,
        "legend.labelcolor"     : TEXT_PRIMARY,
        "legend.fontsize"       : 9,
        "legend.framealpha"     : 0.9,
        "legend.title_fontsize" : 10,

        # Text & fonts
        "text.color"            : TEXT_PRIMARY,
        "font.family"           : "sans-serif",
        "font.sans-serif"       : [FONT_FAMILY, "DejaVu Sans"],
        "font.size"             : 10,

        # Lines & markers
        "lines.linewidth"       : 2.0,
        "lines.markersize"      : 6,
        "patch.edgecolor"       : BG_DARK,
        "patch.linewidth"       : 0.5,

        # Saving
        "savefig.facecolor"     : BG_DARK,
        "savefig.edgecolor"     : BG_DARK,
        "savefig.dpi"           : 150,
        "savefig.bbox"          : "tight",
    })


# ── Key political events (shared across all notebooks) ────────────────────────
# Each entry: (label, date_str, colour)
EVENTS = [
    ('Trump shot',                '2024-07-13', REPUBLICAN),
    ('JD Vance VP pick',          '2024-07-15', '#e07b39'),
    ('Biden withdraws',           '2024-07-21', DEMOCRAT),
    ('Obama endorses Harris',     '2024-07-26', DEMOCRAT),
    ('Harris nominated',          '2024-08-05', '#5dade2'),
    ("Start of DNC", "2024-08-19", "#7dd3fc"),  # lichtblauw
    ('Trump–Harris debate (ABC)', '2024-09-10', NEUTRAL),
    ('2nd assassination attempt', '2024-09-15', '#c0392b'),
    ('Vance-Walz debate (CBC)', '2024-10-01', NEUTRAL),
    ('America PAC offers $47 to supporters who refer another registered voter in a swing state', '2024-10-07', REPUBLICAN),
    ('Musk increases petition reward', '2024-10-10', REPUBLICAN),
]

# Quick lookup: label → colour
EVENT_PALETTE = {lbl: color for lbl, _, color in EVENTS}


def add_events(ax, events=None, zorder=3):
    """Draw dashed vertical event lines on *ax*. Uses EVENTS if not specified."""
    import matplotlib.lines as mlines
    import pandas as pd
    if events is None:
        events = EVENTS
    for lbl, date, color in events:
        ax.axvline(pd.Timestamp(date), color=color, linestyle='--',
                   linewidth=1.4, alpha=0.9, zorder=zorder)


def event_legend_handles(events=None):
    """Return Line2D handles for a legend of the key events."""
    import matplotlib.lines as mlines
    if events is None:
        events = EVENTS
    return [
        mlines.Line2D([], [], color=c, linestyle='--', linewidth=2.5, label=lbl)
        for lbl, _, c in events
    ]


# ── Convenience helpers ────────────────────────────────────────────────────────
def styled_fig(nrows=1, ncols=1, figsize=None, title=None, **kwargs):
    """Create a pre-styled figure. Returns (fig, ax) or (fig, axes)."""
    if figsize is None:
        w = 7 * ncols
        h = 4.5 * nrows
        figsize = (w, h)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
    fig.patch.set_facecolor(BG_DARK)
    if title:
        fig.suptitle(title, color=TEXT_PRIMARY, fontsize=16,
                     fontweight="bold", y=1.02)
    return fig, axes


def style_ax(ax, xlabel=None, ylabel=None, title=None, grid_axis="y"):
    """Apply finishing touches to an individual axes."""
    ax.set_facecolor(BG_PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(SPINE_COLOR)
    if xlabel: ax.set_xlabel(xlabel, color=TEXT_PRIMARY)
    if ylabel: ax.set_ylabel(ylabel, color=TEXT_PRIMARY)
    if title:  ax.set_title(title,  color=TEXT_PRIMARY, fontweight="bold")
    ax.tick_params(colors=TEXT_MUTED)
    ax.grid(axis=grid_axis, color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    return ax


def buzz_legend(ax, loc="upper right"):
    """Add a standard TrumpBuzz / HarrisBuzz / ElectionBuzz legend.
    Labels clarify these are hashtag clusters, not stances."""
    import matplotlib.patches as mpatches
    patches = [
        mpatches.Patch(color=REPUBLICAN, label="Trump buzz (Trump-related hashtags)"),
        mpatches.Patch(color=DEMOCRAT,   label="Harris buzz (Harris-related hashtags)"),
        mpatches.Patch(color=NEUTRAL,    label="General election buzz"),
    ]
    ax.legend(handles=patches, loc=loc,
              facecolor=BG_PANEL, edgecolor=SPINE_COLOR,
              labelcolor=TEXT_PRIMARY)

candidate_legend = buzz_legend  # backwards-compatible alias


# ── Table of contents ──────────────────────────────────────────────────────────
def show_toc(_=None):
    """No-op binnen de kernel — geen bestandsschrijf, geen VSCode-conflict.

    De TOC markdown cel staat al bovenaan het notebook.
    Hergeneren na sectiewijzigingen: voer vanuit de projectroot uit:
        python update_tocs.py
    """
    pass


def _build_toc(nb_path):
    """Interne helper: (her)genereert de TOC markdown cel in een notebook.
    Alleen aan te roepen vanuit update_tocs.py, niet vanuit de kernel.
    """
    import json, re, uuid, pathlib

    nb_path = pathlib.Path(nb_path)
    with open(nb_path, encoding="utf-8") as f:
        nb = json.load(f)

    items = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        for line in "".join(cell["source"]).splitlines():
            if not line.startswith("#"):
                continue
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            anchor = re.sub(r"[^\w\s-]", "", title.lower())
            anchor = re.sub(r"\s+", "-", anchor.strip())
            items.append((level, title, anchor))

    MARKER = "<!-- toc -->"
    lines  = [MARKER + "\n## Contents\n"]
    for level, title, anchor in items:
        indent = "  " * (level - 1)
        link   = f"**[{title}](#{anchor})**" if level == 1 else f"[{title}](#{anchor})"
        lines.append(f"{indent}- {link}\n")
    new_source = "".join(lines)

    toc_idx, code_idx = None, None
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        if cell["cell_type"] == "markdown" and MARKER in src:
            toc_idx = i
        if cell["cell_type"] == "code" and "show_toc" in src and "def show_toc" not in src:
            if code_idx is None:
                code_idx = i

    if toc_idx is not None and "".join(nb["cells"][toc_idx]["source"]) == new_source:
        return False  # niets veranderd

    if toc_idx is not None:
        nb["cells"][toc_idx]["source"] = [new_source]
    elif code_idx is not None:
        nb["cells"].insert(code_idx, {
            "cell_type": "markdown",
            "id": uuid.uuid4().hex[:8],
            "metadata": {},
            "source": [new_source],
        })
    else:
        return False

    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    return True
