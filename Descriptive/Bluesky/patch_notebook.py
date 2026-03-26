"""
patch_notebook.py — update the hashtag configuration in 1_Network_analysis.ipynb.

Run:  python patch_notebook.py
This replaces cell t06 (ELECTIONS config) with the latest expanded hashtag lists.
"""
import json, os

NB_PATH = os.path.join(os.path.dirname(__file__), "1_Network_analysis.ipynb")

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

NEW_CONFIG_SRC = '''\
ELECTIONS = {
    "US_2024": {
        "since"        : "2024-10-05T00:00:00Z",
        "until"        : "2024-11-05T23:59:59Z",
        "election_date": "2024-11-05",
        "hashtags": [
            # Core election tags
            "#Election2024", "#USElection2024", "#ElectionDay", "#Vote2024",
            "#Presidential2024", "#PresidentialElection", "#ElectionNight",
            "#AmericaDecides", "#Decision2024",
            # Trump-side
            "#Trump2024", "#TrumpVance", "#VoteTrump", "#MAGA", "#MAGA2024",
            "#TrumpHarris", "#Trump", "#DonaldTrump", "#AmericaFirst",
            # Harris-side
            "#Harris2024", "#KamalaHarris2024", "#KamalaHarris", "#HarrisWalz",
            "#VoteHarris", "#VoteBlue", "#VoteKamala", "#Kamala2024",
            # Broader politics
            "#USPolitics", "#Democrats", "#Republicans",
            "#Battleground2024", "#SwingState", "#EarlyVoting",
        ],
    },
    "UK_2024": {
        "since"        : "2024-06-04T00:00:00Z",
        "until"        : "2024-07-04T23:59:59Z",
        "election_date": "2024-07-04",
        "hashtags": [
            "#UKElection2024", "#GE2024", "#GeneralElection", "#GeneralElection2024",
            "#UKVotes", "#UKPolitics", "#VoteUK",
            "#VoteLabour", "#Labour", "#LabourParty", "#KeirStarmer",
            "#VoteTory", "#Conservatives", "#ToryOut", "#RishiSunak",
            "#LibDems", "#Reform", "#SNP", "#Greens",
            "#Starmer", "#Sunak",
        ],
    },
    "Germany_2025": {
        "since"        : "2025-01-23T00:00:00Z",
        "until"        : "2025-02-23T23:59:59Z",
        "election_date": "2025-02-23",
        "hashtags": [
            "#Bundestagswahl", "#Bundestagswahl2025", "#BTW25", "#BTW2025",
            "#Wahlkampf", "#WaehlenGehen", "#Demokratie",
            "#Merz", "#FriedrichMerz", "#CDU", "#CSU",
            "#Scholz", "#OlafScholz", "#SPD",
            "#AfD", "#AfDVerbot",
            "#Gruene", "#Grüne", "#FDP",
            "#BSW", "#Linke",
        ],
    },
    "Argentina_2023": {
        "since"        : "2023-10-19T00:00:00Z",
        "until"        : "2023-11-19T23:59:59Z",
        "election_date": "2023-11-19",
        "hashtags": [
            "#Milei", "#JavierMilei", "#LLA", "#LaLibertadAvanza",
            "#Massa", "#SergioMassa", "#PJ",
            "#EleccionesArgentinas", "#EleccionesArgentina2023",
            "#Argentina2023", "#Libertad", "#Peronismo",
            "#Balotaje", "#VotarArgentina",
        ],
    },
    "France_2024": {
        "since"        : "2024-06-09T00:00:00Z",
        "until"        : "2024-07-07T23:59:59Z",
        "election_date": "2024-07-07",
        "hashtags": [
            "#ElectionsLegislatives", "#ElectionsLegislatives2024",
            "#Legislatives2024", "#VoteFrance", "#FrancePolitique",
            "#NFP", "#NouveauFrontPopulaire",
            "#RN", "#RassemblementNational", "#Bardella", "#JorBardella",
            "#LePen", "#MarineLePen",
            "#Macron", "#Renaissance",
            "#Melenchon", "#LFI", "#FranceInsoumise", "#NUPES",
        ],
    },
}

ACTIVE_ELECTION   = "US_2024"
cfg               = ELECTIONS[ACTIVE_ELECTION]
POSTS_PER_HASHTAG = 200
MIN_TEXT_LENGTH   = 30

print(f"Active election : {ACTIVE_ELECTION}")
print(f"Window          : {cfg[\'since\'][:10]}  to  {cfg[\'until\'][:10]}")
print(f"Hashtags        : {len(cfg[\'hashtags\'])}")
print(f"Max posts       : {POSTS_PER_HASHTAG * len(cfg[\'hashtags\']):,}  ({POSTS_PER_HASHTAG} per tag)")
'''

# Find and update cell t06
patched = False
for cell in nb["cells"]:
    if cell.get("id") == "t06":
        cell["source"] = NEW_CONFIG_SRC
        cell["outputs"] = []
        cell["execution_count"] = None
        patched = True
        break

if not patched:
    print("WARNING: cell t06 not found — notebook structure may have changed.")
else:
    with open(NB_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Patched cell t06 in {NB_PATH}")
