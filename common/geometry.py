"""
Polygons on the disk: areas, and the packed-face format of the exact arrangements.

The exact eps -> 0 arrangements (Figures 1-3) store their faces as one (V, 2) array of disk vertices `verts` and an
(F + 1,) int array `offsets`, face i being verts[offsets[i]:offsets[i + 1]].
"""
import numpy as np


def polyarea(p):
    """the area of the polygon p ((n, 2) array, either orientation), by the shoelace formula exactly as
    eulerlib.polyarea / figstrict.py evaluated it: 0.5 |x . roll(y, -1) - y . roll(x, -1)|"""
    p = np.asarray(p, float)
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def unpack_faces(verts, offsets):
    """the list of face polygons [(n_i, 2) arrays] of a packed arrangement"""
    return [verts[offsets[i]:offsets[i + 1]] for i in range(len(offsets) - 1)]


def pack_faces(faces):
    """the inverse of unpack_faces: (verts (V, 2), offsets (F + 1,))"""
    off = np.concatenate([[0], np.cumsum([len(f) for f in faces])]).astype(np.int64)
    return np.vstack(faces), off
