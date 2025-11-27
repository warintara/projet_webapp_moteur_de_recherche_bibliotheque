import os
import re
import json
import time
import logging
import requests
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from tqdm import tqdm

# =========================
# Config logging
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
os.makedirs(LIB_DIR, exist_ok=True)

INDEX_PATH = os.path.join(LIB_DIR, "index.json")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")
PROGRESS_PATH = os.path.join(LIB_DIR, "progress.json")
LOG_PATH = os.path.join(LIB_DIR, "build_index.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# =========================
# NLTK : stopwords & wordnet
# =========================

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

# =========================
# Constantes
# =========================

WORD_REGEX = re.compile(r"\b\w+\b")

TARGET = 1664          # nombre de livres à garder
MIN_WORDS = 10000      # min de mots après nettoyage
SAVE_EVERY = 50        # sauvegarde toutes les 50 acceptations

START_MARKER_REGEX = re.compile(
    r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK .* \*\*\*",
    re.IGNORECASE
)

# =========================
# Fonctions utilitaires
# =========================

def safe_get(url, retries=5, timeout=20):
    """Requête GET robuste avec retry sur erreurs réseau."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout)
            return resp
        except requests.exceptions.RequestException as e:
            logging.warning(f"[safe_get] Erreur réseau sur {url} : {e} (tentative {attempt+1}/{retries})")
            time.sleep(1 + attempt * 2)  # backoff progressif
    logging.error(f"[safe_get] Abandon de {url} après {retries} tentatives.")
    return None


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


def get_text(book_id: int):
    """Récupère le texte brut pour un book_id donné sur Gutendex."""
    url = f"https://gutendex.com/books/{book_id}"
    r = safe_get(url)
    if r is None or r.status_code != 200:
        print(f"Livre {book_id}\nPas de texte")
        return None

    try:
        data = r.json()
    except ValueError:
        logging.warning(f"[get_text] JSON invalide pour book_id={book_id}")
        print(f"Livre {book_id}\nPas de texte")
        return None

    languages = data.get("languages", [])
    if "en" not in languages:
        print(f"Livre {book_id}\n  Pas en anglais, ignoré")
        return None

    formats = data.get("formats", {})
    txt_url = (
        formats.get("text/plain; charset=utf-8")
        or formats.get("text/plain")
        or formats.get("text/plain; charset=us-ascii")
    )
    if not txt_url:
        print(f"Livre {book_id}\nPas de texte (pas de format text/plain)")
        return None

    tr = safe_get(txt_url)
    if tr is None or tr.status_code != 200:
        print(f"Livre {book_id}\nPas de texte (erreur téléchargement)")
        return None

    # Lecture du contenu texte
    try:
        raw_text = tr.text
    except Exception as e:
        logging.warning(f"[get_text] Erreur lecture texte pour book_id={book_id} : {e}")
        print(f"Livre {book_id}\nPas de texte (erreur décodage)")
        return None

    cleaned = clean_gutenberg_text(raw_text)
    return cleaned


def process_book(book_id: int):
    """Traite un livre : téléchargement, nettoyage, tokenisation, comptage."""
    logging.info(f"Traitement du livre {book_id}")
    text = get_text(book_id)
    if text is None:
        return None

    words = tokenize(text)
    if len(words) < MIN_WORDS:
        print(f"Livre {book_id}\n  [Book {book_id}] Trop court ({len(words)} mots)")
        return None

    doc_id = str(book_id)
    print(f"Livre {book_id}\n  [Book {book_id}] Livre accepté comme document {doc_id}")

    word_counts = {}
    for w in words:
        word_counts[w] = word_counts.get(w, 0) + 1

    seen = set(word_counts.keys())
    return doc_id, seen, word_counts


def load_state():
    """Charge l'état précédent si disponible (index, vocab, progress)."""
    index = defaultdict(dict)
    vocab = {}
    next_book_id = 1
    count_docs = 0

    if os.path.exists(INDEX_PATH):
        logging.info("Chargement de l'index existant...")
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            raw_index = json.load(f)
        for w, docs in raw_index.items():
            index[w] = {doc_id: int(c) for doc_id, c in docs.items()}

    if os.path.exists(VOCAB_PATH):
        logging.info("Chargement du vocabulaire existant...")
        with open(VOCAB_PATH, "r", encoding="utf-8") as f:
            vocab = json.load(f)

    if os.path.exists(PROGRESS_PATH):
        logging.info("Chargement du fichier de progression...")
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            p = json.load(f)
        next_book_id = p.get("next_book_id", 1)
        # si count_docs n'est pas présent, on le déduit du vocab
        count_docs = p.get("count_docs", len(vocab))
    else:
        count_docs = len(vocab)

    logging.info(f"État initial : {count_docs} livres valides, prochain ID = {next_book_id}")
    return index, vocab, next_book_id, count_docs


def save_state(index, vocab, next_book_id, count_docs):
    """Sauvegarde l'index, le vocabulaire, et la progression."""
    logging.info(f"Sauvegarde de l'état : {count_docs} livres valides, prochain ID = {next_book_id}")
    # index peut être un defaultdict, il faut le convertir
    plain_index = {w: docs for w, docs in index.items()}

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(plain_index, f)

    with open(VOCAB_PATH, "w", encoding="utf-8") as f:
        json.dump(vocab, f)

    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "next_book_id": next_book_id,
                "count_docs": count_docs,
                "target": TARGET,
            },
            f,
        )


def main():
    index, vocab, book_id, count_docs = load_state()

    # barre de progression sur le nombre de livres valides, pas sur les IDs testés
    pbar = tqdm(total=TARGET, initial=count_docs, desc="Livres valides")
    since_last_save = 0

    while count_docs < TARGET:
        result = process_book(book_id)
        if result is not None:
            doc_id, seen, word_counts = result

            # mise à jour de l'index
            for w, c in word_counts.items():
                index[w][doc_id] = index[w].get(doc_id, 0) + c

            vocab[doc_id] = list(seen)

            count_docs += 1
            since_last_save += 1
            pbar.update(1)

            if since_last_save >= SAVE_EVERY:
                save_state(index, vocab, book_id + 1, count_docs)
                since_last_save = 0

        # on passe au livre suivant, qu'il ait été accepté ou non
        book_id += 1

        # petite pause pour ne pas trop agresser Gutendex
        time.sleep(0.1)

    pbar.close()
    # sauvegarde finale
    save_state(index, vocab, book_id, count_docs)
    print("Index et vocab.json créés !")
    print(f"Total livres valides : {count_docs}")


if __name__ == "__main__":
    main()
