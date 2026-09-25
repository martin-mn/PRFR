"""
latex2md.py -- convert the LaTeX of the paper's SI passages to GitHub Markdown with $...$ math (used by mknotes.py).

Handles exactly the constructs that occur in the passages: the paper's macros (\\ALLD, \\ALLC, \\WSLS, \\Grim,
\\TFTATFT, \\AON, \\Emax, \\eps, \\Methods), \\textbf, \\emph, \\texttt, {\\bf ...}, \\citep (numbered per file),
\\S\\ref and \\eqref (resolved with the label numbers of ms.aux), \\noindent, ~, --, `` '', \\[ \\], \\%, \\\\.
Anything else raises, so that nothing is dropped silently.
"""
import re

NAMES = {"ALLD": "*ALLD*", "ALLC": "*ALLC*", "WSLS": "*WSLS*", "Grim": "*Grim*", "TFTATFT": "*TFT-ATFT*",
         "TFT": "*TFT*", "GTFT": "*GTFT*", "AON": "*AON*$_2$"}
MATH_MACROS = {"eps": r"\epsilon", "Emax": r"E_{\max}", "R": r"\mathbb{R}"}
MATH_OK = set("""beta mu delta pi sigma tau times tfrac frac le ge to Delta varphi sum rho qquad cup in ll dots epsilon
max mathbb texttt cdot ne neq leq geq infty lim min log exp varnothing emptyset quad langle rangle mathrm operatorname
alpha gamma lambda nu omega phi psi theta xi zeta kappa eta chi Sigma Pi Omega Gamma Lambda Phi Psi Theta sqrt left
right big Big bigl bigr Bigl Bigr""".split())


class Converter:
    def __init__(self, labels, cite_order):
        self.labels = labels            # label -> number string ("7", "S9")
        self.cites = cite_order         # list, appended in order of first citation
        self.bold = 0                   # > 0 inside a bold group: Markdown cannot nest **...**

    # ---------------------------------------------------------------- helpers
    @staticmethod
    def group(s, i):
        """s[i] == '{': return (content, index after the matching '}')"""
        assert s[i] == "{", (s[i:i + 30])
        depth = 0
        for k in range(i, len(s)):
            if s[k] == "{":
                depth += 1
            elif s[k] == "}":
                depth -= 1
                if depth == 0:
                    return s[i + 1:k], k + 1
        raise ValueError("unbalanced braces: " + s[i:i + 60])

    def cite(self, keys):
        nums = []
        for k in keys.split(","):
            k = k.strip()
            if k.startswith("SI:"):
                k = k[3:]
            if k not in self.cites:
                self.cites.append(k)
            nums.append(self.cites.index(k) + 1)
        return "[" + ", ".join(str(n) for n in nums) + "]"

    def math(self, m):
        """the content of $...$ or \\[...\\]"""
        out, i = [], 0
        while i < len(m):
            c = m[i]
            if c == "\\":
                mm = re.match(r"\\([A-Za-z]+)", m[i:])
                if mm:
                    name = mm.group(1)
                    i += len(mm.group(0))
                    if name in MATH_MACROS:
                        out.append(MATH_MACROS[name])
                        if i < len(m) and m[i].isalpha():
                            out.append(" ")
                    elif name in NAMES:
                        out.append(r"\textit{%s}" % NAMES[name].strip("*").replace("*$_2$", ""))
                        if i + 1 < len(m) and m[i:i + 2] == "{}":
                            i += 2
                    elif name in MATH_OK:
                        out.append("\\" + name)
                    else:
                        raise ValueError("unknown math macro \\%s in %r" % (name, m))
                    continue
                out.append(m[i:i + 2]); i += 2          # \, \; \% \{ \} \\
                continue
            out.append(c); i += 1
        return "".join(out)

    # ---------------------------------------------------------------- text
    def text(self, s):
        out, i = [], 0
        n = len(s)
        while i < n:
            c = s[i]
            if c == "$":
                j = s.index("$", i + 1)
                body = s[i + 1:j]
                if re.fullmatch(r"-?[0-9]+(\.[0-9]+)?", body):
                    out.append(body.replace("-", "−"))
                elif re.fullmatch(r"[0-9]+(\.[0-9]+)?\\%", body):
                    out.append(body.replace("\\%", "%"))
                else:
                    out.append("$" + self.math(body) + "$")
                i = j + 1
            elif s.startswith("\\[", i):
                j = s.index("\\]", i)
                out.append("\n\n$$\n" + self.math(s[i + 2:j]).strip() + "\n$$\n\n")
                i = j + 2
            elif s.startswith("\\\\", i):
                i += 2
            elif c == "\\":
                mm = re.match(r"\\([A-Za-z]+)", s[i:])
                if not mm:
                    sym = s[i + 1]
                    out.append({"%": "%", ",": " ", ";": " ", "&": "&", "_": "_", "{": "{", "}": "}"}[sym])
                    i += 2
                    continue
                name = mm.group(1)
                i += len(mm.group(0))
                if name in NAMES:
                    out.append(NAMES[name])
                    if s.startswith("{}", i):
                        i += 2
                elif name == "noindent":
                    while i < n and s[i] == " ":
                        i += 1
                elif name in ("textbf", "emph", "texttt"):
                    body, i = self.group(s, i)
                    if name == "texttt":
                        out.append("`" + body.replace("{*}", "*") + "`")
                    else:
                        out.append(self.emph(body, "**" if name == "textbf" else "*"))
                elif name == "citep":
                    keys, i = self.group(s, i)
                    out.append(self.cite(keys))
                elif name == "S":
                    out.append("§")
                    while i < n and s[i] == " ":
                        i += 1
                elif name == "ref":
                    lab, i = self.group(s, i)
                    out.append(self.labels[lab])
                elif name == "eqref":
                    lab, i = self.group(s, i)
                    out.append("(" + self.labels[lab] + ")")
                elif name == "url":
                    body, i = self.group(s, i)
                    out.append("<" + body + ">")
                elif name == "Methods":
                    out.append("**Methods**")
                    if s.startswith("{}", i):
                        i += 2
                elif name == "Emax":
                    out.append("$E_{\\max}$")
                elif name == "emergencystretch":
                    raise ValueError("unexpected \\emergencystretch")
                else:
                    raise ValueError("unknown text macro \\%s near %r" % (name, s[i - 20:i + 40]))
            elif c == "{":
                if s.startswith("{\\bf", i):
                    body, i2 = self.group(s, i)
                    out.append(self.emph(body[3:].lstrip(), "**"))
                    i = i2
                else:
                    body, i = self.group(s, i)
                    out.append(self.text(body))
            elif c == "~":
                out.append(" "); i += 1
            elif s.startswith("---", i):
                out.append("—"); i += 3
            elif s.startswith("--", i):
                out.append("–"); i += 2
            elif s.startswith("``", i):
                out.append("“"); i += 2
            elif s.startswith("''", i):
                out.append("”"); i += 2
            else:
                out.append(c); i += 1
        t = "".join(out)
        t = re.sub(r"[ \t]+\n", "\n", t)
        return t

    def emph(self, body, mark):
        """bold or italic; a bold group inside a bold group is left plain"""
        if mark == "**":
            if self.bold:
                return self.text(body)
            self.bold += 1
            try:
                return "**" + self.text(body).strip() + "**"
            finally:
                self.bold -= 1
        return "*" + self.text(body).strip() + "*"

    def convert(self, s):
        return self.text(s).strip()


ACCENTS = {"\\'y": "ý", "\\'i": "í", "\\'a": "á", "\\'e": "é", "\\'o": "ó", '\\"u': "ü", '\\"o': "ö", '\\"a': "ä"}


def bib_entry(text):
    """a refs.tex \\bibitem text to Markdown"""
    c = Converter({}, [])
    for a, b in ACCENTS.items():
        text = text.replace(a, b).replace(a[:2] + "{" + a[2] + "}", b)
    return c.text(text.replace("\\&", "&")).strip()
