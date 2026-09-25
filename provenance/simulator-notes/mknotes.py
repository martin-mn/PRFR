#!/usr/bin/env python3
"""
mknotes.py -- how ../../notes/*.md were made.

Each note is written for one place of the SI that refers to "the notes deposited with the code".  It consists of
longer versions of passages condensed in the SI, in the author's words, and of the text around them.  notes_text.py
holds that text and some of the passages, in Markdown; the other passages are read from the author's file of
passages, their LaTeX converted to Markdown, with the edits listed in notes_text.py that bring their references to
the paper's numbering (each must apply exactly once).  In every passage, of either kind, the second property is then
renamed from "Nash" to "stable" by the list RENAMES of notes_text.py (the author's decision of 2026-09-25; each rename
must apply the number of times given there), and no note is written in which "Nash" occurs outside "Nash equilibrium",
"Nash equilibria" and the list of references.  Every file ends with the references it cites, numbered in the order
of first citation.

Input (author's environment, the one variable PASSAGES below, read from the environment variable PRFR_PASSAGES):
the author's file of these passages, Markdown with the LaTeX of each passage in a ```latex block under a "## "
heading that names its place in the SI; and, in the same folder, the manuscript's refs.tex for the references and
ms.aux for the section and equation numbers that \\S\\ref and \\eqref resolve to.  The LaTeX is converted by
latex2md.py, which refuses any construct it does not know, so nothing is dropped silently.

    PRFR_PASSAGES=<the author's file of passages> python3 mknotes.py      # writes the six ../../notes/*.md

The notes' README.md and the folder notes/checks/ are not written by this script.
"""
import os, re, sys

# ---- author's environment: the author's file of passages (refs.tex and ms.aux are in the same folder) ----------------
PASSAGES = os.environ.get("PRFR_PASSAGES", "")
# ----------------------------------------------------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from latex2md import Converter, bib_entry  # noqa: E402
from notes_text import FILES, Passage, RENAMES  # noqa: E402

NOTES = os.path.normpath(os.path.join(HERE, os.pardir, os.pardir, "notes"))

KEPT = r"(?!\s+equilibri)"                # "Nash equilibrium", "Nash equilibria", also across a line break


def rename(md, used):
    """the renames of the second property (RENAMES of notes_text.py), counted in used"""
    for i, (old, new, _) in enumerate(RENAMES):
        md, n = re.subn(r"\b%s\b%s" % (re.escape(old), KEPT), new, md)
        used[i] += n
    return md


def nash_left(text):
    """the uses of "Nash" other than "Nash equilibrium" and "Nash equilibria", outside the list of references"""
    body = text.split("\n## References\n")[0]
    return [body[max(0, m.start() - 40):m.end() + 20].replace("\n", " ")
            for m in re.finditer(r"\bNash\b" + KEPT, body)]


def source(name):
    return os.path.join(os.path.dirname(PASSAGES), name)


def labels():
    t = open(source("ms.aux")).read()
    return {m.group(1): m.group(2) for m in re.finditer(r"\\newlabel\{((?:si|eq):[A-Za-z0-9-]+)\}\{\{([^}]*)\}", t)}


def bib():
    t = open(source("refs.tex")).read()
    out = {}
    for m in re.finditer(r"\\bibitem\{([^}]+)\}\s*\n(.*?)(?=\n\s*\n|\n\\bibitem|\Z)", t, re.S):
        out[m.group(1)] = " ".join(m.group(2).split())
    return out


def entries():
    """## heading -> the LaTeX blocks under it, in file order"""
    E, cur, block, inlatex = {}, None, [], False
    for ln in open(PASSAGES).read().split("\n"):
        if inlatex:
            if ln.startswith("```"):
                E[cur].append("\n".join(block)); block = []; inlatex = False
            else:
                block.append(ln)
            continue
        if ln.startswith("## "):
            cur = ln[3:].strip(); E[cur] = []; continue
        if ln.startswith("# "):
            cur = None; continue
        if ln.startswith("```latex") and cur is not None:
            inlatex = True; block = []
    return E


def find(E, key):
    hits = [h for h in E if key in h]
    assert len(hits) == 1, (key, hits)
    return hits[0]


def main():
    if not os.path.isfile(PASSAGES):
        sys.exit("set PRFR_PASSAGES to the author's file of passages (see the docstring)")
    L, B = labels(), bib()
    E = entries()
    os.makedirs(NOTES, exist_ok=True)
    npass = nhere = nedit = 0
    used = [0] * len(RENAMES)
    texts = []
    for fname, title, parts in FILES:
        cites = []
        cv = Converter(L, cites)
        out = ["# " + title, ""]
        for p in parts:
            if isinstance(p, str):                       # Markdown written for the notes
                out += [p.strip(), ""]
                continue
            if isinstance(p, Passage):                   # a passage given in notes_text.py, in Markdown
                heading = p.heading
                md = re.sub(r"\[(@[^\]]+)\]", lambda m: cv.cite(m.group(1).replace("@", "")), p.text)
                nhere += 1
            else:
                key, heading, edits = p                  # a passage of the author's file, its heading in the note, its edits
                h = find(E, key)
                assert E[h], "no LaTeX under %r" % h
                md = "\n\n".join(cv.convert(s) for s in E[h])
                for old, new in edits:
                    n = md.count(old)
                    assert n == 1, "%s: edit applies %d times: %r" % (fname, n, old[:60])
                    md = md.replace(old, new)
                nedit += len(edits)
            md = re.sub(r"\bnash\b", "Nash", md)         # the capitalisation of "Nash equilibrium"
            md = rename(md, used)                        # the second property is "stable"
            if heading:
                out += ["## " + heading, ""]
            out += [md, ""]
            npass += 1
        if cites:
            out += ["## References", ""]
            for k, key in enumerate(cites, 1):
                out.append("%d. %s" % (k, bib_entry(B[key])))
            out.append("")
        text = "\n".join(out).rstrip() + "\n"
        text = re.sub(r"\n{3,}", "\n\n", text)
        left = nash_left(text)
        assert not left, "%s: \"Nash\" for the property: %r" % (fname, left)
        texts.append((fname, text, len(cites)))
    for (old, new, n), k in zip(RENAMES, used):
        assert k == n, "rename %r -> %r applies %d times, not %d" % (old, new, k, n)
    for fname, text, ncites in texts:                    # written only once every note and every rename checks out
        open(os.path.join(NOTES, fname), "w").write(text)
        print("%-24s %6d bytes, %2d references" % (fname, len(text.encode()), ncites))
    print("%d files, %d passages (%d from the author's file, %d given in notes_text.py), %d edit%s and %d rename%s applied"
          % (len(FILES), npass, npass - nhere, nhere, nedit, "s" * (nedit != 1), sum(used), "s" * (sum(used) != 1)))


if __name__ == "__main__":
    main()
