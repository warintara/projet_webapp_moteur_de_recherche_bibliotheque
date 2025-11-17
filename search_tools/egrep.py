import sys
import time
import subprocess
from KMP import *
from DFA import *
from matching import *
from NFA import *
from Parser import *


def egrep(regEx, file):
    """
    Version Python de egrep :
    - Si l'expression est une concaténation simple => utilise KMP
    - Sinon => test via les automates (NFA/DFA)
    """
    if isitconcatenated(regEx):
        kmp = KMP(regEx)
        return kmp.search_in_file(file)
    else:
        # Test avec minimisation
        print("\n--- Test avec minimisation du DFA ---")
        start_min = time.perf_counter()
        found_min = test_regex_on_file(regEx, file)
        time_min = time.perf_counter() - start_min

        # Test sans minimisation
        print("\n--- Test sans minimisation du DFA ---")
        start_no_min = time.perf_counter()
        found_no_min = test_regex_no_minimisation(regEx, file)
        time_no_min = time.perf_counter() - start_no_min

        # Affichage comparatif
        print("\n===============================")
        print("Comparaison minimisation / non-minimisation :")
        print(f"→ Avec minimisation : {time_min:.6f} s ({'trouvé' if found_min else 'non trouvé'})")
        print(f"→ Sans minimisation : {time_no_min:.6f} s ({'trouvé' if found_no_min else 'non trouvé'})")
        print("===============================\n")

        return found_min or found_no_min, time_min, time_no_min


def test_real_egrep(regEx, file):
    """
    Lance le vrai 'grep -E' Linux et mesure son temps d'exécution.
    """
    start_time = time.perf_counter()
    proc = subprocess.run(
        ["grep", "-E", regEx, file],
        capture_output=True,
        text=True
    )
    elapsed = time.perf_counter() - start_time

    if proc.stdout.strip():
        print("\n--- Résultats grep -E (système) ---")
        print(proc.stdout.strip())
        print("\nRésultat : trouvé")
    else:
        print("\nRésultat : non trouvé")

    print(f"\nTemps d'exécution (grep -E) : {elapsed:.6f} secondes\n")
    return bool(proc.stdout.strip()), elapsed


def run_python_egrep(regEx, filepath):
    """
    Lance la version Python seule et mesure les temps avec/sans minimisation.
    """
    start_time = time.perf_counter()
    result = egrep(regEx, filepath)
    elapsed_total = time.perf_counter() - start_time

    print("\n--- Résultats egrep (Python) ---")
    if isinstance(result, tuple):
        found, time_min, time_no_min = result
    else:
        # Cas KMP
        found = result
        time_min = time_no_min = None

    if found:
        print("\nMatching: True (au moins une occurrence trouvée)")
    else:
        print("\nMatching: False (aucune occurrence trouvée)")

    # Affichage temps détaillés
    if time_min is not None and time_no_min is not None:
        print("\n===============================")
        print("Comparaison des temps d'exécution egrep (Python) :")
        print(f"→ Avec minimisation : {time_min:.6f} s")
        print(f"→ Sans minimisation : {time_no_min:.6f} s")
        print("===============================")
    else:
        print(f"\nTemps d'exécution (KMP) : {elapsed_total:.6f} secondes")

    return found, (time_min, time_no_min)


if __name__ == "__main__":
    """
    Utilisation :
      python3 egrep.py <option> <RegEx> <file>

    <option> :
      1 → lancer seulement egrep Python
      2 → lancer egrep Python + grep -E (comparaison)

    Exemples :
      python3 egrep.py 1 "S(a|g|r)+on" 56667-0.txt
      python3 egrep.py 2 "Sargon" 56667-0.txt
    """
    if len(sys.argv) != 4:
        print("Usage: python3 egrep.py <option> <RegEx> <file>")
        print("  <option> : 1 = egrep Python seul, 2 = comparaison avec grep -E")
        sys.exit(1)

    try:
        option = int(sys.argv[1])
    except ValueError:
        print("Erreur : l'option doit être 1 ou 2.")
        sys.exit(1)

    regEx = sys.argv[2]
    filepath = sys.argv[3]

    try:
        if option == 1:
            run_python_egrep(regEx, filepath)

        elif option == 2:
            found, (time_min, time_no_min) = run_python_egrep(regEx, filepath)
            print("\n===============================")
            print("Comparaison avec grep -E :")
            _, time_sys = test_real_egrep(regEx, filepath)
            print("===============================")
            if time_min is not None and time_no_min is not None:
                print(f"→ Temps egrep (Python) avec minimisation : {time_min:.6f} s")
                print(f"→ Temps egrep (Python) sans minimisation : {time_no_min:.6f} s")
            print(f"→ Temps grep -E (système) : {time_sys:.6f} s\n")

        else:
            print("Erreur : option invalide. Choisis 1 ou 2.")
            sys.exit(1)

    except FileNotFoundError:
        print(f"Erreur : fichier '{filepath}' introuvable.")
    except Exception as e:
        print(f"Erreur : {e}")
