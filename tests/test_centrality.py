"""
Test centrality : cohérence + performance
(on ne recalcule plus la centralité)
"""

import json
import time
import os

CENTRALITY_FILE = "../mySearchEngine/library/centrality.json"
TOP_N = 10
REPEAT = 10


def load_centrality():
    """Charge les scores de centralité depuis centrality.json."""
    if not os.path.exists(CENTRALITY_FILE):
        print("ERREUR : centrality.json introuvable. Lance d'abord centrality.py")
        return {}

    with open(CENTRALITY_FILE, "r") as f:
        data = json.load(f)

    return data


def get_top_n(data, n=10):
    """Retourne un top N trié (doc_id, score)."""
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return sorted_items[:n]


def benchmark_load(repeat=10):
    """Mesure le temps nécessaire pour charger + trier le fichier."""
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        data = load_centrality()
        get_top_n(data, TOP_N)
        times.append((time.perf_counter() - t0) * 1000)
    return times


# =======================
#        EXECUTION
# =======================

print("\n========== TEST CENTRALITY (lecture JSON) ==========\n")

data = load_centrality()

if not data:
    exit()

top = get_top_n(data, TOP_N)

print(f"Top {TOP_N} extraits :")
for i, (doc_id, score) in enumerate(top, 1):
    print(f"{i}. Doc {doc_id} | score={score}")

# Performance
times = benchmark_load(REPEAT)
avg = sum(times) / len(times)

print("\n====== Benchmark (lecture JSON) ======")
print("Mesures :", [round(t, 2) for t in times])
print(f"Moyenne : {avg:.2f} ms")

print("\n==== FIN DU TEST CENTRALITY ====\n")
