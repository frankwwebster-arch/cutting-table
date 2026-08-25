#!/usr/bin/env python3
"""The automatic first attempt at a sheet: does it draw the shape that is
printed, and — the half that matters more — does it hold its tongue about
everything that is not a plain rectangle or a plain circle?

⭐️⭐️ THE DESIGNER, 25 August 2026: "I'm also finding the auto-cutting quite
strangely inaccurate... the [one] sheet I uploaded felt like it should be very
easy, blocky colourful shapes, but I basically had to redo the entire thing...
There should be — given these are pieces of board games — a general thought
that most shapes will be regular (squares, circles, rectangles), and will be
strongly differentiated in colour terms from their background. Whilst the
general shapes were OK-ish, the platform added a load of additional nodes and
made some of the shapes look pretty odd."

No browser, no project and nobody's artwork: the sheet is drawn here, out of
the shapes a board game really is made of, and printed the way a real one
arrives — unevenly lit, speckled with scanner noise, and squashed through a
JPEG. Every one of those three is a fault this code was written to survive,
and each of them was found by watching it fail.

⚠️ FOURTEEN OF THESE CHECKS ARE ABOUT SAYING NOTHING. A hexagon squared off, or
an oval rounded into a circle, is a confident wrong answer laid over somebody's
artwork — and fault 25's lesson is that a confident wrong answer is taken
without looking. Tracing is the safe answer and must stay the common one.
"""
import io
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sheets as S                                            # noqa: E402
import cutting_room as room                                   # noqa: E402

W, H = 1800, 1500
GROUND = (232, 228, 214)
EDGE = (30, 30, 40)
bad = []


ran = []


def check(what, ok, saw=""):
    ran.append(what)
    print(("  ok   " if ok else "  WRONG ") + what +
          ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def ring(cx, cy, r, n, turn=0.0):
    return [(cx + math.cos(turn + k * 2 * math.pi / n) * r,
             cy + math.sin(turn + k * 2 * math.pi / n) * r) for k in range(n)]


def coastline(cx, cy, r, seed):
    rnd = random.Random(seed)
    return [(cx + math.cos(i / 24.0 * math.tau) * r * (1 + rnd.uniform(-.25, .25)),
             cy + math.sin(i / 24.0 * math.tau) * r * (1 + rnd.uniform(-.25, .25)))
            for i in range(24)]


# every piece: what it is called, where to prod it, and what was drawn
DRAWN = []


def sheet(gradient=36, noise=10, quality=55):
    """A sheet of the shapes a box really holds, printed as a scan really is."""
    im = Image.new("RGB", (W, H), GROUND)
    d = ImageDraw.Draw(im)
    del DRAWN[:]
    d.rectangle([80, 80, 380, 380], fill=(180, 60, 50), outline=EDGE, width=4)
    DRAWN.append(("a square counter", (230, 230), (80, 80, 380, 380)))
    d.rectangle([480, 80, 880, 330], fill=(60, 120, 180), outline=EDGE, width=4)
    DRAWN.append(("a rectangular card", (680, 205), (480, 80, 880, 330)))
    d.ellipse([980, 80, 1260, 360], fill=(220, 180, 60), outline=EDGE, width=4)
    DRAWN.append(("a round chit", (1120, 220), (980, 80, 1260, 360)))
    d.ellipse([1360, 80, 1740, 320], fill=(120, 200, 170), outline=EDGE, width=4)
    DRAWN.append(("an oval", (1550, 200), (1360, 80, 1740, 320)))
    d.polygon(ring(230, 700, 170, 6), fill=(200, 140, 90), outline=EDGE)
    DRAWN.append(("a hexagon", (230, 700), None))
    d.polygon(ring(650, 700, 170, 6, math.pi / 6), fill=(150, 180, 220), outline=EDGE)
    DRAWN.append(("a hexagon the other way up", (650, 700), None))
    d.polygon([(950, 560), (1250, 860), (910, 860)], fill=(150, 100, 180), outline=EDGE)
    DRAWN.append(("a triangle", (1040, 800), None))
    d.polygon(coastline(1550, 700, 170, 5), fill=(110, 170, 120), outline=EDGE)
    DRAWN.append(("an island", (1550, 700), None))
    d.polygon([(80, 1000), (480, 1030), (465, 1300), (65, 1270)],
              fill=(210, 120, 160), outline=EDGE)
    DRAWN.append(("a rectangle scanned crooked", (270, 1150), (65, 1000, 480, 1300)))
    d.rounded_rectangle([600, 1000, 900, 1300], radius=40, fill=(240, 200, 120),
                        outline=EDGE, width=4)
    DRAWN.append(("a counter with rounded corners", (750, 1150), (600, 1000, 900, 1300)))
    # ⚠️ a large, PALE piece: the one that was swallowed whole when the ground
    # was worked out as "anything near enough the sheet colour"
    d.polygon([(1000, 1000), (1400, 1000), (1400, 1150), (1150, 1150),
               (1150, 1330), (1000, 1330)], fill=(170, 170, 210), outline=EDGE)
    DRAWN.append(("a big pale board", (1050, 1050), None))

    a = np.asarray(im).astype(np.int16)
    yy, xx = np.mgrid[0:H, 0:W]
    a += ((xx / float(W) + yy / float(H)) * gradient
          - gradient / 2).astype(np.int16)[:, :, None]
    rnd = np.random.RandomState(11)
    a += rnd.randint(-noise, noise + 1, a.shape)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(0.5))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality)
    return np.asarray(Image.open(io.BytesIO(buf.getvalue())).convert("RGB"))


def drafted(rgb):
    """Every piece the automatic pass finds, filed under what was drawn there."""
    out = {}
    for got in room.suggest_outlines(rgb):
        xs = [p[0] for p in got["pts"]]
        ys = [p[1] for p in got["pts"]]
        box = (min(xs), min(ys), max(xs), max(ys))
        for name, (px, py), drew in DRAWN:
            if box[0] - 8 <= px <= box[2] + 8 and box[1] - 8 <= py <= box[3] + 8:
                out[name] = dict(got, box=box, drew=drew)
    return out


print("\nthe automatic first attempt at a sheet")
flat = drafted(sheet(gradient=0))
print("  (%d of the %d pieces drawn were found)" % (len(flat), len(DRAWN)))
check("every piece printed on the sheet is found", len(flat) == len(DRAWN),
      sorted(set(n for n, _, _ in DRAWN) - set(flat)))

# ⭐️ THE SHAPES THAT REALLY ARE REGULAR — four nodes and straight sides, which
# is what the person would otherwise sit and make by hand
for name in ("a square counter", "a rectangular card",
             "a rectangle scanned crooked", "a counter with rounded corners"):
    got = flat.get(name) or {}
    check("%s is drawn with four corners and straight sides" % name,
          len(got.get("pts") or []) == 4 and got.get("curve") is False,
          [len(got.get("pts") or []), got.get("curve")])

# ⚠️ AND IT LANDS ON THE ARTWORK. A shape fitted to the wrong place is worse
# than a traced one: it looks deliberate.
for name in ("a square counter", "a rectangular card",
             "a counter with rounded corners"):
    got = flat.get(name) or {}
    drew = got.get("drew") or (0, 0, 0, 0)
    box = got.get("box") or (0, 0, 0, 0)
    wide = (drew[2] - drew[0]) - (box[2] - box[0])
    tall = (drew[3] - drew[1]) - (box[3] - box[1])
    check("and %s is the size it is printed, a whisker inside the edge" % name,
          8 <= wide <= 22 and 8 <= tall <= 22, [wide, tall])

got = flat.get("a round chit") or {}
check("a round chit is drawn as a circle, and a curved one",
      len(got.get("pts") or []) == 16 and got.get("curve") is True,
      [len(got.get("pts") or []), got.get("curve")])
if got.get("pts"):
    cx = sum(p[0] for p in got["pts"]) / 16.0
    cy = sum(p[1] for p in got["pts"]) / 16.0
    rs = [math.hypot(p[0] - cx, p[1] - cy) for p in got["pts"]]
    check("and it is a real circle, at the size it is printed",
          max(rs) - min(rs) < 1.5 and 128 <= sum(rs) / 16.0 <= 138,
          [round(sum(rs) / 16.0, 1), round(max(rs) - min(rs), 2)])

# ⚠️⚠️ AND NOW THE HALF THAT MATTERS: everything the shape does NOT settle.
# A hexagon squared off is a confident wrong answer laid over somebody's
# artwork, and fault 25 is the whole story of why those are the dangerous ones.
print("")
print("  and what it refuses to call a rectangle or a circle")
for name in ("a hexagon", "a hexagon the other way up", "a triangle",
             "an island", "an oval", "a big pale board"):
    got = flat.get(name) or {}
    check("%s is traced, not squared off" % name,
          got.get("curve") is True and len(got.get("pts") or []) >= 4,
          [len(got.get("pts") or []), got.get("curve")])

for name in ("a hexagon", "a triangle", "an island", "an oval"):
    got = flat.get(name) or {}
    pts = got.get("pts") or []
    if len(pts) < 3:
        check("%s keeps its own shape" % name, False, pts)
        continue
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    rs = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
    check("%s is not handed back as a ring of one radius" % name,
          (max(rs) - min(rs)) / max(rs) > 0.04,
          round((max(rs) - min(rs)) / max(rs), 3))

# ⭐️ A TRACED OUTLINE IS A HANDFUL OF NODES, NOT A HUNDRED. The whole
# complaint was "a load of additional nodes"; a scan's jitter is not a corner.
print("")
print("  and how much there is to correct")
worst = max((len(v["pts"]), k) for k, v in flat.items())
check("no piece on the sheet comes back with more than 30 nodes",
      worst[0] <= 30, worst)
check("and the plain shapes come back with four",
      sum(1 for v in flat.values() if len(v["pts"]) == 4) >= 4,
      sorted(len(v["pts"]) for v in flat.values()))

# ⚠️⚠️ THE LIGHT FALLS OFF ACROSS A SCANNER'S GLASS, and one flat colour for
# the whole sheet cannot follow it: the far corner stops counting as paper, so
# it becomes a piece of its own and the fringe of it joins onto real pieces.
print("")
print("  a sheet that is not evenly lit")
lit = drafted(sheet(gradient=45))
check("every piece is still found when one corner is much darker than the other",
      len(lit) == len(DRAWN), sorted(set(n for n, _, _ in DRAWN) - set(lit)))
check("and no corner of the paper is offered as a piece",
      len(room.suggest_outlines(sheet(gradient=45))) == len(DRAWN),
      len(room.suggest_outlines(sheet(gradient=45))))
for name in ("a square counter", "a rectangular card"):
    got = lit.get(name) or {}
    check("and %s is still four straight corners, not a bulge" % name,
          len(got.get("pts") or []) == 4 and got.get("curve") is False,
          [len(got.get("pts") or []), got.get("curve")])

# ⚠️ A PALE PIECE IS STILL A PIECE. Grown outwards without a limit on the
# STEP, the ground walked onto a light board and took four fifths of it.
board = lit.get("a big pale board") or {}
if board.get("box"):
    b = board["box"]
    check("and a big pale board is not eaten by the ground it sits on",
          (b[2] - b[0]) > 360 and (b[3] - b[1]) > 290,
          [round(b[2] - b[0]), round(b[3] - b[1])])
crook = lit.get("a rectangle scanned crooked") or {}
if crook.get("box"):
    b = crook["box"]
    check("nor is a piece whose edge runs nearly level with the paper",
          (b[2] - b[0]) > 380 and (b[3] - b[1]) > 270,
          [round(b[2] - b[0]), round(b[3] - b[1])])

# ⭐️ and the record itself: an outline that cannot say whether it is straight
# is an outline the editor will bend, which is where this began
print("")
print("  and the shape of the answer")
one = room.suggest_outlines(sheet(gradient=0))[0]
check("every suggested outline says whether it is straight or curved",
      isinstance(one, dict) and "pts" in one and isinstance(one.get("curve"), bool),
      sorted(one.keys()) if isinstance(one, dict) else type(one).__name__)

print("")
if bad:
    print("\033[31m%d of the automatic pass's checks are WRONG\033[0m" % len(bad))
    for b in bad:
        print("   - " + b)
    sys.exit(1)
print("\033[32mall %d checks came out right\033[0m" % len(ran))
