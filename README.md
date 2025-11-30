# Projet DAAR 2025 — Moteur de recherche (mySearchEngine)


## Installation et environnement

Ce projet utilise un backend Python et nécessite un environnement virtuel.
Le backend est exécuté via FastAPI (pour les tests et endpoints modernes)

Le README ci-dessous est harmonisé pour supporter les deux cas.

Création de l’environnement virtuel
```bash
python3 -m venv myDAARenv
source myDAARenv/bin/activate
pip install -r requirements.txt
```

Entrer dans l’environnement (si déjà créé)
```bash
source myDAARenv/bin/activate
```
Lancer le serveur backend Backend FastAPI:
```
uvicorn app:app --reload
```
L'API sera alors disponible sur : http://127.0.0.1:8000

Construire les index, metadata et graphe de Jaccard
```bash
cd mySearchEngine
python3 build_index2.py
python3 build_metadata2.py
python3 build_graph_jaccard.py
```
(Assurez-vous que ces scripts ont bien généré :
-l’index des mots
-les métadonnées (longueur, résumé, etc.)
-le graphe de similarité Jaccard
avant de tester la recherche.)

## Le schéma général
```
       1664 livres
            │
     construire index
            ▼
  INDEX : mot → {livres, occurrences}
            │
  utilisateur tape une requête
            │
            ▼
   Détection simple ou regex
    │                     │
simple                 regex
    │                     │
    ▼                     ▼
 Chercher dans index → candidats
            │
            ▼
Appliquer les algorithmes KMP ou Aho-Ullman
(uniquement sur les candidats)
            │
            ▼
 Classement + centralité + Jaccard
            │
            ▼
 Résultats + suggestions associées

```
## Tests du Projet DAAR – Moteur de Recherche

Le dossier /tests contient l’ensemble des scripts permettant de tester l’application web du moteur de recherche (Projet DAAR 2025).

Avant de tester, il faut lancer : 
```bash
uvicorn app:app --reload
```
### Recherche simple
Script : test_search_basic.py
Compare :
       - Résultat CLI (search_in_index.py)
       - Résultat API (/search)
       - Cohérence des doc_id
       - Temps d’exécution (CLI / API / pagination)
→ Log dans perf_search.txt.
Exécution :
```bash
python3 test_search_basic.py
```
#### Recherche RegEx
Script : test_search_regex.py
Mesure :
       - CLI vs API (/search_regex)
       - Pagination
       - Différences éventuelles
       - Performances
→ Log dans perf_regex.txt.
Exécution :
```bash
python3 test_search_regex.py
```
#### Centralité
Script : test_centrality.py
Teste :
       - Lecture de centrality.json
       - Extraction du Top N
       - Temps moyen de chargement.
→ Log dans perf_centrality.txt.
Exécution :
```bash
python3 test_centrality.py
```
#### Suggestions (graphe de Jaccard)
Script : test_suggestion.py
Teste :
       - CLI vs API (/suggest/<id>)
       - Cohérence des doc_id
       - Temps API et CLI.
Exécution :
```bash
python3 test_suggestion.py
```
### Lancer tous les tests

Script : run_all_tests.py
Exécution :
```bash
python3 run_all_tests.py.py
```
Détecte et exécute automatiquement tous les fichiers test_*.py.


### Tests via l’interface Web
Avant de tester, il faut lancer : 
```bash
uvicorn app:app --reload
```
URLs utiles :

http://127.0.0.1:8000/search?q=mot

http://127.0.0.1:8000/search_regex?pattern=...

http://127.0.0.1:8000/book/<id>

http://127.0.0.1:8000/suggest/<id>

Pour tester Frontend : ouvrir frontend/index.html.
