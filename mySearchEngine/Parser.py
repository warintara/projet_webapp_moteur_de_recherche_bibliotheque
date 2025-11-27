from typing import List
CONCAT = 0xC04CA7
STAR   = 0xE7011E
PLUS   = 0xADD17
ALT    = 0xA17E54
PROT   = 0xBADDAD
DOT    = 0xD07
LPAR   = 0x16641664
RPAR   = 0x51515151

class RegExTree:
    root: int
    subs: List["RegExTree"]

    def __init__(self, root: int, subs: List["RegExTree"] = None):
        self.root = root
        self.subs = subs if subs is not None else []

    def __str__(self):
        # pour debug : affiche l'arbre en style textuel
        if not self.subs:
            return root_to_string(self.root)
        return f"{root_to_string(self.root)}(" + ",".join(str(s) for s in self.subs) + ")"


def root_to_string(root: int) -> str:
    if root == CONCAT: return "."
    if root == STAR:   return "*"
    if root == PLUS:   return "+"
    if root == ALT:    return "|"
    if root == DOT:    return "."
    if root == PROT:   return "PROT"
    return chr(root)

def char_to_root(c: str) -> int:
    if c == ".": return DOT
    if c == "*": return STAR
    if c == "+": return PLUS
    if c == "|": return ALT
    if c == "(": return LPAR
    if c == ")": return RPAR
    return ord(c)

def parse(regex: str) -> RegExTree:
    token_list = [RegExTree(char_to_root(c), []) for c in regex]
    return parse_tokens(token_list)

def parse_tokens(token_list: List[RegExTree]) -> RegExTree:
    while contain_par(token_list):
        token_list = process_par(token_list)

    while contain_star(token_list):
        token_list = process_star(token_list)

    while contain_plus(token_list):
        token_list = process_plus(token_list)

    while contain_cont(token_list):
        token_list = process_cont(token_list)

    while contain_alt(token_list):
        token_list = process_alt(token_list)

    if len(token_list) != 1:
        return RegExTree(PROT, token_list)
    return remove_prot(token_list[0])

def remove_prot(token : RegExTree) -> RegExTree:
    if not token.subs: return token
    if token.root == PROT: return remove_prot(token.subs[0])
    return RegExTree(token.root,[remove_prot(x) for x in token.subs])

# -------------- Traitement des parenthèses --------------
def contain_par(token_list: List[RegExTree]) -> bool:
    return any(token.root == LPAR or token.root == RPAR for token in token_list)

def process_par(token_list: List[RegExTree]) -> List[RegExTree]:
    right_par = next(i for i, token in enumerate(token_list) if token.root == RPAR)
    left_par = max(j for j in range(right_par) if token_list[j].root == LPAR)
    sub = parse_tokens(token_list[left_par + 1: right_par])
    return token_list[:left_par] + [RegExTree(PROT, [sub])] + token_list[right_par + 1:]

# -------------- Traitement des concatenations --------------
def contain_cont(token_list: List[RegExTree]) -> bool:
    for i in range(len(token_list) - 1):
        if token_list[i].root != ALT and token_list[i+1].root != ALT:
            return True
    return False


def process_cont(token_list: List[RegExTree]) -> List[RegExTree]:
    out = []
    changed = False
    i = 0
    while i < len(token_list):
        if i+1 < len(token_list) and token_list[i].root != ALT and token_list[i+1].root != ALT:
            out.append(RegExTree(CONCAT, [token_list[i], token_list[i+1]]))
            changed = True
            i += 2
        else:
            out.append(token_list[i])
            i += 1
    return out if changed else token_list

# -------------- Traitement des concatenations --------------
def contain_star(token_list : List[RegExTree]) -> bool:
    return any(token.root == STAR and not token.subs for token in token_list)

def process_star(token_list : List[RegExTree]) -> List[RegExTree]:
    out = []
    found = False
    for token in token_list:
        if not found and token.root == STAR and not token.subs:
            if not out: raise SyntaxError("Star without a previous token")
            found = True
            out[-1] = RegExTree(STAR, [out[-1]])
        else:
            out.append(token)
    return out

# -------------- Traitement des opérations PLUS -------------- ( à faire)
def contain_plus(token_list : List[RegExTree]) -> bool:
    return any(token.root == PLUS and not token.subs for token in token_list)

def process_plus(token_list : List[RegExTree]) -> List[RegExTree]:
    out = []
    found = False
    for token in token_list:
        if not found and token.root == PLUS and not token.subs:
            if not out: raise SyntaxError("PLUS without a previous token")
            found = True
            out[-1] = RegExTree(PLUS, [out[-1]])
        else:
            out.append(token)
    return out


# -------------- Traitement des alternatives --------------
def contain_alt(token_list : List[RegExTree]) -> bool:
    return any(token.root == ALT and not token.subs for token in token_list)

def process_alt(token_list: List[RegExTree]) -> List[RegExTree]:
    out = []
    found = False
    left = None
    for token in token_list:
        if not found and token.root == ALT and not token.subs:
            if not out:
                raise SyntaxError("Alt without a previous token")
            found = True
            left = out.pop()
        elif found:
            out.append(RegExTree(ALT, [left, token]))
            found = False
            left = None
        else:
            out.append(token)
    return out

# --------- TESTS ----------
if __name__ == "__main__":
    tests = [
        # (1) Parenthèses
        "(a(bc))",
        "(((x)))",

        # (2) Concat implicite
        "(a)(b)",
        "a(b)c",
        "a.c",

        # (3) Étoile
        "a*",
        "(ab)*",
        "(ab)*c",
        "a*b",

        # (4) Alternation
        "a|b",
        "(ab)|c",
        "a|(bc)*",
        "(a|b)c",
        "(a|b)*",
        "a|b|c",
        "a|(b|c)d",
        "(a|b)|(c|d)",

        # (5) Plus
        "ba+",
        "(ba)+"
    ]

    for r in tests:
        print("REGEX:", r)
        try:
            print("TREE :", parse(r))
        except Exception as e:
            print("ERROR:", e)
        print("-" * 40)
