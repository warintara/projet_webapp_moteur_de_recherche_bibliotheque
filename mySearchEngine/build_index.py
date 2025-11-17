import os
import requests
import re
import json
from collections import defaultdict

# Dossier où l'on va stocker les fichiers JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
os.makedirs(LIB_DIR, exist_ok=True)     # Création du dossier s'il n'existe pas

# Regex pour découper le texte en mots
WORD_REGEX = re.compile(r"\b\w+\b")

TARGET = 1664
MIN_WORDS = 10000

def tokenize(text):
    return [w.lower() for w in WORD_REGEX.findall(text)]

def get_text(book_id):
    url = f"https://gutendex.com/books/{book_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None

    data = r.json()
    formats = data.get("formats", {})
    txt_url = (
        formats.get("text/plain; charset=utf-8")
        or formats.get("text/plain")
        or formats.get("text/plain; charset=us-ascii")
    )
    if not txt_url:
        return None

    tr = requests.get(txt_url)
    if tr.status_code != 200:
        return None

    return tr.text

def main():
    index = {}
    vocab = {}

    count_docs = 0

    for book_id in range(1, 5000):
        if count_docs >= TARGET:
            break

        print(f"Livre {book_id}")
        text = get_text(book_id)
        if text is None:
            print(" Pas de texte")
            continue

        words = tokenize(text)
        if len(words) < MIN_WORDS:
            print(f"Trop court ({len(words)} mots)")
            continue

        doc_id = str(book_id)
        count_docs += 1
        print(f"Livre accepté comme document {doc_id}")

        # Construire l’index
        seen = set()
        for w in words:
            if w not in index:
                index[w] = {}
            if doc_id not in index[w]:
                index[w][doc_id] = 0

            seen.add(w)

        vocab[doc_id] = list(seen)

    # Sauvegarde
    with open(os.path.join(LIB_DIR, "index.json"), "w") as f:
        json.dump({w: dict(d) for w, d in index.items()}, f)

    with open(os.path.join(LIB_DIR, "vocab.json"), "w") as f:
        json.dump(vocab, f)

    print(f"Total de livres valides : {count_docs}")
    print("Index et vocab.json créés !")

if __name__ == "__main__":
    main()
