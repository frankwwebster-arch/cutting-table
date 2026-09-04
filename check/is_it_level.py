#!/usr/bin/env python3
"""The angle a cut piece's own edges sit at — and, more often, the refusal.

⭐️⭐️ THE DESIGNER, 3 September 2026: "crucial to the rotate tool being
helpful will be the grid in the pieces tab which should show an exact
horizontal vertex... there should be a snap to grid option, as well as perhaps
some kind of obvious highlight of a gridline when a piece is horizontally
and/or vertically aligned."

A highlight needs a FACT to light on. `_skew_of()` is that fact: the smallest
box round the piece's own alpha, and the angle that box is at, folded into
(-45, 45] — measured with the same trimmed rotating calipers the automatic
pass uses (fault 71), so a few speckles at one corner cannot tilt the answer.

⚠️⚠️ AND MOST OF THIS FILE IS ABOUT IT SAYING NOTHING, which is the half that
matters — fault 25's rule arriving on geometry for the second time. A round
counter has no edge to be level with, and the calipers cheerfully answer
anyway: measured before the guard went in, a CIRCLE read -45 degrees and a
hexagon 29. Offering "level it" on a chit and turning it 45 degrees is a
confident wrong answer drawn over somebody's artwork. Eight of these checks
are the room keeping quiet.

No browser and no project: this is arithmetic over drawn pictures, the same
way `one_outline_one_piece.py` tests `label_shapes()` directly.
"""
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cutting_room as R                                      # noqa: E402

bad = []
ran = []


def check(what, ok, saw=""):
    ran.append(what)
    print(("  ok   " if ok else "  WRONG ") + what +
          ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def off(v, want=0.0):
    """How far a reading is from what was wanted — None being no reading at
    all. ⚠️ Written first as `abs(v or 99)`, which reads a PERFECTLY LEVEL
    piece (0.0, and so falsy) as 99 and fails the very case being checked."""
    return 999.0 if v is None else abs(v - want)


def skew(im):
    """The room's own measure, off a picture's alpha — exactly as piece_stats
    asks it: the alpha thresholded and trimmed to the piece's own box."""
    solid = im.getchannel("A").point(lambda v: 255 if v >= 24 else 0)
    bb = solid.getbbox()
    if bb is None:
        return None
    return R.Project._skew_of(None, solid.crop(bb))


def paper(w=900, h=900):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def turned(im, deg):
    return im.rotate(-deg, resample=Image.BICUBIC, expand=True)


def card(radius=22):
    im, dr = paper()
    dr.rounded_rectangle([200, 180, 560, 690], radius=radius,
                         fill=(220, 210, 190, 255))
    return im


# ---- a card laid at an angle somebody would want levelled ------------------
# ⭐️ The point of the whole feature: a card cut from a photograph sits a
# couple of degrees off, and the room has to read that back to a tenth or the
# nudges and the highlight are working to a precision it cannot supply.
for want in (0.0, 0.4, 1.0, 2.5, 7.0, -3.2):
    got = skew(turned(card(), want))
    check("a card laid at %s degrees reads back as %s" % (want, want),
          got is not None and abs(got - want) <= 0.15, got)

# ⚠️ FOLDED INTO (-45, 45]. A card two degrees off is two degrees off, not
# eighty-eight — the piece is levelled by the SHORTEST turn, and a readout
# saying "88 degrees off" of a card that is nearly straight is unusable.
check("a card turned a whole quarter is level, not 90 degrees off",
      off(skew(turned(card(), 90.0))) <= 0.15, skew(turned(card(), 90.0)))
check("and one at 91 degrees is one degree off, not ninety-one",
      off(skew(turned(card(), 91.0)), 1.0) <= 0.15, skew(turned(card(), 91.0)))
check("a card turned the other way reads negative, so the arrow can point",
      (skew(turned(card(), -2.0)) or 0) < 0, skew(turned(card(), -2.0)))

# ⚠️ A REAL CARD HAS ROUNDED CORNERS and is still a card. The fill test must
# not throw away the very shape this was built for.
for rad in (2, 14, 40):
    got = skew(turned(card(rad), 2.5))
    check("a card with corners rounded to %spx is still measured" % rad,
          got is not None and abs(got - 2.5) <= 0.2, got)

# ⚠️ and a few speckles knocked out of the alpha must not tilt it — that is
# what the trimmed calipers are for (fault 71)
im, dr = paper()
dr.rectangle([200, 200, 700, 420], fill=(200, 40, 40, 255))
for x, y in ((205, 205), (690, 410), (400, 203), (600, 415)):
    dr.rectangle([x, y, x + 3, y + 3], fill=(0, 0, 0, 0))
check("a piece with speckles knocked out of its corners still reads level",
      off(skew(im)) <= 0.15, skew(im))


# ---- ⚠️⚠️ THE SILENCES, which are most of the value ------------------------
# Each of these came back with a confident angle before the fill test went in.
def quiet(name, im, was):
    got = skew(im)
    check("%s has no edge to be level with, so the room says nothing "
          "(it used to answer %s)" % (name, was), got is None, got)


im, dr = paper()
dr.ellipse([200, 200, 700, 700], fill=(40, 120, 200, 255))
quiet("a round counter", im, "-45 degrees")

im, dr = paper()
dr.ellipse([150, 300, 780, 600], fill=(40, 120, 200, 255))
quiet("an oval", im, "an angle")

im, dr = paper()
dr.polygon([(450 + 200 * math.cos(math.radians(a)),
             450 + 200 * math.sin(math.radians(a))) for a in range(0, 360, 60)],
           fill=(60, 160, 90, 255))
quiet("a hexagon", im, "29 degrees")

im, dr = paper()
dr.polygon([(450, 180), (720, 700), (180, 700)], fill=(200, 90, 60, 255))
quiet("a triangle", im, "an angle")

im, dr = paper()
dr.polygon([(200, 200), (700, 200), (700, 380), (380, 380), (380, 700),
            (200, 700)], fill=(150, 90, 180, 255))
quiet("an L-shaped board", im, "an angle")

im, dr = paper()
dr.polygon([(450 + (160 + (a * 37 % 90) - 45) * math.cos(math.radians(a)),
             450 + (160 + (a * 53 % 90) - 45) * math.sin(math.radians(a)))
            for a in range(0, 360, 20)], fill=(180, 150, 60, 255))
quiet("a torn island", im, "an angle")

# ⚠️ nothing to measure at all, and a speck of a piece: neither may throw
im, dr = paper(40, 40)
check("an empty picture is not an angle of nought", skew(im) is None, skew(im))
im, dr = paper(40, 40)
dr.rectangle([10, 10, 13, 13], fill=(255, 255, 255, 255))
check("nor is a speck too small to have an edge worth reading",
      skew(im) is None, skew(im))

# ⚠️⚠️ THE NOISE TEST, and it is the one that stops this going too far: the
# cheap way to pass every silence above is to refuse everything. A plain
# rectangle — the commonest cut piece there is — must still be measured.
im, dr = paper()
dr.rectangle([200, 200, 700, 420], fill=(200, 40, 40, 255))
check("but a plain rectangle IS measured, or the guard has eaten the feature",
      skew(im) == 0.0, skew(im))
check("...and so is a plain rectangle sitting crooked",
      off(skew(turned(im, 3.0)), 3.0) <= 0.15, skew(turned(im, 3.0)))

print("")
if bad:
    print("\033[31m%d of these checks are WRONG\033[0m" % len(bad))
    for b in bad:
        print("   - " + b)
    sys.exit(1)
print("\033[32mall %d checks came out right\033[0m" % len(ran))
