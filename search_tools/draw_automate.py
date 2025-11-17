from graphviz import Digraph

from Parser import DOT, parse
from NFA import regex_to_nfa, EPS
from DFA import nfa_to_dfa, minimize_dfa_hopcroft, DFA

def label_from_nfa_symbol(sym_key: int | None) -> str:
    if sym_key is EPS:
        return "ε"
    if sym_key == DOT:
        return "."
    return chr(sym_key)

def label_from_dfa_symbol(sym_key: int) -> str:
    return "." if sym_key == DOT else chr(sym_key)

def draw_nfa(nfa, filename: str = "nfa"):
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")
    dot.node("_start", label="", shape="point")  # flèche d'init

    nodes = {nfa.start, nfa.end}
    for s, outs in nfa.transitions.items():
        nodes.add(s)
        for dests in outs.values():
            nodes.update(dests)

    for s in sorted(nodes):
        shape = "doublecircle" if s == nfa.end else "circle"
        dot.node(str(s), shape=shape)

    dot.edge("_start", str(nfa.start))

    for s, outs in sorted(nfa.transitions.items()):
        for sym_key, dests in sorted(outs.items(), key=lambda kv: (kv[0] is not EPS, kv[0])):  # epsilon d'abord
            label = label_from_nfa_symbol(sym_key)
            for d in sorted(dests):
                dot.edge(str(s), str(d), label=label)

    out = dot.render(filename, cleanup=True)
    print(f"[OK] NFA -> {out}")

def draw_dfa(dfa: DFA, filename: str, title: str = ""):
    dot = Digraph(format="png")
    dot.attr(rankdir="LR")
    dot.attr("node", shape="circle")
    dot.node("_start", label="", shape="point")

    nodes = {dfa.start} | set(dfa.final_states)
    for s, outs in dfa.transitions.items():
        nodes.add(s)
        nodes.update(outs.values())

    for s in sorted(nodes):
        shape = "doublecircle" if s in dfa.final_states else "circle"
        dot.node(str(s), shape=shape)

    dot.edge("_start", str(dfa.start))

    for s, outs in sorted(dfa.transitions.items()):
        for sym_key, d in sorted(outs.items()):
            label = label_from_dfa_symbol(sym_key)
            dot.edge(str(s), str(d), label=label)

    if title:
        dot.attr(label=title, labelloc="t", fontsize="18")

    out = dot.render(filename, cleanup=True)
    print(f"[OK] DFA -> {out}")

if __name__ == "__main__":
    regex = "S(a|g|r)+on"

    # 1) Construire le NFA (Thompson)
    nfa = regex_to_nfa(regex)
    print(nfa)
    draw_nfa(nfa, "nfa")

    # 2) NFA -> DFA (subset construction)
    dfa_before = nfa_to_dfa(nfa)
    print("===== DFA AVANT MINIMISATION =====")
    print(dfa_before)
    draw_dfa(dfa_before, "dfa_before", title="DFA avant minimisation")

    # 3) Minimisation du DFA (Hopcroft)
    dfa_after = minimize_dfa_hopcroft(dfa_before)
    print("===== DFA APRÈS MINIMISATION =====")
    print(dfa_after)
    draw_dfa(dfa_after, "dfa_after", title="DFA après minimisation")
