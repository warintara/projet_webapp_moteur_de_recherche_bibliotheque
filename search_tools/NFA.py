from typing import Dict, Set, Optional
from Parser import RegExTree, parse, DOT, CONCAT, STAR, ALT, PLUS
EPS = None     # epsilon
ANY = DOT      # Any character

class NFA:
    def __init__(self):
        self.start      = -1
        self.end        = -1
        self.transitions : Dict[int, Dict[Optional[int], Set[int]]] = {}
        self.count_id = 0

    def __str__(self):
        lines = []
        lines.append("==========    NFA     ==========")
        lines.append(f"start: {self.start}")
        lines.append(f"end: {self.end}")
        lines.append("transitions:")
        for state, transitions in self.transitions.items():
            for code, next_states in transitions.items():
                if code == EPS:
                    label = "ε"
                elif code == ANY:
                    label = "."
                else:
                    label = chr(code)
                lines.append(f"  {state} -'{label}'-> {sorted(next_states)}")
        return "\n".join(lines)

    def next_id(self) -> int:
        id = self.count_id
        self.count_id += 1
        return id

    def add_transition(self, state: int, char: Optional[str], next_state: int):
        if state not in self.transitions:
            self.transitions[state] = {}
        if isinstance(char, str):
            key = ord(char)
        elif isinstance(char, int):
            key = char
        else:
            key = EPS
        if key not in self.transitions[state]:
            self.transitions[state][key] = set()
        self.transitions[state][key].add(next_state)

    def add_epsilon(self, start: int, end: int):
        self.add_transition(start, EPS, end)

def build_from_regex_tree(tree: RegExTree) -> NFA:
    nfa = NFA()

    def build_from_node(node: RegExTree):
        # Cas 1 : une lettre simple
        if not node.subs:
            s = nfa.next_id()
            t = nfa.next_id()
            nfa.add_transition(s, node.root, t)
            return s, t

        # Cas 2 : une concaténation
        if node.root == CONCAT:
            s1, t1 = build_from_node(node.subs[0])
            s2, t2 = build_from_node(node.subs[1])
            nfa.add_epsilon(t1, s2)
            return s1, t2

        # Cas 3 : une étoile
        if node.root == STAR:
            s1, t1 = build_from_node(node.subs[0])
            start, end = nfa.next_id(), nfa.next_id()
            nfa.add_epsilon(start, s1)
            nfa.add_epsilon(start, end)
            nfa.add_epsilon(t1, s1)
            nfa.add_epsilon(t1, end)
            return start, end
        
        # Cas 3 : un plus supposely R+ equals R⋅R∗
        if node.root == PLUS:
            s1, t1 = build_from_node(node.subs[0])
            start, end = nfa.next_id(), nfa.next_id()
            nfa.add_epsilon(start, s1)
            nfa.add_epsilon(t1, s1)
            nfa.add_epsilon(t1, end)
            return start, end

        # Cas 4 : une alternative
        if node.root == ALT:
            s1, t1 = build_from_node(node.subs[0])
            s2, t2 = build_from_node(node.subs[1])
            start, end = nfa.next_id(), nfa.next_id()
            nfa.add_epsilon(start, s1)
            nfa.add_epsilon(start, s2)
            nfa.add_epsilon(t1, end)
            nfa.add_epsilon(t2, end)
            return start, end

    s, t = build_from_node(tree)
    nfa.start, nfa.end = s, t
    return nfa

def tree_to_nfa(tree: RegExTree) -> NFA:
    return build_from_regex_tree(tree)

def regex_to_nfa(regex: str) -> NFA:
    tree = parse(regex)
    return build_from_regex_tree(tree)

# --------- TESTS ----------
if __name__ == "__main__":
    nfa = regex_to_nfa("(a|b)*c")
    print(nfa)
