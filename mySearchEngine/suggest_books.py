import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")

GRAPH_PATH = os.path.join(LIB_DIR, "graph.json")
CENTRALITY_PATH = os.path.join(LIB_DIR, "centrality.json")
METADATA_PATH = os.path.join(LIB_DIR, "metadata.json")


def load_json(path, required=True):
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(f"Fichier introuvable : {path}")
        else:
            return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_data():
    graph = load_json(GRAPH_PATH)
    centrality = load_json(CENTRALITY_PATH, required=False)
    metadata = load_json(METADATA_PATH, required=False)
    return graph, centrality, metadata


def get_suggestions(doc_id, k=10):
    graph, centrality, metadata = load_data()

    if doc_id not in graph:
        # doc sans voisins dans le graphe → fallback global
        print(f"Doc {doc_id} n'a pas de voisins dans le graphe.")
        print("On renvoie les documents les plus centraux globalement.\n")
        # tri global sur centralité
        if not centrality:
            return []
        sorted_docs = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )
        # enlever le doc lui-même s'il est présent
        suggestions = [d for d, _ in sorted_docs if d != doc_id][:k]
        return format_suggestions(suggestions, metadata, centrality)

    neighbors = graph.get(doc_id, [])
    if not neighbors:
        print(f"Doc {doc_id} n'a pas de voisins dans le graphe.")
        return []

    # On trie les voisins par :
    #   1) centralité décroissante (si disponible)
    #   2) downloads décroissants (si disponible)
    #   3) doc_id croissant (pour stabilité)
    def score(n):
        c = centrality.get(n, 0.0) if centrality else 0.0
        dl = 0
        if metadata and n in metadata:
            dl = metadata[n].get("downloads", 0) or 0
        return (c, dl, -int(n))  # -int(n) pour que doc récent soit favorisé à égalité

    sorted_neighbors = sorted(neighbors, key=score, reverse=True)
    top_neighbors = sorted_neighbors[:k]

    return format_suggestions(top_neighbors, metadata, centrality)


def format_suggestions(doc_ids, metadata, centrality):
    result = []
    for d in doc_ids:
        meta = metadata.get(d, {}) if metadata else {}
        title = meta.get("title", f"Document #{d}")
        author = meta.get("author", "Unknown author")
        year = meta.get("year", None)
        downloads = meta.get("downloads", None)
        cent = centrality.get(d, None) if centrality else None
        result.append({
            "doc_id": d,
            "title": title,
            "author": author,
            "year": year,
            "downloads": downloads,
            "centrality": cent,
        })
    return result


def print_suggestions(doc_id, k=10):
    suggestions = get_suggestions(doc_id, k=k)
    if not suggestions:
        print("Aucune suggestion trouvée.")
        return

    print(f"\nSuggestions pour le document {doc_id} :\n")
    for i, s in enumerate(suggestions, start=1):
        year_str = f" ({s['year']})" if s["year"] else ""
        dl_str = f" | DL={s['downloads']}" if s["downloads"] is not None else ""
        c_str = f" | centrality={s['centrality']:.4f}" if s["centrality"] is not None else ""
        print(f"{i:2d}. Doc {s['doc_id']} | {s['title']}{year_str}")
        print(f"    {s['author']}{dl_str}{c_str}")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage : python3 suggest_books.py <doc_id> [k]")
        sys.exit(1)

    doc_id = sys.argv[1]
    k = 10
    if len(sys.argv) >= 3:
        try:
            k = int(sys.argv[2])
        except ValueError:
            pass

    print_suggestions(doc_id, k=k)


if __name__ == "__main__":
    main()
