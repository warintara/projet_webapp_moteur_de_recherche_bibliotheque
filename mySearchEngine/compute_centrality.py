import os
import json
from collections import deque

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")

GRAPH_PATH = os.path.join(LIB_DIR, "graph.json")
CENTRALITY_PATH = os.path.join(LIB_DIR, "centrality.json")


def load_graph():
    if not os.path.exists(GRAPH_PATH):
        raise FileNotFoundError("graph.json introuvable.")
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def bfs_distances(graph, start):
    """
    BFS classique.
    Retourne la somme des distances de 'start' vers tous les autres nodes.
    """
    visited = {start: 0}
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for nei in graph.get(node, []):
            if nei not in visited:
                visited[nei] = visited[node] + 1
                queue.append(nei)

    # somme des distances (ignorer distance 0 vers soi-même)
    return sum(dist for node, dist in visited.items() if node != start)


def compute_closeness(graph):
    closeness = {}
    total_nodes = len(graph)

    print(f"Calcul de la centralité (closeness) pour {total_nodes} documents...")

    for i, node in enumerate(graph.keys(), start=1):
        S = bfs_distances(graph, node)
        if S > 0:
            closeness[node] = 1 / S
        else:
            closeness[node] = 0  # isolé

        if i % 100 == 0:
            print(f"  {i}/{total_nodes} nodes traités...")

    # normalisation (optionnel : rendre max = 1)
    max_c = max(closeness.values())
    if max_c > 0:
        for node in closeness:
            closeness[node] /= max_c

    return closeness


def main():
    print("Chargement du graphe...")
    graph = load_graph()

    print("Calcul de la centralité...")
    closeness = compute_closeness(graph)

    print(f"Sauvegarde dans {CENTRALITY_PATH} ...")
    with open(CENTRALITY_PATH, "w", encoding="utf-8") as f:
        json.dump(closeness, f, indent=2)

    print("Top 10 des livres les plus centraux :")
    top10 = sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:10]
    for doc_id, score in top10:
        print(f"  Doc {doc_id} | score = {score:.4f}")

    print("Terminé !")


if __name__ == "__main__":
    main()
