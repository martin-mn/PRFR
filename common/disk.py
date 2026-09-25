"""
The disk of games and the lines drawn on it.

THE MAP.   (u, v)  ->  (u, v) / sqrt(K^2 + u^2 + v^2),   K = 4

carries the whole plane of games (R, S, T, P) = (1, u, 1 + v, 0) onto the open unit disk; the rim is the circle
of directions at infinity.  Lines through the origin stay straight, so u = 0 and v = 0 are diameters and the four
classical games are the four quadrants; every other line becomes a conic arc.  Games with |(u, v)| <= K fill
exactly half of the disk's area.

Two implementations of the same map are kept, because the figures used both and they can differ in the last bit
of a double (the sum under the square root is evaluated in a different order):

    to_disk(u, v)  (u, v arrays)   K*K + u*u + v*v    -- DiskM2WF/Opt/disk.py; used for the 512 sunflower points
                                                          and therefore for their Voronoi cells (common.games)
    phi(p)         (p an (n, 2) array)  K*K + sum(p^2) -- PartnersRivals/Figures/disklib.py; used for every line
                                                          and every face drawn on the disk

The special lines (a u + b v = c):
    u + v = 1    the switch line, S + T = 2R: above it alternation beats mutual cooperation, so Emax changes
    u - v = 1    T = S, across which competitiveness changes
    u + v = 0    S + T = R + P, the donation games (drawn as the half-line u < 0 < v only, in the Prisoner's Dilemma)
"""
import numpy as np

K = 4.0            # the disk constant of every figure
RB = 2000.0        # the plane is cut at |t| = RB when a line is sampled; its image is ~K^2/RB^2 inside the rim

# the four classical games, by quadrant, and the angle (degrees) on whose diagonal each name is centred on the rim
NAMES = ((45.0, "Snowdrift"),            # u > 0, v > 0
         (135.0, "Prisoner's Dilemma"),  # u < 0, v > 0
         (225.0, "Stag Hunt"),           # u < 0, v < 0
         (315.0, "Harmony"))             # u > 0, v < 0
NM_FS, NM_TRK, NM_GAP = 42.0, 0.09, 0.028      # rim names: base font size (points), tracking (em), gap to the rim (radii)

SWITCH = (1, 1, 1)             # u + v = 1
TEQS = (1, -1, 1)              # u - v = 1   (T = S)
DONATION = (1, 1, 0)           # u + v = 0   (half-line u < 0 < v)


def to_disk(u, v, k=K):
    """(x, y) on the unit disk of the games (u, v); arrays of any shape, returned as float arrays"""
    u = np.asarray(u, dtype=float); v = np.asarray(v, dtype=float)
    f = np.sqrt(k * k + u * u + v * v)
    return u / f, v / f


def from_disk(x, y, k=K):
    """the inverse map: the game (u, v) at the disk point (x, y), |(x, y)| < 1"""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    r2 = x * x + y * y
    f = k / np.sqrt(np.maximum(1.0 - r2, 1e-300))
    return x * f, y * f


def phi(p, k=K):
    """the map applied to an (n, 2) array (or one point) of games; returns an (n, 2) array of disk points"""
    p = np.atleast_2d(np.asarray(p, dtype=float))
    return p / np.sqrt(k * k + (p ** 2).sum(axis=1))[:, None]


def plane(q, k=K):
    """the inverse of phi for an (n, 2) array of disk points (as fig1.py's plane(); clamps r^2 at 1 - 1e-12)"""
    q = np.atleast_2d(np.asarray(q, float)); r2 = (q ** 2).sum(1)
    return q * (k / np.sqrt(np.maximum(1.0 - r2, 1e-12)))[:, None]


def arc(A, B, f=phi, tol=1e-5, depth=0):
    """the image of the straight edge A--B of the plane under the map f, as a polyline within `tol` of the true conic:
    the chord is subdivided until the drawn polyline sags less than tol.  Returns a list of disk points (the end
    point B is NOT included, so consecutive edges of a polygon can be concatenated)."""
    a, b = np.asarray(A, float), np.asarray(B, float)
    fa, fb = f(a)[0], f(b)[0]
    m = 0.5 * (a + b)
    if depth >= 16 or np.hypot(*(f(m)[0] - 0.5 * (fa + fb))) < tol:
        return [fa]
    return arc(a, m, f, tol, depth + 1) + arc(m, b, f, tol, depth + 1)


def conic(a, b, c, f=phi, rb=RB, arms=(-1, 1), npt=20000):
    """the image of the line a u + b v = c, one (npt, 2) polyline per arm; the line is cut at |t| = rb.
    arms=(1,) draws a half-line (the donation games: direction (-b, a) from the foot of the perpendicular)."""
    d = np.array([-b, a], dtype=float)
    p0 = np.array([a, b], dtype=float) * c / (a * a + b * b)
    t = np.linspace(0, rb, npt)[:, None]
    return [f(p0[None, :] + s * t * d[None, :]) for s in arms]


# ------------------------------------------------------------------ the special lines, as the figures draw them
# style "maps" (Figures 2-5 and every SI disk except SI Figure 1): the switch line crimson dashed, T = S white dashed
# (with a dark halo on the sunflower maps, none on the count maps), the donation half-line cyan dash-dot, all lw 1.5,
# zorder 7.  CONICS is the list atomshares.py / atomcounts.py built: [(polyline, colour, dash)].
CONICS = [(s, col, dash)
          for (a, b, c), col, dash, arms in ((SWITCH, "crimson", (0, (7, 4)), (-1, 1)),
                                             (TEQS, "white", (0, (7, 4)), (-1, 1)),
                                             (DONATION, "#12d7e8", (0, (8, 3, 1.5, 3)), (1,)))
          for s in conic(a, b, c, phi, RB, arms)]


def draw_conics(ax, halo=True, lw=1.5, zorder=7):
    """draw CONICS on ax exactly as the figures did: halo=True as the sunflower maps (atomshares.furniture: a 2.7-pt
    dark-grey stroke under the white T = S dashes), halo=False as the count maps (atomcounts.panel)"""
    import matplotlib.patheffects as pe
    HALO = [pe.withStroke(linewidth=2.7, foreground="0.35")]
    for s, col, dash in CONICS:
        ax.plot(s[:, 0], s[:, 1], color=col, lw=lw, zorder=zorder, linestyle=dash,
                **({"path_effects": HALO} if (halo and col == "white") else {}))


def euler_lines():
    """style "euler" (Figure 1 b, c; eulerlib.draw_map): the switch line and T = S sampled at 40001 values of
    t in [-2000, 2000], as (switch, teqs), each an (40001, 2) disk polyline"""
    tt = np.linspace(-2000, 2000, 40001)
    sw = phi(np.column_stack([tt, 1 - tt]), K)
    ts = phi(np.column_stack([tt, tt - 1]), K)
    return sw, ts


def draw_euler_lines(ax):
    """Figure 1's two lines: the switch line crimson solid lw 1.1, T = S near-black dashed (0, (3, 2)) lw 0.9, zorder 8"""
    sw, ts = euler_lines()
    ax.plot(sw[:, 0], sw[:, 1], color="crimson", lw=1.1, zorder=8)
    ax.plot(ts[:, 0], ts[:, 1], color="0.10", lw=0.9, ls=(0, (3, 2)), zorder=8)


# ------------------------------------------------------------------ the names of the four games, set on the rim
def advances(s, fp, fontsize, tracking):
    """pen advance of every character of s, in points, kerned, plus tracking (disklib.advances)"""
    from matplotlib import font_manager, ft2font
    face = ft2font.FT2Font(font_manager.findfont(fp))
    face.set_size(fontsize, 72.0)            # 72 dpi, so one unit is one point
    adv, prev = [], None
    for ch in s:
        idx = face.get_char_index(ord(ch))
        if prev is not None:
            kk = face.get_kerning(prev, idx, ft2font.KERNING_DEFAULT)
            adv[-1] += kk / 64.0 if kk else 0.0
        adv.append(face.load_char(ord(ch)).linearHoriAdvance / 65536.0 + tracking * fontsize)
        prev = idx
    return adv


def arc_text(ax, s, theta_c, r_in, fontsize, dpu, gap, tracking, color="0.10", zorder=12):
    """set the string s on an arc outside the radius r_in, centred on the angle theta_c (degrees), as PathPatches.

    dpu is data units per point.  On the upper half the letters stand radially outward and read clockwise, on the
    lower half radially inward and read anticlockwise, so both halves read the right way up; the nearest ink is
    `gap` from r_in either way.  Returns (theta_lo, theta_hi, r_outer) in degrees and data units (disklib.arc_text)."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.patches import PathPatch
    from matplotlib.textpath import TextPath
    from matplotlib.transforms import Affine2D
    fp = FontProperties(size=fontsize)
    adv = advances(s, fp, fontsize, tracking)
    total = sum(adv) - tracking * fontsize            # drop trailing tracking
    ink = TextPath((0, 0), s, size=fontsize, prop=fp).get_extents()
    asc, desc = ink.y1, max(-ink.y0, 0.0)             # points above / below
    up = (theta_c % 360.0) < 180.0
    r0 = r_in + gap + (0.0 if up else asc * dpu)      # the baseline radius
    half = 0.5 * total * dpu / r0                     # radians
    th_c, x = np.deg2rad(theta_c), 0.0
    for ch, a in zip(s, adv):
        if ch != " ":
            d = (x + 0.5 * a) * dpu / r0              # centre of this slot
            th = th_c + (half - d) if up else th_c - half + d
            tr = (Affine2D().translate(-0.5 * a, 0.0).scale(dpu)
                  .rotate_deg(np.rad2deg(th) + (-90.0 if up else 90.0))
                  .translate(r0 * np.cos(th), r0 * np.sin(th)))
            ax.add_patch(PathPatch(tr.transform_path(TextPath((0, 0), ch, size=fontsize, prop=fp)),
                                   fc=color, ec="none", lw=0, zorder=zorder))
        x += a
    return (np.rad2deg(th_c - half), np.rad2deg(th_c + half), r0 + (asc if up else desc) * dpu)
