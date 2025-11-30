"""
Test fonctionnement : Recherche RegEx CLI vs API (avec pagination + chronomètre + log file)
"""

import subprocess
import json
import os
import time
from utils import api_get

# -------------- AJOUT POUR LE LOG DANS UN FICHIER --------------
LOG_PATH = "perf_regex.txt"

def log(text):
    with open(LOG_PATH, "a") as f:
        f.write(text + "\n")


# Patterns à tester
REGEX_TESTS = [
    r"king(dom|ly)",
    r".*king",
    r"s(a|e|o)+rgon",
    r"daar(.)+",
]

print("\n=== Test Recherche RegEx (CLI vs API + chronomètre + LOG) ===\n")

SCRIPT_DIR = "../mySearchEngine"
SCRIPT_NAME = "search_regex_in_index.py"

print(f"→ On lance {SCRIPT_NAME} depuis {SCRIPT_DIR}\n")


# --------------------------------------------------------
#     RÉCUPÉRATION DES RÉSULTATS API (pagination)
# --------------------------------------------------------
def get_all_api_regex_results(pattern):
    resp = api_get("/search_regex", {"pattern": pattern, "page": 1})

    if resp is None or "results" not in resp:
        return [], 0.0

    all_results = resp["results"]
    total_pages = resp.get("total_pages", 1)

    t0 = time.perf_counter()

    for p in range(2, total_pages + 1):
        resp_p = api_get("/search_regex", {"pattern": pattern, "page": p})
        if resp_p and "results" in resp_p:
            all_results.extend(resp_p["results"])

    exec_time = (time.perf_counter() - t0) * 1000
    return all_results, exec_time


# --------------------------------------------------------
#                   TEST POUR CHAQUE REGEX
# --------------------------------------------------------
for pattern in REGEX_TESTS:
    print(f"\n=============== RegEx : {pattern} ===============\n")

    # -------- CLI + chrono --------
    try:
        start = time.perf_counter()

        output = subprocess.check_output(
            ["python3", SCRIPT_NAME, pattern],
            stderr=subprocess.STDOUT,
            cwd=SCRIPT_DIR
        ).decode("utf-8")

        cli_time = (time.perf_counter() - start) * 1000
        cli_result = output.strip()

    except subprocess.CalledProcessError as e:
        print(" Erreur CLI :")
        print(e.output.decode("utf-8"))
        cli_result = None
        cli_time = -1

    print("Résultat CLI (DAAR) :")
    print(cli_result)
    print(f" Temps CLI : {cli_time:.2f} ms\n")

    # -------- API page 1 + chrono --------
    start = time.perf_counter()
    resp_page1 = api_get("/search_regex", {"pattern": pattern, "page": 1})
    api_simple_time = (time.perf_counter() - start) * 1000

    api_results_page1 = resp_page1.get("results", []) if resp_page1 else []

    print("Résultat API (page 1) :")
    for idx, book in enumerate(api_results_page1, start=1):
        print(f" {idx}. Doc {book.get('doc_id')} | {book.get('title')}")
    print(f" Temps API page 1 : {api_simple_time:.2f} ms\n")

    # -------- API paginée + chrono --------
    api_all_results, api_paged_time = get_all_api_regex_results(pattern)

    print("Résultat API (all pages) :")
    for idx, book in enumerate(api_all_results, start=1):
        print(f" {idx}. Doc {book.get('doc_id')} | {book.get('title')}")
    print(f" Temps API paginée : {api_paged_time:.2f} ms\n")

    # -------- LOG DANS LE FICHIER --------
    log(f"[{pattern}] CLI={cli_time:.2f}ms  API1={api_simple_time:.2f}ms  APIall={api_paged_time:.2f}ms")


    # --------------------------------------------------------
    #       EXTRACTION DES DOC_ID POUR LA COMPARAISON
    # --------------------------------------------------------

    # --- CLI : extraire doc_id ---
    cli_ids = []
    if cli_result:
        for line in cli_result.split("\n"):
            if line.strip().startswith(tuple(str(i) + "." for i in range(1, 200))) and "Doc" in line:
                try:
                    part = line.split("Doc", 1)[1]
                    doc_id = part.split("|", 1)[0].strip()
                    cli_ids.append(doc_id)
                except:
                    pass

    # --- API : extraire doc_id ---
    api_ids = [b.get("doc_id") for b in api_all_results]


    # --------------------------------------------------------
    #                  COMPARAISON INTELLIGENTE
    # --------------------------------------------------------
    print("Comparaison :")

    cli_set = set(cli_ids)
    api_set = set(api_ids)

    if cli_set == api_set:
        print(" ✔ Les deux systèmes contiennent les MÊMES livres.\n")
    else:
        print("  Différences détectées :\n")

        only_cli = sorted(cli_set - api_set)
        only_api = sorted(api_set - cli_set)

        if only_cli:
            print("   → Présents uniquement dans CLI DAAR :", only_cli)
        if only_api:
            print("   → Présents uniquement dans API web  :", only_api)

        print()

    # --------------------------------------------------------
    #                   RÉSUMÉ DES TEMPS
    # --------------------------------------------------------
    print("Résumé temps :")
    print(f"  CLI DAAR        : {cli_time:.2f} ms")
    print(f"  API (page 1)    : {api_simple_time:.2f} ms")
    print(f"  API (all pages) : {api_paged_time:.2f} ms")
    print("--------------------------------------------------------\n")
