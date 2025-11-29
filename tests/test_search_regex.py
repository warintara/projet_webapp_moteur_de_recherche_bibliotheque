"""
Test fonctionnel : recherche avancée RegEx
"""

from utils import api_get

REGEX_TESTS = [
    r"king(dom|ly)",
    r"(battle|war).{0,20}(army)",
    r"([A-Za-z]{3})*king"
]

print("\n=== Test Recherche RegEx ===\n")

for regex in REGEX_TESTS:
    print(f"RegEx : {regex}")
    data = api_get("/search_regex", {"query": regex})

    if data is None:
        print("API ne répond pas\n")
        continue

    print(f" {len(data)} résultats\n")
