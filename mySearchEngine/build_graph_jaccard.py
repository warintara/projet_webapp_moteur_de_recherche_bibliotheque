import os
import json
from collections import defaultdict
import argparse

# ---------- Chemins ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
INDEX_PATH = os.path.join(LIB_DIR, "index.json")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")
GRAPH_PATH = os.path.join(LIB_DIR, "graph.json")


def load_index():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"index.json introuvable : {INDEX_PATH}")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    return index


def load_doc_ids():
    """
    On peut soit les dériver depuis vocab.json (plus fiable),
    soit depuis index.json. On préfère vocab.json si présent.
    """
    if os.path.exists(VOCAB_PATH):
        with open(VOCAB_PATH, "r", encoding="utf-8") as f:
            vocab = json.load(f)
        return sorted(vocab.keys(), key=lambda x: int(x))
    else:
        # fallback: collecter depuis index.json
        index = load_index()
        doc_ids = set()
        for posting in index.values():
            doc_ids.update(posting.keys())
        return sorted(doc_ids, key=lambda x: int(x))


def compute_doc_lengths(index):
    """
    Calcule la longueur de chaque document:
      len(doc) = sum_w tf_doc(w)
    On l'obtient en parcourant l'index une seule fois.
    """
    doc_len = defaultdict(int)
    for word, posting in index.items():
        for doc_id, tf in posting.items():
            doc_len[doc_id] += int(tf)
    return doc_len


def build_jaccard_graph(index, theta=0.1):
    """
    Construit un graphe basé sur la similarité de Jaccard
    entre vecteurs de fréquences des docs.

    Pour chaque paire de docs (i,j) qui partagent au moins un mot:
      intersection(i,j) = Σ_w min(tf_i(w), tf_j(w))
      union(i,j) = len(i) + len(j) − intersection(i,j)
      sim(i,j) = intersection / union

    Si sim(i,j) >= theta → on ajoute l'arête (i,j).

    On ne parcourt PAS toutes les paires i,j (O(N^2)),
    on ne considère que les paires qui apparaissent ensemble
    dans le posting list d'au moins un mot.
    """
    print("Calcul des longueurs de documents...")
    doc_len = compute_doc_lengths(index)

    # intersections[(doc_i, doc_j)] = somme des min(tf_i, tf_j)
    intersections = defaultdict(float)

    print("Accumulation des intersections via les postings...")
    word_count = len(index)
    for wi, (word, posting) in enumerate(index.items(), start=1):
        # posting : {doc_id: tf}
        docs = list(posting.items())
        n = len(docs)
        if n < 2:
            # le mot n'apparaît que dans un seul doc, donc ne contribue pas
            # à l'intersection entre deux docs
            continue

        # pour chaque paire de docs contenant ce mot
        for i in range(n):
            di, tfi = docs[i]
            tfi = int(tfi)
            for j in range(i + 1, n):
                dj, tfj = docs[j]
                tfj = int(tfj)
                if di == dj:
                    continue
                # on stocke la clé triée pour éviter les doublons (i,j) et (j,i)
                if int(di) < int(dj):
                    key = (di, dj)
                else:
                    key = (dj, di)
                intersections[key] += min(tfi, tfj)

        if wi % 10000 == 0:
            print(f"  traité {wi}/{word_count} mots...")

    print("Nombre de paires de documents avec intersection > 0 :", len(intersections))

    # Construction du graphe
    graph = defaultdict(list)

    print(f"Construction du graphe avec seuil de similarité θ = {theta} ...")
    for (di, dj), inter in intersections.items():
        li = doc_len.get(di, 0)
        lj = doc_len.get(dj, 0)
        if li == 0 or lj == 0:
            continue

        union = li + lj - inter
        if union <= 0:
            continue

        sim = inter / union
        if sim >= theta:
            graph[di].append(dj)
            graph[dj].append(di)

    # enlever les doublons et trier les voisins
    graph_clean = {doc: sorted(set(neighbors), key=lambda x: int(x))
                   for doc, neighbors in graph.items()}

    return graph_clean


def main():
    parser = argparse.ArgumentParser(
        description="Construire le graphe de similarité (Jaccard) entre documents."
    )
    parser.add_argument(
        "--theta",
        type=float,
        default=0.1,
        help="Seuil de similarité Jaccard pour créer une arête (par défaut: 0.1)."
    )
    args = parser.parse_args()
    theta = args.theta

    print("Chargement de l'index inversé...")
    index = load_index()
    print(f"Index chargé avec {len(index)} mots.")

    print("Construction du graphe Jaccard...")
    graph = build_jaccard_graph(index, theta=theta)
    print(f"Graphe construit avec {len(graph)} sommets (docs ayant au moins un voisin).")

    print(f"Sauvegarde dans {GRAPH_PATH} ...")
    os.makedirs(LIB_DIR, exist_ok=True)
    with open(GRAPH_PATH, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print("Terminé !")


if __name__ == "__main__":
    main()
