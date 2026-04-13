import json, uuid
from pathlib import Path

nb = json.load(open('data_retrieval/5_google_trends.ipynb', encoding='utf-8'))
header_cell = nb['cells'][0]

def cell(src):
    return {'cell_type': 'code', 'id': uuid.uuid4().hex[:8],
            'metadata': {}, 'outputs': [], 'source': [src]}

imports = cell(
"""import time
import pandas as pd
from pytrends.request import TrendReq

KEYWORDS = [
    'trump', 'kamala', 'biden', 'elon musk',
    'election 2024', 'vote', 'conspiracy',
    'walz', 'vance', 'campaign',
]

GEO           = 'US'
CATEGORY      = 0
WINDOW_1      = ('2024-07-05', '2024-10-02')
WINDOW_2      = ('2024-08-26', '2024-11-04')
OVERLAP_START = '2024-08-26'
OVERLAP_END   = '2024-10-02'
ANCHOR        = 'trump'
BATCHES = [
    ['trump', 'kamala', 'biden', 'elon musk', 'election 2024'],
    ['trump', 'vote', 'conspiracy', 'walz', 'vance'],
    ['trump', 'campaign'],
]
BRONZE_PATH = '../Data/1_Bronze/Google Trends/'

pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
tf1     = f"{WINDOW_1[0]} {WINDOW_1[1]}"
tf2     = f"{WINDOW_2[0]} {WINDOW_2[1]}"
full_tf = "2024-07-05 2024-11-04\""""
)

helpers = cell(
"""def fetch_window(timeframe, keywords, geo=GEO):
    \"\"\"Fetch interest_over_time for a single window.\"\"\"
    pytrends.build_payload(keywords, cat=CATEGORY, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()
    if df.empty:
        raise ValueError(f'Empty response for timeframe={timeframe}, geo={geo}')
    df = df.drop(columns=['isPartial'], errors='ignore')
    df.index = pd.to_datetime(df.index)
    return df

def stitch(df_w1, df_w2, keywords):
    \"\"\"Rescale window 2 to window 1 using the overlap period, then concatenate.\"\"\"
    w1_ov = df_w1.loc[OVERLAP_START:OVERLAP_END]
    w2_ov = df_w2.loc[OVERLAP_START:OVERLAP_END]
    df_w2s = df_w2.copy()
    for kw in keywords:
        m1, m2 = w1_ov[kw].mean(), w2_ov[kw].mean()
        df_w2s[kw] = (df_w2s[kw] * (m1 / m2 if m2 else 1.0)).clip(0, 100)
    w1_end = pd.Timestamp(WINDOW_1[1])
    out = pd.concat([df_w1, df_w2s.loc[w1_end + pd.Timedelta(days=1):]]).sort_index()
    return out[~out.index.duplicated(keep='first')]"""
)

daily_ts = cell(
"""# Fetch daily interest_over_time per batch, stitch windows, normalise to anchor keyword
batch_stitched = []
for i, batch in enumerate(BATCHES):
    w1 = fetch_window(tf1, batch)
    time.sleep(5)
    w2 = fetch_window(tf2, batch)
    time.sleep(5)
    batch_stitched.append(stitch(w1, w2, batch))

# Normalise batches 2+ to batch 1 via the anchor keyword
anchor_series = batch_stitched[0][ANCHOR]
normalised = [batch_stitched[0]]
for batch_df in batch_stitched[1:]:
    scaled = batch_df.copy()
    for day in scaled.index:
        anchor_b1 = anchor_series.get(day)
        anchor_bn = scaled.loc[day, ANCHOR]
        if anchor_b1 and anchor_bn:
            factor = anchor_b1 / anchor_bn
            for col in scaled.columns:
                if col != ANCHOR:
                    scaled.loc[day, col] = min(scaled.loc[day, col] * factor, 100)
    normalised.append(scaled.drop(columns=[ANCHOR]))

df_combined = pd.concat(normalised, axis=1).sort_index()[KEYWORDS]
df_combined.index.name = 'date'
df_combined.to_csv(f'{BRONZE_PATH}trends_daily_stitched.csv')
print(f'trends_daily_stitched.csv: {df_combined.shape[0]} days x {df_combined.shape[1]} keywords')"""
)

by_state = cell(
"""# Fetch interest_by_region per batch and normalise to anchor keyword
time.sleep(5)
region_dfs = []
anchor_region = None

for i, batch in enumerate(BATCHES):
    pytrends.build_payload(batch, cat=CATEGORY, timeframe=full_tf, geo=GEO)
    df_r = pytrends.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=False)
    if i == 0:
        anchor_region = df_r[ANCHOR]
        region_dfs.append(df_r)
    else:
        scaled = df_r.copy()
        for col in scaled.columns:
            if col != ANCHOR:
                mask = df_r[ANCHOR] > 0
                scaled.loc[mask, col] = (
                    scaled.loc[mask, col] / df_r.loc[mask, ANCHOR] * anchor_region.loc[mask]
                ).clip(0, 100)
        region_dfs.append(scaled.drop(columns=[ANCHOR]))
    time.sleep(5)

df_by_region = pd.concat(region_dfs, axis=1)[KEYWORDS]
df_by_region.to_csv(f'{BRONZE_PATH}trends_by_state.csv')
print(f'trends_by_state.csv: {df_by_region.shape[0]} states x {df_by_region.shape[1]} keywords')"""
)

trump_by_state = cell(
"""# Fetch daily trump interest for each of the 51 US states (stitched across two windows)
# Note: 51 states x 2 windows = 102 requests — allow ~20 min for rate-limit sleeps
STATE_CODES = {
    'Alabama': 'US-AL', 'Alaska': 'US-AK', 'Arizona': 'US-AZ',
    'Arkansas': 'US-AR', 'California': 'US-CA', 'Colorado': 'US-CO',
    'Connecticut': 'US-CT', 'Delaware': 'US-DE', 'District of Columbia': 'US-DC',
    'Florida': 'US-FL', 'Georgia': 'US-GA', 'Hawaii': 'US-HI',
    'Idaho': 'US-ID', 'Illinois': 'US-IL', 'Indiana': 'US-IN',
    'Iowa': 'US-IA', 'Kansas': 'US-KS', 'Kentucky': 'US-KY',
    'Louisiana': 'US-LA', 'Maine': 'US-ME', 'Maryland': 'US-MD',
    'Massachusetts': 'US-MA', 'Michigan': 'US-MI', 'Minnesota': 'US-MN',
    'Mississippi': 'US-MS', 'Missouri': 'US-MO', 'Montana': 'US-MT',
    'Nebraska': 'US-NE', 'Nevada': 'US-NV', 'New Hampshire': 'US-NH',
    'New Jersey': 'US-NJ', 'New Mexico': 'US-NM', 'New York': 'US-NY',
    'North Carolina': 'US-NC', 'North Dakota': 'US-ND', 'Ohio': 'US-OH',
    'Oklahoma': 'US-OK', 'Oregon': 'US-OR', 'Pennsylvania': 'US-PA',
    'Rhode Island': 'US-RI', 'South Carolina': 'US-SC', 'South Dakota': 'US-SD',
    'Tennessee': 'US-TN', 'Texas': 'US-TX', 'Utah': 'US-UT',
    'Vermont': 'US-VT', 'Virginia': 'US-VA', 'Washington': 'US-WA',
    'West Virginia': 'US-WV', 'Wisconsin': 'US-WI', 'Wyoming': 'US-WY',
}

state_series = {}
for i, (state, code) in enumerate(STATE_CODES.items()):
    print(f'[{i+1}/{len(STATE_CODES)}] {state}')
    try:
        w1 = fetch_window(tf1, ['trump'], geo=code)
        time.sleep(10)
        w2 = fetch_window(tf2, ['trump'], geo=code)
        time.sleep(10)
        state_series[state] = stitch(w1, w2, ['trump'])['trump']
    except Exception as e:
        print(f'  ERROR: {e} - skipping')
        time.sleep(15)

df_trump_states = pd.DataFrame(state_series)
df_trump_states.index.name = 'date'
df_trump_states.to_csv(f'{BRONZE_PATH}trump_daily_by_state.csv')
print(f'trump_daily_by_state.csv: {df_trump_states.shape[0]} days x {df_trump_states.shape[1]} states')"""
)

related = cell(
"""# Fetch top and rising related queries for each keyword
time.sleep(10)

for batch in BATCHES:
    pytrends.build_payload(batch, cat=CATEGORY, timeframe=full_tf, geo=GEO)
    related_queries = pytrends.related_queries()
    for kw in batch:
        safe   = kw.replace(' ', '_').lower()
        top    = related_queries[kw]['top']
        rising = related_queries[kw]['rising']
        if top    is not None: top.to_csv(f'{BRONZE_PATH}related_queries_{safe}_top.csv', index=False)
        if rising is not None: rising.to_csv(f'{BRONZE_PATH}related_queries_{safe}_rising.csv', index=False)
    time.sleep(5)

print('All related queries saved.')"""
)

nb['cells'] = [header_cell, imports, helpers, daily_ts, by_state, trump_by_state, related]
json.dump(nb, open('data_retrieval/5_google_trends.ipynb', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done')
