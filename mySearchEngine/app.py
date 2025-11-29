from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response
import requests

from fastapi.middleware.cors import CORSMiddleware
from DFA import DFA

import json
import os
from search_in_index import search_in_index




app = FastAPI()


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


@app.get("/cover/{doc_id}")
def get_cover(doc_id: int):
    """
    Télécharge la couverture depuis l'URL de Project Gutenberg
    et la renvoie depuis le backend (pas de OpaqueResponseBlocking).
    """
    meta = metadata.get(str(doc_id))
    if not meta:
        raise HTTPException(status_code=404, detail="Unknown document")

    url = meta.get("cover_url")
    if not url:
        raise HTTPException(status_code=404, detail="No cover image for this document")

    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error fetching cover: {e}")

    content_type = r.headers.get("Content-Type", "image/jpeg")
    return Response(content=r.content, media_type=content_type)


@app.get("/search")
def api_search(q: str):
    docs = search_in_index(q) 

    results = []
    for doc_id in docs:
        meta = metadata.get(str(doc_id), {})
        results.append({
            "doc_id": doc_id,
            "title": meta.get("title", f"Doc {doc_id}"),
            "author": meta.get("author", "Unknown"),
            "cover_image": f"/cover/{doc_id}" if meta.get("cover_url") else None
        })

    return {
        "query": q,
        "total_results": len(results),
        "page": 1,
        "page_size": len(results),
        "results": results,
        "is_regex": False,
    }


@app.get("/search_regex")
def api_search_regex(pattern: str):
    ranked = search_regex_engine(pattern)

    # limiter à 20 résultats MAX
    ranked = ranked[:20]

    results = []
    for doc_id, score in ranked:
        mid = str(doc_id)
        meta = metadata.get(mid, {})
        results.append({
            "doc_id": doc_id,
            "score": score,
            "title": meta.get("title", f"Doc {doc_id}"),
            "author": meta.get("author", "Unknown author"),
            "cover_image": f"/cover/{doc_id}" if meta.get("cover_url") else None,
        })

    return {
        "query": pattern,
        "total_results": len(results),
        "page": 1,
        "page_size": len(results),
        "results": results,
        "is_regex": True,
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
