#!/usr/bin/env python3
"""One hand-drawn outline must become exactly one cut piece.

⭐️⭐️ THE DESIGNER, 2 September 2026, having outlined and cut a real game's
sheets: "Three keep coming up as blank, even though when I 'mend on page'
they clearly appear, and it seems I can cut them. The numbering is also
haywire - more cut than I have outlined?"

Two sheets, and the shape of the fault was the same on both: one more piece
cut than outlines drawn, and the extra piece showed no size at all. `label()`
is four-connected on purpose (see its own note in sheets.py) — so a hand-drawn
outline whose fill pinches down to a single diagonal pixel, on a tight notch
or a sharp reflex corner the curve smoothing overshoots, comes back as TWO
labels that only ever touch corner to corner. `keep()` has no floor for a
shape a person drew (fault 85), so the sliver — often a handful of
near-invisible pixels — was kept as a real extra piece: one more "cut" than
"outlined", and a piece with no opaque pixels worth measuring, so it showed
"?" x "?" everywhere a size would otherwise be printed.

`label_shapes()`'s own words already say the rule this was missing: shapes
"are separated by being apart" — read to include a corner, not only an edge.
No browser and no project: this is arithmetic over hand-built masks, the same
way `the_automatic_pass.py` tests `keep()` directly.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sheets as S                                            # noqa: E402

bad = []
ran = []


def check(what, ok, saw=""):
    ran.append(what)
    print(("  ok   " if ok else "  WRONG ") + what +
          ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


# ---- the pinch itself: one shape, two lobes touching only at one corner
pinch = np.zeros((10, 10), bool)
pinch[2:5, 2:5] = True
pinch[5:8, 5:8] = True                  # touches the first lobe only at (4,4)-(5,5)

lab, n = S.label(pinch)
check("plain label() is four-connected, so a corner-only pinch reads as two",
      n == 2, n)

merged, nm = S._merge_corners(lab, n)
check("but the same shape is one piece, corner-pinch merged back together",
      nm == 1, nm)
check("and every pixel that was labelled at all is still labelled",
      bool((merged[pinch] > 0).all()) and not (merged[~pinch] > 0).any())

# ---- the guard: two pieces with a REAL gap between them must stay two
apart = np.zeros((10, 10), bool)
apart[1:3, 1:3] = True
apart[6:8, 6:8] = True
lab2, n2 = S.label(apart)
merged2, nm2 = S._merge_corners(lab2, n2)
check("two pieces with a real gap between them are not merged into one",
      n2 == 2 and nm2 == 2, (n2, nm2))

# ---- end to end, through label_shapes(), which is what cut_sheet() calls
colour = np.zeros((10, 10, 3), np.uint8)
colour[pinch] = [40, 160, 220]
_, n_one = S.label_shapes(pinch, colour)
check("label_shapes() counts a corner-pinched hand-drawn outline as ONE piece",
      n_one == 1, n_one)

# ⚠️ a colour-only mask (the automatic pass's own path, colour=None) gets the
# same treatment, or the merge would exist for the room and not the draft.
_, n_bare = S.label_shapes(pinch, None)
check("and the same is true with no colour key at all",
      n_bare == 1, n_bare)

# ---- two DIFFERENT outlines, same ink colour, merely touching at a corner:
# the room already treats same-colour touching outlines as one piece when
# they touch edge to edge (see label_shapes()'s own docstring); a corner is
# the same touch, read more carefully, so this is consistent rather than new.
colour3 = np.zeros((12, 12, 3), np.uint8)
ink3 = np.zeros((12, 12), bool)
ink3[1:4, 1:4] = True
ink3[4:7, 4:7] = True
colour3[ink3] = [10, 200, 10]
_, n3 = S.label_shapes(ink3, colour3)
check("two same-colour outlines touching only at a corner count as one piece",
      n3 == 1, n3)

# ⚠️ and a piece drawn in a colour that never occurs elsewhere on the sheet
# must not be disturbed by any of this — nothing to merge, nothing changes.
solo = np.zeros((10, 10), bool)
solo[3:6, 3:6] = True
colour4 = np.zeros((10, 10, 3), np.uint8)
colour4[solo] = [90, 90, 90]
_, n4 = S.label_shapes(solo, colour4)
check("an ordinary, unpinched piece is still exactly one piece",
      n4 == 1, n4)

print("")
if bad:
    print("\033[31m%d of these checks are WRONG\033[0m" % len(bad))
    for b in bad:
        print("   - " + b)
    sys.exit(1)
print("\033[32mall %d checks came out right\033[0m" % len(ran))
