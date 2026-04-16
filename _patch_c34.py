import json, sys
sys.stdout.reconfigure(encoding='utf-8')
PATH = 'c:/Users/verme_hzys4y0/UGent/2025-2026/Social media and webanalytics/group-project-SMWA/Descriptive/8_events/8.1_trump_era.ipynb'
with open(PATH, encoding='utf-8') as f:
    nb = json.load(f)

new_src = """\
# ── All-8 emotion profile: time series + radar chart (before vs after Trump Shot) ─
EMOTIONS_BT  = ['fear', 'anger', 'disgust', 'trust', 'anticipation']   # in basetable
EMOTIONS_SLV = ['joy', 'sadness', 'surprise']                           # in silver
ALL_EMOTIONS = EMOTIONS_BT + EMOTIONS_SLV

EMOT_COLORS = {
    'fear':         C_FEAR,        # focus
    'anger':        C_ANGER,       # focus
    'disgust':      '#8b939e',     # muted
    'trust':        '#8b939e',     # muted
    'anticipation': '#8b939e',     # muted
    'joy':          '#8b939e',     # muted
    'sadness':      '#8b939e',     # muted
    'surprise':     '#06B6D4',     # focus
}
FOCUS_EMOTIONS = {'fear', 'anger', 'surprise'}

# ── Load missing emotions from silver sentiment features ──────────────────────
slv = pd.read_csv(ROOT / '2_Silver/Newspapers/sentiment_features_newspapers.csv',
                  parse_dates=['date'])
slv['date'] = pd.to_datetime(slv['date']).dt.normalize()
for e in EMOTIONS_SLV:
    cols = [f'nrc_{e}_dem', f'nrc_{e}_rep', f'nrc_{e}_cen']
    available = [c for c in cols if c in slv.columns]
    slv[f'nrc_{e}_avg'] = slv[available].mean(axis=1)

bt_era = bt[(bt['date'] >= ERA_START) & (bt['date'] <= ERA_END)].sort_values('date')
bt_era = bt_era.merge(
    slv[['date'] + [f'nrc_{e}_avg' for e in EMOTIONS_SLV]],
    on='date', how='left'
)

# Build uniform column mapping for all 8 emotions
EMOT_COLS = {}
for e in EMOTIONS_BT:
    c = f'news_trump_{e}_ratio'
    if c in bt_era.columns:
        EMOT_COLS[e] = c
for e in EMOTIONS_SLV:
    c = f'nrc_{e}_avg'
    if c in bt_era.columns:
        EMOT_COLS[e] = c

emotions = list(EMOT_COLS.keys())

pre_window  = bt_era[bt_era['date'] < SHOT]
post_window = bt_era[bt_era['date'] >= SHOT]
series_map  = {e: bt_era[EMOT_COLS[e]].rolling(2, min_periods=1).mean() for e in emotions}

# Pre-compute delta values for focus emotions
pre_vals  = np.array([pre_window[EMOT_COLS[e]].mean()  for e in emotions], dtype=float)
post_vals = np.array([post_window[EMOT_COLS[e]].mean() for e in emotions], dtype=float)
delta_map = {e: post_window[EMOT_COLS[e]].mean() - pre_window[EMOT_COLS[e]].mean()
             for e in FOCUS_EMOTIONS if e in EMOT_COLS}
pre_map   = {e: pre_window[EMOT_COLS[e]].mean()  for e in FOCUS_EMOTIONS if e in EMOT_COLS}
post_map  = {e: post_window[EMOT_COLS[e]].mean() for e in FOCUS_EMOTIONS if e in EMOT_COLS}

# ── Figure 1: time series all 8 emotions + delta legend below ────────────────
fig1, (ax1, ax_leg) = plt.subplots(
    2, 1, figsize=(16, 10),
    gridspec_kw={'height_ratios': [8, 1.6], 'hspace': 0.08}
)
fig1.patch.set_facecolor(BG_DARK)
ax1.set_facecolor(BG_PANEL)
for sp in ax1.spines.values():
    sp.set_edgecolor(SPINE_COLOR)

for e in emotions:
    s = series_map[e]
    is_focus = e in FOCUS_EMOTIONS
    ax1.plot(bt_era['date'], s, color=EMOT_COLORS[e],
             linewidth=3.2 if is_focus else 1.4,
             alpha=1.0 if is_focus else 0.4,
             label=e.capitalize(), zorder=6 if is_focus else 3)
    ax1.fill_between(bt_era['date'], s, color=EMOT_COLORS[e],
                     alpha=0.14 if is_focus else 0.03, zorder=2)

add_era_events(ax1)
ax1.set_title('Trump Emotion Profile Over Time \u2014 All 8 NRC Emotions  (Jul 5-21)',
              color=TEXT_PRIMARY, fontsize=20, fontweight='bold', loc='left')
ax1.set_ylabel('Emotion ratio', color=TEXT_MUTED, fontsize=16)
ax1.tick_params(colors=TEXT_MUTED, labelsize=14)
ax1.grid(axis='y', color='#2d2d2d', linewidth=0.6, alpha=0.7)
ax1.set_xlim(ERA_START, ERA_END)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right', color=TEXT_MUTED, fontsize=14)
ax1.legend(facecolor=BG_PANEL, edgecolor=SPINE_COLOR, labelcolor=TEXT_PRIMARY,
           fontsize=15, ncol=4, loc='upper left')

# ── Delta legend panel (far below the chart) ─────────────────────────────────
ax_leg.set_facecolor(BG_DARK)
ax_leg.axis('off')
ax_leg.set_xlim(0, 1)
ax_leg.set_ylim(0, 1)

col_positions = {'fear': 0.04, 'anger': 0.37, 'surprise': 0.70}
for e in ['fear', 'anger', 'surprise']:
    if e not in delta_map:
        continue
    col  = EMOT_COLORS[e]
    pv   = pre_map[e]
    pov  = post_map[e]
    dv   = delta_map[e]
    sign = '+' if dv >= 0 else ''
    x    = col_positions[e]
    # Emotion name header
    ax_leg.text(x, 0.90, e.capitalize(), color=col,
                fontsize=17, fontweight='bold', va='top', transform=ax_leg.transAxes)
    # Before / After values
    ax_leg.text(x, 0.45, f'Before  {pv:.4f}    After  {pov:.4f}', color=TEXT_MUTED,
                fontsize=13, va='top', transform=ax_leg.transAxes)
    # Delta
    ax_leg.text(x, 0.02, f'\u0394 {sign}{dv:.4f}', color=col,
                fontsize=16, fontweight='bold', va='bottom', transform=ax_leg.transAxes)

ax_leg.axhline(1.0, color=SPINE_COLOR, linewidth=1.2, transform=ax_leg.transAxes)
plt.tight_layout()
plt.show()

# ── Figure 2: radar chart before vs after Trump Shot ──────────────────────────
fig2 = plt.figure(figsize=(11, 9))
fig2.patch.set_facecolor(BG_DARK)
ax2 = fig2.add_subplot(1, 1, 1, polar=True)
ax2.set_facecolor(BG_PANEL)
ax2.spines['polar'].set_edgecolor(SPINE_COLOR)
ax2.set_theta_offset(np.pi / 2)
ax2.set_theta_direction(-1)
ax2.set_rlabel_position(0)

N      = len(emotions)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
pre_closed  = list(pre_vals)  + [pre_vals[0]]
post_closed = list(post_vals) + [post_vals[0]]

ax2.plot(angles, pre_closed,  color='#4a6080', linewidth=2.2, linestyle='--', label='Before Shot', alpha=0.85)
ax2.fill(angles, pre_closed,  color='#4a6080', alpha=0.08)
ax2.plot(angles, post_closed, color=TEXT_PRIMARY, linewidth=2.0, linestyle='-',  label='After Shot',  alpha=0.75)
ax2.fill(angles, post_closed, color=TEXT_PRIMARY, alpha=0.05)

# Coloured sector fill per emotion (post-shot values)
half_step = np.pi / N
for idx, e in enumerate(emotions):
    a_c       = angles[idx]
    theta_arc = np.linspace(a_c - half_step, a_c + half_step, 50)
    ax2.fill(
        np.concatenate([[a_c - half_step], theta_arc, [a_c + half_step]]),
        np.concatenate([[0], np.full(50, post_vals[idx]), [0]]),
        color=EMOT_COLORS[e], alpha=0.32, zorder=2,
    )

# Spoke labels in emotion colour
ax2.set_thetagrids(
    [a * 180 / np.pi for a in angles[:-1]],
    [e.capitalize() for e in emotions],
    fontsize=16,
)
for lbl in ax2.get_xticklabels():
    key = lbl.get_text().strip().lower()
    lbl.set_color(EMOT_COLORS.get(key, TEXT_MUTED))
    lbl.set_fontweight('bold')

for ylbl in ax2.get_yticklabels():
    ylbl.set_color(TEXT_MUTED)
    ylbl.set_fontsize(12)

ax2.set_title('Trump Emotion Shock Radar \u2014 Before vs After (All 8 NRC Emotions)',
              color=TEXT_PRIMARY, fontsize=16, fontweight='bold', pad=22)
ax2.yaxis.grid(True, color='#2d2d2d', linewidth=0.6, alpha=0.65)
ax2.xaxis.grid(True, color='#2d2d2d', linewidth=0.6, alpha=0.65)
ax2.legend(loc='upper right', bbox_to_anchor=(1.45, 1.15),
           facecolor=BG_PANEL, edgecolor=SPINE_COLOR, labelcolor=TEXT_PRIMARY, fontsize=13)
plt.tight_layout()
plt.show()
"""

nb['cells'][34]['source'] = new_src.splitlines(keepends=True)
with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Saved OK. Lines in cell 34:', len(nb['cells'][34]['source']))
