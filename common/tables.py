"""
Small CSV tables with a commented header, the format of every deposited table in this repository.

    # free text: what the table is, where it came from, one line per column
    # ...
    name1,name2,...                          <- the header line (column names)
    v11,v12,...

Floats are written with repr(), the shortest string that reads back as the same double, so a table round-trips
exactly; integers as integers; strings as they are (no commas, quotes or newlines allowed).

    write_table(path, columns, comments)     columns: an ordered dict {name: (n,) array or list}
    read_table(path) -> dict                 {name: (n,) numpy array}; a column whose every entry parses as an integer
                                             is int64, else float64 if every entry parses as a float ("nan", "inf"
                                             allowed), else str

Per-game atom tables use the column names  <prefix>_000, <prefix>_100, ... in common.atoms.ORDER:

    atom_columns("S", S)  -> {"S_000": S[:, 0], ..., "S_111": S[:, 6]}     S an (n, 7) array in ORDER
    atom_array(table, "S") -> the (n, 7) array back
"""
import csv

import numpy as np

from .atoms import ORDER


def _fmt(x):
    if isinstance(x, (bool, np.bool_)):
        return "1" if x else "0"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, (float, np.floating)):
        return repr(float(x))
    s = str(x)
    assert not any(c in s for c in ',"\n\r'), "a string cell may not contain a comma, a quote or a newline: %r" % s
    return s


def write_table(path, columns, comments=()):
    """write the columns (dict name -> sequence, all of one length) to path as a commented CSV"""
    if isinstance(comments, str):
        comments = comments.splitlines()
    names = list(columns)
    cols = [list(columns[k]) for k in names]
    n = len(cols[0])
    assert all(len(c) == n for c in cols), "columns of different lengths"
    with open(path, "w") as f:
        for c in comments:
            f.write("# " + c.rstrip() + "\n" if not c.startswith("#") else c.rstrip() + "\n")
        f.write(",".join(names) + "\n")
        for i in range(n):
            f.write(",".join(_fmt(c[i]) for c in cols) + "\n")


def _convert(vals):
    try:
        return np.array([int(v) for v in vals], dtype=np.int64)
    except ValueError:
        pass
    try:
        return np.array([float(v) for v in vals], dtype=np.float64)
    except ValueError:
        return np.array(vals)


def read_table(path):
    """the table at path as {column name: numpy array}, in file order (comment lines skipped)"""
    with open(path) as f:
        lines = [l for l in f if not l.startswith("#")]
    rows = list(csv.reader(lines))
    head, body = rows[0], rows[1:]
    return {h: _convert([r[j] for r in body]) for j, h in enumerate(head)}


def comments(path):
    """the header comment lines of a table, without the leading '# '"""
    out = []
    with open(path) as f:
        for l in f:
            if not l.startswith("#"):
                break
            out.append(l[2:].rstrip("\n") if l.startswith("# ") else l[1:].rstrip("\n"))
    return out


def atom_columns(prefix, A):
    """{prefix_000: A[:, 0], ...} for an (n, 7) array A in ORDER"""
    A = np.asarray(A)
    assert A.ndim == 2 and A.shape[1] == 7, A.shape
    return {"%s_%s" % (prefix, c): A[:, i] for i, c in enumerate(ORDER)}


def atom_array(table, prefix):
    """the (n, 7) array in ORDER from the columns prefix_000 ... prefix_111 of a read_table dict"""
    return np.column_stack([table["%s_%s" % (prefix, c)] for c in ORDER])
