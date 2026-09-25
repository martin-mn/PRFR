"""
The colours the figures share (no drawing, no side effects; matplotlib is imported only for its colormap registry).

Atoms (keys are the atom strings of common.atoms.ORDER):
    WINCOL   the saturated atom colours of every "most abundant / most enriched atom" map and its swatch legend
             (Figures 4, SI Figures 2-4, 8-10, 12): blues for the efficient atoms (100 light, 110 dark), reds for the
             competitive ones (001 light, 011 dark), purple 111, gold 010, dark grey 000 -- Figure 1's hues, saturated
    TINT     the light atom tints of Figure 1 (the Euler diagram, panel a, and the key); 000 is white
    COL_E, COL_C, COL_N   the outlines of the efficient circle (blue), the competitive circle (red), the dashed
                          curve of the stable strategies (Figure 1a)
    GREY     "0.84": a cell or face where the atom (or property) has no strategy at that game (all count and share maps)

Scales:
    share maps     viridis, linear, 0 to 1 (Normalize(0, 1)); SHARE_CMAP()
    efficiency     viridis 0 to 1 with values below 0 drawn black; EFF_CMAP(), EFF_NORM
    count maps     magma, per panel (common.counts.atom_scale)
"""
import matplotlib
from matplotlib.colors import Normalize

WINCOL = {"000": "0.36", "100": "#8fb8e8", "010": "#dba622", "001": "#f0a48c",
          "110": "#2f5fb3", "011": "#c43d3b", "111": "#7a4fa8"}
TINT = {"000": "white", "100": "#d2dff5", "001": "#f8d7d3", "010": "#e6e6e6", "110": "#b9c8ea", "011": "#ebbcbc",
        "111": "#cbbbe6"}
COL_E, COL_C, COL_N = "#1f4e9c", "#b3232b", "0.10"
GREY = "0.84"
SHARE_NORM = Normalize(vmin=0.0, vmax=1.0)
EFF_NORM = Normalize(vmin=0.0, vmax=1.0)


def SHARE_CMAP():
    """a fresh copy of viridis (the share maps; atomshares.CMAP without its logit-only under-colour)"""
    return matplotlib.colormaps["viridis"].copy()


def EFF_CMAP():
    """viridis with under-colour black (the efficiency maps: a negative mean payoff; fig4.ECMAP)"""
    cm = matplotlib.colormaps["viridis"].copy()
    cm.set_under("black")
    return cm
