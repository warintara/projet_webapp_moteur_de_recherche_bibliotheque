# DAAR | Projet 1 : Clone de egrep 

**Auteurs :** Selma BELKADI  | Warintara MUNSUP <br>

**Langage :** Python 3 <br>

## Comment compiler et exécuter : 

### 1 Lancer le programme

La commande générale est :

```bash
python3 egrep.py <option> <RegEx> <fichier>
```
option : <br>
      1 → lancer seulement egrep Python <br>
      2 → lancer egrep Python + grep -E (comparaison)
    
RegEx : expression régulière textuelle <br>
fichier : le texte dans lequel la recherche de motif s'effectue
 
### 2 exemple d'utilisation 
1. egrep Python seul
    ```bash
    python3 egrep.py 1 "sargon" 56667-0.txt
    ```
2. Comparaison egrep Python vs grep -E
    ```bash
    python3 egrep.py 2 "S(a|g|r)+on" 56667-0.txt
    ````

## Tests unitaires intégrés
Chaque module Python (KMP.py, DFA.py, NFA.py, Parser.py, matching.py) contient un petit test interne permettant de vérifier son bon fonctionnement individuellement.

Pour lancer le test d’un module, exécutez simplement le fichier correspondant :
```bash
python3 KMP.py
python3 DFA.py
python3 NFA.py
python3 Parser.py
python3 matching.py

```

## Supprime les fichiers __pycache__ locaux

Exécute :
```bash
rm -rf __pycache__/
```