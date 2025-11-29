import os
import subprocess

print("\n============================")
print(" Lancement de TOUS les tests DAAR (automatique)")
print("============================\n")

# lister tous les fichiers test_*.py
tests = sorted([f for f in os.listdir('.') if f.startswith("test_") and f.endswith(".py")])

if not tests:
    print("Aucun fichier de test trouvé.")
    exit(1)

print(" Tests détectés :", tests)

for test in tests:
    print(f"\n---------------------------------------")
    print(f"Exécution du test : {test}")
    print("---------------------------------------\n")
    
    try:
        subprocess.run(["python3", test], check=False)
    except Exception as e:
        print(f" Erreur lors de l'exécution de {test} : {str(e)}")

print("\n============================")
print("   Tous les tests ont été exécutés")
print("============================\n")
