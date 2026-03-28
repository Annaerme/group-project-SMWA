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
