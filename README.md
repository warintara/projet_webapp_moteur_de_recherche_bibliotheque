# Projet DAAR 2025 — Moteur de recherche (mySearchEngine)


## Installation et environnement

Ce projet utilise un backend Python et nécessite un environnement virtuel.
Le backend peut être exécuté de deux façons suivant ta version du projet :

soit via Django + Django REST Framework

soit via FastAPI (pour les tests et endpoints modernes)

Le README ci-dessous est harmonisé pour supporter les deux cas.

Création de l’environnement virtuel
python3 -m venv myDAARenv
source myDAARenv/bin/activate
pip install -r requirements.txt

Entrer dans l’environnement (si déjà créé)
source myDAARenv/bin/activate

Lancer le serveur backend

Cas 1 — Backend Django :
cd mySearchEngine
python3 manage.py runserver

Cas 2 — Backend FastAPI (recommandé pour les tests) :
uvicorn app:app --reload
Ton API sera alors disponible sur : http://127.0.0.1:8000

Construire les index, metadata et graphe de Jaccard
cd mySearchEngine
python3 build_index2.py
python3 build_metadata2.py
python3 build_graph_jaccard.py

(Assure-toi que ces scripts ont bien généré :

l’index des mots

les métadonnées (longueur, résumé, etc.)

le graphe de similarité Jaccard
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

Ce dossier contient l’ensemble des scripts permettant de tester l’application web du moteur de recherche (Projet DAAR 2025).
Les tests sont organisés selon trois catégories.

### Tests fonctionnels

Scripts :

test_search_basic.py
Vérifie la recherche simple par mot-clé via l’endpoint /search?q=mot.

test_search_regex.py
Vérifie la recherche avancée via expressions régulières avec /search_regex?pattern=regex.

test_ranking_centrality.py
Vérifie la cohérence du classement en utilisant les scores de centralité (exemple : Pagerank construit à partir du graphe de Jaccard).

test_suggestion.py
Test supplémentaire important.
Compare automatiquement :

la version CLI via : python3 suggest_books.py <id>

la version API FastAPI via : /suggest/<id>
Ce test permet de vérifier la cohérence et l’accuracy entre la logique interne (CLI) et la logique exposée via l’API.

### Tests de performance

Scripts :

test_performance_search.py
Mesure le temps d’exécution pour une recherche simple.

test_performance_regex.py
Mesure le temps de réponse aux recherches utilisant des expressions régulières.

test_performance_centrality.py
Mesure le temps de calcul de l’indice de centralité (ex : recalcul du Pagerank si exposé).

### Utilitaires

utils.py
Fichier central pour :

gérer l’adresse du backend (BASE_URL = http://127.0.0.1:8000

)

envoyer des requêtes API

mesurer le temps d’exécution

simplifier les appels dans les tests

### Exécution des tests

Option 1 : lancer un test spécifique
python3 test_search_basic.py

Option 2 : lancer automatiquement tous les tests
python3 run_all_tests.py

(run_all_tests.py détecte tous les fichiers commençant par test_*.py et les exécute un à un.)

### Tester l'application dans l’interface web

Pour tester manuellement les fonctionnalités :

Lancer le serveur FastAPI :
uvicorn app:app --reload

Aller sur les URLs suivantes :

Recherche simple :
http://127.0.0.1:8000/search?q=dragon

Recherche RegEx :
http://127.0.0.1:8000/search_regex?pattern=dr.*n
Affichage des détails d’un livre :
http://127.0.0.1:8000/book/52
Suggestions basées sur le graphe Jaccard :
http://127.0.0.1:8000/suggest/52

Interface web (frontend)
Ouvrir simplement le fichier index.html du dossier frontend dans un navigateur pour accéder à la webapp graphique.