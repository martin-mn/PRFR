"""
common -- what the figure folders of this repository share: the 512 sampled games and their Voronoi cells, the disk
map and its special lines, the atom order and the colours, and the drawing helpers used by more than one figure.

    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    from common import games, disk, atoms, style, tables     # side-effect free
    from common import furniture, counts, wfsheet, checks    # drawing: importing furniture (which counts and wfsheet
                                                             # import) selects Agg and sets the figures' rcParams

See common/README.md for the API.
"""
from . import atoms, disk, games, geometry, style, tables           # noqa: F401
from .atoms import IDX, NAME, ORDER, PROPS                          # noqa: F401
from .disk import K, phi, to_disk                                   # noqa: F401
from .games import cell_areas, cells, cells_keep, index_of, uv, xy  # noqa: F401
from .geometry import polyarea, unpack_faces                        # noqa: F401
from .style import GREY, TINT, WINCOL                               # noqa: F401
