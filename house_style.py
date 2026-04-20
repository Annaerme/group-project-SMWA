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
import random

# ── Colour palette ─────────────────────────────────────────────────────────────
BG_DARK      = "#0f171f"   # figure / axes background
BG_PANEL     = "#16232e"   # slightly lighter panel background
REPUBLICAN   = "#e6524d"   # CandidateA (Trump / Republican)
DEMOCRAT     = "#207dff"   # CandidateB (Harris / Democrat)
ACCENT       = "#243c69"   # secondary accent (borders, highlights)
NEUTRAL      = "#77787A"   # neutral posts / misc elements
BLUESKY_BLUE = "#1185fe"   # platform color for Bluesky volume/series
REDDIT_ORG   = "#e85a28"   # platform color for Reddit volume/series

# ── Topic modelling colours ───────────────────────────────────────────────────
TM_BLUE        = "#007ef9"
TM_ORANGE      = "#e85a28"
TM_LAVENDER    = "#b39ddb"
TM_CRIMSON     = "#9f193e"
TM_BURGUNDY    = "#8b1a5c"
TM_DEEP_BLUE   = "#1a3875"

TOPIC_MODEL_COLORS = [
    TM_BLUE,
    TM_ORANGE,
    TM_LAVENDER,
    TM_CRIMSON,
    TM_BURGUNDY,
    TM_DEEP_BLUE,
]
TOPIC_COLORS = TOPIC_MODEL_COLORS  # short alias for notebook use

# ── Word cloud colours ────────────────────────────────────────────────────────
WC_START = "#7d0d2c"  # burgundy endpoint
WC_END = "#1a3875"    # deep-blue endpoint


def _hex_to_rgb(hex_color):
    """Convert #RRGGBB to (r, g, b)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    """Convert (r, g, b) to #RRGGBB."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _blend_hex(hex_a, hex_b, ratio=0.5):
    """Blend two hex colours by `ratio` (0 = a, 1 = b)."""
    ratio = max(0.0, min(1.0, float(ratio)))
    a = _hex_to_rgb(hex_a)
    b = _hex_to_rgb(hex_b)
    rgb = tuple(int(round((1 - ratio) * a[i] + ratio * b[i])) for i in range(3))
    return _rgb_to_hex(rgb)


def wordcloud_palette(topic_id=None, n_shades=6):
    """Return n_shades colours for a word cloud.

    - topic_id=None: blue-red gradient (WC_START -> WC_END)
    - topic_id set : shades around that specific topic colour
    """
    if n_shades <= 0:
        if topic_id is None:
            return [WC_START]
        return [TOPIC_MODEL_COLORS[int(topic_id) % len(TOPIC_MODEL_COLORS)]]

    if topic_id is None:
        if n_shades == 1:
            return [_blend_hex(WC_START, WC_END, ratio=0.5)]
        return [
            _blend_hex(WC_START, WC_END, ratio=i / (n_shades - 1))
            for i in range(n_shades)
        ]

    base = TOPIC_MODEL_COLORS[int(topic_id) % len(TOPIC_MODEL_COLORS)]
    dark = _blend_hex(base, "#000000", ratio=0.28)
    light = _blend_hex(base, "#ffffff", ratio=0.18)
    if n_shades == 1:
        return [base]
    return [
        _blend_hex(dark, light, ratio=i / (n_shades - 1))
        for i in range(n_shades)
    ]


# Ready-to-use gradient list for quick notebook usage.
WORDCLOUD_GRADIENT = wordcloud_palette(n_shades=12)


def wordcloud_color_func(topic_id=None, seed=42, n_shades=7):
    """Create a deterministic WordCloud color_func for one topic.

    Usage:
        wc = WordCloud(background_color=BG_PANEL, color_func=wordcloud_color_func(topic_id=2))
    """
    palette = wordcloud_palette(topic_id=topic_id, n_shades=n_shades)
    offset = 0 if topic_id is None else int(topic_id)
    rng = random.Random(seed + offset)

    def _color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return rng.choice(palette)

    return _color_func

# ── Signal colours ─────────────────────────────────────────────────────────────
C_VIX    = "#e69c1e"   # oranje        — marktvolatiliteit (VIX)
C_SP500  = "#4a90e2"   # middenblauw   — S&P 500
C_DIFF   = "#8a9bb0"   # grijs-blauw   — verschil-/spread-lijn (nooit wit)

# ── NRC emotion colours ────────────────────────────────────────────────────────
C_FEAR         = "#8b1a5c"   # bordeaux-paars
C_ANGER        = "#cc2222"   # rood
C_TRUST        = "#27ae60"   # groen
C_DISGUST      = "#1e6b35"   # donkergroen
C_SADNESS      = "#3b82c4"   # blauw
C_JOY          = "#f0c330"   # geel
C_ANTICIPATION = "#f5a0c0"   # babyroze

# Sentiment/model colours
C_SURPRISE = "#8fd3ff"   # lichtblauw
C_VADER    = "#f39c12"   # oranje
C_NRC_LEX  = "#f5b041"   # geeloranje
C_TEXTBLOB = "#d62828"   # rood
C_ROBERTA  = "#1f8cff"   # fel blauw

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
        "figure.titlesize"      : 20,
        "figure.titleweight"    : "bold",

        # Axes
        "axes.facecolor"        : BG_PANEL,
        "axes.edgecolor"        : SPINE_COLOR,
        "axes.labelcolor"       : TEXT_PRIMARY,
        "axes.labelsize"        : 12,
        "axes.labelpad"         : 8,
        "axes.titlesize"        : 15,
        "axes.titleweight"      : "bold",
        "axes.titlecolor"       : TEXT_PRIMARY,
        "axes.titlepad"         : 12,
        "axes.spines.top"       : False,
        "axes.spines.right"     : False,
        "axes.prop_cycle"       : mpl.cycler(color=PALETTE),
        "axes.grid"             : True,
        "axes.axisbelow"        : True,
        "axes.xmargin"          : 0.0,
        "axes.ymargin"          : 0.03,

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
        "legend.title_fontsize" : 13,
        "legend.loc"            : "lower center",

        # Text & fonts
        "text.color"            : TEXT_PRIMARY,
        "font.family"           : "sans-serif",
        "font.sans-serif"       : [FONT_FAMILY, "DejaVu Sans"],
        "font.size"             : 11,

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
    ('Biden withdraws',           '2024-07-21', '#5dade2'),
    ('Obama endorses Harris',     '2024-07-26', '#5dade2'),
    ('Harris nominated',          '2024-08-05', DEMOCRAT),
    ("Start of DNC", "2024-08-19", '#5dade2'), 
    ('Trump–Harris debate (ABC)', '2024-09-10', NEUTRAL),
    ('2nd assassination attempt', '2024-09-15',REPUBLICAN ),
    ('Vance-Walz debate (CBC)', '2024-10-01', NEUTRAL),
    ('Musk at Butler rally',   '2024-10-05', '#f5a623'),
    ('$47 per registered voter in a swing state', '2024-10-07', '#f5a623'),
    ('Musk increases petition reward', '2024-10-10', '#f5a623'),
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
        fig.suptitle(title, color=TEXT_PRIMARY,
                     fontsize=mpl.rcParams["figure.titlesize"],
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


def limit_x_to_data(ax, x_values=None):
    """Trim x-limits to data range so plots don't show empty time edges."""
    import matplotlib.dates as mdates

    vals = []
    if x_values is not None:
        vals = list(x_values)
    else:
        for line in ax.get_lines():
            vals.extend(list(line.get_xdata()))

    nums = []
    for v in vals:
        try:
            nums.append(float(v))
            continue
        except Exception:
            pass
        try:
            nums.append(mdates.date2num(v))
        except Exception:
            continue

    if nums:
        ax.set_xlim(min(nums), max(nums))
    return ax


def place_legends_bottom(ax, event_handles=None, main_ncol=2, event_ncol=4,
                         main_y=0.20, event_y=0.03,
                         main_handles=None, main_labels=None,
                         main_title=None, event_title=None):
    """Place main legend and optional separate event legend below the figure.

    Uses fig.legend() so positioning is stable regardless of tight_layout.
    Call plt.tight_layout(rect=[0, 0.26, 1, 1]) afterwards to leave room.
    main_y sits above event_y — defaults tuned for 14×4/14×5 figures.

    Pass main_handles (and optionally main_labels) to override ax handles.
    Use main_title / event_title to add a header to each legend group.
    """
    fig = ax.get_figure()

    if main_handles is None:
        handles, labels = ax.get_legend_handles_labels()
        pairs = [(h, l) for h, l in zip(handles, labels) if l and not l.startswith("_")]
        if pairs:
            main_handles, main_labels = zip(*pairs)
        else:
            main_handles, main_labels = [], []

    main_legend = None
    if main_handles:
        legend_kwargs = dict(
            loc="lower center", bbox_to_anchor=(0.5, main_y),
            ncol=max(1, min(main_ncol, len(main_handles))),
            facecolor=BG_PANEL, edgecolor=SPINE_COLOR, labelcolor=TEXT_PRIMARY,
            framealpha=0.95,
            title=main_title, title_fontsize=10,
        )
        if main_labels is not None:
            main_legend = fig.legend(list(main_handles), list(main_labels), **legend_kwargs)
        else:
            main_legend = fig.legend(handles=list(main_handles), **legend_kwargs)
        if main_title and main_legend.get_title():
            main_legend.get_title().set_color(TEXT_MUTED)

    event_legend = None
    if event_handles:
        event_legend = fig.legend(
            handles=event_handles,
            loc="lower center", bbox_to_anchor=(0.5, event_y),
            ncol=max(1, min(event_ncol, len(event_handles))),
            facecolor=BG_PANEL, edgecolor=SPINE_COLOR, labelcolor=TEXT_PRIMARY,
            framealpha=0.95,
            title=event_title, title_fontsize=10,
        )
        if event_title and event_legend.get_title():
            event_legend.get_title().set_color(TEXT_MUTED)

    return main_legend, event_legend


def finalize_plot(ax, x_values=None, events=None, add_event_legend=False,
                  main_ncol=2, event_ncol=4):
    """Common final step: trim x-axis and place bottom legends."""
    limit_x_to_data(ax, x_values=x_values)
    event_handles = event_legend_handles(events) if add_event_legend else None
    place_legends_bottom(ax, event_handles=event_handles,
                         main_ncol=main_ncol, event_ncol=event_ncol)
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
