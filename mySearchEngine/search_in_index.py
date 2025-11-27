import os
import json
import re
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import sys

# ========= NLTK : même config que dans build_index.py =========

try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

WORD_REGEX = re.compile(r"\b\w+\b")

# ========= Chemins =========

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
INDEX_PATH = os.path.join(LIB_DIR, "index.json")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")


# ========= Normalisation de la requête =========

def normalize_tokens(text: str, mode="stem"):
    """
    Même pipeline que dans build_index.py :
      - lower()
      - tokenisation
      - suppression des stopwords
      - stemming ou lemmatisation
    """
    tokens = [w.lower() for w in WORD_REGEX.findall(text)]
    tokens = [w for w in tokens if w not in stop_words]

    if mode == "stem":
        tokens = [stemmer.stem(w) for w in tokens]
    elif mode == "lemma":
        tokens = [lemmatizer.lemmatize(w) for w in tokens]

    return tokens


# ========= Chargement de l'index =========

def load_index():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"index.json introuvable : {INDEX_PATH}")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)

    vocab = {}
    if os.path.exists(VOCAB_PATH):
        with open(VOCAB_PATH, "r", encoding="utf-8") as f:
            vocab = json.load(f)

    return index, vocab


# ========= Recherche dans l'index =========

def search_query(query: str, index: dict, top_k: int = 20):
    """
    Recherche de livres par mot-clé (ou plusieurs mots).
    - On normalise la requête avec le même pipeline que l'indexation.
    - On ne garde que les documents qui contiennent *tous* les mots.
    - Score = somme des fréquences des mots dans le document.
    """
    tokens = normalize_tokens(query, mode="stem")
    if not tokens:
        print("Requête vide après normalisation (stopwords uniquement ?).")
        return []

    print(f"Tokens normalisés pour la requête : {tokens}")

    # postings pour chaque token
    docs_per_token = []
    doc_scores = defaultdict(int)

    for t in tokens:
        posting = index.get(t)
        if not posting:
            print(f"Mot '{t}' absent de l'index.")
            return []
        docs_per_token.append(set(posting.keys()))
        for doc_id, count in posting.items():
            doc_scores[doc_id] += int(count)

    # intersection : docs qui contiennent tous les mots de la requête
    common_docs = set.intersection(*docs_per_token)
    if not common_docs:
        print("Aucun document ne contient tous les mots de la requête.")
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
        # pour l'instant on n'a pas encore de titre/metadata ; on affiche juste l'id
        words_count = len(vocab.get(doc_id, []))
        print(f"{rank:2d}. Doc {doc_id}  | score={score}  | vocab_size={words_count}")


# ========= CLI =========

def main():
    index, vocab = load_index()

    # deux modes :
    #  - python3 search_in_index.py "your query"
    #  - ou mode interactif si aucun argument
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        results = search_query(query, index)
        pretty_print_results(results, vocab)
    else:
        print("Mode interactif. Tape 'quit' pour sortir.")
        while True:
            try:
                q = input("\nRequête > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break
            if not q:
                continue
            if q.lower() in {"quit", "exit"}:
                print("Bye.")
                break
            results = search_query(q, index)
            pretty_print_results(results, vocab)


if __name__ == "__main__":
    main()
