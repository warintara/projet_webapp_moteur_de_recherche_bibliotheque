"""
Benchmark recherche simple
"""

from utils import api_get, measure_time

KEYWORD = "king"

def do_search():
    api_get("/search", {"query": KEYWORD})

print("\n=== Benchmark : Recherche simple ===\n")

mean, all_times = measure_time(do_search, repeat=20)

print(f"Temps moyen : {mean:.2f} ms")
print("Mesures individuelles (ms) :", [round(t,2) for t in all_times])
