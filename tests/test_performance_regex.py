"""
Benchmark recherche RegEx
"""

from utils import api_get, measure_time

REGEX = r"([A-Za-z]{3})*king"

def do_regex():
    api_get("/search_regex", {"query": REGEX})

print("\n=== Benchmark : Recherche RegEx ===\n")

mean, all_times = measure_time(do_regex, repeat=10)

print(f"Temps moyen : {mean:.2f} ms")
print("Mesures individuelles :", [round(t,2) for t in all_times])
