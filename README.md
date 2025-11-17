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
### 4. Téléchargement les livres en anglais (si ce n'est pas déjà fait)
```bash
python3 download_gutenberg_fr.py
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