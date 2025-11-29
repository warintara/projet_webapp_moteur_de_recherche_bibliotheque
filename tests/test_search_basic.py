"""
Test fonctionnel : recherche simple par mot-clé
"""

from utils import api_get

TEST_KEYWORDS = ["king", "love", "magic", "sea", "truth", "zebra"]

print("\n=== Test Recherche Simple ===\n")

for word in TEST_KEYWORDS:
    print(f"Recherche : {word}")
    data = api_get("/search", {"query": word})

    if data is None:
        print("API ne répond pas\n")
        continue

    if len(data) == 0:
        print("Aucun livre trouvé (peut être normal pour certains mots)\n")
        continue

    print(f"{len(data)} livres trouvés. Premier titre : {data[0].get('title','?')}\n")
