from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from DFA import DFA

import json
import os

# ----- Paths -----

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")

INDEX_PATH = os.path.join(LIB_DIR, "index.json")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")
META_PATH  = os.path.join(LIB_DIR, "metadata.json")
GRAPH_PATH = os.path.join(LIB_DIR, "graph.json")
CENTRALITY_PATH = os.path.join(LIB_DIR, "centrality.json")

# ----- Load JSON Files -----

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

index = load_json(INDEX_PATH)
vocab = load_json(VOCAB_PATH)
metadata = load_json(META_PATH)
graph = load_json(GRAPH_PATH)
centrality = load_json(CENTRALITY_PATH)

# ----- FastAPI app -----

app = FastAPI(title="DAAR Search Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Search helpers -----

def dfa_match(dfa, text: str) -> bool:
    state = dfa.start
    for ch in text:
        code = ord(ch)

        if state not in dfa.transitions:
            return False

        if code not in dfa.transitions[state]:
            return False

        state = dfa.transitions[state][code]

    return state in dfa.final_states


def tokenize_query(q):
    import re
    return re.findall(r"\b\w+\b", q.lower())


def search_normal(query):
    tokens = tokenize_query(query)
    results = {}

    for token in tokens:
        if token in index:
            for doc_id, tf in index[token].items():
                results[doc_id] = results.get(doc_id, 0) + tf

    ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
    return ranked


def search_regex_engine(pattern):
    from NFA import regex_to_nfa
    from DFA import nfa_to_dfa, minimize_dfa_hopcroft

    # 1) Construire DFA minimal
    nfa = regex_to_nfa(pattern)
    dfa = minimize_dfa_hopcroft(nfa_to_dfa(nfa))

    # 2) Trouver tous les mots de l'index qui matchent la regex
    matching_words = []
    for word in index.keys():
        if dfa_match(dfa, word):      
            matching_words.append(word)

    # 3) Récupérer les documents correspondants
    doc_scores = {}

    for w in matching_words:
        postings = index[w]          # {doc_id : tf }
        for doc_id, tf in postings.items():
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + tf

    # 4) Tri par score décroissant
    ranked_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

    return ranked_docs



def suggest_neighbors(doc_id, k=10):
    if doc_id not in graph:
        return []

    neigh = graph[doc_id]

    def score(n):
        return (
            centrality.get(n, 0),
            metadata.get(n, {}).get("downloads", 0)
        )

    neigh_sorted = sorted(neigh, key=score, reverse=True)
    return neigh_sorted[:k]

# ----- API Routes -----

@app.get("/")
def root():
    return {"message": "DAAR Search Engine API: OK"}

@app.get("/search")
def api_search(q: str, page: int = 1, page_size: int = 9):

    ranked = search_normal(q)
    response = []

    for doc_id, score in ranked[:20]:
        meta = metadata.get(doc_id, {})
        response.append({
            "doc_id": doc_id,
            "score": score,
            "title": meta.get("title"),
            "author": meta.get("author"),
            "year": meta.get("year"),
            "downloads": meta.get("downloads"),
            "cover_url": meta.get("cover_url"),
        })

    return {
        "total": len(ranked),
        "page": 1,
        "page_size": len(response),
        "results": response,
    }


@app.get("/search_regex")
def api_search_regex(pattern: str, page: int = 1, page_size: int = 9):

    ranked = search_regex_engine(pattern)

    # Pagination backend
    start = (page - 1) * page_size
    end = start + page_size
    paginated = ranked[start:end]

    results = []

    for entry in paginated:
        # entry vient de search_regex_engine : (doc_id, score)
        doc_id = entry[0]
        score = entry[1]

        meta = metadata.get(str(doc_id), {})

        results.append({
            "doc_id": doc_id,
            "title": meta.get("title", "Unknown"),
            "author": meta.get("author", "Unknown"),
            "cover_image": meta.get("cover_url", None),
            "score": score,
        })

    return {
        "total": len(ranked),
        "page": page,
        "page_size": page_size,
        "results": results,
    }


@app.get("/book/{doc_id}")
def api_book(doc_id: str):
    if doc_id not in metadata:
        raise HTTPException(404, "Document non trouvé")
    return metadata[doc_id]

@app.get("/suggest/{doc_id}")
def api_suggest(doc_id: str, k: int = 10):
    neigh = suggest_neighbors(doc_id, k)
    return [
        {
            "doc_id": d,
            "title": metadata.get(d, {}).get("title"),
            "author": metadata.get(d, {}).get("author"),
            "downloads": metadata.get(d, {}).get("downloads"),
            "cover_url": metadata.get(d, {}).get("cover_url"),
            "centrality": centrality.get(d),
        }
        for d in neigh
    ]
