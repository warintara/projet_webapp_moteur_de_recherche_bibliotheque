from typing import Dict, Set, Optional, Iterable, Tuple, List, FrozenSet
from Parser import DOT
from NFA import NFA, EPS, regex_to_nfa

class DFA:
    def __init__(self):
        self.start = None
        self.final_states: Set[int] = set()
        self.transitions: Dict[int, Dict[int, int]] = {}

    def add_transition(self, state: int, symbol: int, next_state: int):
        if state not in self.transitions:
            self.transitions[state] = {}
        self.transitions[state][symbol] = next_state

    def __str__(self):
        out = ["========== DFA =========="]
        out.append(f"start: {self.start}")
        out.append(f"finals: {sorted(self.final_states)}")
        out.append("transitions:")
        for s, trans in sorted(self.transitions.items()):
            for sym, dest in sorted(trans.items()):
                ch = '.' if sym == DOT else chr(sym)
                out.append(f"  {s} -'{ch}'-> {dest}")
        return "\n".join(out)

def epsilon_closure(nfa, states):
    closure = set(states)
    to_visit = list(states)
    while to_visit:
        state = to_visit.pop()
        for next_state in nfa.transitions.get(state, {}).get(EPS, []):
            if next_state not in closure:
                closure.add(next_state)
                to_visit.append(next_state)
    return closure

def move(nfa, states, symbol):
    dest = set()
    for s in states:
        trans = nfa.transitions.get(s, {})
        if symbol in trans:
            dest.update(trans[symbol])
        if DOT in trans:
            dest.update(trans[DOT])
    return dest

def extract_symbols_nfa(nfa):
    symbols = set()
    for trans in nfa.transitions.values():
        for sym in trans.keys():
            if sym is not EPS:
                symbols.add(sym)
    return symbols

def nfa_to_dfa(nfa: NFA) -> DFA:
    dfa = DFA()
    alpha = extract_symbols_nfa(nfa)

    start_set = frozenset(epsilon_closure(nfa, {nfa.start}))
    set_id: Dict[frozenset, int] = {start_set: 0}
    id_set: List[frozenset] = [start_set]
    dfa.start = 0

    if nfa.end in start_set:
        dfa.final_states.add(0)

    work: List[int] = [0]

    while work:
        cur_id = work.pop()
        cur_set = id_set[cur_id]

        for sym in alpha:
            if sym == EPS:
                continue
            dest_raw = move(nfa, cur_set, sym)
            if not dest_raw:
                continue
            dest_set = frozenset(epsilon_closure(nfa, dest_raw))

            if dest_set not in set_id:
                new_id = len(id_set)
                set_id[dest_set] = new_id
                id_set.append(dest_set)
                work.append(new_id)
                if nfa.end in dest_set:
                    dfa.final_states.add(new_id)

            dfa.add_transition(cur_id, sym, set_id[dest_set])
    return dfa

def extract_symbols_dfa(dfa: DFA):
    symbols = set()
    for trans in dfa.transitions.values():
        for sym in trans.keys():
            symbols.add(sym)
    return symbols

def dfa_states(dfa: DFA):
    states = set(dfa.transitions.keys())
    for trans in dfa.transitions.values():
        states.update(trans.values())
    states.add(dfa.start)
    states.update(dfa.final_states)
    return states

def minimize_dfa_hopcroft(dfa: DFA) -> DFA:
    all_states = dfa_states(dfa)
    alphabet = extract_symbols_dfa(dfa)

    final_states = dfa.final_states
    non_final_states = all_states - final_states

    partitions: List[FrozenSet[int]] = []

    if final_states:
        partitions.append(frozenset(final_states))
    if non_final_states:
        partitions.append(frozenset(non_final_states))

    worklist: Set[Tuple[FrozenSet[int], int]] = set()

    if partitions:
        smallest_group = min(partitions, key = len )
        for symbol in alphabet:
            worklist.add((smallest_group, symbol))

    while worklist:
        current_group, symbol = worklist.pop()

        predecessors = set()
        for state, transitions in dfa.transitions.items():
            if transitions.get(symbol) in current_group:
                predecessors.add(state)

        new_partitions: List[FrozenSet[int]] = []

        for group in partitions:
            intersect = frozenset(group & predecessors)
            difference = frozenset(group - predecessors)

            if intersect and difference:
                new_partitions.extend([intersect, difference])

                for sym in alphabet:
                    if (group, sym) in worklist:
                        worklist.remove((group, sym))
                        worklist.add((intersect, sym))
                        worklist.add((difference, sym))
                    else:
                        smaller = intersect if len(intersect) <= len(difference) else difference
                        worklist.add((smaller, sym))
            else:
                new_partitions.append(group)

        partitions = new_partitions

    minimized_dfa = DFA()

    state_to_group_id: Dict[int, int] = {}
    for group_id, group in enumerate(partitions):
        for state in group:
            state_to_group_id[state] = group_id

    if dfa.start is not None:
        minimized_dfa.start = state_to_group_id[dfa.start]

    for state in final_states:
        minimized_dfa.final_states.add(state_to_group_id[state])

    for state, transitions in dfa.transitions.items():
        for symbol, next_state in transitions.items():
            minimized_dfa.add_transition(
                state_to_group_id[state],
                symbol,
                state_to_group_id[next_state]
            )

    return minimized_dfa


if __name__ == "__main__":
    # --- Exemple simple ---
    # Alphabet : { 'a', 'b' }
    # DFA non minimal (4 états) :
    #
    # start = 0
    # finals = {2, 3}
    #
    # 0 -a-> 1   0 -b-> 1
    # 1 -a-> 2   1 -b-> 3
    # 2 -a-> 2   2 -b-> 3
    # 3 -a-> 2   3 -b-> 3
    #
    # 2 et 3 ont le même comportement de finaux => ils vont être fusionnés.

    dfa = DFA()
    dfa.start = 0
    dfa.final_states = {2, 3}

    dfa.add_transition(0, ord('a'), 1)
    dfa.add_transition(0, ord('b'), 1)

    dfa.add_transition(1, ord('a'), 2)
    dfa.add_transition(1, ord('b'), 3)

    dfa.add_transition(2, ord('a'), 2)
    dfa.add_transition(2, ord('b'), 3)

    dfa.add_transition(3, ord('a'), 2)
    dfa.add_transition(3, ord('b'), 3)

    print("===== DFA AVANT MINIMISATION =====")
    print(dfa)

    min_dfa = minimize_dfa_hopcroft(dfa)
    print("\n===== DFA APRÈS MINIMISATION =====")
    print(min_dfa)


