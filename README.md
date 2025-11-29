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

### 5. Tester les fonctions 
#### Pour app.py Depuis mySearchEngine :
```bash
uvicorn app:app --reload
```
on peut tester :

http://127.0.0.1:8000/search?q=dragon

http://127.0.0.1:8000/search_regex?pattern=dr.*n

http://127.0.0.1:8000/book/52

http://127.0.0.1:8000/suggest/52

ou partir sur le site à partir du fichier 
```
index.html
```