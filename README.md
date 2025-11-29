# Projet DAAR 2025 — Moteur de recherche (mySearchEngine)

## Installation et environnement

Ce projet utilise **Django + Django REST Framework** pour le backend,  
et un environnement virtuel Python pour isoler les dépendances.

### 1. Créer un environnement virtuel
```bash
python3 -m venv myDAARenv
source myDAARenv/bin/activate
pip install -r requirements.txt
```
### 2. Entrer dans l'environnement 
```bash
source myDAARenv/bin/activate
```
### 3. Lancer le serveur 
```bash
cd mySearchEngine/
python3 manage.py runserver
```
### 4. Constructions des index, metadata et graph de Jaccard si c'est pas déjà fait
```bash
cd mySearchEngine
python3 buid_index2.py
python3 buid_metadata2.py
pyhton3 build_graph_jaccard
```

## Le schéma général
```
         ┌───────────────────────┐
         │      1664 livres      │
         └─────────┬─────────────┘
                   │ construire
                   ▼
         ┌───────────────────────┐
         │         INDEX         │
         │ mot → {livres, k}     │
         └─────────┬─────────────┘
              l’utilisateur tape
                   │
                   ▼
     ┌──────────────────────────────┐
     │   Détecter : simple ou regex │
     └──────────────┬───────────────┘
                    │
       simple       │        regex
       (mot)        │     (expression)
                    ▼
         ┌───────────────────────┐
         │   Chercher dans index │
         │   → obtenir candidats │
         └─────────┬─────────────┘
                   │
                   ▼
         ┌───────────────────────┐
         │ Appliquer ALGOS       │
         │ KMP ou Aho–Ullman     │
         │ MAIS uniquement sur   │
         │ les candidats         │
         └─────────┬─────────────┘
                   │
                   ▼
         ┌───────────────────────┐
         │ Classement + Jaccard  │
         └─────────┬─────────────┘
                   │
                   ▼
         ┌────────────────────────┐
         │ Résultats + suggestions│
         └────────────────────────┘
```

# Tests du Projet DAAR – Moteur de Recherche

Ce dossier contient l'ensemble des scripts permettant de tester notre application web
de moteur de recherche de bibliothèque (Projet 3 – DAAR).

Les tests sont organisés selon trois catégories :

---

## 1. Tests fonctionnels

Scripts :

- `test_search_basic.py`  
  → Vérifie la recherche simple par mot-clé.

- `test_search_regex.py`  
  → Vérifie la recherche avancée via expressions régulières.

- `test_ranking_centrality.py`  
  → Vérifie la cohérence du classement par centralité (Pagerank ou autre).

---

## 2. Tests de performance

Scripts :

- `test_performance_search.py`  
  → Mesure le temps de la recherche simple.

- `test_performance_regex.py`  
  → Mesure les temps de réponse pour les recherches RegEx.

- `test_performance_centrality.py`  
  → Mesure le temps de calcul de l'indice de centralité.

---

## 3. Utilitaires

- `utils.py`  
  → Contient les fonctions communes : appel API, mesure de temps, URL du backend.

---

## ▶ Exécution des tests

### Option 1 — Lancer un test spécifique  
```bash
python3 test_search_basic.py
```
### Option 2 — Lancer tous les tests automatiquement
```bash
python3 run_all_tests.py
```