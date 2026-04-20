import json

NB_PATH = 'c:/Users/verme_hzys4y0/UGent/2025-2026/Social media and webanalytics/group-project-SMWA/Descriptive/5_google_trends/5.1_eda.ipynb'
with open(NB_PATH, encoding='utf-8') as f:
    nb = json.load(f)

def src(cell):
    s = cell.get('source', '')
    return ''.join(s) if isinstance(s, list) else s

def set_src(cell, new_source):
    cell['source'] = new_source
    cell['outputs'] = []

idx = next(i for i, c in enumerate(nb['cells']) if 'top15' in src(c) and 'nlargest' in src(c))

s = src(nb['cells'][idx])
s = s.replace(
    "plt.tight_layout()\nplt.savefig(f'{BRONZE_PATH}plot_states_top15.png')",
    "import matplotlib.patches as mpatches\n"
    "fig.legend(\n"
    "    handles=[\n"
    "        mpatches.Patch(color=REPUBLICAN, label='Trump search interest'),\n"
    "        mpatches.Patch(color=DEMOCRAT,   label='Kamala search interest'),\n"
    "    ],\n"
    "    loc='lower center', bbox_to_anchor=(0.5, 0.0), ncol=2,\n"
    "    fontsize=10, facecolor=BG_PANEL, edgecolor=SPINE_COLOR,\n"
    "    labelcolor=TEXT_PRIMARY, framealpha=0.95, borderpad=0.9\n"
    ")\n"
    "plt.tight_layout(rect=[0, 0.06, 1, 1])\n"
    "plt.savefig(f'{BRONZE_PATH}plot_states_top15.png')"
)
set_src(nb['cells'][idx], s)
print(f"states legend: OK (cell {idx})")

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
print('Done.')
