#!/usr/bin/env python3
import os
import re
import time
import requests

TARGET_BOOKS = 1664
MIN_WORDS = 10_000

OUTPUT_DIR = "books"

BASE_URL = "https://gutendex.com/books"

INITIAL_PARAMS = {
    "languages": "en",       
    "mime_type": "text/",
    "sort": "popular",
}

REQUEST_TIMEOUT = 60
MAX_RETRIES = 5
RETRY_SLEEP = 5


def safe_request(url, params=None):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if params:
                r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            else:
                r = requests.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r
        except Exception as e:
            print(f"[!] Erreur : {e} (tentative {attempt}/{MAX_RETRIES})")
            time.sleep(RETRY_SLEEP)
    print("[X] Trop d'échecs, abandon.")
    return None


def sanitize_filename(s):
    s = re.sub(r"[^A-Za-z0-9\-_]+", "_", s.strip())
    return s[:80] if s else "untitled"


def strip_gutenberg_boilerplate(text):
    lower = text.lower()
    start = end = None

    for marker in ["*** start of", "***start of"]:
        pos = lower.find(marker)
        if pos != -1:
            start = text.find("\n", pos)
            break

    for marker in ["*** end of", "***end of"]:
        pos = lower.find(marker)
        if pos != -1:
            end = pos
            break

    if start is None: start = 0
    if end is None: end = len(text)

    return text[start:end]


def count_words(t):
    return len(t.split())


def choose_text_url(formats):
    for mime, url in formats.items():
        if mime.startswith("text/plain"):
            return url
    for mime, url in formats.items():
        if mime.startswith("text/"):
            return url
    return None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Objectif : {TARGET_BOOKS} livres en anglais, >= {MIN_WORDS} mots.")
    print(f"Enregistrement dans ./{OUTPUT_DIR}")

    downloaded = 0
    seen = set()

    next_url = BASE_URL
    params = INITIAL_PARAMS

    while downloaded < TARGET_BOOKS and next_url:
        print(f"\n[INFO] Récupération : {next_url}")

        res = safe_request(next_url, params=params if next_url == BASE_URL else None)
        if res is None:
            print("[X] Arrêt : impossible de récupérer la page.")
            break

        data = res.json()
        books = data["results"]
        next_url = data["next"]

        if next_url and not next_url.startswith("http"):
            next_url = "https://gutendex.com" + next_url

        params = None  # Après la première page

        for bk in books:
            if downloaded >= TARGET_BOOKS:
                break

            book_id = bk["id"]
            title = bk["title"]

            if book_id in seen:
                continue
            seen.add(book_id)

            if "en" not in bk.get("languages", []):
                continue

            text_url = choose_text_url(bk["formats"])
            if not text_url:
                print(f"  [-] Aucun texte pour {book_id} : {title}")
                continue

            print(f"\n=== Livre {book_id} : {title} ===")
            print(f"  Téléchargement : {text_url}")

            txt_res = safe_request(text_url)
            if txt_res is None:
                print("  [-] Échec téléchargement.")
                continue

            text = txt_res.text
            clean = strip_gutenberg_boilerplate(text)
            nb_words = count_words(clean)

            print(f"  → {nb_words} mots")

            if nb_words < MIN_WORDS:
                print("  [-] Livre trop court.")
                continue

            filename = f"{book_id}_{sanitize_filename(title)}.txt"
            path = os.path.join(OUTPUT_DIR, filename)

            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(clean)
                downloaded += 1
                print(f"  [✔] Sauvegardé ({downloaded}/{TARGET_BOOKS})")
            except Exception as e:
                print(f"  [!] Erreur écriture fichier : {e}")

            time.sleep(1)

    print("\n--- FIN ---")
    print(f"Total téléchargés : {downloaded}/{TARGET_BOOKS}")


if __name__ == "__main__":
    main()
