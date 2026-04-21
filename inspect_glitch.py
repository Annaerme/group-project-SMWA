path = r'c:/Users/verme_hzys4y0/UGent/2025-2026/Social media and webanalytics/group-project-SMWA/Descriptive/2_bluesky/2.4_nlp.ipynb'

with open(path, 'rb') as f:
    raw = f.read()

# Pattern 1: double-encoded em dash around "Build Dictionary"
# hex from earlier: c383c2a2c3a2e2809ac2acc3a2e282acc29d
emdash_garble = bytes.fromhex('c383c2a2c3a2e2809ac2acc3a2e282acc29d')
count1 = raw.count(emdash_garble)
print(f'Pattern 1 (em dash garble): {count1} occurrences')

# Pattern 2: find bytes around "TrumpBuzz" to get the other pattern
idx = raw.find(b'TrumpBuzz')
if idx >= 0:
    chunk = raw[idx:idx+60]
    print(f'\nBytes after TrumpBuzz: {chunk.hex()}')

# Also search around "HarrisBuzz"
idx2 = raw.find(b'HarrisBuzz')
if idx2 >= 0:
    chunk2 = raw[max(0,idx2-20):idx2+5]
    print(f'Bytes before HarrisBuzz: {chunk2.hex()}')
