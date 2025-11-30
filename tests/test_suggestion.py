"""
Test Suggestion : CLI vs API + Performance + Log
"""

import subprocess
import time
from utils import api_get

# ---------------- CONFIG ----------------
BOOK_IDS = [1723, 2016]   # Livres à tester
SCRIPT_DIR = "../mySearchEngine"
SCRIPT_NAME = "suggest_books.py"
LOG_PATH = "perf_suggestion.txt"

print("\n=== Test Suggestion (CLI vs API + performance + log) ===\n")
print(f"→ On lance {SCRIPT_NAME} depuis {SCRIPT_DIR}\n")


# ---------------- LOG FILE ----------------
def log(text):
    with open(LOG_PATH, "a") as f:
        f.write(text + "\n")


# ---------------- BENCHMARK ----------------
def measure_time(fn, repeat=5):
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn()
        times.append((time.perf_counter() - t0) * 1000)
    return sum(times) / len(times), times


# -------------------------------------------------------
#            TEST POUR CHAQUE LIVRE
# -------------------------------------------------------

for book_id in BOOK_IDS:

    print(f"\n=============== Test pour le livre {book_id} ===============\n")

    # ---------------- CLI ----------------
    print("🔹 CLI (DAAR)")
    cli_result = None
    try:
        t0 = time.perf_counter()
        output = subprocess.check_output(
            ["python3", SCRIPT_NAME, str(book_id)],
            stderr=subprocess.STDOUT,
            cwd=SCRIPT_DIR
        ).decode("utf-8")
        cli_time = (time.perf_counter() - t0) * 1000
        cli_result = output.strip()
    except subprocess.CalledProcessError as e:
        print("Erreur CLI :", e.output.decode("utf-8"))
        cli_time = -1

    print(cli_result)
    print(f"⏱ Temps CLI : {cli_time:.2f} ms\n")

    # ---------------- API ----------------
    print("🔹 API /suggest/")
    t0 = time.perf_counter()
    api_result = api_get(f"/suggest/{book_id}")
    api_time = (time.perf_counter() - t0) * 1000

    if isinstance(api_result, list):
        for i, book in enumerate(api_result, start=1):
            print(f" {i}. Doc {book['doc_id']} | {book['title']}")
            print(f"    {book['author']} | DL={book['downloads']} | centrality={book['centrality']:.4f}\n")
    else:
        print(api_result)

    print(f"⏱ Temps API : {api_time:.2f} ms\n")

    # ---------------- COMPARAISON ----------------
    print("🔹 Comparaison CLI vs API")

    if cli_result is None or api_result is None:
        print(" Impossible de comparer (erreur CLI ou API)\n")
        continue

    # extraire doc_id CLI
    cli_ids = []
    for line in cli_result.split("\n"):
        line = line.strip()
        if line.startswith(tuple(str(x) + "." for x in range(1, 20))) and "Doc" in line:
            try:
                part = line.split("Doc", 1)[1]
                doc_id = part.split("|", 1)[0].strip()
                cli_ids.append(doc_id)
            except:
                pass

    api_ids = [b["doc_id"] for b in api_result]

    print("doc_id CLI :", cli_ids)
    print("doc_id API :", api_ids)

    if cli_ids == api_ids:
        print("✔ CLI et API donnent les MÊMES suggestions.\n")
    else:
        print(" CLI et API DIFFÈRENT (normal si scoring différent).\n")

    # ---------------- LOG ----------------
    log(f"[{book_id}] CLI={cli_time:.2f}ms API={api_time:.2f}ms")

    # ---------------- RÉSUMÉ TEMPS ----------------
    print("Résumé temps :")
    print(f"  CLI DAAR : {cli_time:.2f} ms")
    print(f"  API Web  : {api_time:.2f} ms")
    print("--------------------------------------------------------\n")


# -------------------------------------------------------
#            BENCHMARK GLOBAL (optionnel)
# -------------------------------------------------------
print("\n=== Benchmark Global (API seulement) ===\n")

def bench_api():
    api_get("/suggest/1723")

mean, times = measure_time(bench_api, repeat=10)

print(f"Temps moyen API : {mean:.2f} ms")
print("Mesures :", [round(t, 2) for t in times])

log(f"[GLOBAL] API_mean={mean:.2f}ms")
