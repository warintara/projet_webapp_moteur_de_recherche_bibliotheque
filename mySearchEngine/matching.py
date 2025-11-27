from DFA import *
from NFA import NFA, EPS, regex_to_nfa

from colorama import Fore, Style, init
init(autoreset=True)

def match_dfa_in_file(dfa, filepath):
    found = False
    with open(filepath, 'r') as f:
        line_no = 0
        while True:
            line = f.readline()
            if not line:
                break
            line_no += 1
            line = line.rstrip('\n')
            for start in range(len(line)):
                state = dfa.start
                i = start
                while i < len(line) and state in dfa.transitions and ord(line[i]) in dfa.transitions[state]:
                    state = dfa.transitions[state][ord(line[i])]
                    if state in dfa.final_states:
                        found = True
                        colored_line = (
                            line[:start] +
                            Fore.RED + line[start:i+1] + Style.RESET_ALL +
                            line[i+1:]
                        )
                        print(f"Match found: line {line_no}, column {start+1}, text '{line[start:i+1]}', full line: {colored_line}")
                    i += 1
    return found


def test_regex_on_file(pattern, filename):
    nfa = regex_to_nfa(pattern)
    # print(nfa)
    # print("\n===== DFA AVANT MINIMISATION =====")
    dfa = nfa_to_dfa(nfa)
    #print(dfa)
    min_dfa = minimize_dfa_hopcroft(dfa)
    #print("\n===== DFA APRÈS MINIMISATION =====")
    #print(min_dfa)
    found = match_dfa_in_file(min_dfa, filename)
    if found:
        print(f"[translate:{pattern}] a été trouvé dans le fichier.")
    else:
        print(f"[translate:{pattern}] n'a pas été trouvé dans le fichier.")
    return found

def test_regex_no_minimisation(pattern, filename):
    nfa = regex_to_nfa(pattern)
    # print(nfa)
    dfa = nfa_to_dfa(nfa)
    #print(dfa)
    found = match_dfa_in_file(dfa, filename)
    if found:
        print(f"[translate:{pattern}] a été trouvé dans le fichier.")
    else:
        print(f"[translate:{pattern}] n'a pas été trouvé dans le fichier.")
    return found




# --------- TESTS ----------
if __name__ == "__main__":
    # Exemple d'utilisation :
    print("--------------------test 1 : S(a|g|r)+on --------------------------------")
    test_regex_on_file("S(a|g|r)+on", "56667-0.txt")
    print("--------------------test 2 : yikes --------------------------------")
    test_regex_on_file("yikes", "56667-0.txt")

