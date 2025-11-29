"""
Test fonctionnel : classement par centralité (Pagerank)
"""

from utils import api_get

print("\n=== Test Classement Centralité ===\n")

key = "war"
results = api_get("/search", {"query": key})

if results is None:
    print("API ne répond pas\n")
    exit()

if len(results) < 3:
    print("Pas assez de résultats pour tester la centralité")
    exit()

print(f"Top 3 pour '{key}' :")
for r in results[:3]:
    print(f" - {r['title']} (score={r.get('score')})")

print("\n Classement récupéré sans erreur")
