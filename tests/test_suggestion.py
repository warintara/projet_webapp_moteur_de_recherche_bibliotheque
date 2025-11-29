"""
Test suggestion : compare la version CLI (suggest_books.py)
avec la version WEB (API FastAPI /suggest/<id>).
"""

import subprocess
import json
from utils import api_get

BOOK_ID = 1723   # tu peux changer
CLI_COMMAND = ["python3", "suggest_books.py", str(BOOK_ID)]

print("\n=== Test de Suggestion (CLI vs API) ===\n")

# --- Appel CLI ---
print(f"🔹 Exécution CLI : suggest_books.py {BOOK_ID}")

try:
    result_cli = subprocess.check_output(CLI_COMMAND, stderr=subprocess.STDOUT)
    result_cli = result_cli.decode("utf-8").strip()
except Exception as e:
    print("Erreur CLI :", e)
    result_cli = None

# Essaye de parser en JSON si possible
try:
    json_cli = json.loads(result_cli)
except:
    json_cli = result_cli

print("\nRésultat CLI :", json_cli, "\n")


# --- Appel API ---
print(f" Exécution API : /suggest/{BOOK_ID}")

api_response = api_get(f"/suggest/{BOOK_ID}")

if api_response is None:
    print("Impossible de récupérer la réponse API")
    exit()

print("\nRésultat API :", api_response, "\n")


# --- Comparaison ---
print("Comparaison...")

if json_cli == api_response:
    print("\nLes deux systèmes donnent EXACTEMENT le même résultat.\n")
else:
    print("\nLes résultats CLI et API DIFFÈRENT.\n")
    print("CLI  :", json_cli)
    print("API  :", api_response)
