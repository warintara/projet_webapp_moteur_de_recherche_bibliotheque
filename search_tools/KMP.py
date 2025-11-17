from typing import List
from Parser import STAR, PLUS, ALT, PROT, DOT, LPAR, RPAR
from colorama import Fore, Style, init
init(autoreset=True)


class KMP:
    def __init__(self, RegEx: str):
        self.factor = list(RegEx)
        self.CarryOver = self.step1()
        self.step2()
        self.step3()

    
    def __str__(self):
        lines = ["RegEx: " + "".join(self.factor), "CarryOver: " + str(self.CarryOver)]
        return "\n".join(lines)

    def step1(self) -> List[int]:
        """Compute the CarryOver (prefix-suffix) table"""
        co = [-1] * len(self.factor)
        for i in range(1, len(self.factor)):
            k = co[i - 1]
            while k != -1 and self.factor[k + 1] != self.factor[i]:
                k = co[k]
            if self.factor[k + 1] == self.factor[i]:
                co[i] = k + 1
            else:
                co[i] = -1
        return co
    
    def step2(self):
        """Optimisation for a particular carry over case."""
        for i in range(len(self.factor)):
            if self.factor[i] == self.factor[self.CarryOver[i]]:
                self.CarryOver[self.CarryOver[i]] = -1

    def step3(self):
        """Optimisation for transitions using carry over."""
        for i in range(len(self.factor)):
            if (self.factor[i] == self.factor[self.CarryOver[i]] and 
                self.CarryOver[self.CarryOver[i]] != -1 and
                self.CarryOver[self.CarryOver[i]] != 0):
                self.CarryOver[i] = self.CarryOver[self.CarryOver[i]]

    def search_in_line(self, text: str, line_no : int) -> bool:
        """Search for pattern occurrences in text using KMP."""
        found = False
        m, n = len(self.factor), len(text)
        j = 0  

        for i in range(n):
            while j > 0 and text[i] != self.factor[j]:
                j = self.CarryOver[j - 1] + 1 if self.CarryOver[j - 1] != -1 else 0
            if text[i] == self.factor[j]:
                j += 1
            if j == m:
                found = True
                start = i - m + 1
                end = i + 1
                # Affichage coloré comme dans match_dfa_in_file
                colored_line = (
                    text[:start]
                    + Fore.RED + text[start:end] + Style.RESET_ALL
                    + text[end:]
                )
                print(f"Match found: line {line_no}, column {start+1}, text '{text[start:end]}', full line: {colored_line}")
                j = self.CarryOver[j - 1] + 1 if self.CarryOver[j - 1] != -1 else 0

        return found
    def search_in_file(self, filepath: str) -> bool:
        """Search for pattern occurrences in an entire file."""
        found_any = False
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            line_no = 0
            for line in f:
                line_no += 1
                line = line.rstrip('\n')
                if self.search_in_line(line, line_no):
                    found_any = True
        return found_any

def isitconcatenated(regEx):
    specials = {'*', '+', '|', '.', '(', ')'}
    for c in regEx:
        if c in specials:
            return False
    return True

# --------- TESTS ----------
if __name__ == "__main__":
    # Test KMP pour regex "mami" dans le texte donné
    text = "maman mamé mia ! mm maaah mami!"
    pattern = "mami"
    kmp = KMP(pattern)
    resultats = kmp.search_in_line(text,0)
    print("Positions du motif trouvé :", resultats)
    print("is abcd concatenated? :", isitconcatenated("abcd"))
    print("is (ab)+(cd) concatenated? :", isitconcatenated("(ab)+(cd)"))
    print("================== test 2 avec le fichier txt ======================")
    pattern2 = "Sargon"
    file_path2 = "56667-0.txt"  # remplace par ton fichier réel
    kmp2 = KMP(pattern2)
    found = kmp2.search_in_file(file_path2)
    print("Matching:", found)
