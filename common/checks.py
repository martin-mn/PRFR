"""
The self-checks the figure scripts run before saving: no text runs off the sheet, no two heads overlap.

    check_sheet(fig, W, H, xticks=True, yticks=True, heads=True)

draws the canvas (fig.canvas.draw(), as every original did before savefig) and asserts, for every figure-level text and
every visible, non-empty text of every axes (plus the x and/or y tick labels of axes whose axis is on), that its window
extent lies strictly inside the W x H inch sheet; with heads=True also that no two texts of one axes with va="bottom"
and ha in ("center", "left") -- the panel letter and the head -- overlap.  Returns the renderer.

The originals differ in which tick labels they check: atomshares.py and figstrict.py x and y (the defaults),
atomcounts.finish y only (xticks=False), fig4.py / fig5.py x only and no heads (yticks=False, heads=False).
"""


def check_sheet(fig, W, H, xticks=True, yticks=True, heads=True):
    fig.canvas.draw()
    R = fig.canvas.get_renderer()

    def on_sheet(t):
        bb = t.get_window_extent(R)
        assert 0 < bb.x0 and bb.x1 < W * fig.dpi and 0 < bb.y0 and bb.y1 < H * fig.dpi, "text runs off the sheet: %r" % t.get_text()

    for t_ in fig.texts:
        on_sheet(t_)
    for ax_ in fig.axes:
        ticks = []
        if ax_.axison:
            ticks = (ax_.get_xticklabels() if xticks else []) + (ax_.get_yticklabels() if yticks else [])
        for t_ in list(ax_.texts) + ticks:
            if t_.get_text() and t_.get_visible():
                on_sheet(t_)
        if heads:
            hs = [t_ for t_ in ax_.texts if t_.get_text() and t_.get_va() == "bottom" and t_.get_ha() in ("center", "left")]
            for i_ in range(len(hs)):
                for j_ in range(i_ + 1, len(hs)):
                    assert not hs[i_].get_window_extent(R).overlaps(hs[j_].get_window_extent(R)), \
                        "texts overlap: %r / %r" % (hs[i_].get_text(), hs[j_].get_text())
    return R
