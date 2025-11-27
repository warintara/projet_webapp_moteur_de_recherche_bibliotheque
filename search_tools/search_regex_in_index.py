import os
import json
import sys
from collections import defaultdict

from NFA import regex_to_nfa          # ton code Aho–Ullman NFA :contentReference[oaicite:1]{index=1}
from DFA import nfa_to_dfa, minimize_dfa_hopcroft, DFA  # ton code DFA + minimisation :contentReference[oaicite:2]{index=2}
from Parser import DOT                # pour le symbole '.' (joker) :contentReference[oaicite:3]{index=3}

# ========= Chemins =========

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(BASE_DIR, "library")
INDEX_PATH = os.path.join(LIB_DIR, "index.json")
VOCAB_PATH = os.path.join(LIB_DIR, "vocab.json")


# ========= Construction DFA à partir de la RegEx =========

def build_dfa_from_regex(pattern: str) -> DFA:
    """
    Compile une RegEx en DFA minimal en utilisant TON pipeline Aho–Ullman :
      RegEx -> NFA (Thompson) -> DFA (subset) -> DFA minimal (Hopcroft).
    """
    nfa = regex_to_nfa(pattern)
    dfa = nfa_to_dfa(nfa)
    min_dfa = minimize_dfa_hopcroft(dfa)
    return min_dfa


# ========= Matching d'un MOT (clé de l'index) avec le DFA =========

def dfa_match_word(dfa: DFA, word: str) -> bool:
    """
    Teste si le DFA accepte un mot COMPLET (token de l'index).
    On suit les transitions du DFA caractère par caractère.
    On gère aussi le joker '.' via DOT.
    """
    state = dfa.start
    for ch in word:
        code = ord(ch)
        trans = dfa.transitions.get(state, {})

        if code in trans:            # transition exacte
            state = trans[code]
        elif DOT in trans:           # transition via joker '.'
            state = trans[DOT]
        else:
            return False

    return state in dfa.final_states


# ========= Chargement de l'index =========

def load_index_and_vocab():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"index.json introuvable : {INDEX_PATH}")
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)

    vocab = {}
    if os.path.exists(VOCAB_PATH):
        with open(VOCAB_PATH, "r", encoding="utf-8") as f:
            vocab = json.load(f)

    return index, vocab


# ========= Recherche RegEx sur l'INDEX =========

def search_regex(pattern: str, index: dict, top_k: int = 20):
    """
    Recherche avancée avec RegEx :
      1) Compile la RegEx en DFA (Aho–Ullman).
      2) Teste la RegEx sur chaque mot de l'index (clé de index.json).
      3) Récupère tous les documents qui contiennent au moins un mot qui matche.
      4) Score du doc = somme des fréquences de tous les mots matchés.
    """
    print(f"Compilation de la RegEx en DFA minimal : {pattern!r}")
    dfa = build_dfa_from_regex(pattern)

    matched_words = []
    doc_scores = defaultdict(int)

    for word, posting in index.items():
        if dfa_match_word(dfa, word):
            matched_words.append(word)
            for doc_id, count in posting.items():
                doc_scores[doc_id] += int(count)

    if not doc_scores:
        print("Aucun mot de l'index ne matche cette RegEx.")
        return [], matched_words

    ranked_docs = sorted(
        doc_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return ranked_docs[:top_k], matched_words


def pretty_print(pattern: str, results, matched_words, vocab):
    print("\n============================")
    print(f"RegEx : {pattern}")
    print("============================")

    print(f"\nMots de l'index qui matchent la RegEx ({len(matched_words)} trouvés) :")
    # on n'affiche que les 30 premiers pour ne pas exploser la console
    for w in matched_words[:30]:
        print("  -", w)
    if len(matched_words) > 30:
        print(f"  ... (+{len(matched_words) - 30} autres)")

    if not results:
        print("\nAucun document ne contient ces mots.")
        return

    print("\n=== Documents correspondants (top résultats) ===")
    for rank, (doc_id, score) in enumerate(results, start=1):
        vocab_size = len(vocab.get(doc_id, []))
        print(f"{rank:2d}. Doc {doc_id} | score={score} | vocab_size={vocab_size}")


# ========= CLI =========

def main():
    index, vocab = load_index_and_vocab()

    if len(sys.argv) > 1:
        pattern = " ".join(sys.argv[1:])
        results, matched_words = search_regex(pattern, index)
        pretty_print(pattern, results, matched_words, vocab)
    else:
        print("Mode interactif RegEx. Tape 'quit' pour sortir.")
        while True:
            try:
                pattern = input("\nRegEx > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break
            if not pattern:
                continue
            if pattern.lower() in {"quit", "exit"}:
                print("Bye.")
                break

            results, matched_words = search_regex(pattern, index)
            pretty_print(pattern, results, matched_words, vocab)


if __name__ == "__main__":
    main()
