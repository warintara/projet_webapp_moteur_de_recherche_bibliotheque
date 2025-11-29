import os
import json
import re
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import sys

# ========= NLTK config =========

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

WORD_REGEX = re.compile(r"\b\w+\b")

# ========= Paths =========

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
INDEX_PATH = os.path.join(LIB_DIR, "index.json")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")

# ========= Normalisation =========

def normalize(text: str):
    tokens = [w.lower() for w in WORD_REGEX.findall(text)]
    tokens = [w for w in tokens if w not in stop_words]
    tokens = [stemmer.stem(w) for w in tokens]
    return tokens

# ========= Load index =========

def load_index():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    with open(VOCAB_PATH, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    return index, vocab

# ≡≡≡ Chargement global (pour import dans FastAPI) ≡≡≡
index, vocab = load_index()

# ========= TRUE SEARCH FUNCTION (used by both CLI AND FastAPI) =========

def search_in_index(query: str, top_k: int = 20):
    """
    La fonction OFFICIELLE : même logique que search_query()
    mais renvoie seulement la liste des doc_id triés.
    """

    tokens = normalize(query)
    if not tokens:
        return []

    docs_per_token = []
    doc_scores = defaultdict(int)

    for t in tokens:
        posting = index.get(t)
        if not posting:
            return []
        docs_per_token.append(set(posting.keys()))
        for doc_id, count in posting.items():
            doc_scores[doc_id] += int(count)

    # intersection stricte
    common_docs = set.intersection(*docs_per_token)
    if not common_docs:
        return []

    ranked = sorted(common_docs, key=lambda d: doc_scores[d], reverse=True)

    return ranked[:top_k]

# ========= CLI TOOL =========

def search_query(query: str, index, top_k=20):
    """(Version CLI avec affichage score + vocab size)"""
    tokens = normalize(query)
    if not tokens:
        print("Requête vide.")
        return []

    docs_per_token = []
    doc_scores = defaultdict(int)

    for t in tokens:
        posting = index.get(t)
        if not posting:
            print(f"Mot '{t}' absent.")
            return []
        docs_per_token.append(set(posting.keys()))
        for doc_id, count in posting.items():
            doc_scores[doc_id] += int(count)

    common_docs = set.intersection(*docs_per_token)
    if not common_docs:
        print("Aucun document trouvé.")
        return []

    ranked = sorted(
        [(doc_id, doc_scores[doc_id]) for doc_id in common_docs],
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]

def pretty_print_results(results, vocab):
    if not results:
        print("Aucun résultat.")
        return

    print("\n=== Résultats ===")
    for rank, (doc_id, score) in enumerate(results, start=1):
        vocab_size = len(vocab.get(doc_id, []))
        print(f"{rank}. Doc {doc_id} | score={score} | vocab_size={vocab_size}")


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        results = search_query(query, index)
        pretty_print_results(results, vocab)
    else:
        print("Mode interactif, tape 'quit' pour sortir.")
        while True:
            q = input("> ").strip()
            if q.lower() in ("quit", "exit"):
                break
            results = search_query(q, index)
            pretty_print_results(results, vocab)


if __name__ == "__main__":
    main()
