import os
import requests
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- NLTK stopwords ----------
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")
    nltk.download("omw-1.4")


stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# ---------- Dossiers ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
os.makedirs(LIB_DIR, exist_ok=True)     # Création du dossier s'il n'existe pas

# ---------- Constantes ----------
WORD_REGEX = re.compile(r"\b\w+\b")

TARGET = 1664          # nombre de livres à garder
MIN_WORDS = 10000      # min de mots après nettoyage
MAX_BOOK_ID = 5000     # id max à tester
MAX_WORKERS = 8        # nb de threads (à ajuster)

START_MARKER_REGEX = re.compile(
    r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK .* \*\*\*",
    re.IGNORECASE
)

# ---------- Fonctions utilitaires ----------
def clean_gutenberg_text(raw_text: str) -> str:
    m = START_MARKER_REGEX.search(raw_text)
    if m:
        return raw_text[m.end():]
    return raw_text

def tokenize(text, mode="stem"):  # mode: "stem" ou "lemma"
    tokens = [w.lower() for w in WORD_REGEX.findall(text)]
    tokens = [w for w in tokens if w not in stop_words]

    if mode == "stem":
        tokens = [stemmer.stem(w) for w in tokens]
    elif mode == "lemma":
        tokens = [lemmatizer.lemmatize(w) for w in tokens]

    return tokens

def get_text(book_id):
    url = f"https://gutendex.com/books/{book_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None

    data = r.json()

    languages = data.get("languages", [])
    if "en" not in languages:
        print("  Pas en anglais, ignoré")
        return None

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
    
    raw_text = tr.text

    cleaned = clean_gutenberg_text(raw_text)
    return cleaned

def process_book(book_id):
    print(f"Livre {book_id}")
    text = get_text(book_id)
    if text is None:
        print("Pas de texte")
        return None

    words = tokenize(text)
    if len(words) < MIN_WORDS:
        print(f"  [Book {book_id}] Trop court ({len(words)} mots)")
        return None

    doc_id = str(book_id)
    print(f"  [Book {book_id}] Livre accepté comme document {doc_id}")

    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1

    seen = set(word_counts.keys())

    return doc_id, seen, word_counts

# def main():
#     index = {}
#     vocab = {}

#     count_docs = 0

#     for book_id in range(1, 5000):
#         if count_docs >= TARGET:
#             break

#         print(f"Livre {book_id}")
#         text = get_text(book_id)
#         if text is None:
#             print(" Pas de texte")
#             continue

#         words = tokenize(text)
#         if len(words) < MIN_WORDS:
#             print(f"Trop court ({len(words)} mots)")
#             continue

#         doc_id = str(book_id)
#         count_docs += 1
#         print(f"Livre accepté comme document {doc_id}")

#         # Construire l’index
#         seen = set()
#         for w in words:
#             if w not in index:
#                 index[w] = {}
#             if doc_id not in index[w]:
#                 index[w][doc_id] = 0
#             index[w][doc_id] += 1

#             seen.add(w)

#         vocab[doc_id] = list(seen)

#     # Sauvegarde
#     with open(os.path.join(LIB_DIR, "index.json"), "w") as f:
#         json.dump({w: dict(d) for w, d in index.items()}, f)

#     with open(os.path.join(LIB_DIR, "vocab.json"), "w") as f:
#         json.dump(vocab, f)

#     print(f"Total de livres valides : {count_docs}")
#     print("Index et vocab.json créés !")

# ---------- Main ----------

# def main():
#     index = defaultdict(dict)
#     vocab = {}

#     count_docs = 0

#     with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
#         futures = {
#             executor.submit(process_book, book_id): book_id
#             for book_id in range(1, MAX_BOOK_ID)
#         }

#         for future in as_completed(futures):
#             result = future.result()
#             if result is None:
#                 continue

#             if count_docs >= TARGET:
#                 continue

#             doc_id, seen, word_counts = result
#             count_docs += 1
#             print(f"==> Document {doc_id} ajouté ({count_docs}/{TARGET})")

#             for w, c in word_counts.items():
#                 index[w][doc_id] = index[w].get(doc_id, 0) + c

#             vocab[doc_id] = list(seen)

#             if count_docs >= TARGET:
#                 print("Quota de documents atteint, on arrête.")
#                 break

#     # Sauvegarde
#     print("Sauvegarde des fichiers JSON...")
#     with open(os.path.join(LIB_DIR, "index.json"), "w") as f:
#         json.dump({w: dict(docs) for w, docs in index.items()}, f)

#     with open(os.path.join(LIB_DIR, "vocab.json"), "w") as f:
#         json.dump(vocab, f)

#     print(f"Total de livres valides : {count_docs}")
#     print("Index et vocab.json créés !")

def main():
    index = defaultdict(dict)
    vocab = {}

    book_id = 3
    result = process_book(book_id)

    if result is None:
        print(f"Le livre {book_id} n'a pas pu être traité.")
        return

    doc_id, seen, word_counts = result
    print(f"==> Document {doc_id} ajouté")

    # Construire l'index pour ce seul document
    for w, c in word_counts.items():
        index[w][doc_id] = c

    vocab[doc_id] = list(seen)

    # Sauvegarde
    print("Sauvegarde des fichiers JSON...")
    with open(os.path.join(LIB_DIR, "index.json"), "w") as f:
        json.dump({w: dict(docs) for w, docs in index.items()}, f)

    with open(os.path.join(LIB_DIR, "vocab.json"), "w") as f:
        json.dump(vocab, f)

    print("Terminé pour le livre 10 !")


if __name__ == "__main__":
    main()
