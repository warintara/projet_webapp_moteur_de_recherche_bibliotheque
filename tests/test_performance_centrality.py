"""
Benchmark calcul centralité Pagerank (via endpoint dédié à recalculer)
"""

from utils import api_get, measure_time

def do_compute():
    api_get("/compute_pagerank")

print("\n=== Benchmark : Centralité Pagerank ===\n")

mean, all_times = measure_time(do_compute, repeat=5)

print(f"Temps moyen : {mean:.2f} ms")
print("Mesures individuelles :", [round(t,2) for t in all_times])
