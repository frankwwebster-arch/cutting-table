#!/usr/bin/env python3
"""The Cutting Room — cut the components out of a board game's scanned sheets.

    ./cutting_room.py              # start it and open the browser
    ./cutting_room.py --port 8765 --home ~/Documents/"Cutting Room"

One local web app, no network, nothing leaves the machine. It runs on
127.0.0.1 only. What it does, in the order a person does it:

  IMPORT   Drop a PDF, a scan (PNG/JPEG/TIFF), a Word file (.docx/.doc)
           with pictures in it, or a ZIP of any of those, on a project.
           Every page and picture becomes a SHEET at 300dpi.

  OUTLINE  Open a sheet in the Cutting Table (the editor from this
           repository, served by the room and saved to the room as you
           draw) and draw, or accept, an outline round each piece.

  CUT      Press "Cut this sheet". The room paints the outlines into a
           mask, cuts every piece out at full resolution with a smoothed,
           bitten-in edge, measures it in inches, and files it.

  NAME     On the Pieces page each cut piece is shown at its printed size
           on a one-inch grid and given a name, a kind, a type, a note, a
           quarter-turn — and linked to the component it IS.

  WANTED   The index of what the game needs: every counter, template,
           ruler and card deck the box should contain, with cut / not cut
           against each and a completeness figure for the game.

A PROJECT is a folder with a project.json in it. By default projects live
under ~/Documents/Cutting Room/<name>/; a project elsewhere (inside a game's
own repository, say) is registered in ~/Documents/Cutting Room/projects.json
and its project.json may point each of its stores at a path of its own:

  {
   "id": "boxgame", "name": "A Boxed Game", "game": "A Boxed Game", "dpi": 300,
   "paths": {"sheets": "sheets", "outlines": "outlines.json",
             "masks": "masks", "pieces": "pieces",
             "index": "pieces/index.json", "manifest": "manifest.json",
             "wanted": "wanted.json"},
   "hooks": [{"id": "finish", "label": "Hand the cut pieces to the game",
              "cmd": ["/usr/bin/python3", "tools/finish_pieces.py"],
              "cwd": "/path/to/the/game"}],
   "sheets": [ ... kept by the room ... ]
  }

Needs Python 3.9+, numpy and Pillow; pdftoppm (poppler) for PDFs; on a
Mac, textutil (built in) turns an old .doc into a .docx first.
"""
import argparse
import csv
import io
import json
import math
import os
import platform
import re
import shlex
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheets as sheetlib                                   # noqa: E402
import cut as cutter                                         # noqa: E402

Image.MAX_IMAGE_PIXELS = None

# ⭐️⚠️ WHEN THIS COPY OF THE ROOM STARTED RUNNING, and what the code on the
# disk says now. The designer, 23 August 2026, on pressing a button built that same
# afternoon: "when I press 'Split it' I get a 'no such call' error."
#
# The room had been open for hours. Its PAGES are read off the disk on every
# request, so the new button was there; its PYTHON is whatever was loaded when
# the process started, so the route behind the button was not. A new button
# that answers "no such call" looks like a bug in the button, and the one
# thing that would have told them — that the room itself is out of date — was
# the one thing nothing said.
#
# So the room compares its own source against the clock it started at and says
# so on every page. See `stale_code()`.
STARTED_AT = time.time()

ROOM_DIR = os.path.join(HERE, "room")
TEMPLATE = os.path.join(HERE, "cutting_table.tpl.html")
DEFAULT_HOME = os.path.expanduser("~/Documents/Cutting Room")
DPI = 300
JPEG_Q = 85
THUMB_PX = 640                # long edge of a sheet thumbnail
PIECE_THUMB_PX = 260
MIN_PIECE_IN = 0.25
# ⚠️ ONE SET OF NUMBERS FOR THE AUTOMATIC PASS, in sheets.py, or the room and
# the baked table would draft the same sheet two different ways (fault 24)
SUGGEST_VERSION = 3     # bump when the automatic pass changes; see /suggest
SUGGEST_TOL = sheetlib.SUGGEST_TOL
SUGGEST_INSET = sheetlib.SUGGEST_INSET
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".bmp", ".gif")

# tools/cutting_table.tpl.html: INKS, in order. A piece's ink is an index
# into this, and the cutter tells two touching pieces apart by their colour
# alone, so these must stay exactly as they are.
INKS = ["#FF3B30", "#34C759", "#FFD60A", "#0A84FF", "#FF2D95",
        "#5AC8FA", "#FF9F0A", "#BF5AF2", "#FFFFFF", "#00C7BE",
        "#A2845E", "#6E56CF"]
SMOOTH = 0.5                              # var smooth in the template
CORNER = math.cos(52 * math.pi / 180)     # var CORNER in the template

# ⭐️ "card back" earns its place among the kinds rather than being a tick of
# its own. The designer, 24 August 2026: "helpful if a card back element can be
# flagged as such, and then ONLY card backs appear in the ITS BACK dropdown, or
# that really is an exhaustive process." A back IS a piece — cut once, pointed
# at by every card in the deck (fault 46) — so what it needs is a way of saying
# what sort of piece it is, which is what `kind` is for. It travels in the
# inventory with everything else, and nothing guesses it: only a person knows.
KINDS = ["counter", "template", "ruler", "card", "card back", "deck", "terrain",
         "ship_template", "chart", "sheet", "tile", "board", "token", "other"]

# ⚠️ WHAT THE ROOM WORKS OUT IS NOT PART OF THE LIST. `wanted_status()` hangs
# what has been cut against each component onto the component every time it is
# asked, and the page sends the list back exactly as it was given it — so these
# would land in `wanted.json` as a stale answer on disk that looks exactly like
# a real one. The ROOM takes them off again, in the one place that saves the
# list, rather than every caller remembering to: a set of names known in two
# places is fault 24, which has bitten this codebase five times.
WORKED_OUT = ("pieces", "guesses", "state", "need", "got", "cut_pieces",
              "each_on")


# ------------------------------------------------------------------ helpers

def slug(s, keep=28):
    s = re.sub(r"\.[a-z0-9]+$", "", str(s).lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return (s[:keep].strip("-") or "sheet")


def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def write_json(path, data, indent=1):
    """Atomic: a half-written project file would be worse than none."""
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False, sort_keys=False)
        fh.write("\n")
    os.replace(tmp, path)


def now_ms():
    return int(time.time() * 1000)


def stale_code():
    """Has the room's own code been changed since this copy of it started?

    Only the Python matters: every page, stylesheet and script is read off the
    disk as it is asked for, so those are always current. The Python is not,
    and cannot be — a running program cannot re-read itself.
    """
    newest = 0.0
    for mod in (os.path.join(HERE, "cutting_room.py"),
                os.path.join(HERE, "sheets.py"),
                os.path.join(HERE, "cut.py")):
        try:
            newest = max(newest, os.path.getmtime(mod))
        except OSError:
            continue
    # a second of slack: a file written in the same second the room started is
    # the file the room started FROM
    return newest > STARTED_AT + 1.0


def stem_of(sheet_id):
    """The name a sheet's pieces are filed under: `core-03` -> `core_p03`,
    so a piece is `core_p03_00`. Any other id is used as it is."""
    m = re.match(r"^(.+)-(\d+)$", sheet_id)
    if m:
        return "%s_p%02d" % (m.group(1).replace("-", "_"), int(m.group(2)))
    return sheet_id.replace("-", "_")


def overlap(a, b):
    """How much of the smaller box the two boxes share."""
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    inter = (x1 - x0) * (y1 - y0)
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return inter / float(small) if small else 0.0


# ------------------------------------------------------ the curve (ported)
# A transcription of the template's own Bézier — the same handles, the
# same corner test, the same half-strength smoothing — so the mask is the
# shape that was on screen. Change one and change both.

def _unit(x, y):
    d = math.hypot(x, y)
    return None if d == 0 else (x / d, y / d)


def _along(pts, i):
    n = len(pts)
    back = _unit(pts[i][0] - pts[(i - 1) % n][0], pts[i][1] - pts[(i - 1) % n][1])
    on = _unit(pts[(i + 1) % n][0] - pts[i][0], pts[(i + 1) % n][1] - pts[i][1])
    if back is None:
        return on
    if on is None:
        return back
    if back[0] * on[0] + back[1] * on[1] < CORNER:
        return None
    return _unit(back[0] + on[0], back[1] + on[1])


def _arc(pts, k):
    n = len(pts)
    p1, p2 = pts[k], pts[(k + 1) % n]
    L = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) * SMOOTH / 3.0
    a, b = _along(pts, k), _along(pts, (k + 1) % n)
    return ((p1[0] + a[0] * L, p1[1] + a[1] * L) if a else (p1[0], p1[1]),
            (p2[0] - b[0] * L, p2[1] - b[1] * L) if b else (p2[0], p2[1]),
            (p2[0], p2[1]))


def flatten(pts, curve):
    n = len(pts)
    if not curve or n < 3:
        return [tuple(p) for p in pts]
    out = []
    for k in range(n):
        p1 = pts[k]
        c1, c2, p2 = _arc(pts, k)
        span = (math.hypot(c1[0] - p1[0], c1[1] - p1[1])
                + math.hypot(c2[0] - c1[0], c2[1] - c1[1])
                + math.hypot(p2[0] - c2[0], p2[1] - c2[1]))
        steps = max(4, min(200, int(span / 1.5) + 1))
        for s in range(steps):
            t = s / float(steps)
            u = 1.0 - t
            out.append((u * u * u * p1[0] + 3 * u * u * t * c1[0]
                        + 3 * u * t * t * c2[0] + t * t * t * p2[0],
                        u * u * u * p1[1] + 3 * u * u * t * c1[1]
                        + 3 * u * t * t * c2[1] + t * t * t * p2[1]))
    return out


def outline_box(pc):
    """One outline's own bounding box, in sheet pixels — the same flattening
    the mask is painted from, so the two cannot disagree about where it is."""
    poly = flatten(pc.get("pts") or [], pc.get("curve", False))
    if len(poly) < 3:
        return None
    xs = [q[0] for q in poly]
    ys = [q[1] for q in poly]
    return [int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1]


def paint_mask(pieces, size):
    """One sheet's mask layer: every piece filled flat in its own ink, on
    transparency. Each piece on its own layer then laid down, so a piece
    drawn over another replaces it exactly as the canvas does."""
    w, h = size
    mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    drawn = 0
    for pc in pieces:
        pts = pc.get("pts") or []
        if len(pts) < 3:
            continue
        poly = flatten(pts, pc.get("curve", False))
        ink = INKS[int(pc.get("ink", 0)) % len(INKS)]
        rgb = tuple(int(ink[i:i + 2], 16) for i in (1, 3, 5))
        drawn += 1
        # ⚠️⚠️ EACH PIECE COSTS ITS OWN BOX, NOT THE WHOLE SHEET. This made two
        # full-sheet images per piece — an L layer and an RGBA patch — and
        # composited both across the entire sheet. On a 170-megapixel scan
        # that is 200MB of allocation and pixel work for one counter, and the
        # designer's seventeen sheets carried a hundred and forty outlines.
        # Drawing the polygon in its own bounding box and pasting it at that
        # offset is the identical picture: a piece drawn over another still
        # replaces it exactly, because the paste still happens in order.
        px0 = max(0, int(min(q[0] for q in poly)) - 1)
        py0 = max(0, int(min(q[1] for q in poly)) - 1)
        px1 = min(w, int(max(q[0] for q in poly)) + 2)
        py1 = min(h, int(max(q[1] for q in poly)) + 2)
        if px1 <= px0 or py1 <= py0:
            continue                     # drawn entirely off the sheet
        layer = Image.new("L", (px1 - px0, py1 - py0), 0)
        ImageDraw.Draw(layer).polygon([(q[0] - px0, q[1] - py0) for q in poly], fill=255)
        mask.paste(Image.new("RGBA", (px1 - px0, py1 - py0), rgb + (255,)),
                   (px0, py0), layer)
    return mask, drawn


# --------------------------------------------------- suggestions (ported)

# ⭐️⭐️ A PART OF THE SHEET THE AUTOMATIC PASS IS TOLD TO LEAVE ALONE. The
# designer, 25 August 2026: "one quick tool that would be useful would be the
# ability to mask off a section of any given sheet, so that it doesn't get run
# for suggestions."
#
# ⭐️ Why it is worth more than it looks: the flood is right about cards and
# counters on a plain ground and hopeless about a printed rulebook page, a
# title panel, a colour bar down the margin or the scanner's own shadow — and
# ONE such region is enough to fill a sheet with suggestions nobody wants. The
# person can see at a glance which part that is; no measurement can.
#
# ⚠️ IT MASKS THE SUGGESTIONS AND NOTHING ELSE. It is not a crop, it does not
# touch the scan, it does not stop anybody outlining there by hand, and the
# cut pays it no attention whatever. A region drawn in the wrong place costs
# a suggestion, never a piece.
MAX_SKIPS = 40          # more than anybody would draw; a guard, not a rule


def sheet_skips(s, shape=None):
    """The masked-off regions of a sheet, as whole pixels inside the picture.

    ⚠️ ONE READING OF THEM, because three things ask: the drafting, the record
    kept beside the draft so a changed region re-drafts, and the route that
    hands them to the editor. Written out three times they would disagree
    about the scaling, which is the sort of fault that shows as a mask sitting
    an inch from where it was drawn.
    """
    out = []
    for r in (s or {}).get("skip") or []:
        try:
            x1, y1, x2, y2 = (float(r[0]), float(r[1]), float(r[2]), float(r[3]))
        except (TypeError, ValueError, IndexError):
            continue
        if shape:
            # the editor works in the sheet's own pixels; the PNG on disk is
            # normally the same size, but never assume it
            h, w = shape[:2]
            sx = w / float((s.get("w") or w) or w)
            sy = h / float((s.get("h") or h) or h)
            x1, x2, y1, y2 = x1 * sx, x2 * sx, y1 * sy, y2 * sy
            x1, x2 = max(0, min(w, x1)), max(0, min(w, x2))
            y1, y2 = max(0, min(h, y1)), max(0, min(h, y2))
        lo_x, hi_x = int(round(min(x1, x2))), int(round(max(x1, x2)))
        lo_y, hi_y = int(round(min(y1, y2))), int(round(max(y1, y2)))
        if hi_x - lo_x < 2 or hi_y - lo_y < 2:
            continue
        out.append([lo_x, lo_y, hi_x, hi_y])
    return out[:MAX_SKIPS]

# ⚠️ ONE COPY OF THE TRACING, in `sheets.py`, because the baked Cutting Table
# has to do exactly the same thing to exactly the same sheets and two copies
# would drift (fault 24). What is left here is only which blobs to trace.
contour = sheetlib.contour
thin = sheetlib.thin


def suggest_outlines(rgb, mask_path=None, dpi=DPI):
    """The automatic attempt at a sheet, as outlines with nodes on them.
    From a mask if one is lying about; otherwise from the colour flood,
    which is right for cards and counters on a plain ground and only a
    rough start on terrain."""
    h, w = rgb.shape[:2]
    if mask_path and os.path.exists(mask_path):
        im = Image.open(mask_path).convert("RGBA")
        a = np.asarray(im)
        ink = a[:, :, 3] > 128
        lab, n = sheetlib.label_shapes(ink, a[:, :, :3])
        sx, sy = w / float(im.width), h / float(im.height)
    else:
        found = sheetlib.separate(rgb, None, None)[0]
        if not found:
            return []
        lab = np.zeros((h, w), np.int32)
        for i, p in enumerate(found, 1):
            lab[p["mask"]] = i
        n = len(found)
        sx = sy = 1.0
    # ⚠️ ONE COPY OF WHICH BLOBS BECOME SUGGESTIONS, in `sheets.py`, for the
    # same reason as the tracing itself: the baked table drafts the same
    # sheets and a second copy here would drift (fault 71's lesson, arriving
    # one function further out).
    return sheetlib.trace_all(lab, n, sx, sy, dpi)


# ------------------------------------------------- guessing what a piece is

# ⭐️ NAMING IS THE EXPENSIVE PART, NOT CUTTING. The designer, 22 August 2026, having
# cut a sheet: "naming is always going to be the fiddly bit here as it will
# tend to rely on 3rd party lists etc, or rules manuals which may be tricky to
# comprehend." The room can never know what a piece is CALLED — that comes from
# outside it — but it has already measured every piece to the thousandth of an
# inch, and a shape says a great deal on its own. Two and a half by three and a
# half inches is a playing card in every game ever printed.
#
# ⚠️ IT PROPOSES. IT NEVER DECIDES. Nothing here writes a kind onto a piece;
# the answer is offered with its reason beside it and a person presses the
# button. A wrong guess accepted without looking is worse than no guess, so a
# rule is written down ONLY WHERE THE SHAPE REALLY SETTLES IT. A piece the size
# of a page could be a board, a chart, a player mat or the back of the box —
# so the room says nothing about it at all rather than tossing a coin.
#
# ⚠️ AND IT MUST STAY GENERIC — the constraint on this whole repository. Every
# rule below is about card stock and punchboard, which are bought rather than
# designed, so they are the same in a game about spaceships and a game about
# farming. Nothing here may ever learn what a particular game contains.

# Card stock comes in a handful of sizes and always has. Short side first.
CARD_SIZES = [
    (2.50, 3.50, "a poker card"),          # 63.5 x 88.9mm — much the commonest
    (2.25, 3.50, "a bridge card"),         # 57 x 89mm
    (2.32, 3.62, "a euro card"),           # 59 x 92mm
    (1.75, 2.50, "a mini card"),           # 44.5 x 63.5mm
    (1.73, 2.68, "a small euro card"),     # 44 x 68mm
    (2.75, 4.75, "a tarot card"),          # 70 x 120mm
    (3.50, 5.00, "a large card"),
]
CARD_SLOP = 0.10           # inches: scanning, printing and cutting all drift


def guess_kind(w_in, h_in, cover=None):
    """What this piece probably is, judged on its printed size and its shape
    alone, or None when the measurements do not settle it.

    `cover` is how much of its own bounding box the piece actually fills — the
    number `piece_stats` already works out. It is what tells a circle from a
    square: a rectangle fills its box, a disc fills about 0.79 of it and a
    hexagon about 0.75. Without it the round rules simply stand down.
    """
    try:
        w, h = float(w_in), float(h_in)
    except (TypeError, ValueError):
        return None
    if w <= 0 or h <= 0:
        return None
    short, long_ = min(w, h), max(w, h)
    squareness = short / long_          # 1.0 is a square, small is a splinter
    round_ish = cover is not None and 0.62 <= cover <= 0.90
    boxy = cover is None or cover > 0.90

    def size(a, b):
        return "%.2f × %.2f in" % (a, b)

    # A ruler or a range stick. Nothing else in a game box is this shape.
    # ⚠️ IT MUST BE A SOLID STRIP. Tried against a real game, this rule called
    # two TERRAIN TILES rulers — 1.89 x 6.79in and satisfyingly long and thin, but
    # ragged blobs of terrain filling three quarters of their box rather than
    # printed strips. `boxy` is the whole difference and it costs nothing: the
    # Long range ruler on the same sheet fills 0.99 of its box.
    if boxy and long_ >= 3.0 and squareness <= 0.28:
        return {"kind": "ruler", "sure": True, "why": size(long_, short) +
                " — long and thin, the shape of a ruler or a range stick."}

    # A standard card size, either way up. The strongest signal there is.
    best, gap = None, 9.0
    for cw, ch, called in CARD_SIZES:
        if abs(short - cw) <= CARD_SLOP and abs(long_ - ch) <= CARD_SLOP:
            d = abs(short - cw) + abs(long_ - ch)
            if d < gap:
                best, gap = called, d
    if best and boxy:
        return {"kind": "card", "sure": True,
                "why": size(short, long_) + " — the size of " + best + "."}

    # ⭐️ A CARD THAT WAS NEVER A STANDARD SIZE. A game's publisher does not
    # buy card stock off a shelf: one box's player marker cards are 2.54 x 3.80in,
    # which is not any size above and was being passed over in silence. But a
    # card is a thing held in the hand, so its PROPORTIONS are the same even
    # when its measurements are nobody's standard. Judged on shape rather than
    # a known size, so it says it is the less certain of the two.
    if (boxy and 1.70 <= short <= 3.60 and 2.40 <= long_ <= 5.00
            and 1.30 <= long_ / short <= 1.75):
        return {"kind": "card", "sure": False, "why": size(short, long_) +
                " — no standard size, but held in the hand like a card."}

    # ⭐️ A SMALL CHIT OF PUNCHBOARD — SQUARE, ROUND OR HEXAGONAL, ALL ONE KIND.
    # There were two rules here, offering "counter" for a small square and
    # "token" for a small disc. The designer, shown the result: "not sure I know the
    # difference between a token and a counter tbh!" — and they are right that
    # there is not a firm one. It varies by publisher and often by nothing at
    # all: one box has a 0.74in disc and a 0.66in square on the same sheet,
    # and they do the same job in the same way.
    #
    # ⚠️ THE WHOLE PURPOSE OF THIS FILE IS TO TAKE A DECISION OUT OF NAMING, so
    # a rule that hands one back has failed at the only thing it is for. The
    # shape is not lost — it is said in the reason, the piece's measurements
    # carry it, and the picture shows it — and "token" is still on the Kind box
    # for anybody whose game really does tell them apart.
    if squareness >= 0.86 and 0.30 <= long_ <= 1.30 and (cover is None or cover >= 0.62):
        return {"kind": "counter", "sure": True,
                "why": (size(short, long_) + " — a small square, the size "
                        "counters are punched at.") if boxy else
                       ("%.2f in across with its corners off — a small round "
                        "chit, punched like a counter." % long_)}

    # ⭐️ THERE WAS A RULE HERE THAT OFFERED "tile" FOR A BIGGER SQUARE, AND IT
    # HAS BEEN TAKEN OUT. Tried against a real game of 79 cut pieces it spoke
    # exactly once, and what it called a tile was an Elf Hawkship TURN
    # TEMPLATE. That is the whole argument at the top of this file arriving in
    # person: a 2in square is not only ever one thing, the shape does not
    # settle it, and an offer made to somebody working down a list of three
    # hundred pieces will be taken. Silence is the right answer here.
    # If a game turns up whose floor tiles this would earn its keep on, it is
    # four lines — but put the evidence in the message that brings it back.

    return None


# ---------------------------------------------------------------- projects

class Project:
    DEFAULT_PATHS = {
        "sheets": "sheets", "thumbs": "thumbs", "cache": "cache",
        "outlines": "outlines.json", "masks": "masks", "pieces": "pieces",
        "index": "pieces/index.json", "manifest": "manifest.json",
        "wanted": "wanted.json",
    }

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.file = os.path.join(self.path, "project.json")
        self.meta = read_json(self.file, None)
        if self.meta is None:
            raise FileNotFoundError(self.file)
        self.id = str(self.meta.get("id") or slug(os.path.basename(self.path)))
        self.lock = threading.RLock()

    # ---- paths
    def p(self, key):
        rel = (self.meta.get("paths") or {}).get(key, self.DEFAULT_PATHS[key])
        return rel if os.path.isabs(rel) else os.path.join(self.path, rel)

    @property
    def dpi(self):
        return int(self.meta.get("dpi") or DPI)

    def save_meta(self):
        write_json(self.file, self.meta, indent=1)

    # ---- sheets
    @property
    def sheets(self):
        return self.meta.setdefault("sheets", [])

    def sheet(self, sid):
        for s in self.sheets:
            if s["id"] == sid:
                return s
        return None

    def sheet_png(self, sid):
        return os.path.join(self.p("sheets"), sid + ".png")

    def sheet_jpg(self, sid):
        """The sheet as the editor loads it: a JPEG of the 300dpi master,
        made once."""
        src = self.sheet_png(sid)
        out = os.path.join(self.p("cache"), sid + ".jpg")
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
            os.makedirs(self.p("cache"), exist_ok=True)
            Image.open(src).convert("RGB").save(out, "JPEG", quality=JPEG_Q, optimize=True)
        return out

    def sheet_thumb(self, sid, marks=False):
        """The whole sheet, small — margins and all, because a page with its
        white edge trimmed off is not the page you are looking at.

        ⭐️ WITH `marks`, EVERY PIECE ALREADY OUTLINED IS KNOCKED OUT OF IT:
        darkened, ringed in the colour it was drawn in and numbered, so what
        is still bright on the sheet is what nobody has cut yet. The designer asked
        for it back on 21 August 2026 — the old proof page had it and the room
        had lost it, and it is the one thing a sheet thumbnail is FOR.
        """
        src = self.sheet_png(sid)
        out = os.path.join(self.p("thumbs"), sid + ("-marks.jpg" if marks else ".jpg"))
        newest = os.path.getmtime(src)
        if marks and os.path.exists(self.p("outlines")):
            newest = max(newest, os.path.getmtime(self.p("outlines")))
        if not os.path.exists(out) or os.path.getmtime(out) < newest:
            os.makedirs(self.p("thumbs"), exist_ok=True)
            im = Image.open(src).convert("RGB")
            full_w, full_h = im.size
            im.thumbnail((THUMB_PX, THUMB_PX), Image.LANCZOS)
            if marks:
                im = self._mark_up(im, sid, full_w, full_h)
            im.save(out, "JPEG", quality=82, optimize=True)
        return out

    def _mark_up(self, im, sid, full_w, full_h):
        """Knock the outlined pieces out of a thumbnail of the sheet."""
        pieces = (self.outlines().get("sheets", {}).get(sid) or {}).get("pieces") or []
        if not pieces:
            return im
        k = im.width / float(full_w)
        polys = []
        for pc in pieces:
            pts = pc.get("pts") or []
            if len(pts) < 3:
                continue
            polys.append((pc, [(x * k, y * k) for x, y in flatten(pts, pc.get("curve", False))]))
        if not polys:
            return im
        dark = Image.new("RGB", im.size, (11, 16, 22))
        cut = Image.new("L", im.size, 0)
        pen = ImageDraw.Draw(cut)
        for _, poly in polys:
            pen.polygon(poly, fill=255)
        im = Image.composite(Image.blend(im, dark, 0.82), im, cut)
        edge = ImageDraw.Draw(im)
        for n, (pc, poly) in enumerate(polys, 1):
            ink = INKS[int(pc.get("ink", 0)) % len(INKS)]
            rgb = tuple(int(ink[i:i + 2], 16) for i in (1, 3, 5))
            edge.line(poly + [poly[0]], fill=rgb, width=2)
            cx = sum(q[0] for q in poly) / len(poly)
            cy = sum(q[1] for q in poly) / len(poly)
            # a number a person can read at thumbnail size: dark disc, light figure
            r = 9
            edge.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(11, 16, 22), outline=rgb)
            edge.text((cx - (3 if n < 10 else 6), cy - 5), str(n), fill=rgb)
        return im

    # ---- the four stores
    def outlines(self):
        book = read_json(self.p("outlines"), {})
        if "sheets" not in book:
            book = {"tool": "cutting-table", "version": 2, "sheets": {}}
        return book

    # ⭐️⭐️ THE THREE FILES THAT CANNOT BE REBUILT KEEP THEIR OWN HISTORY.
    #
    # The designer, 24 August 2026, on being told to commit their checklist to git more
    # often: "I'm afraid this means nothing to me - it needs to be automated if
    # it needs to happen." Quite right. A safety net somebody has to remember
    # to use is not a safety net, it is a second thing to forget — and the room
    # had just eaten two of their components through a bug of mine. What saved
    # them was git, which they do not use and should not have to.
    #
    # So: before any of the three irreplaceable stores is written, the copy
    # that is about to be replaced is kept. Everything else in a project can be
    # rebuilt from the sheets and the outlines; these three cannot.
    KEEP_HISTORY = 60          # copies per file, oldest thrown away first

    def history_dir(self):
        return os.path.join(self.path, "history")

    def keep_a_copy(self, key):
        """Put today's copy of `key` aside before it is overwritten."""
        src = self.p(key)
        if not os.path.exists(src):
            return
        try:
            with open(src, "rb") as fh:
                now = fh.read()
            folder = self.history_dir()
            os.makedirs(folder, exist_ok=True)
            mine = sorted(f for f in os.listdir(folder)
                          if f.startswith(key + "-") and f.endswith(".json"))
            # ⚠️ nothing is kept unless it actually differs from the newest
            # copy: the room saves a moment after every edit, and a shelf of
            # sixty identical files would push the real history off the end
            if mine:
                with open(os.path.join(folder, mine[-1]), "rb") as fh:
                    if fh.read() == now:
                        return
            stamp = time.strftime("%Y%m%d-%H%M%S")
            out = os.path.join(folder, "%s-%s.json" % (key, stamp))
            n = 1
            while os.path.exists(out):          # two saves in one second
                out = os.path.join(folder, "%s-%s-%d.json" % (key, stamp, n))
                n += 1
            with open(out, "wb") as fh:
                fh.write(now)
            mine = sorted(f for f in os.listdir(folder)
                          if f.startswith(key + "-") and f.endswith(".json"))
            for old in mine[:-self.KEEP_HISTORY]:
                try:
                    os.remove(os.path.join(folder, old))
                except OSError:
                    pass
        except OSError:
            # ⚠️ keeping history must NEVER stop the work being saved. A full
            # disk or a read-only folder loses the safety net, not the work.
            pass

    def save_store(self, key, blob, indent=1):
        """Write one of the three irreplaceable stores, keeping the copy it
        replaces — and doing nothing at all when nothing has changed.

        ⚠️ A SAVE THAT CHANGES NOTHING MUST KEEP NOTHING. The room saves a
        moment after every edit and several of those carry the same content;
        without this, a shelf of sixty identical copies would push the real
        history off the end, which is the one thing the history exists to
        prevent."""
        text = json.dumps(blob, indent=indent, ensure_ascii=False,
                          sort_keys=False) + "\n"
        path = self.p(key)
        try:
            with open(path, encoding="utf-8") as fh:
                if fh.read() == text:
                    return False
        except (OSError, ValueError):
            pass
        self.keep_a_copy(key)
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
        return True

    def save_outlines(self, book):
        self.save_store("outlines", book, indent=1)

    def index(self):
        return read_json(self.p("index"), {"pieces": {}})

    def save_index(self, idx):
        write_json(self.p("index"), idx, indent=1)

    def manifest(self):
        m = read_json(self.p("manifest"), {})
        m.setdefault("pieces", {})
        return m

    def save_manifest(self, m):
        self.save_store("manifest", m, indent=2)

    def wanted(self):
        w = read_json(self.p("wanted"), {})
        w.setdefault("items", [])
        return w

    def save_wanted(self, w):
        self.save_store("wanted", w, indent=1)

    # ---- pieces on disk
    def piece_files(self):
        d = self.p("pieces")
        if not os.path.isdir(d):
            return []
        return sorted(f[:-4] for f in os.listdir(d) if f.endswith(".png"))

    # ⭐️ THE DESIGNER, 22 August 2026: "Binning a piece shouldn't be destructive — it
    # should be merely to hide a piece from the main manifest. eg there are two
    # identical terrain tiles. The game only needs to store one, even though it
    # could be placed twice in an actual game."
    #
    # So a set-aside piece is MOVED, not deleted, into a `spare` folder inside
    # the pieces store. That one move is what keeps it out of the hand-over:
    # anything reading the store globs the folder itself and does not recurse,
    # so a spare is invisible to it without the room having to know anything
    # about who is reading. Its name, kind, note and component link all stay in
    # the manifest, marked `spare`, and the mark follows the piece across a
    # re-cut the way a name does — otherwise every re-cut would resurrect the
    # nineteen duplicates you had just put away.
    # ⭐️ WHICH BOX A SHEET CAME OUT OF, and what that box is called. The room
    # has always worked this out on the page (`bookOf()` in project.html) —
    # the same rule, which is the part that matters: the box is the sheet id
    # with the page number taken off (fault 42).
    # ⭐️⭐️ ONE BOX OUT OF THE GAME, RATHER THAN THE WHOLE GAME. The designer,
    # 26 August 2026: "I'd like to be able to just export a set of cut pieces,
    # rather than everything in one project folder."
    #
    # ⭐️ A box is the room's own unit of work — it is what Sheets, Pieces,
    # Match and the Checklist all gather by (fault 42) — so it is the right
    # thing to be able to hand over on its own. A game is 161 sheets and four
    # boxes; wanting one of them is the normal case, not a special one.
    def book_label(self, book):
        """What a box of sheets is CALLED. ⚠️ One reading of it, because the
        folder is named from it and the README says it — two would disagree
        the moment somebody renamed a box."""
        told = (self.meta.get("books") or {}).get(book)
        return str(told).strip() if told and str(told).strip() else str(book or "")

    def books(self):
        """Every box in this game, in order, with its name and how many
        sheets it holds."""
        out, seen = [], {}
        for s in self.sheets:
            b = self.book_of(s.get("id"))
            if b not in seen:
                seen[b] = {"id": b, "name": self.book_label(b), "sheets": 0}
                out.append(seen[b])
            seen[b]["sheets"] += 1
        return out

    def pieces_of_book(self, book):
        """The stems cut from one box of sheets.

        ⚠️ A piece the index knows nothing about belongs to NO box (fault 39 —
        a project's pieces folder may hold files the room did not put there),
        so it is left out of a set rather than swept into one.
        """
        idx = self.index().get("pieces", {})
        return {st for st, meta in idx.items()
                if self.book_of(meta.get("sheet") or "") == book}

    def book_of(self, sid):
        # ⭐️ A SET CAN BE SAID RATHER THAN DERIVED. The designer, 25 August 2026:
        # "I just imported 12 new files... assuming they would all stay
        # together as a single set of 12 sheets, but they've all turned into
        # separate sets." A sheet may now carry the set it belongs to, and the
        # id it was filed under is only the fallback — which means sheets can
        # be gathered into one set WITHOUT their ids changing, and pieces are
        # named from those ids.
        told = str((self.sheet(sid) or {}).get("book") or "").strip()
        if told:
            return told
        m = re.match(r"^(.+)-\d+$", str(sid or ""))
        return m.group(1) if m else str(sid or "")

    # ⭐️⭐️ WHAT IS BEING CUT NOW, AND WHAT WAS ONLY UPLOADED FOR LATER.
    # The designer, 25 August 2026: "I find the overall checklist % isn't very
    # helpful... I've decided to not yet cut some pieces which belong to
    # advanced rule sets that I don't want to bring in the v1 of the game.
    # Maybe I need a user-defined divide between live cutting and a sheet
    # backlog/future cutting which I may have uploaded only for convenience?"
    #
    # Quite so, and it is one mark rather than a new kind of project: a set is
    # either being cut now or PUT BY. `later` is a list of keys — "book:<id>"
    # for a box of sheets, "set:<id>" for a set of components that has no box
    # of its own — and every count in the room reads it.
    #
    # ⚠️ NOTHING IS HIDDEN AND NOTHING IS DELETED. The sheets stay, the
    # components stay, anything already cut still counts. All the mark does is
    # take a set out of the figure that says how far you have got, because a
    # percentage that includes work you have decided not to do can never
    # reach 100 and so tells you nothing (fault 50's lesson about a flag
    # nobody can clear, arriving on a number instead of a list).
    def later_keys(self):
        return set(self.meta.get("later") or [])

    def book_later(self, book):
        return ("book:" + str(book or "")) in self.later_keys()

    # ⭐️⭐️ AND THE OTHER END OF THE SAME SHELF: A BOX THAT IS FINISHED AND
    # FILED AWAY. The designer, 1 September 2026, having cut and named every
    # component in a game's core box and ticked every one of its sheets:
    # "There should now be a way to move those (not out of sight) but just to
    # ensure they don't pop up anymore, no need for them to populate
    # dropdowns, or the sheets page anymore etc."
    #
    # ⚠️⚠️ IT IS NOT THE SAME MARK AS `later`, AND MUST NOT BE MADE ONE.
    # Put by for later means NOT CUT YET, and is left out of the figures
    # because a percentage counting work you have decided not to do can never
    # reach 100 (fault 68). Filed away means DONE, and it goes on counting as
    # done. A box filed under `later` would be reported by the end-of-job
    # check as never cut — a lie about the very work the mark is celebrating,
    # and precisely the sort of two-readings-of-one-flag that fault 50 warns
    # about.
    #
    # ⭐️ WHAT IT DOES IS PUT THINGS LAST, NOT HIDE THEM. Nothing is deleted,
    # nothing moves on the disk, and every list can still be pointed at a
    # filed box — it simply stops being in the way. The word is the designer's
    # own, 23 August 2026: "I waste time wading through lots of cut and filed
    # sheets before I find my next sheet to cut."
    def filed_keys(self):
        return set(self.meta.get("filed") or [])

    def book_filed(self, book):
        return ("book:" + str(book or "")) in self.filed_keys()

    # ⚠️ ONE RULE, ASKED IN ONE PLACE (fault 24, seven times over). A set of
    # components made from a box of sheets — which is how they are normally
    # made, see fault 64 — answers to that BOX, so putting the box by on the
    # Sheets page and putting the set by on the checklist are the same switch
    # rather than two that will disagree. Only a set with no box of its own
    # carries the mark itself.
    # ⚠️ And BOTH marks ask it. Written out once for `later` and again for
    # `filed`, the two copies would drift, and the one that drifted would be
    # the one that quietly marked the wrong box.
    @staticmethod
    def group_key(g):
        book = str((g or {}).get("book") or "").strip()
        if book:
            return "book:" + book
        return "set:" + str((g or {}).get("id") or "")

    def group_later(self, g, later=None):
        later = self.later_keys() if later is None else later
        return self.group_key(g) in later

    def group_filed(self, g, filed=None):
        filed = self.filed_keys() if filed is None else filed
        return self.group_key(g) in filed

    def sheet_title(self, s):
        """What to CALL this sheet.

        ⭐️ The designer, 25 August 2026: "I need to rename them from their current
        file names (which are lots of nonsense)." A sheet's label is made from
        the file it arrived in — `a-scan-of-the-box.pdf p.7` — so naming the box
        has to reach the sheets as well, or the nonsense is still on every
        card and every tab of the rail.

        ⚠️ It is a DISPLAY name and nothing is rewritten: the label in
        `project.json` is left exactly as it was, so clearing the box's name
        puts every sheet straight back. And a label somebody has typed
        themselves is left alone — only one that is still the file's own name
        is swapped, which is what the slug test is for.
        """
        label = s.get("label") or s.get("id") or ""
        named = (self.meta.get("books") or {}).get(self.book_of(s.get("id")))
        if not named:
            return label
        m = re.match(r"^(.*?)(\s(?:p\.\d+|·\s*picture\s*\d+))$", label)
        front = m.group(1) if m else label
        # ⚠️ BOTH SPELLINGS. Sheet ids made before the two slug functions were
        # untangled kept the file's extension in them ("a-scan-pdf-01"), and
        # those sheets are on people's disks. Either reading counts as "this
        # label is still the file's own name".
        book = self.book_of(s.get("id"))
        if slug(front, 40) == book or file_slug(front) == book:
            return named + (m.group(2) if m else "")
        return label

    def spare_dir(self):
        return os.path.join(self.p("pieces"), "spare")

    def piece_path(self, stem):
        "Where a piece in play lives — and where the cutter always writes."
        return os.path.join(self.p("pieces"), stem + ".png")

    def spare_path(self, stem):
        return os.path.join(self.spare_dir(), stem + ".png")

    def piece_file(self, stem):
        "Wherever the piece actually is, in play or set aside."
        live = self.piece_path(stem)
        if os.path.exists(live):
            return live
        aside = self.spare_path(stem)
        return aside if os.path.exists(aside) else live

    def spare_stems(self):
        "Every piece actually sitting in the spare folder, whatever any list says."
        d = self.spare_dir()
        if not os.path.isdir(d):
            return set()
        return {f[:-4] for f in os.listdir(d) if f.endswith(".png")}

    # ⚠️⚠️ THE FOLDER IS THE TRUTH; THE MARK IS ONLY THE RECORD OF IT — AND THE
    # RECORD WENT MISSING FOR EXACTLY THE PIECES THIS IS FOR. The designer, 24
    # August 2026: "setting pieces aside seems pretty temperamental — I just
    # tried to get rid of multiple copies of [one piece], but didn't seem to
    # work, either in bulk when suggested, or individually when selected."
    #
    # It had half worked, every time, which is worse. `set_aside` wrote the
    # mark only onto pieces the manifest ALREADY knew — and a duplicate you
    # want rid of is precisely the piece nobody has bothered to name, so it
    # has no manifest entry at all. The file moved; nothing was written down;
    # and the room reads the mark, so the piece came back onto the screen
    # undimmed and unflagged, looking exactly as though the press had done
    # nothing. Three of the designer's pieces were sitting in that state.
    # ⚠️ And it is not only cosmetic: a re-cut reads the mark to put a piece
    # straight back into the spare folder, so an unmarked spare would be
    # handed back to the game the next time its sheet was cut — fault 19's
    # whole subject.
    #
    # So: whatever is in the folder is set aside, and the manifest is made to
    # say so. Called where the folder is read (the pieces list) and where it
    # is about to be destroyed (a re-cut sweeps the last cut out of it).
    def adopt_spares(self):
        loose = self.spare_stems()
        if not loose:
            return 0
        man = self.manifest()
        book = man.setdefault("pieces", {})
        n = 0
        for st in sorted(loose):
            if not (book.get(st) or {}).get("spare"):
                book.setdefault(st, {})["spare"] = True
                n += 1
        if n:
            self.save_manifest(man)
        return n

    def set_aside(self, stems, aside=True):
        "Move pieces between the store and its `spare` folder. Deletes nothing."
        moved = 0
        man = self.manifest()
        idx = self.index()
        for st in stems:
            src = self.piece_path(st) if aside else self.spare_path(st)
            dst = self.spare_path(st) if aside else self.piece_path(st)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                os.replace(src, dst)
                moved += 1
            # ⚠️ THE MANIFEST IS TOLD EVEN IF IT HAD NEVER HEARD OF THE PIECE.
            # `if st in book` was the whole fault above: an unnamed duplicate
            # has no entry, so the one piece this feature exists for was the
            # one piece it did not record.
            book = man.setdefault("pieces", {})
            if aside:
                book.setdefault(st, {})["spare"] = True
            elif st in book:
                book[st].pop("spare", None)
                if not book[st]:
                    book.pop(st)          # an entry holding nothing is not an entry
            # the index says where a piece was CUT from, so it is not invented
            # here — only kept in step where it already knows the piece
            ib = idx.get("pieces", {})
            if st in ib:
                if aside:
                    ib[st]["spare"] = True
                else:
                    ib[st].pop("spare", None)
        self.save_manifest(man)
        self.save_index(idx)
        return moved

    def piece_thumb(self, stem):
        src = self.piece_file(stem)
        out = os.path.join(self.p("cache"), "piece-" + stem + ".png")
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
            os.makedirs(self.p("cache"), exist_ok=True)
            im = Image.open(src).convert("RGBA")
            im.thumbnail((PIECE_THUMB_PX, PIECE_THUMB_PX), Image.LANCZOS)
            im.save(out, "PNG", optimize=True)
        return out

    def piece_stats(self, stem, dpi=None, sheet_size=None, box=None):
        """Everything the review needs to know about a cut piece, worked out
        once and kept: its printed size, a 64-bit look-alike hash, how much of
        its bounding box is actually inked, and whether it runs off the edge of
        the sheet it was cut from.

        ⭐️ THE HASH IS WHAT MAKES "you have cut this counter six times" a
        question the room can answer. A component sheet prints twenty of each
        counter and only ONE is wanted; without this, spotting the repeats is
        the person's job and it is a tedious one.
        """
        path = self.piece_file(stem)
        if not os.path.exists(path):
            return None
        cache = os.path.join(self.p("cache"), "stats.json")
        book = read_json(cache, {})
        mt = int(os.path.getmtime(path))
        got = book.get(stem)
        if got and got.get("mt") == mt and got.get("v") == 3:
            return got
        im = Image.open(path).convert("RGBA")
        alpha = im.getchannel("A")
        solid = alpha.point(lambda v: 255 if v >= 24 else 0)
        bb = solid.getbbox()
        if bb is None:
            return None
        im = im.crop(bb)
        solid = solid.crop(bb)
        d = float(dpi or self.dpi)
        # ⚠️ A LOOK-ALIKE HASH ON ITS OWN IS NOT ENOUGH, and the first version
        # proved it on real cardboard: at 8x8 grey it called NO MOVEMENT and NO
        # FIRING the same counter, and one game's two sides' ship cards one
        # card. They ARE the same shape, the same size and the same layout —
        # what tells them apart is the ink. So: a finer 12x12 grid (144 bits),
        # and the piece's mean colour carried beside it. Two pieces are the same
        # component only if the pattern AND the colour agree.
        grid = 12
        small = im.convert("L").resize((grid, grid), Image.LANCZOS)
        px = list(small.getdata())
        mean = sum(px) / float(grid * grid)
        bits = 0
        for i, v in enumerate(px):
            if v >= mean:
                bits |= 1 << i
        tiny = im.convert("RGB").resize((6, 6), Image.LANCZOS)
        cols = list(tiny.getdata())
        rgb = [round(sum(c[i] for c in cols) / float(len(cols))) for i in range(3)]
        hist = solid.histogram()
        cover = hist[255] / float(max(1, solid.width * solid.height))
        rec = {"v": 3, "mt": mt,
               "w_in": round(im.width / d, 3), "h_in": round(im.height / d, 3),
               "w": im.width, "h": im.height,
               "hash": "%036x" % bits, "bits": grid * grid, "rgb": rgb,
               "cover": round(cover, 3)}
        if sheet_size and box:
            near = 6
            rec["edge"] = bool(box[0] <= near or box[1] <= near
                               or box[2] >= sheet_size[0] - near
                               or box[3] >= sheet_size[1] - near)
        book[stem] = rec
        write_json(cache, book, indent=0)
        return rec

    def measure_piece(self, stem, dpi=None):
        """A piece's true printed size, off its own alpha."""
        p = self.piece_file(stem)
        if not os.path.exists(p):
            return None
        im = Image.open(p).convert("RGBA")
        box = im.getchannel("A").point(lambda v: 255 if v >= 24 else 0).getbbox()
        if box is None:
            return None
        d = float(dpi or self.dpi)
        return {"w_in": round((box[2] - box[0]) / d, 3),
                "h_in": round((box[3] - box[1]) / d, 3),
                "w": box[2] - box[0], "h": box[3] - box[1]}

    # ---- status
    def cut_state(self, sid, book, idx, by_sheet):
        """How one sheet stands: outlines on it, pieces cut off it, and
        whether the outlines have MOVED since that cut.

        ⚠️⚠️ ONE RULE, because four things ask it and a fifth acted on
        no rule at all. *Cut every outlined sheet* re-cut the whole game
        every time — the designer, 26 August 2026, having outlined 22 new
        sheets: "it then started cutting every single page I have ever
        outlined in the entire game." Its own tip said it cut sheets that
        "[have] not been cut yet" and the note beside it counted exactly
        those, while the room behind it cut everything with an outline on
        it. Fault 24 for the eleventh time, and fault 16's shape as well:
        the words and the action were worked out separately, so they
        disagreed.
        """
        o = book.get(sid) or {}
        cut = by_sheet.get(sid, [])
        stale = bool(o.get("stamp") and cut and
                     o.get("stamp", 0) > (idx.get(cut[0], {}).get("cut_at") or 0))
        return len(o.get("pieces") or []), cut, stale

    def waiting_to_cut(self, only=None):
        """The sheets that really are waiting: outlined, and either never cut
        or outlined again since. `only` holds it to a list of sheet ids — the
        sheets the person is actually looking at.

        ⚠️ It INTERSECTS rather than obeys: a page open for an hour may name
        a sheet another tab has since cut, and cutting it again would be the
        very waste this exists to stop. An id this game does not have is
        ignored rather than refused, for the same reason.
        """
        book = self.outlines().get("sheets", {})
        idx = self.index().get("pieces", {})
        by_sheet = {}
        for stem, v in idx.items():
            by_sheet.setdefault(v.get("sheet", ""), []).append(stem)
        want = None if only is None else set(only)
        out = []
        for s in self.sheets:
            if want is not None and s["id"] not in want:
                continue
            n_out, cut, stale = self.cut_state(s["id"], book, idx, by_sheet)
            if n_out and (not cut or stale):
                out.append(s["id"])
        return out

    def status(self):
        book = self.outlines().get("sheets", {})
        idx = self.index().get("pieces", {})
        by_sheet = {}
        for stem, v in idx.items():
            by_sheet.setdefault(v.get("sheet", ""), []).append(stem)
        man = self.manifest().get("pieces", {})
        sheets = []
        for s in self.sheets:
            o = book.get(s["id"]) or {}
            n_out, cut, stale = self.cut_state(s["id"], book, idx, by_sheet)
            # a piece set aside is not waiting to be named — it is put away
            named = sum(1 for st in cut
                        if (man.get(st) or {}).get("name")
                        or (man.get(st) or {}).get("spare"))
            # ⭐️ the box's name reaches the sheets themselves — see
            # sheet_title(). The stored label is untouched.
            sheets.append(dict(s, label=self.sheet_title(s),
                               outlines=n_out, cut=len(cut), named=named,
                               # the thumbnail is drawn from the outlines, so the
                               # page has to know when they last moved
                               stamp=int(o.get("stamp") or 0),
                               stale=stale))
        wanted = self.wanted_status(man, idx)
        return {
            "id": self.id, "name": self.meta.get("name", self.id),
            "game": self.meta.get("game", ""), "notes": self.meta.get("notes", ""),
            "path": self.path, "dpi": self.dpi,
            "sheets": sheets,
            "pieces": len(idx) if idx else len(self.piece_files()),
            "named": sum(1 for st in man
                         if man[st].get("name") or man[st].get("spare")),
            "wanted": wanted["summary"],
            # ⭐️ what each BOX of sheets is called. A sheet id comes from the
            # file it was imported from, so a game arrives as "a-box-scan-07"
            # and the room has been calling the box that ever since — see the
            # `book` route for why the id itself is never touched.
            "books": self.meta.get("books") or {},
            # ⭐️ where each box of sheets would be written if it were taken
            # away on its own. ⚠️ The page must not work this name out for
            # itself: the room owns it (export_dir), and two spellings of it
            # would show one folder and fill another (fault 24).
            "sets": [{"id": b["id"],
                      "folder": os.path.basename(export_dir(self, b["id"]))}
                     for b in self.books()],
            # ⭐️ the sets put by for later — "book:<id>" for a box of sheets,
            # "set:<id>" for a set of components with no box. See later_keys().
            "later": sorted(self.later_keys()),
            # ⭐️ the sets FINISHED and filed away — same key shape, opposite
            # meaning. See filed_keys() for why it is not the same list.
            "filed": sorted(self.filed_keys()),
            "hooks": [{"id": h.get("id"), "label": h.get("label")}
                      for h in (self.meta.get("hooks") or [])],
            "kinds": KINDS,
            "types": self.meta.get("types") or {},
        }

    @staticmethod
    def counts_each(item):
        """Is this component counted as ALL DIFFERENT — one piece per unit of
        its quantity — or as one design printed that many times?

        ⚠️ ONE COPY OF THE RULE. Two things ask: how many pieces the component
        needs (`wanted_needs`), and the word on the button that switches it
        (`each_on`, sent to the page). Written out twice, the label and the
        number it produces would eventually disagree — fault 24, which has
        bitten this codebase a dozen times. See `wanted_needs` for why a deck
        answers yes without anybody pressing anything.
        """
        if item.get("each"):
            return True          # all different, however that came to be said
        # ⚠️⚠️ AND `each: false` IS NOT AN ANSWER — IT IS THE DEFAULT WRITTEN
        # DOWN. `new_wanted()` stamps `each` on every component it makes,
        # from a pasted contents list, a split line or a group of cut pieces,
        # so a real game's list is full of `false` that nobody ever chose.
        # Reading that as a decision would have made this whole rule do
        # NOTHING on the one list it was asked for — which is fault 54, the
        # easy question in place of the real one, and it was found by the
        # check going green while the real path could never reach it.
        # `each_said` is written only when somebody presses the button.
        if item.get("each_said"):
            return False
        return str(item.get("kind") or "").strip().lower() == "deck"

    @staticmethod
    def wanted_needs(item):
        """How many pieces this component wants cut before it is accounted for.

        ⭐️ ONE IS ENOUGH, UNLESS EVERY ONE IS DIFFERENT. A sheet prints
        twenty-six damage counters and the game repeats one for ever, so `26
        Damage counters` wants ONE piece cut and always has — that is the rule
        the whole room is built on. A deck of twenty-four damage cards is
        twenty-four DIFFERENT pieces of card, and one of them is not the deck.

        Nothing in a printed contents list tells the two apart, so the person
        says which by turning `each` on, and the room never guesses it.
        The designer, 23 August 2026: "build checklist counting deck against quantity
        — it's then my responsibility to ensure I have the correct number of
        cards to fill each deck."

        ⭐️⭐️ EXCEPT WHERE THEY HAVE ALREADY SAID IT, BY CALLING IT A DECK.
        The designer, 26 August 2026: "when something is a deck it should also
        report that each component dropped is unique in the checklist ie '[n]
        needed' rather than '1 needed'." Quite so, and this is not the room
        guessing: `kind` is a word the person typed, and **a deck of thirty-two
        cards is thirty-two different cards by its nature**. The room already
        said so — the end-of-job check reports a deck counted as one card as a
        FINDING (fault 52) — so it was asserting this and then not acting on
        it, which is half a report.

        ⚠️⚠️ AND ONLY `deck`, WHICH IS EVIDENCE, NOT REASONING. Fault 52 tried
        this rule against the designer's real list with `card` included as
        well: the findings went from nine to twenty and **all eleven it added
        were wrong** — two designs of one component, and a card printed twice.
        A deck is many different cards; a line of cards is not.

        ⚠️ IT IS A DEFAULT, NOT A DECISION. Pressing "one is enough" on a deck
        is obeyed and stays obeyed, so the button can always be pressed back —
        a rule that could only be turned ON would be fault 50's shape.
        """
        if not Project.counts_each(item):
            return 1
        digits = re.sub(r"[^0-9]", "", str(item.get("qty") or ""))
        try:
            return max(1, int(digits)) if digits else 1
        except ValueError:
            return 1

    def wanted_status(self, man=None, idx=None):
        """Every wanted item with what has been cut against it: an explicit
        link on a piece wins; failing that the item's own match pattern
        against the names people have typed."""
        man = man if man is not None else self.manifest().get("pieces", {})
        book = self.wanted()
        items = book.get("items", [])
        linked = {}
        for stem, v in man.items():
            w = v.get("wanted")
            if w:
                linked.setdefault(w, []).append(stem)
        # ⭐️ ONE DESIGN, CUT ONCE, WANTED TWENTY TIMES — AND THE DECK IS FULL.
        # The designer, 24 August 2026, of a deck of thirteen different cards in
        # which one of them is printed twenty times, thirty-two cards in all:
        # "I have marked the 20x component, but [the deck] reads — relatively
        # justifiably — 13 of 32. How do I fix given the deck is technically
        # complete?"
        #
        # `copies` on a piece already says the game wants that design twenty
        # times (fault 47) and the checklist simply was not reading it, so a
        # deck that really is complete could never reach its own quantity and
        # the box could never read as finished. A piece FILLS as many of the
        # wanted quantity as the game wants of it, so thirteen pieces fill
        # thirty-two cards and the deck says so.
        #
        # ⚠️ Fault 47 warns that these are two different questions — the
        # checklist counts what you have CUT, `copies` tells the game what to
        # do with it — and they still are: the room does not cut anything
        # twice and nothing sets `copies` by itself, any more than anything
        # sets `each`. This only stops the room asking for pieces that would
        # be identical to ones it already has.
        def fills(stems):
            n = 0
            for stem in stems:
                try:
                    c = int((man.get(stem) or {}).get("copies") or 1)
                except (TypeError, ValueError):
                    c = 1
                n += max(1, c)
            return n

        out = []
        done = 0
        for it in items:
            iid = it.get("id", "")
            have = list(linked.get(iid, []))
            guess = []
            pat = it.get("match")
            if not have and pat:
                try:
                    rx = re.compile(pat)
                except re.error:
                    rx = None
                if rx:
                    for stem, v in man.items():
                        text = " ".join(str(v.get(k, "")) for k in ("name", "id", "use"))
                        if text.strip() and rx.search(text):
                            guess.append(stem)
            # ⚠️ A DECK HALF FULL IS NOT A DECK. `part` is its own answer:
            # something has been cut against this component but not enough of
            # it, which is neither "done" nor "nothing yet" and must not be
            # rounded into either.
            #
            # ⚠️⚠️ AND THE COUNT COMES FIRST. Written the other way round —
            # asking "does any piece's name match?" before "are there enough of
            # them?" — a deck of twenty-four with NOTHING cut read as probably
            # cut and the whole checklist showed 100%, because three pieces
            # happened to be called "Damage card 01" and up. A guess may only
            # speak for a whole component when there are enough of it to go
            # round.
            need = self.wanted_needs(it)
            got = fills(have)
            if got >= need:
                state = "cut"
            elif have:
                state = "part"
            elif fills(guess) >= need:
                state = "probably"
            elif guess:
                state = "part"
            else:
                state = "missing"
            if state in ("cut", "probably"):
                done += 1
            # ⭐️ `got` counts CARDS and `cut` counts PIECES, and where a design
            # is wanted more than once they differ — so both are sent, or a
            # deck reading "32 of 32" off thirteen pictures looks like a
            # miscount to the person who cut them.
            # ⭐️ `each_on` is the room's ANSWER to "is this counted as all
            # different?", so the page never re-derives it — the label on the
            # button and the number it produces cannot disagree. Fault 24.
            out.append(dict(it, pieces=have, guesses=guess, state=state,
                            need=need, got=got, cut_pieces=len(have),
                            each_on=Project.counts_each(it)))
        groups = book.get("groups") or []
        # ⭐️⭐️ A FIGURE FOR EACH SET, AND A HEADLINE OVER WHAT IS BEING CUT
        # NOW. The designer, 25 August 2026: "I find the overall checklist %
        # isn't very helpful - would be preferable to have a % completion per
        # set of files uploaded for cutting."
        #
        # One number over a whole game answers a question nobody is asking:
        # the work is done a box at a time (fault 42), so what is wanted is
        # how far THIS box has got — and a box deliberately not being cut yet
        # must not drag the figure down for ever.
        later = self.later_keys()
        put_by = {g.get("id", ""): self.group_later(g, later) for g in groups}
        # ⭐️ and which sets are FINISHED and filed away. It changes no figure
        # — a filed set is done and counts as done — but every list in the
        # room puts it last, so the page has to be told. See filed_keys().
        filed = self.filed_keys()
        away = {g.get("id", ""): self.group_filed(g, filed) for g in groups}

        def is_later(gid):
            if gid in put_by:
                return put_by[gid]
            return ("set:" + str(gid or "")) in later

        def is_filed(gid):
            if gid in away:
                return away[gid]
            return ("set:" + str(gid or "")) in filed

        per_group = {}
        for it in out:
            g = it.get("group", "")
            d = per_group.setdefault(g, {"total": 0, "done": 0, "later": is_later(g),
                                         "filed": is_filed(g)})
            d["total"] += 1
            d["done"] += 1 if it["state"] in ("cut", "probably") else 0
        for d in per_group.values():
            d["pct"] = round(100.0 * d["done"] / d["total"]) if d["total"] else 0
        # ⚠️ TWO NUMBERS THAT DISAGREE IN SILENCE ARE WORSE THAN ONE THAT IS
        # BLUNT (fault 67). The whole-game figure is still here and still
        # true; the live one is what the room leads with, and the page says
        # in as many words what the difference between them is made of.
        # ⭐️ WHICH FIELDS THE ROOM WORKS OUT, told to the page. It has to
        # know, because a save must refresh these and keep everything else the
        # page holds (see saveWantedAll) — and a second copy of this list in
        # JavaScript is fault 24 with a saved store underneath it.
        live = [i for i in out if not is_later(i.get("group", ""))]
        live_done = sum(1 for i in live if i["state"] in ("cut", "probably"))
        # ⭐️ and the same sum in CARDS as well as in components, because a
        # deck of twenty-four counts once here and is twenty-four evenings of
        # nothing if you only ever read the component figure. Over what is
        # being cut now, so it cannot contradict the figure above it.
        want_pieces = sum(i["need"] for i in live)
        got_pieces = sum(min(i["got"], i["need"]) for i in live)
        return {"items": out, "groups": groups, "kinds": book.get("kinds") or KINDS,
                "note": book.get("note", ""), "later": sorted(later),
                "filed": sorted(filed),
                "worked_out": list(WORKED_OUT),
                "summary": {"total": len(out), "done": done,
                            "pct": (round(100.0 * done / len(out)) if out else 0),
                            "live_total": len(live), "live_done": live_done,
                            "live_pct": (round(100.0 * live_done / len(live))
                                         if live else 0),
                            "later_total": len(out) - len(live),
                            "later_sets": len([1 for d in per_group.values()
                                               if d["later"] and d["total"]]),
                            "pieces_wanted": want_pieces, "pieces_cut": got_pieces,
                            "groups": per_group}}

    # ⭐️⭐️ THE LAST LOOK BEFORE THE PIECES LEAVE THE ROOM. The designer, 24 August
    # 2026: "I want (once I've done my cutting work) to be able to run a
    # verification check against the original component index - a secondary
    # check to ensure we have every piece cut. Is that possible?"
    #
    # Most of it existed already — the checklist knows what the box should
    # hold and what has been cut against each line. What did not exist is the
    # END-OF-JOB form of it: not a screen to work in but a REPORT you read
    # once, with the box open in front of you, and act on.
    #
    # ⭐️ And the half the room could not do at all: the INVERSE. A cut piece
    # that answers to nothing on the list is either something the contents
    # list forgot, or a piece cut twice, or something cut from the wrong
    # sheet — and every one of them is worth a look before the hand-over.
    #
    # ⚠️ IT REPORTS; IT NEVER FIXES. The same rule as the kinds, the
    # look-alikes and the splitting: it says what it sees and leaves every
    # decision to the person, because every one of these is a judgement.
    def cut_review(self, book=None):
        """⭐️ `book` narrows the whole report to one box of sheets — its
        pieces, and the checklist sets that answer to it — so a set handed
        over on its own carries a check about itself and not about the game.

        ⚠️ ONLY A BOX SOMEBODY HAS ACTUALLY PICKED counts here. Fault 51 works
        out which set a box answers to from the links already made, for
        ORDERING, and its rule is that it orders and never hides; using that
        guess to decide what a report is about would break it. So a set counts
        as this box's only if its `book` was set outright (fault 64).
        """
        man = self.manifest().get("pieces", {})
        idx = self.index().get("pieces", {})
        st = self.wanted_status(man=man)
        items = st["items"]
        names = {g.get("id"): (g.get("name") or g.get("id"))
                 for g in (st.get("groups") or [])}
        mine = None
        if book:
            ours = {g.get("id") for g in (st.get("groups") or [])
                    if str(g.get("book") or "") == book}
            items = [it for it in items if it.get("group", "") in ours]
            mine = self.pieces_of_book(book)

        def about(it):
            return {"id": it.get("id", ""), "name": it.get("name") or it.get("id"),
                    "kind": it.get("kind") or "", "group": it.get("group", ""),
                    "got": it["got"], "need": it["need"],
                    "pieces": it["pieces"], "guesses": it["guesses"]}

        # ⭐️ A SET PUT BY FOR LATER IS NOT A SET FALLING SHORT. The designer
        # has some sheets in the game they have decided not to cut yet, and a
        # report that lists every one of those components as missing is a
        # report they stop reading — which is fault 50's lesson (a list nobody
        # can shorten is a list nobody opens) arriving on the end-of-job check.
        # So they are counted on their own, at the end, and nothing above
        # counts them.
        per_group = (st.get("summary") or {}).get("groups") or {}
        by_group, order = {}, []
        for it in items:
            g = it.get("group", "")
            if g not in by_group:
                by_group[g] = {"id": g, "name": names.get(g, g) or "Everything else",
                               "later": bool((per_group.get(g) or {}).get("later")),
                               # ⭐️ a filed set is still checked and still
                               # counted — filing is a CLAIM that it is
                               # finished, and this report is the only thing
                               # that checks it (fault 81). All the mark does
                               # here is say so on the band.
                               "filed": bool((per_group.get(g) or {}).get("filed")),
                               "total": 0, "accounted": 0,
                               "missing": [], "part": [], "probably": []}
                order.append(g)
            band = by_group[g]
            band["total"] += 1
            if it["state"] in ("cut", "probably"):
                band["accounted"] += 1
            if it["state"] in ("missing", "part", "probably"):
                band[it["state"]].append(about(it))
        sets = [by_group[g] for g in sorted(order, key=lambda x: (x == "", x))]
        live_sets = [x for x in sets if not x["later"]]
        put_by = [x for x in sets if x["later"]]

        # ⭐️⭐️ A DECK COUNTED AS ONE CARD WILL READ AS DONE ON THE FIRST CARD
        # CUT. This came straight out of reading a real game's list: NINE
        # of its twelve decks had never been set to "all different", so each of
        # them wanted ONE piece — and a 32-card deck with one card cut would
        # have shown as accounted for, and the box as complete when it is not.
        # That is fault 36's whole subject, and nothing in the room said so.
        #
        # ⚠️ THE TEST IS THE KIND, NOT THE NUMBER. "26 Damage counters" has the
        # same shape — a quantity of 26 wanting one piece — and is exactly
        # RIGHT, because one design is printed twenty-six times. Flag the
        # number alone and every counter in the game becomes a finding, which
        # is worse than saying nothing at all.
        #
        # ⚠️⚠️ AND ONLY A DECK. Written to include `card` as well and read
        # against the real list, it went from nine findings to twenty — and the
        # eleven it added were all wrong: that game's two player marker cards are two
        # DESIGNS of one component (fault 18), and its nine identically worded
        # armament card lines are one card printed twice. Both count once,
        # quite correctly. A DECK is many different cards by its nature; a line
        # of cards is not. Reading the game's own data changed this rule twice.
        loose = []
        for it in items:
            if (per_group.get(it.get("group", "")) or {}).get("later"):
                continue          # not being cut yet; see the sets put by, below
            if it["need"] > 1 or (it.get("kind") or "") != "deck":
                continue
            digits = re.sub(r"[^0-9]", "", str(it.get("qty") or ""))
            if digits and int(digits) > 1:
                loose.append(dict(about(it), qty=it.get("qty") or "",
                                  set_name=names.get(it.get("group", ""),
                                                     it.get("group", ""))))

        # ⭐️ Every piece the room has, in play or set aside — the same reading
        # as the Pieces page, so the two cannot disagree about what exists.
        stems = sorted(set(idx) | set(self.piece_files()) |
                       set(k for k, v in man.items() if v.get("spare")))
        if mine is not None:
            stems = [st_ for st_ in stems if st_ in mine]
        spoken_for = set()
        for it in items:
            spoken_for.update(it["pieces"])
            spoken_for.update(it["guesses"])
        orphans, aside, unnamed, held = [], [], [], []
        for stem in stems:
            d = man.get(stem, {})
            meta = idx.get(stem, {})
            row = {"stem": stem, "name": d.get("name") or "",
                   "kind": d.get("kind") or "", "sheet": meta.get("sheet", "")}
            if d.get("spare"):
                aside.append(row)
                continue
            if not row["name"]:
                unnamed.append(row)
            if d.get("hold"):
                held.append(dict(row, why=d.get("hold")))
            if stem not in spoken_for:
                orphans.append(row)
        # ⚠️ WITH NO CONTENTS LIST EVERY PIECE IS AN ORPHAN, which is not a
        # finding, it is the absence of a list. Say that instead of printing
        # two hundred and twenty-one names under a heading that reads as a
        # fault. The checklist has always been optional and this must not
        # quietly make it compulsory.
        has_list = bool(items)
        if not has_list:
            orphans = []
        # ⭐️ SAY WHAT AN ORPHAN MEASURES. A piece that answers to nothing on
        # the contents list is very often recognisable from its size alone —
        # a 0.6in square is a counter, a 2.5 x 3.5in rectangle is a card — so
        # a column of bare stems is a column nobody can read, and the same
        # column with a size beside it is a list somebody can work down with
        # the box open. ⚠️ It costs nothing on a game whose Pieces page has
        # ever been opened: piece_stats() keeps its answer in cache/stats.json
        # and this is the same record that page reads.
        for row in orphans:
            rec = self.piece_stats(row["stem"]) or {}
            if rec.get("w_in"):
                row["w_in"], row["h_in"] = rec["w_in"], rec["h_in"]
        s = st["summary"]
        # ⚠️ THE HEADLINE FIGURE IS WORKED OUT OVER THE WHOLE GAME, and for a
        # report about ONE box that would be a plain lie — "44 of 221" over a
        # folder holding one set. Work it out again from the bands that are
        # actually in this report.
        live_total, live_done, live_pct = (
            s["live_total"], s["live_done"], s["live_pct"])
        if mine is not None:
            live_total = sum(x["total"] for x in live_sets)
            live_done = sum(x["accounted"] for x in live_sets)
            live_pct = (round(100.0 * live_done / live_total) if live_total else 100)
        return {"has_list": has_list, "sets": live_sets, "put_by": put_by,
                "orphans": orphans,
                "aside": aside, "unnamed": unnamed, "held": held,
                "loose_decks": loose,
                "summary": {
                    "components": live_total, "accounted": live_done,
                    "pct": live_pct,
                    "later_sets": len(put_by),
                    "later_components": sum(x["total"] for x in put_by),
                    "later_left": sum(x["total"] - x["accounted"] for x in put_by),
                    "pieces_wanted": s["pieces_wanted"],
                    "pieces_cut": s["pieces_cut"],
                    "pieces": len(stems) - len(aside),
                    "missing": sum(len(x["missing"]) for x in live_sets),
                    "part": sum(len(x["part"]) for x in live_sets),
                    "probably": sum(len(x["probably"]) for x in live_sets),
                    "orphans": len(orphans), "aside": len(aside),
                    "unnamed": len(unnamed), "held": len(held),
                    "loose_decks": len(loose)}}


# ---------------------------------------------------------------- registry

class Registry:
    def __init__(self, home):
        self.home = os.path.abspath(os.path.expanduser(home))
        os.makedirs(self.home, exist_ok=True)
        self.file = os.path.join(self.home, "projects.json")
        # ⭐️ The shelf of kept shapes sits BESIDE the projects rather than
        # inside one of them, because that is the point of it: a door from
        # one dungeon game and a door from another are the same piece of
        # card, and a shape drawn once should be usable in either.
        self.shapes_file = os.path.join(self.home, "shapes.json")
        self.shapes_lock = threading.RLock()
        self._cache = {}

    def shapes(self):
        book = read_json(self.shapes_file, {})
        if not isinstance(book.get("shapes"), list):
            book = {"tool": "cutting-table", "version": 1, "shapes": []}
        return book

    def save_shapes(self, book):
        write_json(self.shapes_file, book, indent=1)

    def paths(self):
        reg = read_json(self.file, {"projects": []})
        paths = []
        for p in reg.get("projects", []):
            p = os.path.expanduser(p if isinstance(p, str) else p.get("path", ""))
            if p and os.path.exists(os.path.join(p, "project.json")):
                paths.append(os.path.abspath(p))
        for name in sorted(os.listdir(self.home)):
            d = os.path.join(self.home, name)
            if os.path.isdir(d) and os.path.exists(os.path.join(d, "project.json")):
                if os.path.abspath(d) not in paths:
                    paths.append(os.path.abspath(d))
        return paths

    def register(self, path):
        reg = read_json(self.file, {"projects": []})
        path = os.path.abspath(path)
        if path not in [os.path.abspath(os.path.expanduser(p)) for p in reg.get("projects", [])]:
            reg.setdefault("projects", []).append(path)
            write_json(self.file, reg)

    def projects(self):
        out = []
        for p in self.paths():
            try:
                pr = self._cache.get(p) or Project(p)
                self._cache[p] = pr
                out.append(pr)
            except (FileNotFoundError, ValueError):
                continue
        return out

    def get(self, pid):
        for pr in self.projects():
            if pr.id == pid:
                pr.meta = read_json(pr.file, pr.meta)     # pick up edits by hand
                return pr
        return None

    def create(self, name, game=""):
        base = slug(name, 40) or "project"
        pid, n = base, 1
        while os.path.exists(os.path.join(self.home, pid)) or any(p.id == pid for p in self.projects()):
            n += 1
            pid = "%s-%d" % (base, n)
        d = os.path.join(self.home, pid)
        os.makedirs(d)
        write_json(os.path.join(d, "project.json"),
                   {"id": pid, "name": name, "game": game or name, "dpi": DPI,
                    "notes": "", "paths": {}, "hooks": [], "sheets": []})
        write_json(os.path.join(d, "wanted.json"),
                   {"game": game or name, "note": "", "kinds": KINDS,
                    "groups": [{"id": "core", "name": "The box"}], "items": []})
        return Project(d)


# ------------------------------------------------------- the shelf of shapes

# ⭐️ The designer, 23 August 2026, on a game whose pieces repeat: "I will need to cut a
# number of pieces that are different, but also EXACTLY the same shape — I
# only want to create that shape mask ONCE." Whole games are printed on one
# die. So a shape can be kept and laid down again, and because it is kept in
# INCHES rather than in one sheet's pixels it crosses to a sheet scanned at
# another resolution and to another game entirely.
#
# ⚠️ This comes off a web page, so nothing in it is believed. A shape that
# does not measure up is refused with a reason rather than written to a file
# every project on the machine then reads.

SHAPE_MAX_IN = 60.0        # inches: bigger than any sheet anybody scans
SHAPE_MAX_NODES = 4000     # a freehand coastline, and then some


def clean_shape(raw):
    """A shape as the shelf will keep it, or a plain sentence saying why not."""
    if not isinstance(raw, dict):
        return "that is not a shape"
    pts = raw.get("pts")
    if not isinstance(pts, list) or len(pts) < 3:
        return "a shape needs at least three nodes"
    if len(pts) > SHAPE_MAX_NODES:
        return "that shape has more nodes than the shelf will hold"
    out = []
    for p in pts:
        if not isinstance(p, (list, tuple)) or len(p) < 2:
            return "one of the nodes is not a point"
        try:
            x, y = float(p[0]), float(p[1])
        except (TypeError, ValueError):
            return "one of the nodes is not a number"
        if not (math.isfinite(x) and math.isfinite(y)):
            return "one of the nodes is not a number"
        if abs(x) > SHAPE_MAX_IN or abs(y) > SHAPE_MAX_IN:
            return "that shape is bigger than any sheet"
        out.append([round(x, 5), round(y, 5)])
    size = []
    for k in ("w", "h"):
        try:
            v = float(raw.get(k))
        except (TypeError, ValueError):
            return "the shape does not say how big it is"
        if not math.isfinite(v) or v <= 0 or v > SHAPE_MAX_IN:
            return "the shape does not say how big it is"
        size.append(round(v, 5))
    name = str(raw.get("name") or "").strip()[:80] or "a shape"
    return {"name": name, "curve": bool(raw.get("curve")),
            "w": size[0], "h": size[1], "pts": out}


def starred(shape):
    """Which projects have marked this shape as one of theirs."""
    return [x for x in (shape.get("stars") or []) if isinstance(x, str)]


def shelf_keep(reg, shape, project="", game=""):
    """Put a clean shape on the shelf and hand back the whole shelf. Both ways
    in — the table's own button and a piece already cut — come through here,
    because a set of rules written out twice will disagree with itself
    (fault 24)."""
    with reg.shapes_lock:
        book = reg.shapes()
        shapes = book.get("shapes") or []
        shape["id"] = "s%x%03x" % (now_ms(), len(shapes) % 4096)
        shape["project"] = str(project or "")[:80]
        shape["game"] = str(game or "")[:80]
        shape["made"] = now_ms()
        # ⭐️ A shape is one of THIS game's from the moment it is drawn there.
        shape["stars"] = [shape["project"]] if shape["project"] else []
        shapes.insert(0, shape)
        book["shapes"] = shapes
        reg.save_shapes(book)
    return shapes


def shape_of_cut_piece(project, stem, name=""):
    """The shape of a piece that has ALREADY been cut, or a plain sentence
    saying why not.

    ⭐️ The designer, 23 August 2026: "I should be able to save a shape cut from a
    piece already cut - or is that too difficult?" It is not difficult at
    all, because nothing has to be read back out of the picture: the outline
    that made the piece is still in outlines.json, and the piece's own record
    says which sheet it came off and which box it filled. The outline is
    matched to the piece by that box — the same trick that keeps names on
    their pieces across a re-cut — so what is kept is the line that was
    drawn, exactly, curves and all."""
    entry = (project.index().get("pieces") or {}).get(stem)
    if not entry:
        return "there is no cut piece by that name"
    sid = entry.get("sheet")
    rec = (project.outlines().get("sheets") or {}).get(sid) or {}
    box = entry.get("box") or []
    best, score = None, 0.0
    for pc in rec.get("pieces") or []:
        pts = pc.get("pts") or []
        if len(pts) < 3:
            continue
        poly = flatten(pts, pc.get("curve", False))
        xs = [q[0] for q in poly]
        ys = [q[1] for q in poly]
        got = overlap([min(xs), min(ys), max(xs), max(ys)], box) if box else 0.0
        if got > score:
            best, score = (pc, min(xs), min(ys), max(xs), max(ys)), got
    if best is None or score < 0.6:
        # ⚠️ Say which of the two it is. An outline redrawn since the cut is a
        # different situation from a sheet nobody has outlined at all.
        return ("the outline this piece was cut from is not on %s any more, "
                "so there is no shape left to keep" % (sid or "its sheet"))
    pc, x0, y0, x1, y1 = best
    dpi = float(entry.get("dpi") or 0) or float(rec.get("dpi") or 0) or float(project.dpi)
    shape = clean_shape({
        "name": name or (project.manifest().get("pieces", {}).get(stem) or {}).get("name") or stem,
        "curve": pc.get("curve", False),
        "w": (x1 - x0) / dpi, "h": (y1 - y0) / dpi,
        "pts": [[(q[0] - x0) / dpi, (q[1] - y0) / dpi] for q in pc.get("pts")],
    })
    return shape


# ------------------------------------------------------------------ import

def render_pdf_pages(pdf, out_dir, dpi, progress=None):
    """Every page of a PDF at dpi, as PNGs — ONE pdftoppm run, which parses
    the file once (a forty-page, twenty-megabyte book took ten seconds a page
    when each page was its own run) — with progress read off the pages as
    they land."""
    n = 0
    try:
        info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=False).stdout
        m = re.search(r"^Pages:\s+(\d+)", info, re.M)
        n = int(m.group(1)) if m else 0
    except FileNotFoundError:
        pass
    if progress:
        progress(0, n, "rendering %d page%s at %d dpi" % (n, "" if n == 1 else "s", dpi))
    stem = os.path.join(out_dir, "p")
    proc = subprocess.Popen(["pdftoppm", "-r", str(dpi), "-png", pdf, stem],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    seen = -1
    while proc.poll() is None:
        time.sleep(0.8)
        done = len([f for f in os.listdir(out_dir) if f.startswith("p-") and f.endswith(".png")])
        # the page being written is not finished: count one fewer
        shown = max(0, done - 1)
        if shown != seen and progress:
            seen = shown
            progress(shown, n, "rendered page %d of %d" % (shown, n))
    if proc.returncode != 0:
        raise RuntimeError("pdftoppm failed: %s" % proc.stderr.read().decode("utf-8", "replace")[-200:])
    out = []
    for f in sorted(f for f in os.listdir(out_dir) if f.startswith("p-") and f.endswith(".png")):
        mm = re.match(r"p-(\d+)\.png$", f)
        if not mm:
            continue
        page = int(mm.group(1))
        final = os.path.join(out_dir, "page-%03d.png" % page)
        os.replace(os.path.join(out_dir, f), final)
        out.append((page, final))
    if progress:
        progress(len(out), n or len(out), "rendered %d pages" % len(out))
    return out


def docx_images(path, out_dir):
    """The pictures inside a Word file, in the order they are stored."""
    out = []
    with zipfile.ZipFile(path) as z:
        names = sorted(n for n in z.namelist() if n.startswith("word/media/"))
        for i, n in enumerate(names, 1):
            ext = os.path.splitext(n)[1].lower()
            if ext not in IMAGE_EXT:
                continue                     # EMF/WMF and friends: not raster
            data = z.read(n)
            try:
                im = Image.open(io.BytesIO(data))
                im.load()
            except Exception:                # noqa: BLE001
                continue
            dst = os.path.join(out_dir, "image-%03d.png" % i)
            im.convert("RGB").save(dst, "PNG")
            out.append((i, dst))
    return out


def doc_to_docx(path, out_dir):
    """macOS textutil turns an old binary .doc into .docx, pictures and all."""
    dst = os.path.join(out_dir, "converted.docx")
    r = subprocess.run(["textutil", "-convert", "docx", "-output", dst, path],
                       capture_output=True, check=False)
    if r.returncode != 0 or not os.path.exists(dst):
        raise RuntimeError("could not convert the .doc (textutil): %s"
                           % r.stderr.decode("utf-8", "replace")[-200:])
    return dst


DRIVE_ID = re.compile(r"/file/d/([A-Za-z0-9_-]{10,})|[?&]id=([A-Za-z0-9_-]{10,})|/folders/([A-Za-z0-9_-]{10,})")

# ⭐️ A GOOGLE DOC IS NOT A FILE, IT IS A THING GOOGLE WILL MAKE A FILE OUT OF.
# The designer, 24 August 2026, trying one: a document, a sheet or a set of slides
# has no download at its own address — the link opens the editor, and what
# comes back to anything else asking is the editor's own web PAGE. Asked to
# export, the same document comes back as a PDF, which is exactly what the
# room wants. So the room asks for the export rather than reporting a
# perfectly good link as unshared (which is what it used to say, and it was
# wrong: the file was shared, it simply is not a file).
# ⚠️ Only the plain `/d/<id>` form: a PUBLISHED link (`/d/e/<id>/pub`) is a
# different address with no export, and is left exactly as it is.
DOC_EXPORT = re.compile(r"//docs\.google\.com/(document|presentation|spreadsheets)"
                        r"/d/(?!e/)([A-Za-z0-9_-]{10,})")


def human_bytes(n):
    if n >= 1e6:
        return "%.1f MB" % (n / 1e6)
    if n >= 1000:
        return "%d kB" % round(n / 1000)
    return "%d bytes" % n


def fetch_url(url, progress=None):
    """Pull a file down from a link. Returns (filename, bytes).

    ⭐️ GOOGLE DRIVE LINKS ARE UNDERSTOOD, which is the whole point of this:
    The designer's scans live in Drive and the alternative is downloading each one by
    hand before dropping it on the page. A share link
    (`.../file/d/<id>/view`) is turned into the direct download Drive serves at
    `drive.usercontent.google.com`, with `confirm=t` so the "this file is large,
    scan it anyway?" page is not what comes back.

    ⚠️ IT ONLY WORKS FOR A FILE SHARED "ANYONE WITH THE LINK". A private file
    answers with a sign-in PAGE and HTTP 200 — which would otherwise be saved
    as a perfectly valid, perfectly useless HTML file — so an HTML answer to a
    request for a document is reported as what it is.

    ⚠️ A FOLDER LINK IS NOT A FILE. Drive has no plain download for a folder;
    say so rather than fetching its listing page.
    """
    url = url.strip()
    if not re.match(r"^https?://", url):
        raise RuntimeError("that is not a link — it should start with http:// or https://")
    name = None
    doc = DOC_EXPORT.search(url) if "docs.google.com" in url else None
    if doc:
        kind, doc_id = doc.group(1), doc.group(2)
        url = ("https://docs.google.com/%s/d/%s/export?format=pdf" % (kind, doc_id))
        name = "%s-%s.pdf" % (kind, doc_id[:8])
    m = DRIVE_ID.search(url) if (not doc and "google.com" in url) else None
    if m:
        if m.group(3):
            raise RuntimeError(
                "that is a link to a Drive FOLDER, and Drive has no download for a "
                "whole folder. Open the folder, copy the link of one file, and paste "
                "that — or select the files in Drive, download them as a ZIP, and drop "
                "the ZIP on this page.")
        file_id = m.group(1) or m.group(2)
        url = ("https://drive.usercontent.google.com/download"
               "?id=%s&export=download&confirm=t" % file_id)
    if progress:
        progress(0, 0, "asking the link for the file")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh) CuttingRoom/1",
        "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
            disp = r.headers.get("Content-Disposition") or ""
            mm = re.search(r'filename\*?=(?:UTF-8\'\'|")?([^";]+)', disp)
            if mm:
                name = urllib.parse.unquote(mm.group(1)).strip('"')
            # ⭐️⭐️ READ IT IN PIECES, AND SAY SO AS IT COMES. The designer, 24
            # August 2026: "status says 'Fetching...' but would be much more
            # useful if that were an actual progress bar or at the very least
            # something a little more animated so i can see if it's stalled."
            # `r.read()` in one call is a wait of unknown length with nothing
            # to look at — and the one question a person has during it is the
            # one thing a frozen word cannot answer. Read in blocks and count
            # them: a number that keeps moving IS the answer to "has it
            # stalled?", and it costs nothing.
            # ⚠️ Content-Length is often missing (Drive and Docs both send the
            # export as it makes it), so the count has to read sensibly with
            # no total to compare against — hence "so far".
            size = 0
            try:
                size = int(r.headers.get("Content-Length") or 0)
            except ValueError:
                size = 0
            # ⚠️ `read1`, NOT `read`: read(n) waits until it has all n bytes,
            # so on a slow link the count jumps in lumps and sits perfectly
            # still between them — which is the very thing being fixed here.
            # read1 hands back whatever has arrived, so the number moves when
            # the bytes move.
            reader = getattr(r, "read1", None) or r.read
            blocks, got = [], 0
            while True:
                block = reader(65536)
                if not block:
                    break
                blocks.append(block)
                got += len(block)
                if progress:
                    progress(got, size, "downloading — %s%s" % (
                        human_bytes(got),
                        (" of %s" % human_bytes(size)) if size else " so far"))
            data = b"".join(blocks)
    except urllib.error.HTTPError as exc:
        raise RuntimeError("the link answered %s %s" % (exc.code, exc.reason))
    except urllib.error.URLError as exc:
        raise RuntimeError("could not reach that link: %s" % exc.reason)
    if ctype in ("text/html", "application/xhtml+xml"):
        raise RuntimeError(
            "that link gave back a web page rather than a file. On Google that "
            "nearly always means it is not shared: set it to \"Anyone with the "
            "link\" and paste it again. Otherwise, download it and drop it on "
            "this page.")
    if not name:
        name = os.path.basename(urllib.parse.urlsplit(url).path) or "download"
        ext = {"application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg",
               "image/tiff": ".tif", "application/zip": ".zip",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
               "application/msword": ".doc"}.get(ctype)
        if ext and not name.lower().endswith(ext):
            name += ext
    if progress:
        progress(1, 1, "fetched %s (%.1f MB)" % (name, len(data) / 1e6))
    return name, data


def import_into(project, filename, data, prefix=None, progress=None, report=None):
    """Turn an uploaded file into sheets. Returns the sheet records made.

    ⚠️⚠️ `report` IS HOW THE ROOM SAYS WHAT IT DID, and it exists because this
    function has two quite different behaviours that looked identical from the
    outside. A file whose name matches one already imported does NOT make new
    sheets: it REPLACES the pictures of the sheets that file made before,
    keeping their ids, their labels and — the dangerous part — their outlines.

    The designer, 1 September 2026, having exported a different scan of a
    different box under a name they had used before: "Tile Sheets.pdf was
    processed but isn't showing." It had been processed. It had quietly
    replaced thirteen sheets, and the page said "13 sheets added", which is
    fault 81's shape — a sentence claiming something nothing was checking.

    ⭐️ Refreshing in place is worth keeping: it is how somebody swaps a better
    scan in under outlines they have already drawn. But it must be SAID, and
    where the sheets being replaced carry outlines it must be said loudly,
    because those outlines now lie over a picture that may be nothing like the
    one they were drawn on. See fault 94.

    Callers pass a dict; it comes back with `added` and `refreshed` in it, and
    is threaded through the zip recursion so a folder reports as one thing.
    """
    if report is not None:
        report.setdefault("added", [])
        report.setdefault("refreshed", [])
    name = os.path.basename(filename)
    ext = os.path.splitext(name)[1].lower()
    base = prefix or slug(name)
    made = []
    with tempfile.TemporaryDirectory() as work:
        src = os.path.join(work, "in" + ext)
        with open(src, "wb") as fh:
            fh.write(data)
        pages = []                               # (number, png path, label)
        if ext == ".pdf":
            for page, path in render_pdf_pages(src, work, project.dpi, progress):
                pages.append((page, path, "%s p.%d" % (name[:-4], page)))
        elif ext in IMAGE_EXT:
            im = Image.open(src)
            im.load()
            dst = os.path.join(work, "image.png")
            im.convert("RGB").save(dst, "PNG")
            pages.append((None, dst, os.path.splitext(name)[0]))
        elif ext == ".docx":
            for i, path in docx_images(src, work):
                pages.append((i, path, "%s · picture %d" % (os.path.splitext(name)[0], i)))
        elif ext == ".doc":
            docx = doc_to_docx(src, work)
            for i, path in docx_images(docx, work):
                pages.append((i, path, "%s · picture %d" % (os.path.splitext(name)[0], i)))
        elif ext == ".zip":
            with zipfile.ZipFile(src) as z:
                for member in z.namelist():
                    mext = os.path.splitext(member)[1].lower()
                    if member.startswith("__MACOSX") or os.path.basename(member).startswith("."):
                        continue
                    if mext in IMAGE_EXT + (".pdf", ".docx", ".doc"):
                        made += import_into(project, os.path.basename(member), z.read(member),
                                            None, progress, report)
            return made
        else:
            raise RuntimeError("I do not know how to read a %s file. PDF, PNG, JPEG, TIFF, DOCX, DOC or ZIP." % (ext or "nameless"))
        if not pages:
            raise RuntimeError("nothing in %s could be turned into a sheet" % name)

        with project.lock:
            os.makedirs(project.p("sheets"), exist_ok=True)
            existing = {s["id"] for s in project.sheets}
            # A prefix already in use from a different file keeps numbering
            # on from where it left off, so two scans do not collide.
            used_nums = [int(s["id"].rsplit("-", 1)[1]) for s in project.sheets
                         if s["id"].startswith(base + "-") and s["id"].rsplit("-", 1)[1].isdigit()]
            for page, path, label in pages:
                if page is not None and (base + "-%02d" % page) in existing and \
                        any(s.get("source") == name for s in project.sheets if s["id"] == base + "-%02d" % page):
                    # ⚠️⚠️ THE SAME FILE NAME AGAIN, so this REPLACES the
                    # picture of a sheet that already exists rather than making
                    # a new one — keeping its id, its label and its outlines.
                    # That is how a better scan is swapped in under work
                    # already done, and it is also how a completely different
                    # scan silently overwrote thirteen sheets. It is only safe
                    # because the room now says so. See fault 94.
                    sid = base + "-%02d" % page
                    if report is not None:
                        drew = len(((project.outlines().get("sheets") or {}).get(sid)
                                    or {}).get("pieces") or [])
                        report["refreshed"].append(
                            {"id": sid,
                             "label": project.sheet_title(project.sheet(sid) or {"id": sid}),
                             "outlines": drew})
                else:
                    n = (max(used_nums) + 1) if used_nums else 1
                    while (base + "-%02d" % n) in existing:
                        n += 1
                    sid = base + "-%02d" % n
                    used_nums.append(n)
                im = Image.open(path)
                w, h = im.size
                shutil.copyfile(path, project.sheet_png(sid))
                rec = project.sheet(sid)
                if rec is None:
                    rec = {"id": sid, "label": label, "name": "", "w": w, "h": h,
                           "done": False, "rot": 0, "source": name, "added": now_ms()}
                    project.sheets.append(rec)
                    existing.add(sid)
                    if report is not None:
                        report["added"].append(sid)
                else:
                    rec.update({"w": w, "h": h, "source": name})
                for stale in (os.path.join(project.p("cache"), sid + ".jpg"),
                              os.path.join(project.p("thumbs"), sid + ".jpg"),
                              os.path.join(project.p("cache"), sid + ".suggest.json")):
                    if os.path.exists(stale):
                        os.remove(stale)
                made.append(rec)
            project.save_meta()
    return made


# --------------------------------------------------------------------- cut

def cut_sheet(project, sid, only=None):
    """Paint the outlines into a mask, cut every piece off the sheet, measure
    it, file it — and keep the names that were already given to pieces on
    this sheet, even where a re-cut renumbers them.

    ⭐️⭐️ `only` IS ONE OUTLINE, MENDED. The designer, 26 August 2026: "If I'm
    mending a piece, it seems obvious that default should be to just recut that
    specific piece no?" Quite so — a sheet holds forty and thirty-nine of them
    were right.

    ⚠️⚠️ THE WHOLE SHEET IS STILL PAINTED AND LABELLED, because a piece's
    NUMBER is its position in reading order over every piece on the sheet: cut
    one outline on its own and it would be `_00` whatever it really is, which
    is precisely the renaming this function exists to prevent. What `only`
    saves is the cutting, measuring and writing of the other thirty-nine — on
    a big scan that is nearly all of the work.

    ⚠️ AND IT FALLS BACK TO THE WHOLE SHEET THE MOMENT ANYTHING ELSE MOVED.
    If the mend changed how many pieces the sheet has, or moved this one past
    a neighbour in reading order, every number below it shifts and the names
    must follow — so the full path runs and the answer says so. A fast path
    that quietly left the store inconsistent would be far worse than a slow
    one.
    """
    with project.lock:
        s = project.sheet(sid)
        if s is None:
            raise RuntimeError("no such sheet: " + sid)
        book = project.outlines()
        o = (book.get("sheets") or {}).get(sid) or {}
        pcs = o.get("pieces") or []
        if not pcs:
            raise RuntimeError("nothing is outlined on %s yet" % s.get("label", sid))
        rgb = np.asarray(Image.open(project.sheet_png(sid)).convert("RGB"))
        h, w = rgb.shape[:2]
        mask, drawn = paint_mask(pcs, (w, h))
        os.makedirs(project.p("masks"), exist_ok=True)
        mask.save(os.path.join(project.p("masks"), sid + ".png"))
        a = np.asarray(mask)
        ink = a[:, :, 3] > 128
        colour = a[:, :, :3]
        lab, n = sheetlib.label_shapes(ink, colour)
        # ⚠️ `drawn` — these outlines were made by a person, so nothing here
        # is thrown away for being too big or too small. See keep().
        found = sheetlib.keep(lab, n, (h, w), drawn=True)
        # ⚠️⚠️ A CUT THAT KEEPS NOTHING MUST SAY SO. The designer, 26 August
        # 2026: "I have outlined the single large component on the sheet. But
        # it won't cut." The cut had run perfectly, thrown the one piece away
        # for covering 90% of the sheet, written an empty answer and reported
        # success — so there was nothing to read and nothing to go on. Silence
        # reads as a broken button (fault 58).
        if not found:
            raise RuntimeError(
                "%d outline%s on %s, but nothing came off it. The outlines may "
                "be drawn over one another, or lie outside the picture."
                % (drawn, "" if drawn == 1 else "s", s.get("label", sid)))
        found.sort(key=lambda p: (p["box"][1] // (project.dpi // 2), p["box"][0]))

        stem = stem_of(sid)
        idx = project.index()
        old = {k: v for k, v in idx.get("pieces", {}).items() if v.get("sheet") == sid}
        os.makedirs(project.p("pieces"), exist_ok=True)

        # ⭐️⭐️ ONE MENDED OUTLINE — see the note at the top of this function.
        # Which of the found pieces IS the mended outline is answered the way
        # names are carried across a re-cut: by how much the boxes overlap.
        # ⚠️ It gives up rather than guessing, and a full cut is always the
        # safe answer, so every road out of here that is not certain takes it.
        single = None
        if only is not None and 0 <= only < len(pcs):
            want = outline_box(pcs[only])
            if want and len(found) == len(old):
                best, score = None, 0.0
                for i, f in enumerate(found):
                    q = overlap(list(f["box"]), want)
                    if q > score:
                        best, score = i, q
                if best is not None and score >= 0.6:
                    was = old.get("%s_%02d" % (stem, best))
                    # ⚠️ and only if THAT slot already held a piece in the same
                    # place: if the mend moved it past a neighbour, the numbers
                    # below it all shift and the names have to follow
                    if was and overlap(list(found[best]["box"]), was.get("box") or []) >= 0.6:
                        single = best

        # ⚠️ Anything in the spare folder is written down as set aside BEFORE
        # the sweep takes it away: the mark is what carries "put this one back
        # in the spare folder" across the re-cut, and the folder is about to
        # stop being able to say so.
        project.adopt_spares()
        # sweep the last cut of this sheet — from the spare folder too, or a
        # piece put away on the previous cut would linger with stale artwork
        # ⚠️⚠️ NOT WHEN ONE PIECE IS BEING MENDED. This is the line that makes
        # a re-cut safe by starting from nothing, and it is exactly the line
        # the fast path must not run: the other thirty-nine pieces are staying
        # where they are. The one being mended is removed by name below.
        if single is None:
            for folder in (project.p("pieces"), project.spare_dir()):
                for f in (os.listdir(folder) if os.path.isdir(folder) else []):
                    if f.startswith(stem + "_") and f.endswith(".png"):
                        os.remove(os.path.join(folder, f))
        dpi = float(o.get("dpi") or 0) or float(project.dpi)

        # ⭐️ THE FAST PATH: cut this one piece, leave its neighbours' files,
        # names and index entries exactly as they are. The stem is unchanged,
        # so the name follows without anything having to be rewritten.
        if single is not None:
            p = found[single]
            name = "%s_%02d" % (stem, single)
            was_spare = (project.manifest().get("pieces", {}).get(name) or {}).get("spare")
            for folder in (project.p("pieces"), project.spare_dir()):
                f = os.path.join(folder, name + ".png")
                if os.path.exists(f):
                    os.remove(f)
            piece = cutter.cut(rgb, p["mask"], p["box"], dict(cutter.DEFAULTS))
            piece.save(project.piece_path(name))
            entry = {"name": name, "w": piece.width, "h": piece.height, "sheet": sid,
                     "box": [int(v) for v in p["box"]], "dpi": dpi, "cut_at": now_ms()}
            bx0, by0, bx1, by1 = p["box"]
            sub = colour[by0:by1, bx0:bx1][p["mask"][by0:by1, bx0:bx1]]
            if len(sub):
                packed = (sub[:, 0].astype(np.uint32) * 65536 +
                          sub[:, 1].astype(np.uint32) * 256 + sub[:, 2])
                vals, counts = np.unique(packed, return_counts=True)
                best = int(vals[counts.argmax()])
                entry["ink_rgb"] = [best >> 16, (best >> 8) & 255, best & 255]
            idx["pieces"][name] = {k: v for k, v in entry.items() if k != "name"}
            project.save_index(idx)
            # ⚠️ a piece that was set aside goes back to the spare folder, the
            # same as on a full cut — or mending it would hand the game back a
            # duplicate that had been put away
            if was_spare:
                project.set_aside([name], True)
            thumb = os.path.join(project.p("cache"), "piece-" + name + ".png")
            if os.path.exists(thumb):
                os.remove(thumb)
            mm = project.measure_piece(name, dpi) or {}
            named = (project.manifest().get("pieces", {}).get(name) or {}).get("name", "")
            return {"made": [dict(entry, w_in=mm.get("w_in"), h_in=mm.get("h_in"),
                                  named=named)],
                    "renames": {}, "drawn": drawn, "retired": {}, "one": name}

        made = []
        for i, p in enumerate(found):
            name = "%s_%02d" % (stem, i)
            piece = cutter.cut(rgb, p["mask"], p["box"], dict(cutter.DEFAULTS))
            piece.save(project.piece_path(name))
            entry = {"name": name, "w": piece.width, "h": piece.height, "sheet": sid,
                     "box": [int(v) for v in p["box"]], "dpi": dpi, "cut_at": now_ms()}
            # ⚠️⚠️ THE COMMONEST INK UNDER THE PIECE, AND IT WAS 85% OF THE
            # WHOLE CUT. `np.unique(..., axis=0)` lexsorts three columns of
            # every pixel in the piece, and it was asked over a WHOLE-SHEET
            # boolean besides. On the designer's own sheets — 10909 x 15355,
            # a hundred and seventy megapixels each — that was 87 seconds of a
            # 102-second sheet, and seventeen sheets took eighteen minutes.
            # ⭐️ Packing the three channels into one number and asking the
            # same question of a 1-D array is the identical answer, measured
            # 117 times faster; cropping to the piece's own box first is
            # another threefold. Measured, not reasoned — see the note in
            # CLAUDE.md under *Measuring*.
            bx0, by0, bx1, by1 = p["box"]
            sub = colour[by0:by1, bx0:bx1][p["mask"][by0:by1, bx0:bx1]]
            if len(sub):
                packed = (sub[:, 0].astype(np.uint32) * 65536 +
                          sub[:, 1].astype(np.uint32) * 256 + sub[:, 2])
                vals, counts = np.unique(packed, return_counts=True)
                best = int(vals[counts.argmax()])
                entry["ink_rgb"] = [best >> 16, (best >> 8) & 255, best & 255]
            made.append(entry)

        # ⚠️ NAMES FOLLOW THEIR PIECES WHEN A SHEET IS CUT AGAIN. Pieces are
        # numbered in READING ORDER, so outlining one more near the top of a
        # sheet shifts every piece below it up a number and a name given to
        # `..._03` would quietly land on what used to be `..._02`. Each new
        # piece is matched to an old one by how much their boxes overlap.
        taken, from_old = set(), {}          # new stem -> the old stem it is
        for m in made:
            best, score = None, 0.0
            for oname, v in old.items():
                if oname in taken or "box" not in v:
                    continue
                q = overlap(m["box"], v["box"])
                if q > score:
                    best, score = oname, q
            if best and score >= 0.6:
                taken.add(best)
                from_old[m["name"]] = best

        man = project.manifest()
        pieces_man = man.get("pieces", {})
        # this sheet's names are the only ones that may move; every other
        # sheet's are carried across untouched
        head = stem + "_"
        mine = {k: v for k, v in pieces_man.items() if k.startswith(head)}
        kept = {k: v for k, v in pieces_man.items() if not k.startswith(head)}
        for new_stem, old_stem in from_old.items():
            if old_stem in mine:
                kept[new_stem] = mine[old_stem]

        # ⚠️ A NAME WHOSE PIECE NO LONGER EXISTS MUST NOT BE LEFT LYING UNDER
        # ITS OLD NUMBER. This used to happen whenever the LAST outline on a
        # sheet was removed: nothing above it was renumbered, so the rename
        # map came out empty, so the manifest was not rewritten at all and
        # the dead piece's name stayed. Outline something else in that spot,
        # cut again, and the new piece took the number — and the name with
        # it. That is precisely the fault this whole mechanism exists to
        # stop, arriving by the one door nobody had tried.
        #
        # manifest.json is one of the two stores that cannot be rebuilt, so
        # the name is not thrown away: it is set aside under `retired`, and
        # the cut says what it let go and why.
        matched = set(from_old.values())
        retired = {k: v for k, v in mine.items()
                   if k not in matched and (v or {}).get("name")}
        if retired:
            man.setdefault("retired", {}).update(retired)
        man["pieces"] = kept
        project.save_manifest(man)
        pieces_man = kept
        renames = {o: n for n, o in from_old.items() if o != n}
        idx["pieces"] = {k: v for k, v in idx.get("pieces", {}).items() if v.get("sheet") != sid}
        for m in made:
            idx["pieces"][m["name"]] = {k: v for k, v in m.items() if k != "name"}
        project.save_index(idx)
        # ⭐️ A piece that was set aside goes straight back to the spare folder.
        # The mark rode across on its manifest entry, but the cutter writes
        # every piece into the store proper, so without this a re-cut would
        # hand the game back the nineteen duplicates you had just put away.
        again = [m["name"] for m in made if (kept.get(m["name"]) or {}).get("spare")]
        if again:
            project.set_aside(again, True)
        for f in os.listdir(project.p("cache")) if os.path.isdir(project.p("cache")) else []:
            if f.startswith("piece-" + stem + "_"):
                os.remove(os.path.join(project.p("cache"), f))
        out = []
        for m in made:
            mm = project.measure_piece(m["name"], dpi) or {}
            out.append(dict(m, w_in=mm.get("w_in"), h_in=mm.get("h_in"),
                            named=(pieces_man.get(m["name"]) or {}).get("name", "")))
        return {"made": out, "renames": renames, "drawn": drawn,
                "retired": {k: v.get("name", "") for k, v in retired.items()}}


# -------------------------------------------------------------------- jobs

JOBS = {}
JOBS_LOCK = threading.Lock()


def start_job(label, fn):
    jid = uuid.uuid4().hex[:10]
    job = {"id": jid, "label": label, "state": "running", "done": 0, "total": 0,
           "message": "starting", "result": None, "error": None, "started": now_ms()}
    with JOBS_LOCK:
        JOBS[jid] = job

    def progress(done, total, message):
        job["done"], job["total"], job["message"] = done, total, message

    def run():
        try:
            job["result"] = fn(progress)
            job["state"] = "done"
            job["message"] = "done"
        except Exception as exc:               # noqa: BLE001
            job["state"] = "failed"
            job["error"] = str(exc)
            job["message"] = str(exc)
            traceback.print_exc()
    threading.Thread(target=run, daemon=True).start()
    return job


# ------------------------------------------------------------- the way out

# ⭐️⭐️ THE DESIGNER, 22 August 2026: "the cutting tool should remain relatively
# generic — not every user is going to be building their own version of [a
# game] to play on a computer! Output format is important."
#
# So the way out of the room is A PLAIN FOLDER ANYBODY CAN USE. The pieces come
# out as ordinary PNGs named by what they ARE rather than by which corner of
# which sheet they were cut from, with an inventory beside them: JSON for a
# program, CSV for a spreadsheet — because most of the people this could serve
# live in Numbers and Excel, not in a text editor. Sizes in inches AND
# millimetres, because half the world uses each.
#
# NOTHING IN HERE IS SHAPED FOR A GAME ENGINE. A game of your own can reach
# into the project's own stores if it likes, because it can and because it
# lives next door; everybody
# else — a Tabletop Simulator mod, a VASSAL module, somebody reprinting a lost
# counter, somebody cutting chipboard on a craft cutter, somebody archiving an
# out-of-print box — gets this, and it is enough for all of them.

# ⚠️⚠️ WHAT IS CUT HERE IS SOMEBODY ELSE'S WORK, AND THE ROOM MUST SAY SO.
#
# The designer, 22 August 2026: "one thing that does seem important to me, from a
# legal perspective. Some kind of warning that this is personal use, copyright
# in all things you cut is not your own — a real disclaimer. Don't share cut
# pieces etc etc."
#
# They are right, and the EXPORT is exactly where it matters: up to that point the
# pieces sit in a folder on one person's machine, and from that point on they
# are a tidy, named, portable set that is trivially easy to put somewhere
# public without thinking about it. So the warning travels WITH the folder —
# in its README, in a file of its own, and at the foot of every page meant to
# be printed — rather than being shown once and forgotten.
#
# It is deliberately not written like a licence. Somebody has to actually read
# it.
# The longer side of a picture on the contact sheet. Big enough to print a
# card at true size and still look printed; small enough that a page of five
# hundred of them opens.
CONTACT_PX = 600

COPYRIGHT_NOTICE = """ABOUT COPYRIGHT — PLEASE READ THIS PART

The pictures in this folder were cut out of somebody else's work. Copyright in
a game's artwork, its design and its words belongs to its publisher and to the
artists who made it. Scanning it, cutting it up and giving the pieces tidy
names changes none of that. NOTHING IN THIS FOLDER IS YOURS TO GIVE AWAY.

This is for your own use, with a copy of the game that you own — replacing a
piece you have lost, playing a game you already have, keeping a record of what
is on your own shelf.

    Do NOT put these pieces on the internet.
    Do NOT share them, sell them, or build them into anything you release.
    Do NOT upload them to a mod workshop, a file host, or a forum.

The Cutting Room is a tool, like a scalpel is a tool. It gives you no rights
over anything you cut with it. Its authors are not lawyers, and this is not
legal advice: what counts as personal or fair use differs from one country to
the next, and where you stand is yours to know.
"""

# The same thing in one line, for the foot of a page that will be printed.
COPYRIGHT_LINE = ("The artwork here is somebody else's copyright, and cutting "
                  "it up does not change that. For your own use, with a copy "
                  "of the game you own — not for sharing.")

def open_folder(path):
    """Show a folder in the desktop's own file browser.

    ⚠️ This used to be guarded by `sys.platform == "darwin"` and so did
    NOTHING AT ALL anywhere else, silently — the button was there and the
    press did not fail, it just had no effect. One line each fixes it.
    """
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif os.name == "nt":
            os.startfile(path)                          # noqa: S606
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:                                   # noqa: BLE001
        return False


_SLUG_BAD = re.compile(r"[^a-z0-9]+")


# ⚠️⚠️ THIS WAS CALLED `slug`, AND SO IS THE ONE AT THE TOP OF THIS FILE.
# A second definition of a name does not clash in Python, it silently REPLACES
# the first — for the whole module, including code written hundreds of lines
# above it. So every `slug(...)` in here was reaching this one, whichever its
# author meant, and the two take different second arguments: `slug(x, 40)`
# meant "keep 40 characters" and was quietly passing 40 as the FALLBACK. It
# came out as a sheet whose set was literally called "40".
# ⭐️ The two really are different jobs and now say so: `slug()` makes an ID
# (and drops a file extension), `file_slug()` makes a FILE NAME a person can
# read. Nothing in here may define either name twice again.
def file_slug(text, fallback="piece", cap=60):
    """A file name a person can read, out of a name a person typed."""
    s = _SLUG_BAD.sub("-", str(text or "").lower()).strip("-")
    if len(s) > cap:                     # cut at a word, not mid-word
        s = s[:cap].rsplit("-", 1)[0] or s[:cap]
    return s or fallback


def turned(img, deg):
    """A piece the right way up.

    ⚠️ A turn lives in the manifest and is NEVER baked into the cut PNG: a
    re-cut and the look-alike hash both need that file to be exactly what came
    off the sheet (fault 15). THE EXPORT IS THE ONE PLACE IT SHOULD BE BAKED
    IN — what leaves the room is finished, and somebody opening the folder
    wants the picture the way it reads, not the way it happened to be printed.
    """
    # ⚠️ FLOAT. This was int(), which silently threw away every angle the
    # levelling tool exists to set: a piece turned 1.4 degrees came out
    # turned 1. The quarter turns still take the exact path below.
    try:
        deg = round(float(deg or 0) % 360.0, 1)
    except (TypeError, ValueError):
        deg = 0.0
    if not deg:
        return img
    square = {90: Image.ROTATE_270, 180: Image.ROTATE_180, 270: Image.ROTATE_90}
    if deg in square:                    # exact, no resampling at all
        return img.transpose(square[deg])
    out = img.rotate(-deg, expand=True, resample=Image.BICUBIC)
    # ⭐️⭐️ AND RE-CROPPED TO WHAT IS ACTUALLY THERE. Rotating by a few
    # degrees puts transparent wedges at the corners and `expand=True` grows
    # the canvas to hold them, so a levelled piece would measure LARGER than
    # the crooked one it came from — which is the wrong way round, since
    # levelling is what makes the box fit. The designer, 3 September 2026:
    # "I'm going to have to go through them all again and remove white space
    # you have left." Trimming here is what stops that being true of a turn.
    box = out.getbbox()
    return out.crop(box) if box else out


EXPORT_README = """WHAT IS IN THIS FOLDER
======================

The components of %(game)s, cut out of its own printed sheets.

------------------------------------------------------------------------
%(copyright)s------------------------------------------------------------------------

%(contents)s
EVERY PICTURE IS AT ITS TRUE PRINTED SIZE. The inventory gives each piece in
inches and in millimetres, and every picture is %(dpi)d dots per inch, so a
piece 300 pixels wide is one inch wide on the table. Print at %(dpi)d dpi and
it comes out the size it was in the box.

Pieces that were turned in the room have been turned here, so they read the
right way up.

%(counts)s

Made by the Cutting Room
Everything in this folder is written fresh each time you export, so do not
keep anything of your own in it.
"""


# ⭐️ THE PRINTABLE PAGES ARE HTML, NOT PICTURES, AND THAT IS THE POINT.
# "True size" only means anything if it survives the printer. A browser
# honours millimetres in a print stylesheet, so a page laid out in mm comes
# out of the printer at the size it says — which a PNG at a guessed dpi does
# not. Both pages carry a 25mm reference square so you can hold a ruler to it
# and know at a glance whether "fit to page" has quietly shrunk everything.
#
# They are laid out light: these are for paper and ink, whatever the room's
# own ground is.

PRINT_CSS = """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 14mm; background: #fff; color: #111;
         font: 11pt/1.45 "Iowan Old Style", Palatino, Georgia, serif; }
  h1 { font-size: 17pt; margin: 0 0 2mm; }
  .sub { color: #666; font-size: 9.5pt; margin: 0 0 6mm; }
  h2 { font-size: 11pt; letter-spacing: .06em; text-transform: uppercase;
       color: #666; margin: 9mm 0 3mm; border-bottom: 1px solid #ddd;
       padding-bottom: 1mm; page-break-after: avoid; }
  .ruler { display: flex; align-items: center; gap: 3mm; margin: 0 0 7mm;
           font-size: 9pt; color: #666; }
  .ruler i { display: block; width: 25mm; height: 25mm; border: 1px solid #111;
             flex: none; }
  .grid { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 6mm; }
  .p { page-break-inside: avoid; break-inside: avoid; text-align: center; }
  .p img { display: block; }
  .p .cap { font-size: 8pt; line-height: 1.25; color: #333; margin-top: 1.5mm;
            max-width: 46mm; margin-left: auto; margin-right: auto; }
  .p .sz { color: #888; }
  .p.spare { opacity: .55; }
  table { border-collapse: collapse; width: 100%; font-size: 10pt; }
  th { text-align: left; font-size: 8.5pt; letter-spacing: .06em;
       text-transform: uppercase; color: #666; border-bottom: 1px solid #ccc;
       padding: 1.5mm 2mm; }
  td { padding: 1.5mm 2mm; border-bottom: 1px solid #eee; vertical-align: top; }
  tr.missing td.s { color: #a33; }
  tr.probably td.s { color: #a76; }
  tr.cut td.s { color: #275; }
  .box { display: inline-block; width: 3.5mm; height: 3.5mm; border: 1px solid #666;
         margin-right: 2mm; vertical-align: -0.4mm; }
  .box.on { background: #275; border-color: #275; }
  /* ⭐️ the check against the contents list: a report to read once, so it wants
     sub-headings, and a plain way of saying "this is a fact" against "this is
     a guess" — see review_page() */
  h3 { font-size: 10.5pt; margin: 5mm 0 2mm; page-break-after: avoid; }
  p.good { color: #275; }
  p.warn { color: #8a5a1a; }
  code { font: 9.5pt/1.3 ui-monospace, Menlo, Consolas, monospace; color: #444; }
  /* ⭐️ A PIECE NAMED IN THE REPORT IS A LINK BACK INTO THE ROOM — but only in
     the copy the room serves; see piece_link() in review_page(). On paper a
     link is just words, so it must not shout. */
  a { color: #245; }
  a code { color: #245; }
  p.how { color: #666; font-size: 9.5pt; margin: 0 0 6mm; }
  .rights { margin: 10mm 0 0; padding-top: 2.5mm; border-top: 1px solid #ccc;
            font-size: 8pt; color: #666; max-width: 120mm; }
  @page { margin: 12mm; }
  @media print { body { padding: 0; } .noprint { display: none; } }
"""


# ⚠️ `ruler` is not decoration. Every page the room prints that has a PICTURE
# on it must carry the 25mm square, because a printer set to "fit to page"
# silently scales everything and a piece printed at 97% is the wrong piece. But
# a page of nothing but words has nothing to measure, and the square there
# would only invite somebody to doubt a report that is perfectly true.
def print_page(title, subtitle, body, ruler=True):
    square = ("""<div class="ruler"><i></i><span>This square is <b>25&nbsp;mm</b>
(about one inch) on every side. Hold a ruler to it: if it does not measure
25&nbsp;mm, the printer has scaled the page and nothing else on it is true size
either. Print at 100%, not "fit to page".</span></div>""" if ruler else "")
    return ("""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title><style>%s</style></head><body>
<h1>%s</h1><p class="sub">%s</p>
%s
%s
<p class="rights">%s</p>
</body></html>
""" % (esc_html(title), PRINT_CSS, esc_html(title), subtitle, square, body,
       esc_html(COPYRIGHT_LINE)))


def esc_html(t):
    return (str(t if t is not None else "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def contact_sheet(rows, game):
    """Every piece at its true printed size, grouped by kind."""
    by_kind = {}
    for r in rows:
        by_kind.setdefault(r["kind"] or "not said", []).append(r)
    out = []
    for kind in sorted(by_kind, key=lambda k: (k == "not said", k)):
        got = by_kind[kind]
        out.append("<h2>%s — %d</h2><div class=\"grid\">" % (esc_html(kind), len(got)))
        for r in got:
            out.append(
                '<div class="p%s"><img src="%s" loading="lazy" '
                'width="%s" height="%s" style="width:%.2fmm;height:%.2fmm">'
                '<div class="cap">%s<br><span class="sz">%.2f × %.2f in · '
                '%.0f × %.0f mm%s</span></div></div>'
                % (" spare" if r["spare"] else "",
                   esc_html(r["file"].replace("pieces/", "contact-sheet-files/", 1)),
                   r["width_px"], r["height_px"], r["width_mm"], r["height_mm"],
                   esc_html(r["name"] or "(unnamed)"),
                   r["width_in"], r["height_in"], r["width_mm"], r["height_mm"],
                   " · set aside" if r["spare"] else ""))
        out.append("</div>")
    live = len([r for r in rows if not r["spare"]])
    sub = ("%d component%s, every one at the size it is printed. Those shown "
           "faint were set aside as duplicates." % (live, "" if live == 1 else "s"))
    return print_page("%s — every piece" % game, sub, "\n".join(out))


def checklist_page(pr, game):
    """What is still to cut, to take to the table with a scalpel."""
    st = pr.wanted_status()
    items = st["items"]
    if not items:
        return None
    names = {g.get("id"): g.get("name") or g.get("id")
             for g in (st.get("groups") or [])}
    by_group = {}
    for it in items:
        by_group.setdefault(it.get("group", ""), []).append(it)
    words = {"cut": "cut", "probably": "probably cut", "missing": "not yet"}
    per_group = (st.get("summary") or {}).get("groups") or {}
    out = []
    # ⭐️ the sets being cut now first, the ones put by after them, each with
    # its own figure — the work is done a box at a time and so is the reading
    for g in sorted(by_group, key=lambda x: (bool((per_group.get(x) or {}).get("later")),
                                             x == "", x)):
        got = by_group[g]
        left = len([i for i in got if i["state"] == "missing"])
        band = per_group.get(g) or {}
        out.append("<h2>%s — %d of %d still to cut (%d%% done)%s</h2>"
                   % (esc_html(names.get(g, g) or "Everything else"), left, len(got),
                      band.get("pct", 0),
                      " · put by for later" if band.get("later")
                      else " · filed away" if band.get("filed") else ""))
        out.append("<table><tr><th>Component</th><th>Kind</th><th>Where it stands</th></tr>")
        for it in sorted(got, key=lambda i: (i["state"] != "missing", (i.get("name") or "").lower())):
            out.append('<tr class="%s"><td><span class="box%s"></span>%s</td>'
                       '<td>%s</td><td class="s">%s</td></tr>'
                       % (it["state"], " on" if it["state"] == "cut" else "",
                          esc_html(it.get("name") or it.get("id")),
                          esc_html(it.get("kind") or ""), words[it["state"]]))
        out.append("</table>")
    s = st["summary"]
    sub = ("%d of %d accounted for (%d%%). Tick as you go — the empty boxes are "
           "the work." % (s["live_done"], s["live_total"], s["live_pct"]))
    if s.get("later_total"):
        # ⚠️ the figure is over what is being cut NOW, so it has to say so —
        # two numbers that disagree in silence is fault 67's subject
        sub = ("%d of %d accounted for (%d%%) in the sets you are cutting now, "
               "and a further %d component%s put by for later. Tick as you go."
               % (s["live_done"], s["live_total"], s["live_pct"],
                  s["later_total"], "" if s["later_total"] == 1 else "s"))
    return print_page("%s — still to cut" % game, sub, "\n".join(out))


# ⭐️⭐️ THE CHECK AGAINST THE CONTENTS LIST, AS A PAGE TO READ ONCE. The designer
# asked for it by name: a secondary check, run when the cutting is done, to be
# sure every piece is there. It is printable on purpose — it is a list to work
# through with the box open in front of you — and it goes into the exported
# folder as well as onto the screen, so the check travels with the pieces.
#
# ⚠️ IT REPORTS; IT NEVER FIXES. And every heading says whether what is under
# it is a FACT (nothing is linked to this component) or a GUESS (a name looks
# about right), because those two are worth very different amounts.

def review_page(pr, game, rv=None, home=None):
    rv = rv if rv is not None else pr.cut_review()
    s = rv["summary"]
    out = []

    # ⭐️⭐️ A REPORT THAT NAMES A PIECE AND CANNOT OPEN IT IS HALF A REPORT.
    # Every line below names a `stem` — the one name the room, the inventory
    # and whatever ingests the pieces afterwards can all say — so the stem is
    # the right handle for "this one is wrong, go and fix it". The room reads
    # ?piece=<stem> in ONE place (fromHash in project.html), so this is a
    # link and not a second way of saying where to go.
    # ⚠️ ONLY THE COPY THE ROOM SERVES GETS ONE. The identical page is written
    # into the export folder, which leaves the room and is meant to be read by
    # somebody with no room running (fault 22) — a dead link to a local port
    # sitting in their folder is worse than plain text. So `home` is passed by
    # the route that serves it and by nothing else.
    def piece_link(stem):
        code = "<code>%s</code>" % esc_html(stem)
        if not home:
            return code
        return ('<a href="%s?tab=pieces&amp;piece=%s">%s</a>'
                % (esc_html(home), urllib.parse.quote(stem), code))

    def size_of(r):
        if not r.get("w_in"):
            return "—"
        return ("%.2f &times; %.2f in <span style=\"color:#888\">&middot; "
                "%.0f &times; %.0f mm</span>"
                % (r["w_in"], r["h_in"], r["w_in"] * 25.4, r["h_in"] * 25.4))

    if home:
        out.append('<p class="how noprint">Every piece named below opens in '
                   'the room &mdash; the report says what it sees and changes '
                   'nothing itself.</p>')

    def table(rows, head, cells):
        out.append("<table><tr>" +
                   "".join("<th>%s</th>" % esc_html(h) for h in head) + "</tr>")
        for r in rows:
            out.append("<tr>" + "".join("<td>%s</td>" % c for c in cells(r)) + "</tr>")
        out.append("</table>")

    if not rv["has_list"]:
        out.append("<h2>There is no contents list for this game</h2>")
        out.append("<p>So there is nothing to check the cut against. Type the "
                   "box's contents list into the Checklist — once — and this "
                   "page becomes a real report: what is missing, what is "
                   "half-done, and which cut pieces answer to nothing on the "
                   "list.</p>")
    for band in rv["sets"]:
        # ⭐️ FILING A SET AWAY IS A CLAIM, AND THIS PAGE IS WHAT CHECKS IT.
        # The room takes somebody at their word and files the set — but it
        # goes on counting it, so anything left undone in it still turns up
        # here under its own name. A mark that stopped the checking would be
        # a mark that quietly buried the one thing it was hiding.
        out.append("<h2>%s — %d of %d accounted for%s</h2>"
                   % (esc_html(band["name"]), band["accounted"], band["total"],
                      " · filed away" if band.get("filed") else ""))
        if not (band["missing"] or band["part"] or band["probably"]):
            out.append("<p class=\"good\">Every component in this set is "
                       "accounted for. \u2713</p>")
        if band["missing"]:
            out.append("<h3>Nothing cut for these — %d</h3>" % len(band["missing"]))
            table(band["missing"], ["Component", "Kind", "Wanted"],
                  lambda r: ['<span class="box"></span>' + esc_html(r["name"]),
                             esc_html(r["kind"]),
                             ("%d pieces" % r["need"]) if r["need"] > 1 else "one piece"])
        if band["part"]:
            out.append("<h3>Not enough cut yet — %d</h3>" % len(band["part"]))
            # ⚠️ 0 OF 32 IS NOT "STARTED". A component reaches this heading two
            # quite different ways: some pieces really are tied to it and there
            # are not enough of them, or NOTHING is tied to it and a name or
            # two merely looked right. Read against a real game — a 32-card
            # deck nobody had started — the second came out as "0 of 32 cut so far",
            # which reads as work in hand when there is none. Say which.
            table(band["part"], ["Component", "Kind", "Where it stands"],
                  lambda r: ['<span class="box"></span>' + esc_html(r["name"]),
                             esc_html(r["kind"]),
                             ("<b>%d</b> of %d cut" % (r["got"], r["need"]))
                             if r["got"] else
                             ("<b>none</b> of %d — %d name%s merely looks right"
                              % (r["need"], len(r["guesses"]),
                                 "" if len(r["guesses"]) == 1 else "s"))])
        if band["probably"]:
            out.append("<h3>Counted only because a name looks right — %d</h3>"
                       % len(band["probably"]))
            out.append("<p class=\"warn\">⚠️ These are a <b>guess</b>. Nothing "
                       "is linked to them; the room matched the words. Tie the "
                       "piece to the component, or say it is not the same "
                       "thing, before you trust the total above.</p>")
            table(band["probably"], ["Component", "Kind", "Guessed from"],
                  lambda r: ['<span class="box"></span>' + esc_html(r["name"]),
                             esc_html(r["kind"]),
                             esc_html(", ".join(r["guesses"][:6]) or "—")])

    if rv.get("loose_decks"):
        out.append("<h2>Decks you have told the room to count as one — %d</h2>"
                   % len(rv["loose_decks"]))
        # ⚠️ THIS USED TO BE A LIST OF ACCIDENTS AND IS NOW A LIST OF
        # DECISIONS. A component called a deck counts all its cards by itself
        # (counts_each), so the only way to reach this heading is to have
        # pressed "one is enough" on one — which is a perfectly good answer for
        # a line called a deck that really is one piece. So it says what it is
        # about and says there may well be nothing to do: a report that tells
        # somebody off for a choice they made on purpose is fault 50's stain,
        # and gets stopped being read.
        out.append("<p class=\"warn\">⚠️ A deck is usually many different "
                   "cards, and the room counts one against every card of its "
                   "quantity unless it is told otherwise. Each of these lines "
                   "<b>has been told otherwise</b>, so it is accounted for the "
                   "moment one piece is tied to it — a deck of thirty-two with "
                   "one card cut reads as done. If that is what you meant, "
                   "there is nothing to do here. If it is not, set the line "
                   "back to <b>all different</b> on the Checklist.</p>")
        table(rv["loose_decks"], ["Component", "Set", "The list says", "Counted as"],
              lambda r: ['<span class="box"></span>' + esc_html(r["name"]),
                         esc_html(r["set_name"]),
                         esc_html(r["qty"]),
                         "one piece is enough"])
    if rv["orphans"]:
        out.append("<h2>Pieces that answer to nothing on the list — %d</h2>"
                   % len(rv["orphans"]))
        out.append("<p>Each of these is one of three things: something the "
                   "printed contents list forgot, a piece cut twice, or a "
                   "piece cut from the wrong place. All three are worth a look "
                   "before the pieces leave the room.</p>")
        table(rv["orphans"],
              ["Piece", "What it is called", "How big it is", "Off which sheet"],
              lambda r: ['<span class="box"></span>' + piece_link(r["stem"]),
                         esc_html(r["name"] or "(nothing yet)"),
                         size_of(r),
                         esc_html(r["sheet"] or "no sheet the room knows")])
    if rv["unnamed"]:
        out.append("<h2>Pieces with no name yet — %d</h2>" % len(rv["unnamed"]))
        out.append("<p>They will be written out filed under the number they "
                   "were cut as, which is no use to anybody later.</p>")
        table(rv["unnamed"], ["Piece", "Off which sheet"],
              lambda r: ['<span class="box"></span>' + piece_link(r["stem"]),
                         esc_html(r["sheet"] or "no sheet the room knows")])
    if rv["held"]:
        out.append("<h2>Pieces held back — %d</h2>" % len(rv["held"]))
        table(rv["held"], ["Piece", "What it is called", "Why"],
              lambda r: [piece_link(r["stem"]),
                         esc_html(r["name"] or "(nothing yet)"),
                         esc_html(r["why"])])
    # ⭐️ PUT BY FOR LATER, AND SAID SO RATHER THAN LEFT OUT IN SILENCE. A
    # report that quietly dropped a whole box would be a report that lies by
    # omission — so the sets are named, with what they hold, under a heading
    # that says plainly that none of it is in the figures above.
    if rv.get("put_by"):
        out.append("<h2>Sets put by for later — %d</h2>" % len(rv["put_by"]))
        out.append("<p>You have said these are not being cut yet, so "
                   "<b>nothing in them is counted anywhere above</b> — not as "
                   "missing, and not in the percentage. Bring one back into "
                   "the cutting from the Sheets page or the Checklist and it "
                   "joins the figures again; nothing has been deleted or "
                   "hidden.</p>")
        table(rv["put_by"], ["Set", "Accounted for", "Still to cut"],
              lambda r: [esc_html(r["name"]),
                         "%d of %d" % (r["accounted"], r["total"]),
                         "%d" % (r["total"] - r["accounted"])])
    if rv["aside"]:
        out.append("<h2>Pieces set aside — %d</h2>" % len(rv["aside"]))
        out.append("<p>Kept on disk and left out of the hand-over, on purpose. "
                   "They are here so that it is a decision and not an "
                   "accident.</p>")
        table(rv["aside"], ["Piece", "What it is called"],
              lambda r: [piece_link(r["stem"]),
                         esc_html(r["name"] or "(nothing yet)")])

    sub = ("%d of %d components accounted for (%d%%), out of %d pieces cut."
           % (s["accounted"], s["components"], s["pct"], s["pieces"]))
    if s.get("later_components"):
        sub += (" %d component%s in %d set%s put by for later %s not counted."
                % (s["later_components"], "" if s["later_components"] == 1 else "s",
                   s["later_sets"], "" if s["later_sets"] == 1 else "s",
                   "is" if s["later_components"] == 1 else "are"))
    if not rv["has_list"]:
        sub = "%d pieces cut, and no contents list to check them against." % s["pieces"]
    return print_page("%s — the cut checked against the list" % game, sub,
                      "\n".join(out), ruler=False)


# ⭐️ FOR A LASER OR A CRAFT CUTTER. One closed path per outline, at true size
# in MILLIMETRES with the unit written on the width and the height — a laser is
# set up in millimetres, and an SVG without units gets guessed at. Each piece
# keeps the colour it was drawn in, because LightBurn (and Glowforge, and
# Silhouette) sort a job into layers by colour, so the pieces arrive sorted.
#
# ⚠️ THE PATHS ARE IN THE SHEET'S OWN POSITIONS, NOT NESTED. That is on
# purpose and it is the useful thing: print the sheet at true size, stick it to
# the board, and the cut lines fall exactly on the printing. Nesting the pieces
# onto a fresh blank would need a matching print file to be worth anything, and
# would put the artwork and the cut out of register at the first mistake.
# `sheet-print.png` beside it is that same sheet, ready to print.

def laser_svg(pieces, sheet, dpi, title):
    mm = 25.4 / float(dpi or DPI)
    ready = [p for p in pieces if len(p.get("pts") or []) >= 3]
    if not ready:
        return None
    body = []
    for n, pc in enumerate(ready):
        pts = pc["pts"]
        ink = INKS[int(pc.get("ink", 0)) % len(INKS)]

        def at(p):
            return "%.3f %.3f" % (p[0] * mm, p[1] * mm)

        d = ["M " + at(pts[0])]
        if pc.get("curve") and len(pts) >= 3:
            for k in range(len(pts)):          # the same Béziers as on screen
                c1, c2, p2 = _arc(pts, k)
                d.append("C %s %s %s" % (at(c1), at(c2), at(p2)))
        else:
            for p in pts[1:]:
                d.append("L " + at(p))
        d.append("Z")
        body.append('  <path id="piece-%02d" fill="none" stroke="%s" '
                    'stroke-width="0.1" d="%s"/>' % (n + 1, ink, " ".join(d)))
    w, h = (sheet.get("w") or 0) * mm, (sheet.get("h") or 0) * mm
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n'
            '     width="%.3fmm" height="%.3fmm" viewBox="0 0 %.3f %.3f">\n'
            '  <title>%s</title>\n'
            '  <desc>%d pieces at true size, in millimetres. Cut on the line. '
            '%s</desc>\n%s\n</svg>\n'
            % (w, h, w, h, esc_html(title), len(ready),
               esc_html(COPYRIGHT_LINE), "\n".join(body)))


def export_dir(pr, book=None):
    """Where an export goes: `export/` for the whole game, `export-<set>/`
    for one box of sheets.

    ⚠️ ONE RULE FOR THE NAME, because two things ask — the writing of it and
    the button that opens the folder afterwards. Written out twice they would
    disagree the moment a box was renamed, and the button would open an empty
    folder while the pieces sat in another (fault 24).
    """
    return os.path.join(pr.path, "export" if not book
                        else "export-" + file_slug(book, "set", cap=60))


def export_laser(pr, root, progress=None, only=None):
    """One cut file and one printable sheet per outlined sheet.
    ⭐️ `only` holds it to one box of sheets, for a set handed over alone."""
    book = pr.outlines().get("sheets", {})
    outlined = [s for s in pr.sheets if (book.get(s["id"]) or {}).get("pieces")
                and (only is None or pr.book_of(s["id"]) == only)]
    if not outlined:
        return 0
    out = os.path.join(root, "laser")
    os.makedirs(out, exist_ok=True)
    game = pr.meta.get("name") or pr.id
    made = 0
    for n, s in enumerate(outlined):
        sid = s["id"]
        rec = book.get(sid) or {}
        svg = laser_svg(rec["pieces"], s, rec.get("dpi") or pr.dpi,
                        "%s — %s" % (game, s.get("label") or sid))
        if not svg:
            continue
        stem = file_slug(sid, "sheet", cap=70)  # the id is unique and stable
        with open(os.path.join(out, stem + "-cut.svg"), "w") as fh:
            fh.write(svg)
        # the same sheet as a picture, so the cut lines have something to
        # fall on. Copied rather than re-encoded: it is already what it is.
        src_png = pr.sheet_png(sid)
        if os.path.exists(src_png):
            shutil.copyfile(src_png, os.path.join(out, stem + "-print.png"))
        made += 1
        if progress:
            progress(n + 1, len(outlined), "cut file for %s" % (s.get("label") or sid))
    with open(os.path.join(out, "README.txt"), "w") as fh:
        fh.write("""CUT FILES
=========

One pair of files per sheet:

  ...-cut.svg     where to run the laser. True size, in millimetres, one
                  closed path per piece. Each piece is a different colour
                  because LightBurn and its like sort a job into layers by
                  colour, so they arrive already sorted.
  ...-print.png   the same sheet as a picture, at %(dpi)d dots per inch.

HOW THEY GO TOGETHER
Print the -print.png at 100%% (NOT "fit to page"), stick it to your board,
and load the -cut.svg. The cut lines are in the sheet's own positions, so
they fall exactly on the printing. Check one measurement with a ruler before
you cut anything: if the print is not true size, nothing will line up.

%(copyright)s""" % {"dpi": pr.dpi, "copyright": COPYRIGHT_NOTICE})
    return made


def export_project(pr, progress=None, book=None):
    """Write the plain folder. Returns a summary of what came out.

    ⭐️⭐️ `book` writes ONE BOX OF SHEETS instead of the whole game. The
    designer, 26 August 2026: "I'd like to be able to just export a set of cut
    pieces, rather than everything in one project folder." A box is what every
    list in the room gathers by (fault 42), so it is the natural thing to hand
    over on its own — and on a game of 161 sheets and four boxes, wanting one
    of them is the normal case rather than a special one.

    ⚠️ IT GOES IN A FOLDER OF ITS OWN. Writing a set into `export/` would
    destroy the whole-game folder that was there — the export is replaced
    wholesale each time, on purpose — so somebody exporting one box would
    silently lose the export of everything else. One folder per box, named
    after it.
    """
    root = export_dir(pr, book)
    # Everything here is made by the room and can be made again, so it is
    # replaced wholesale rather than merged — a half-old export listing pieces
    # that are no longer there would be worse than no export at all.
    if os.path.isdir(root):
        shutil.rmtree(root)
    piece_dir = os.path.join(root, "pieces")
    spare_dir = os.path.join(piece_dir, "spare")
    small_dir = os.path.join(root, "contact-sheet-files")
    os.makedirs(spare_dir)
    os.makedirs(os.path.join(small_dir, "spare"))

    man = pr.manifest().get("pieces", {})
    idx = pr.index().get("pieces", {})
    labels = {s["id"]: (s.get("label") or s["id"]) for s in pr.sheets}
    # a component's own name is worth more in a spreadsheet than its id
    components = {w.get("id"): w.get("name") or w.get("id")
                  for w in (pr.wanted().get("items") or [])}

    # everything cut: in play, set aside, and anything the index remembers
    aside = set()
    if os.path.isdir(pr.spare_dir()):
        aside = {f[:-4] for f in os.listdir(pr.spare_dir()) if f.endswith(".png")}
    stems = sorted(set(idx) | set(pr.piece_files()) | aside)
    if book:
        mine = pr.pieces_of_book(book)
        stems = [st for st in stems if st in mine]
    dpi = pr.dpi
    rows, taken, unnamed = [], {}, 0
    # stem -> the file it was written as, so a piece can point at another one
    # by the name it actually has in this folder
    where = {}
    for n, stem in enumerate(stems):
        src = pr.piece_file(stem)
        if not os.path.exists(src):
            continue
        d = man.get(stem, {})
        spare = bool(d.get("spare"))
        name = (d.get("name") or "").strip()
        if not name:
            unnamed += 1
        # ⭐️ Named by WHAT IT IS. Two pieces may honestly share a name — the
        # two identical terrain tiles — so the second gets a number rather than
        # quietly overwriting the first.
        base = file_slug(name or stem)
        key = ("spare/" if spare else "") + base
        taken[key] = taken.get(key, 0) + 1
        fname = base + ("" if taken[key] == 1 else "-%d" % taken[key]) + ".png"
        rel = ("spare/" if spare else "") + fname

        im = turned(Image.open(src).convert("RGBA"), d.get("rotate"))
        box = im.getchannel("A").point(lambda v: 255 if v >= 24 else 0).getbbox()
        if box:
            im = im.crop(box)            # so the picture IS the piece
        im.save(os.path.join(piece_dir, rel))
        where[stem] = "pieces/" + rel
        # ⚠️ THE CONTACT SHEET GETS ITS OWN, SMALLER, COPY. A real game is
        # hundreds of pieces; a single page pointing at hundreds of
        # full-resolution scans asks the browser for gigabytes of pixels and
        # is fault 12 by another door. Capped at CONTACT_PX on the longer
        # side, which is still more than enough to print at true size — a
        # 3.5in card comes out at about 170 dots per inch.
        small = im.copy()
        small.thumbnail((CONTACT_PX, CONTACT_PX), Image.LANCZOS)
        small.save(os.path.join(small_dir, rel))

        meta = idx.get(stem, {})
        sid = meta.get("sheet", "")
        w_in, h_in = im.width / float(dpi), im.height / float(dpi)
        rows.append({
            "file": "pieces/" + rel,
            "name": name,
            "kind": d.get("kind") or "",
            "component": components.get(d.get("wanted"), d.get("wanted") or ""),
            "sheet": labels.get(sid, sid),
            "width_in": round(w_in, 3), "height_in": round(h_in, 3),
            "width_mm": round(w_in * 25.4, 1), "height_mm": round(h_in * 25.4, 1),
            "width_px": im.width, "height_px": im.height,
            "spare": "yes" if spare else "",
            "variant_of": d.get("alike") or "",
            # ⭐️ the back is another piece in this same folder, named the way
            # everything else here is named — by what it is
            "back": d.get("back") or "",
            # ⭐️ one design, cut once, wanted this many times by the game
            "copies": int(d.get("copies") or 1),
            # ⚠️ float, not int: a piece levelled by 1.4 degrees was reported
            # in the inventory as 1, which is a picture of the wrong thing.
            "turned_degrees": round(float(d.get("rotate") or 0), 1),
            "note": d.get("note") or "",
            "cut_from": stem,
        })
        if progress:
            progress(n + 1, len(stems), "writing %s" % rel)

    # ⭐️ a card's back is another piece in this folder, so say which FILE it
    # is — a stem means nothing to anybody reading the inventory
    for r in rows:
        r["back"] = where.get(r["back"], "") if r["back"] else ""

    rows.sort(key=lambda r: (r["spare"], r["kind"], r["name"].lower(), r["file"]))
    live = [r for r in rows if not r["spare"]]
    counts = ("This set has %d component%s%s.%s"
              % (len(live), "" if len(live) == 1 else "s",
                 "" if len(rows) == len(live)
                 else ", and %d more set aside as duplicates" % (len(rows) - len(live)),
                 "" if not unnamed else
                 "\n%d of them have not been given a name yet and are filed under "
                 "the number they were cut as." % unnamed))
    game = pr.meta.get("game") or pr.meta.get("name") or pr.id
    if book:
        # ⚠️ SAY THAT THIS IS PART OF SOMETHING. A folder of one box that did
        # not say so reads as the whole game, and somebody checking it against
        # a printed contents list would find most of the game missing and
        # think the room had lost it.
        counts += ("\n\nThis folder holds ONE SET out of %s — the pieces cut "
                   "from %s. The game's other sets are exported separately, "
                   "each into a folder of its own; nothing here is missing."
                   % (game, pr.book_label(book)))
    # ⭐️ What this FOLDER is about, said once and used by everything that
    # names it — the README, the contact sheet, the check. A set's folder that
    # called itself by the game's name would look exactly like the whole game.
    subject = game if not book else ("%s — %s" % (game, pr.book_label(book)))

    def readme(made_files, spares, has_tick, laser_sheets):
        # ⚠️ Describe the folder that was ACTUALLY written. A README naming a
        # file that is not there sends the reader looking for it.
        lines = ["  pieces/            one picture per component, PNG with a",
                 "                     transparent background, at full scan",
                 "                     resolution and named by what the piece is."]
        if spares:
            lines += ["  pieces/spare/      duplicates deliberately set aside — a",
                      "                     second identical tile the set does not",
                      "                     need twice. Kept, not thrown away."]
        lines += ["  inventory.csv      the same list as a spreadsheet. Open it in",
                  "                     Numbers, Excel or anything else.",
                  "  inventory.json     the same list again, for a program to read.",
                  "  contact-sheet.html every piece at true printed size on one page.",
                  "                     Open it in a browser; print it at 100%.",
                  "                     (Its pictures live in contact-sheet-files/ and",
                  "                     are smaller copies, so the page opens quickly.",
                  "                     The full-size ones are in pieces/.)"]
        if has_tick:
            lines += ["  still-to-cut.html  the checklist, to print and take to the",
                      "                     table with a scalpel."]
        # ⭐️ THE CHECK TRAVELS WITH THE PIECES. It is the last thing read
        # before they leave the room, so it is no use only on the screen: the
        # folder gets copied about and the report has to go with it. Twice
        # over — once to read and print, once for a program to read, because
        # whatever ingests these pieces wants the room's own account of what
        # is missing rather than working it out again.
        lines += ["  check-against-the-list.html",
                  "                     the cut checked against the contents list:",
                  "                     what is missing, what is half-done, and",
                  "                     which pieces answer to nothing on it.",
                  "  check-against-the-list.json",
                  "                     the same findings, for a program."]
        if laser_sheets:
            lines += ["  laser/             %d sheet%s for a laser or craft cutter, at"
                      % (laser_sheets, "" if laser_sheets == 1 else "s"),
                      "                     true size in millimetres, each with the",
                      "                     printable sheet beside it."]
        lines += ["  COPYRIGHT.txt      the part above, on its own, so it travels."]
        return "\n".join(lines) + "\n"
    # ⚠️ On its own as well, because a folder full of pictures gets copied
    # about and a README is the first thing anybody stops reading.
    with open(os.path.join(root, "COPYRIGHT.txt"), "w") as fh:
        fh.write(COPYRIGHT_NOTICE)
    write_json(os.path.join(root, "inventory.json"),
               {"game": game, "set": pr.book_label(book) if book else "",
                "dpi": dpi,
                "made": "the Cutting Room",
                "pieces": rows}, indent=1)
    cols = ["file", "name", "kind", "component", "copies", "back", "sheet",
            "width_in", "height_in", "width_mm", "height_mm",
            "width_px", "height_px", "spare", "variant_of", "turned_degrees",
            "note", "cut_from"]
    # ⚠️ newline="" or every row comes out double-spaced on Windows.
    with open(os.path.join(root, "inventory.csv"), "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for r in rows:
            wr.writerow(r)

    made = ["README.txt", "COPYRIGHT.txt", "inventory.csv", "inventory.json",
            "pieces/"]
    if progress:
        progress(len(stems), len(stems), "the contact sheet")
    with open(os.path.join(root, "contact-sheet.html"), "w") as fh:
        fh.write(contact_sheet(rows, subject))
    made.append("contact-sheet.html")
    # ⚠️ THE CHECKLIST IS ABOUT THE WHOLE GAME, so it goes with the whole
    # game. A page headed "what is still to cut" listing three other boxes,
    # sitting in a folder holding one, would send somebody looking for pieces
    # that were never meant to be in it.
    tick = None if book else checklist_page(pr, game)
    if tick:
        with open(os.path.join(root, "still-to-cut.html"), "w") as fh:
            fh.write(tick)
        made.append("still-to-cut.html")
    # ⭐️⭐️ THE CHECK AGAINST THE CONTENTS LIST, beside the pieces it is about.
    # ⚠️ It reports and never fixes, so it cannot fail the export: a report
    # that stopped the folder being written would be worse than no report.
    # ⭐️ For one box it is a check about THAT box — its pieces, and the sets
    # that answer to it — because a report saying "44 of 221" over a folder
    # holding one set is a lie by arithmetic.
    review = pr.cut_review(book)
    with open(os.path.join(root, "check-against-the-list.html"), "w") as fh:
        fh.write(review_page(pr, subject, review))
    write_json(os.path.join(root, "check-against-the-list.json"),
               dict(review, game=subject), indent=1)
    made += ["check-against-the-list.html", "check-against-the-list.json"]
    cuts = export_laser(pr, root, progress, book)
    if cuts:
        made.append("laser/ (%d sheet%s)" % (cuts, "" if cuts == 1 else "s"))
    with open(os.path.join(root, "README.txt"), "w") as fh:
        fh.write(EXPORT_README % {
            "game": subject, "dpi": dpi, "counts": counts,
            "copyright": COPYRIGHT_NOTICE,
            "contents": readme(made, len(rows) - len(live), bool(tick), cuts)})
    return {"folder": root, "pieces": len(live), "spare": len(rows) - len(live),
            "unnamed": unnamed, "laser": cuts, "files": made,
            "book": book or "", "set": pr.book_label(book) if book else ""}


# ------------------------------------------------- closing the room safely

# ⚠️ The designer does not want to touch a terminal, so the room has to be closable
# from the room. But fault 1 is the whole reason this thing exists: the work
# lives on disk, and a save that never lands is work destroyed. So the room
# refuses to close quietly over the top of anything still in flight, and says
# what it is waiting for.
#
# Two things can be in flight, and the room can only see one of them by
# itself:
#   * a JOB — an import or a cut, running on a thread here.
#   * an EDITOR — a browser tab with a sheet on the table. The room cannot
#     see a tab, so each open table says hello every few seconds and says
#     whether it has an edit that has not been written down yet.
TABLES = {}                    # tab id -> what that tab is doing
TABLES_LOCK = threading.Lock()
TABLE_SILENT = 30.0            # a table unheard from this long has gone away
LAST_SAVE = {"at": 0.0, "what": ""}


def at_the_table(tab, info):
    """An editor tab reporting in. `info` is None when the tab has gone."""
    with TABLES_LOCK:
        if info is None:
            TABLES.pop(tab, None)
        else:
            info["seen"] = time.time()
            TABLES[tab] = info


def open_tables():
    """The tables heard from lately, freshest first. Forgets the stale ones."""
    cutoff = time.time() - TABLE_SILENT
    with TABLES_LOCK:
        for tab in [t for t, v in TABLES.items() if v.get("seen", 0) < cutoff]:
            del TABLES[tab]
        return sorted(TABLES.values(), key=lambda v: -v.get("seen", 0))


def work_in_flight():
    """Everything that would be cut short by closing now, in plain English."""
    reasons = []
    with JOBS_LOCK:
        running = [j for j in JOBS.values() if j.get("state") == "running"]
    for j in running:
        reasons.append({"kind": "job", "hold": True,
                        "what": "%s — %s" % (j.get("label") or "a job",
                                             j.get("message") or "running")})
    for t in open_tables():
        where = t.get("label") or t.get("sheet") or ""
        game = t.get("name") or ""
        at = ((where + " ") if where else "") + ("(%s) " % game if game else "")
        if t.get("dirty"):
            reasons.append({"kind": "unsaved", "hold": True,
                            "what": ("%shas an edit still being written down" % at)
                                    if where else
                                    "the cutting table %shas an edit still being written down" % at})
        else:
            reasons.append({"kind": "table", "hold": False,
                            "what": ("%sis open on the cutting table" % at)
                                    if where else
                                    "the cutting table %sis open" % at})
    # A save that landed a moment ago means somebody is working right now,
    # even if their tab has not managed to say so yet.
    since = time.time() - (LAST_SAVE["at"] or 0)
    if LAST_SAVE["at"] and since < 3.0:
        reasons.append({"kind": "just-saved", "hold": True,
                        "what": "%s was saved a second ago" % (LAST_SAVE["what"] or "a sheet")})
    return reasons


def close_the_room(httpd):
    """Stop the server, a moment after the answer has reached the browser."""
    def run():
        time.sleep(0.5)
        httpd.shutdown()
    threading.Thread(target=run, daemon=True).start()


# ⭐️⭐️ OPENING IT AGAIN, WITHOUT THE TERMINAL. The designer, 24 August 2026: "is
# there a way to build a relaunch button into the browser tab it uses
# somehow?" — asked after being told, twice in one day, to close the room and
# open it again because it was running older code than its pages (fault 38).
# The advice is right and the errand is the problem: it means finding a
# Terminal window they never wanted to see.
#
# So the room starts itself again, in place: the same window, the same port,
# the same arguments, and a NEW process — which is the whole point, because a
# running program cannot re-read itself.
#
# ⚠️ The exec happens in the MAIN thread, after `serve_forever` has returned
# and the listening socket has been closed. Doing it from the handler's thread
# would race the main thread's own tidying up, and whichever won, the room
# might simply be gone.
RELAUNCH = {"asked": False}


def code_that_will_not_start():
    """⚠️ A RELAUNCH THAT CANNOT COME BACK IS A QUIT. The button exists to be
    pressed after the room's code has changed — which is exactly the moment
    that code might not parse. The old process is about to be replaced by the
    new one and there is nothing to fall back to, so the new code is read and
    compiled BEFORE anything is stopped, and a room that would not start again
    refuses to stop. Says which file, and what is wrong with it."""
    for mod in ("cutting_room.py", "sheets.py", "cut.py"):
        path = os.path.join(HERE, mod)
        try:
            with open(path, encoding="utf-8") as fh:
                compile(fh.read(), path, "exec")
        except OSError as exc:
            return "%s cannot be read (%s)" % (mod, exc)
        except SyntaxError as exc:
            return "%s would not start: %s at line %s" % (mod, exc.msg, exc.lineno)
    return None


# --------------------------------------------------------- the table page

_TABLE_CACHE = {"mtime": None, "html": None}

# Each patch is (old, new) on the editor template, applied by exact match.
# An anchor that fails to match raises, loudly, at the first request — a
# silently unpatched editor would save nothing to the room.
TABLE_PATCHES = [
    # the room's handles, injected beside the sheets
    ("""  var SHEETS = /*__SHEETS__*/;
  var SUBJECT = "/*__SUBJECT__*/";
""", """  var SHEETS = /*__SHEETS__*/;
  var SUBJECT = "/*__SUBJECT__*/";
  var ROOM = /*__ROOM__*/;
  var SAVED = /*__SAVED__*/;
  function byId(id) {
    for (var i = 0; i < SHEETS.length; i++) if (SHEETS[i].id === id) return SHEETS[i];
    return null;
  }
  var roomTimers = {};
  function roomFlash(ok) {
    var el = document.getElementById("roomState");
    if (!el) return;
    el.textContent = ok ? "kept in the room" : "⚠ not saved to the room";
    el.className = ok ? "roomok" : "roombad";
  }
  /* Every save goes to the room as well as to this browser, a moment after
     the last edit. The room's copy is the one the cut is made from. */
  var roomWaiting = {};       // sheets edited but not yet written down
  function roomSave(id, payload) {
    SAVED[id] = payload;
    clearTimeout(roomTimers[id]);
    roomWaiting[id] = true;
    roomTimers[id] = setTimeout(function () {
      roomTimers[id] = 0;
      fetch(ROOM.api + "/outlines/" + encodeURIComponent(id), {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload) })
        .then(function (r) { if (!r.ok) throw new Error(String(r.status)); roomFlash(true); })
        .catch(function () { roomFlash(false); })
        // Clear the mark only if no FURTHER edit has been made since; a live
        // timer here means this sheet is dirty again already.
        .then(function () { if (!roomTimers[id]) roomWaiting[id] = false; });
    }, 500);
  }
  function roomPost(path, body) {
    return fetch(ROOM.api + path, { method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}) }).then(function (r) { return r.json(); });
  }

  /* CLOSING THE ROOM MUST NOT CUT A SAVE SHORT. The room can see its own
     jobs but it cannot see a browser tab, so every open table says hello
     every few seconds and says whether it is holding an edit that has not
     been written down yet. That is what the front page asks about before it
     closes the room. Fault 1 in a new coat: the work goes to disk or it is
     not work. */
  var roomTab = "t" + Math.random().toString(36).slice(2) + Date.now().toString(36);
  function roomHolding() {
    for (var k in roomWaiting) if (roomWaiting[k]) return true;
    return false;
  }
  function roomHello(gone) {
    var text = JSON.stringify({ tab: roomTab, gone: !!gone,
      project: ROOM.project, name: ROOM.name,
      sheet: sheet ? sheet.id : "", label: sheet ? sheet.label : "",
      dirty: roomHolding() });
    // On the way out the page is already going, so a beacon is the only
    // send that is guaranteed to leave.
    if (gone && navigator.sendBeacon) { navigator.sendBeacon("/api/at-the-table", text); return; }
    fetch("/api/at-the-table", { method: "POST",
      headers: { "Content-Type": "application/json" }, body: text })
      .catch(function () { /* the room has gone; nothing to be done from here */ });
  }
  roomHello(false);
  setInterval(function () { roomHello(false); }, 8000);
  window.addEventListener("pagehide", function () { roomHello(true); });
"""),
    ('  var STORE = "cuttingtable.v2.";',
     '  var STORE = "cuttingroom.v1." + ROOM.project + ".";'),
    # load: the room's copy is the truth unless this browser has a newer one
    ("""    try {
      var raw = localStorage.getItem(STORE + s.id);
      if (raw) {
        var got = JSON.parse(raw);
""", """    try {
      var raw = localStorage.getItem(STORE + s.id);
      var srv = (SAVED && SAVED[s.id]) ? SAVED[s.id] : null;
      var loc = null;
      try { loc = raw ? JSON.parse(raw) : null; } catch (e3) { loc = null; }
      if (srv && (!loc || (srv.stamp || 0) >= (loc.stamp || 0))) {
        raw = JSON.stringify(srv);
        try { localStorage.setItem(STORE + s.id, raw); } catch (e4) { /* full */ }
      } else if (loc && (loc.stamp || 0) > ((srv && srv.stamp) || 0)) {
        roomSave(s.id, loc);        // an edit made while the room was away
      }
      if (raw) {
        var got = JSON.parse(raw);
"""),
    ("""      var spun = localStorage.getItem(STORE + "rot." + s.id);
      view.rot = spun ? (parseInt(spun, 10) % 4 + 4) % 4 : 0;
""", """      var spun = localStorage.getItem(STORE + "rot." + s.id);
      view.rot = spun ? (parseInt(spun, 10) % 4 + 4) % 4 : 0;
      if (typeof s.rot === "number") view.rot = ((s.rot % 4) + 4) % 4;
"""),
    # save: to the room as well
    ("""  function save() {
    try {
      localStorage.setItem(STORE + sheet.id, JSON.stringify(
        { pieces: pieces, draft: draft, guides: guides,
          dpi: scales[sheet.id] || 0 }));
""", """  function save() {
    var payload = { pieces: pieces, draft: draft, guides: guides,
                    dpi: scales[sheet.id] || 0, stamp: Date.now() };
    roomSave(sheet.id, payload);
    try {
      localStorage.setItem(STORE + sheet.id, JSON.stringify(payload));
"""),
    ("""      localStorage.setItem(STORE + "rot." + sheet.id, String(view.rot));
""", """      localStorage.setItem(STORE + "rot." + sheet.id, String(view.rot));
      sheet.rot = view.rot;
      roomPost("/sheet/" + encodeURIComponent(sheet.id), { rot: view.rot });
"""),
    ("""  function counts(id) {
    if (sheet && id === sheet.id) return pieces.length;
    try {
""", """  function counts(id) {
    if (sheet && id === sheet.id) return pieces.length;
    if (SAVED && SAVED[id] && SAVED[id].pieces) return SAVED[id].pieces.length;
    try {
"""),
    ("""  function isDone(id) {
    try { return localStorage.getItem(STORE + "done." + id) === "1"; }
    catch (e) { return false; }
  }

  function setDone(id, on) {
    try {
""", """  function isDone(id) {
    var sx = byId(id);
    if (sx && typeof sx.done === "boolean") return sx.done;
    try { return localStorage.getItem(STORE + "done." + id) === "1"; }
    catch (e) { return false; }
  }

  function setDone(id, on) {
    var sx = byId(id);
    if (sx) sx.done = !!on;
    roomPost("/sheet/" + encodeURIComponent(id), { done: !!on });
    try {
"""),
    # the automatic attempt is worked out by the room when first asked for
    ("""  function offers() {
    var n = (sheet && sheet.suggested ? sheet.suggested.length : 0);
""", """  function offers() {
    if (sheet && sheet.suggested === null) {
      elSuggest.textContent = "Find the suggested outlines";
      elSuggest.disabled = false;
      return;
    }
    var n = (sheet && sheet.suggested ? sheet.suggested.length : 0);
"""),
    ("""  function addSuggested(quiet) {
    var offered = (sheet.suggested || []);
""", """  function addSuggested(quiet) {
    if (sheet.suggested === null) {
      var s0 = sheet;
      elSuggest.disabled = true;
      elSuggest.textContent = "Looking for the pieces…";
      fetch(ROOM.api + "/suggest/" + encodeURIComponent(s0.id))
        .then(function (r) { return r.json(); })
        .then(function (j) {
          s0.suggested = j.suggested || [];
          if (sheet !== s0) return;
          offers();
          if (s0.suggested.length) addSuggested(quiet);
          else if (!quiet) window.alert("The colour flood found nothing on this sheet to suggest — draw the outlines by hand.");
        })
        .catch(function () { s0.suggested = []; if (sheet === s0) offers(); });
      return 0;
    }
    var offered = (sheet.suggested || []);
"""),
    # + Sheet hands the file to the room, which renders it and keeps it
    ("""  document.getElementById("sheetFile").addEventListener("change", function () {
    var input = this;
    takeFiles(input.files, function (made) {
      input.value = "";
      if (!made.length) return;
      made.forEach(function (s) { SHEETS.push(s); });
      load(made[0]);
      tabs();
    });
  });
""", """  document.getElementById("sheetFile").addEventListener("change", function () {
    var input = this;
    var files = Array.prototype.slice.call(input.files || []);
    input.value = "";
    if (!files.length) return;
    var btn = document.getElementById("addSheet");
    btn.disabled = true; btn.textContent = "Adding…";
    var chain = Promise.resolve(), firstId = null;
    files.forEach(function (f) {
      chain = chain.then(function () {
        return fetch(ROOM.api + "/import", { method: "POST",
            headers: { "X-Filename": encodeURIComponent(f.name), "X-Wait": "1" }, body: f })
          .then(function (r) { return r.json(); })
          .then(function (j) {
            if (j.error) throw new Error(j.error);
            if (!firstId && j.sheets && j.sheets.length) firstId = j.sheets[0].id;
          });
      });
    });
    chain.then(function () { location.hash = firstId || ""; location.reload(); })
      .catch(function (e) {
        window.alert("Could not add that: " + e.message);
        btn.disabled = false; btn.textContent = "+ Sheet";
      });
  });
"""),
    ('    <input type="file" id="sheetFile" accept="image/*" multiple hidden>',
     '    <input type="file" id="sheetFile" accept="image/*,.pdf,.docx,.doc,.zip" multiple hidden>'),
    # the header: a way back, and the cut
    ("""      <span id="subject">Card components</span>
    </div>
""", """      <span id="subject">Card components</span>
    </div>
    <a class="btn quiet" id="roomBack" href="/*__BACK__*/" title="Back to the project">⟵ Room</a>
    <button class="btn primary" id="roomCut" type="button" title="Cut the outlined pieces off this sheet">Cut this sheet</button>
    <span id="roomCutNote" class="tiny" style="color:#8494A5;font-size:12px"></span>
    <span id="roomState" class="roomok"></span>
"""),
    ("""  /* ---------------------------------------------------------------- scale */
""", """  /* ------------------------------------------------------------ the room */

  /* ⭐️⭐️ MENDING ONE PIECE CUTS THAT PIECE. The designer, 26 August 2026: "If
     I'm mending a piece, it seems obvious that default should be to just recut
     that specific piece no?" Quite so — and the room already had the control
     that says which piece you mean: working on one alone. The mend link from
     the Pieces page turns it on, so that flow gets this without asking. Turn
     it off and the button cuts the sheet, as it always did.
     ⚠️ The room still decides: it falls back to the whole sheet whenever
     cutting one would leave the numbering wrong. See cut_sheet(). */
  window.roomCutLabel = function () {
    var b = document.getElementById("roomCut");
    var note = document.getElementById("roomCutNote");
    if (!b) return;
    var one = solo && current >= 0;
    b.textContent = one ? "Cut this piece" : "Cut this sheet";
    b.title = one
      ? "Cut piece " + String(current + 1) + " off this sheet again, on its own — much quicker than the whole sheet, and the name it already has is kept. Nothing else on the sheet is touched."
      : "Cut the outlined pieces off this sheet";
    note.textContent = one ? "the other outlines are left alone" : "";
  };

  document.getElementById("roomCut").addEventListener("click", function () {
    if (!sheet) return;
    if (!pieces.length) { window.alert("Nothing is outlined on this sheet yet."); return; }
    var b = this;
    var one = (solo && current >= 0) ? current : null;
    b.disabled = true; b.textContent = "Cutting…";
    clearTimeout(roomTimers[sheet.id]);
    var sid = sheet.id, lab = sheet.label;
    var payload = { pieces: pieces, draft: draft, guides: guides,
                    dpi: scales[sheet.id] || 0, stamp: Date.now() };
    SAVED[sid] = payload;
    fetch(ROOM.api + "/outlines/" + encodeURIComponent(sid), { method: "PUT",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
      .then(function () { return roomPost("/cut/" + encodeURIComponent(sid), { only: one }); })
      .then(function (j) {
        b.disabled = false;
        window.roomCutLabel();
        if (j.error) { window.alert("The cut failed: " + j.error); return; }
        var n = (j.made || []).length;
        // ⚠️ SAY WHICH IT DID. Asked for one piece and given the whole sheet
        // — which the room does whenever the numbering would otherwise go
        // wrong — a silent answer would look as though the button had been
        // ignored. Fault 58 again.
        if (one !== null && !j.one) {
          window.alert("The whole sheet was cut rather than the one piece, because "
            + "mending it changed where the pieces fall in reading order. Every name "
            + "has followed its piece.");
        }
        // ⚠️ Never let a name go without saying so. A piece whose outline
        // has been removed has nothing left to be the name of, so the name
        // is set aside, kept in the manifest under `retired`. The person who
        // typed it is the one who needs to hear about it.
        // ⚠️ NO BACKSLASH ESCAPES IN HERE. This is a Python string in
        // TABLE_PATCHES before it is JavaScript, so an escaped newline is a real
        // newline by the time the page sees it, and a newline inside a string
        // kills the whole editor silently. That is fault 6, and it bit
        // TWICE while this very message was being written: once in the
        // message, and once in the comment warning about the message.
        var gone = Object.keys(j.retired || {}).map(function (k) { return j.retired[k]; })
                         .filter(function (x) { return x; });
        if (gone.length) {
          window.alert(gone.length + (gone.length === 1 ? " name is" : " names are") +
            " no longer on a piece, because the outline" +
            (gone.length === 1 ? " it belonged to is" : "s they belonged to are") +
            " gone: " + gone.join(" \u00b7 ") +
            ". They are kept in the project's manifest.json under retired, " +
            "if you need them back.");
        }
        if (j.one) {
          window.alert("Piece " + (one + 1) + " cut again from " + lab +
                       ". Its name and everything else on the sheet are untouched.");
          return;
        }
        if (window.confirm(n + " piece" + (n === 1 ? "" : "s") + " cut from " + lab + ". Go and name them?")) {
          location.href = ROOM.home + "#pieces/" + encodeURIComponent(sid);
        }
      })
      .catch(function (e) { b.disabled = false; window.roomCutLabel(); window.alert("The cut failed: " + e.message); });
  });

  /* ---------------------------------------------------------------- scale */
"""),
    ("""      } else {
        try {
          var raw = localStorage.getItem(STORE + s.id);
          if (raw) work.sheets[s.id] = JSON.parse(raw);
        } catch (e) { /* skip a sheet we cannot read */ }
      }
""", """      } else if (SAVED && SAVED[s.id]) {
        work.sheets[s.id] = SAVED[s.id];
      } else {
        try {
          var raw = localStorage.getItem(STORE + s.id);
          if (raw) work.sheets[s.id] = JSON.parse(raw);
        } catch (e) { /* skip a sheet we cannot read */ }
      }
"""),
    ("""      names.forEach(function (id) {
        try {
          localStorage.setItem(STORE + id, JSON.stringify(work.sheets[id]));
""", """      names.forEach(function (id) {
        roomSave(id, work.sheets[id]);
        try {
          localStorage.setItem(STORE + id, JSON.stringify(work.sheets[id]));
"""),
    # ⭐️ Every control says what it does. The room can serve the shared
    # script; the baked offline page cannot fetch anything, so its controls
    # keep the browser's own tooltips instead — the same sentences either way,
    # written once in the markup.
    ("<title>The Cutting Table</title>",
     "<title>/*__TITLE__*/</title>\n<script src=\"/room/tips.js\"></script>"),
    ("  load(SHEETS[SHEETS.length > 1 ? 1 : 0]);   // a sheet must exist before",
     "  load(SHEETS[0]);                           // a sheet must exist before"),
    ("""    .ledger { max-height: none; }
  }
</style>
""", """    .ledger { max-height: none; }
  }
  .mark { flex: 0 1 auto; }
  a.btn { text-decoration: none; display: inline-flex; align-items: center; }
  .roomok { font-size: 12px; color: #4FB477; white-space: nowrap; }
  .roombad { font-size: 12px; color: #ff9e85; white-space: nowrap; }
</style>
"""),
]


def table_template():
    mtime = os.path.getmtime(TEMPLATE)
    if _TABLE_CACHE["mtime"] == mtime and _TABLE_CACHE["html"]:
        return _TABLE_CACHE["html"]
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()
    for i, (old, new) in enumerate(TABLE_PATCHES):
        if old not in html:
            raise RuntimeError("the editor template has changed under the room: patch %d found no anchor:\n%s" % (i, old[:120]))
        html = html.replace(old, new, 1)
    _TABLE_CACHE.update(mtime=mtime, html=html)
    return html


def js(obj):
    """JSON that is safe inside a <script>."""
    return json.dumps(obj).replace("</", "<\\/")


def table_page(project, sheet_ids=None):
    html = table_template()
    book = project.outlines().get("sheets", {})
    sheets = []
    for s in project.sheets:
        if sheet_ids and s["id"] not in sheet_ids:
            continue
        sheets.append({
            # the rail says what the box is called too, or the table and the
            # room disagree about the name of the sheet on the table
            "id": s["id"], "label": project.sheet_title(s), "name": s.get("name") or "",
            "w": s.get("w"), "h": s.get("h"),
            "src": "/p/%s/sheet/%s.jpg" % (project.id, s["id"]),
            "suggested": None, "done": bool(s.get("done")), "rot": int(s.get("rot") or 0),
            "skip": sheet_skips(s),
        })
    saved = {sid: book[sid] for sid in book if any(x["id"] == sid for x in sheets)}
    room = {"project": project.id, "api": "/api/p/%s" % project.id,
            "home": "/p/%s/" % project.id, "name": project.meta.get("name", project.id)}
    subject = (project.meta.get("name") or project.id)
    # ⚠️⚠️ THE EDITOR MUST BE TOLD THE PROJECT'S SCALE. It carried a bare
    # `var DPI = 300` and nothing ever told it otherwise, so every inch figure
    # on the table — the piece readout, the measuring tool, the scale panel,
    # the millimetres in the SVG — was wrong for any project not set to 300,
    # and a shape laid from the shelf at a typed size came out at the wrong
    # number of pixels. The cut itself was always right, because that is done
    # here at project.dpi; it was only the screen that lied. See fault 93.
    html = (html.replace("/*__DPI__*/300", str(int(project.dpi)))
                .replace("/*__SHEETS__*/", js(sheets))
                .replace("/*__SUBJECT__*/", subject.replace('"', "'"))
                .replace("/*__ROOM__*/", js(room))
                .replace("/*__SAVED__*/", js(saved))
                .replace("/*__BACK__*/", "/p/%s/" % project.id)
                .replace("/*__TITLE__*/", "%s — the Cutting Table" % subject.replace("<", "&lt;")))
    return html


# ------------------------------------------------------------------ server

class Room(BaseHTTPRequestHandler):
    registry = None            # set by main()
    httpd = None               # set by main(), so the room can close itself
    server_version = "CuttingRoom/1"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):          # quieter than the default
        # ⚠️ args[0] is a string for a served request but an HTTPStatus when
        # the base class logs an error, so it has to be made one first — this
        # threw a traceback on every malformed request until it was seen in
        # the room's own window.
        first = str(args[0]) if args else ""
        if "/api/" in first and " 200 " in first:
            return
        sys.stderr.write("%s - %s\n" % (self.log_date_time_string(), fmt % args))

    # ---- plumbing
    def send(self, code, body, ctype="text/html; charset=utf-8", headers=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_json(self, obj, code=200):
        self.send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def send_file(self, path, ctype=None, cache=True):
        if not os.path.exists(path):
            return self.send_json({"error": "no such file"}, 404)
        ctype = ctype or {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".html": "text/html; charset=utf-8", ".json": "application/json",
        }.get(os.path.splitext(path)[1].lower(), "application/octet-stream")
        # ⚠️ A SHEET IS TWO MEGABYTES AND IS ASKED FOR AGAIN EVERY TIME IT
        # COMES BACK TO THE TABLE. Stamped with the file's own time, the
        # browser asks "still this one?" and is told yes in a few bytes,
        # so stepping between sheets does not re-fetch the whole picture.
        stamp = formatdate(os.path.getmtime(path), usegmt=True)
        if cache and self.headers.get("If-Modified-Since") == stamp:
            self.send_response(304)
            self.send_header("Cache-Control", "max-age=60")
            self.send_header("Last-Modified", stamp)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        with open(path, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=60" if cache else "no-store")
        if cache:
            self.send_header("Last-Modified", stamp)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def body(self):
        # Read once in route(), for every request, wanted or not — see there.
        return self._body

    def body_json(self):
        raw = self.body()
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            return {}

    def redirect(self, where):
        self.send_response(302)
        self.send_header("Location", where)
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ---- routing
    def do_GET(self):
        self.route("GET")

    def do_HEAD(self):
        self.route("GET")

    def do_POST(self):
        self.route("POST")

    def do_PUT(self):
        self.route("PUT")

    def do_DELETE(self):
        self.route("DELETE")

    def route(self, method):
        try:
            # ⚠️⚠️ THE BODY IS ALWAYS READ, WHETHER THE HANDLER WANTS IT OR NOT.
            #
            # This connection is kept alive and carries one request after
            # another. A handler that answers a POST without reading its body
            # leaves those bytes in the socket, and the NEXT request on the
            # same connection is read starting from them: the browser asked
            # for a page and the room saw the request line "{}GET /p/... " and
            # answered 501 Unsupported method. The project page came up as an
            # error page with nothing on it.
            #
            # "Cut this sheet" was the handler that forgot. It was found by
            # check.sh going red on the Match board — and it had been there
            # all along, hidden, because log_message() used to CRASH on the
            # error it was reporting, which killed the connection, which made
            # the browser quietly try again on a clean one. Fixing the crash
            # is what let the fault be seen.
            #
            # ⚠️ This is fault 14 again — a guard that only SOME of a set of
            # handlers remember is a guard one of them will forget. So it is
            # not each handler's job any more; it is done once, here.
            n = int(self.headers.get("Content-Length") or 0)
            self._body = self.rfile.read(n) if n else b""
            url = urllib.parse.urlsplit(self.path)
            parts = [urllib.parse.unquote(p) for p in url.path.split("/") if p]
            query = urllib.parse.parse_qs(url.query)
            self._route(method, parts, query)
        except ConnectionError:
            pass
        except Exception as exc:               # noqa: BLE001
            traceback.print_exc()
            try:
                self.send_json({"error": str(exc)}, 500)
            except Exception:                  # noqa: BLE001
                pass

    def _route(self, method, parts, query):
        reg = self.registry
        # -- pages and static
        if not parts:
            return self.send_file(os.path.join(ROOM_DIR, "home.html"), cache=False)
        if parts[0] == "room":
            path = os.path.normpath(os.path.join(ROOM_DIR, *parts[1:]))
            if not path.startswith(ROOM_DIR):
                return self.send_json({"error": "no"}, 403)
            return self.send_file(path)
        if parts[0] == "p" and len(parts) >= 2:
            pr = reg.get(parts[1])
            if pr is None:
                return self.send(404, "<h1>No such project</h1><p><a href='/'>Back to the room.</a></p>")
            rest = parts[2:]
            if not rest:
                return self.send_file(os.path.join(ROOM_DIR, "project.html"), cache=False)
            if rest[0] == "table":
                if not pr.sheets:
                    return self.redirect("/p/%s/" % pr.id)
                only = query.get("sheet")
                return self.send(200, table_page(pr, set(only) if only else None))
            if rest[0] == "sheet" and len(rest) == 2:
                sid = rest[1][:-4] if rest[1].endswith(".jpg") else rest[1]
                if not pr.sheet(sid):
                    return self.send_json({"error": "no such sheet"}, 404)
                return self.send_file(pr.sheet_jpg(sid), "image/jpeg")
            if rest[0] == "thumb" and len(rest) == 2:
                sid = rest[1][:-4] if rest[1].endswith(".jpg") else rest[1]
                if not pr.sheet(sid):
                    return self.send_json({"error": "no such sheet"}, 404)
                return self.send_file(pr.sheet_thumb(sid, bool(query.get("marks"))),
                                      "image/jpeg")
            if rest[0] == "mask" and len(rest) == 2:
                return self.send_file(os.path.join(pr.p("masks"), rest[1]), "image/png")
            if rest[0] == "piece" and len(rest) == 2:
                stem = rest[1][:-4] if rest[1].endswith(".png") else rest[1]
                return self.send_file(pr.piece_file(stem), "image/png", cache=False)
            if rest[0] == "piece-thumb" and len(rest) == 2:
                stem = rest[1][:-4] if rest[1].endswith(".png") else rest[1]
                if not os.path.exists(pr.piece_file(stem)):
                    return self.send_json({"error": "no such piece"}, 404)
                return self.send_file(pr.piece_thumb(stem), "image/png", cache=False)
            return self.send_json({"error": "no such page"}, 404)

        # -- API
        if parts[0] != "api":
            return self.send_json({"error": "no such page"}, 404)
        api = parts[1:]
        if api == ["projects"]:
            if method == "GET":
                return self.send_json({"home": reg.home,
                                       "projects": [p.status() for p in reg.projects()]})
            if method == "POST":
                d = self.body_json()
                name = str(d.get("name") or "").strip()
                if not name:
                    return self.send_json({"error": "a project needs a name"}, 400)
                if d.get("path"):
                    path = os.path.expanduser(str(d["path"]))
                    if not os.path.exists(os.path.join(path, "project.json")):
                        return self.send_json({"error": "no project.json at %s" % path}, 400)
                    reg.register(path)
                    return self.send_json({"ok": True, "project": Project(path).status()})
                pr = reg.create(name, str(d.get("game") or ""))
                return self.send_json({"ok": True, "project": pr.status()})
        # ---- opening and quitting without a terminal
        if api == ["at-the-table"] and method == "POST":
            # An open editor saying hello. Kept deliberately tiny: it is sent
            # every few seconds by every tab that has a sheet on the table.
            d = self.body_json()
            tab = str(d.get("tab") or "")
            if not tab:
                return self.send_json({"error": "no tab"}, 400)
            at_the_table(tab, None if d.get("gone") else {
                "project": str(d.get("project") or ""),
                "name": str(d.get("name") or ""),
                "sheet": str(d.get("sheet") or ""),
                "label": str(d.get("label") or ""),
                "dirty": bool(d.get("dirty"))})
            return self.send_json({"ok": True})
        # ⭐️ Every page asks this, so that a room running yesterday's code
        # says so rather than answering "no such call" to a button built today.
        if api == ["health"] and method == "GET":
            return self.send_json({"ok": True, "stale": stale_code(),
                                   "started": int(STARTED_AT * 1000)})

        if api == ["busy"] and method == "GET":
            reasons = work_in_flight()
            return self.send_json({"reasons": reasons,
                                   "hold": any(r["hold"] for r in reasons)})
        if api == ["close"] and method == "POST":
            reasons = work_in_flight()
            hold = any(r["hold"] for r in reasons)
            if hold and not self.body_json().get("force"):
                # Not an error — a question. The browser asks it of the person.
                return self.send_json({"closed": False, "hold": True, "reasons": reasons})
            if self.httpd is None:                # started some other way
                return self.send_json({"closed": False, "hold": False, "reasons": reasons,
                                       "error": "this room cannot close itself"}, 500)
            self.send_json({"closed": True, "how": HOW_TO_OPEN[0]})
            close_the_room(self.httpd)
            return
        # ⭐️⭐️ THE SAME DOOR, BUT IT OPENS AGAIN BEHIND YOU. Stopping and
        # starting are one act here, and they answer to the same guard as
        # closing — a room that must not be closed must not be restarted
        # either, because a restart IS a close with a promise attached.
        if api == ["relaunch"] and method == "POST":
            reasons = work_in_flight()
            hold = any(r["hold"] for r in reasons)
            if hold and not self.body_json().get("force"):
                return self.send_json({"relaunching": False, "hold": True,
                                       "reasons": reasons})
            if self.httpd is None:
                return self.send_json({"relaunching": False, "hold": False,
                                       "error": "this room cannot start itself again"},
                                      500)
            # ⚠️ read the new code before letting go of the old room
            bad = code_that_will_not_start()
            if bad:
                return self.send_json({"relaunching": False, "hold": False,
                                       "reasons": reasons, "wont_start": bad})
            RELAUNCH["asked"] = True
            self.send_json({"relaunching": True, "was": int(STARTED_AT * 1000),
                            "how": HOW_TO_OPEN[0]})
            close_the_room(self.httpd)
            return
        if len(api) >= 2 and api[0] == "jobs":
            job = JOBS.get(api[1])
            return self.send_json(job or {"error": "no such job"}, 200 if job else 404)
        # ⭐️ The shelf of kept shapes belongs to the room, not to a project,
        # so that a shape drawn for one game can be laid down in another.
        if api == ["shapes"] and method == "POST":
            d = self.body_json()
            what = str(d.get("what") or "list")
            with reg.shapes_lock:
                book = reg.shapes()
                shapes = book.get("shapes") or []
                if what == "keep":
                    sh = clean_shape(d.get("shape") or {})
                    if isinstance(sh, str):
                        return self.send_json({"error": sh}, 400)
                    shapes = shelf_keep(reg, sh, d.get("project"), d.get("game"))
                elif what == "star":
                    # ⭐️ The mark is the PROJECT's, not the shape's: the same
                    # door can be one game's kept shape and another game's at
                    # the same time, and neither of them has to know the other
                    # exists.
                    wanted = str((d.get("shape") or {}).get("id") or "")
                    pid = str(d.get("project") or "")[:80]
                    for s0 in shapes:
                        if s0.get("id") == wanted and pid:
                            marks = starred(s0)
                            if pid in marks:
                                marks.remove(pid)
                            else:
                                marks.append(pid)
                            s0["stars"] = marks
                elif what == "forget":
                    gone = str((d.get("shape") or {}).get("id") or "")
                    shapes = [s for s in shapes if s.get("id") != gone]
                elif what != "list":
                    return self.send_json({"error": "no such thing to do with a shape"}, 400)
                if what in ("star", "forget"):
                    book["shapes"] = shapes
                    reg.save_shapes(book)
            return self.send_json({"shapes": shapes})

        if len(api) >= 2 and api[0] == "p":
            pr = reg.get(api[1])
            if pr is None:
                return self.send_json({"error": "no such project"}, 404)
            return self.project_api(method, pr, api[2:], query)
        return self.send_json({"error": "no such call"}, 404)

    def project_api(self, method, pr, rest, query):
        if not rest:
            if method == "GET":
                return self.send_json(pr.status())
            if method == "POST":                     # edit name / game / notes
                d = self.body_json()
                for k in ("name", "game", "notes"):
                    if k in d:
                        pr.meta[k] = str(d[k])
                pr.save_meta()
                return self.send_json(pr.status())
        head = rest[0]

        if head == "import" and method == "POST":
            fname = urllib.parse.unquote(self.headers.get("X-Filename") or "upload.bin")
            prefix = self.headers.get("X-Prefix") or None
            data = self.body()
            if not data:
                return self.send_json({"error": "empty upload"}, 400)
            # ⚠️ `report` — what the import DID, which is not always what it
            # looks like: a file whose name has been used before replaces the
            # pictures of the sheets it made last time. See fault 94.
            if self.headers.get("X-Wait"):
                report = {}
                made = import_into(pr, fname, data, prefix, None, report)
                return self.send_json(dict({"ok": True, "sheets": made}, **report))

            def run(progress):
                report = {}
                made = import_into(pr, fname, data, prefix, progress, report)
                return dict({"sheets": made}, **report)
            job = start_job("import " + fname, run)
            return self.send_json({"job": job["id"]})

        if head == "fetch" and method == "POST":
            d = self.body_json()
            urls = [u.strip() for u in re.split(r"[\s,]+", str(d.get("url") or "")) if u.strip()]
            if not urls:
                return self.send_json({"error": "paste a link first"}, 400)
            prefix = str(d.get("prefix") or "") or None

            def run(progress):
                made = []
                report = {}
                for i, u in enumerate(urls, 1):
                    progress(i - 1, len(urls), "fetching link %d of %d" % (i, len(urls)))
                    name, blob = fetch_url(u, progress)
                    made += import_into(pr, name, blob, prefix, progress, report)
                return dict({"sheets": made}, **report)
            job = start_job("fetch %d link(s)" % len(urls), run)
            return self.send_json({"job": job["id"]})

        # ⭐️⭐️ WHAT A BOX OF SHEETS IS CALLED. The designer, 25 August 2026: "Ability
        # to rename imported sections (I've imported two separate sets of
        # things into the project, the first is the core box, the second a
        # supplement. I need to rename them from their current file names
        # (which are lots of nonsense)."
        #
        # A sheet's id is made from the name of the file it came in as, and
        # the box is the part of that id before the page number (fault 42) —
        # so a game imported from a folder of scans is filed under whatever
        # the scanner called them, and every list in the room says so.
        #
        # ⚠️⚠️ THE ID IS NEVER TOUCHED, and that is the whole design. A piece
        # is named from its sheet's id (`core_p03_00`), the outlines are filed
        # under it, and a game reading the manifest knows pieces by it. This
        # writes down what the box is CALLED and nothing else: a name is a
        # label, and renaming things that other things are keyed by is how
        # work gets lost.
        # ⭐️⭐️ WHAT SCALE THIS PROJECT'S SCANS ARE AT. Until now this was
        # settable only by editing project.json by hand, and a new project was
        # hard-coded to 300 — so somebody importing 600dpi scans had no way to
        # say so except measuring a line on every single sheet, one at a time.
        # ⚠️ IT CHANGES WHAT EVERY PIECE MEASURES, so the page says so before
        # asking, and says it in inches rather than in the abstract: this is
        # the one setting in the room that silently rewrites numbers somebody
        # may already have written down elsewhere. See fault 93.
        # ⚠️ A SHEET TOLD ITS OWN SCALE STILL WINS. `scales[sheet.id]` is
        # measured on that sheet and is better evidence than a project-wide
        # default, so this only moves the sheets that never said.
        if head == "dpi" and method == "POST":
            try:
                want = int(float((self.body_json() or {}).get("dpi") or 0))
            except (TypeError, ValueError):
                want = 0
            # the same fence the table's own ruler uses: below or above this
            # is a typo, not a scan
            if not (20 <= want <= 2400):
                return self.send_json(
                    {"error": "A scale of %s is not a scan. Give a number "
                              "between 20 and 2400 dots per inch — 300 for a "
                              "PDF rendered at true size, 600 for most "
                              "scanners." % (want or "that")}, 400)
            with pr.lock:
                was = int(pr.dpi)
                pr.meta["dpi"] = want
                pr.save_meta()
            return self.send_json({"ok": True, "dpi": want, "was": was})

        if head == "book" and len(rest) == 2 and method == "POST":
            name = str((self.body_json() or {}).get("name") or "").strip()[:80]
            with pr.lock:
                books = dict(pr.meta.get("books") or {})
                if name:
                    books[rest[1]] = name
                else:
                    books.pop(rest[1], None)     # back to its own name
                pr.meta["books"] = books
                pr.save_meta()
            return self.send_json({"ok": True, "books": books})

        # ⭐️⭐️ PUT BY FOR LATER, OR BROUGHT BACK INTO THE CUTTING. One door
        # for both, because the Sheets page and the checklist are pressing the
        # same switch — see `later_keys()` for why the mark is a key rather
        # than a flag on the sheet or on the set.
        # ⚠️ IT DELETES NOTHING AND HIDES NOTHING: the sheets stay where they
        # are and anything already cut from them still counts. All it changes
        # is which sets the room adds up when it says how far you have got.
        # ⭐️ ONE DOOR FOR BOTH MARKS. `later` is a set not being cut yet and
        # `filed` is one that is finished (see filed_keys); they are opposite
        # in meaning and identical in mechanism, so writing the route out
        # twice would be fault 24 over the two switches most likely to be
        # pressed by mistake for one another.
        if head in ("later", "filed") and len(rest) == 1 and method == "POST":
            d = self.body_json()
            key = str(d.get("key") or "").strip()[:120]
            if not (key.startswith("book:") or key.startswith("set:")):
                return self.send_json({"error": "a set is marked as book:<id> "
                                                "or set:<id>"}, 400)
            with pr.lock:
                keys = [k for k in (pr.meta.get(head) or []) if k != key]
                if d.get(head):
                    keys.append(key)
                pr.meta[head] = sorted(keys)
                pr.save_meta()
            return self.send_json({"ok": True, head: pr.meta[head]})

        # ⭐️⭐️ PUTTING SHEETS INTO ONE SET. The designer, 25 August 2026, having dragged
        # twelve files in at once: "assuming they would all stay together as a
        # single set of 12 sheets, but they've all turned into separate sets,
        # which is highly inefficient."
        # ⚠️ NOTHING IS RENAMED and no file moves: this writes `book` on each
        # sheet, which is only what SET it belongs to. The id every piece is
        # named from, every outline is filed under, and every mask and
        # thumbnail is stored as, is untouched — so this is completely
        # reversible, and an empty book puts them back where they were.
        if head == "sheets" and len(rest) == 2 and rest[1] == "book" and method == "POST":
            d = self.body_json()
            ids = [str(x) for x in (d.get("ids") or [])]
            # ⚠️ EMPTY MEANS EMPTY. `slug()` answers "sheet" for nothing at
            # all, which is a sensible id and a terrible answer here: it would
            # file every sheet under a set called "sheet" instead of putting
            # them back where they were.
            raw = str(d.get("book") or d.get("name") or "").strip()
            book = slug(raw, 40) if raw else ""
            name = str(d.get("name") or "").strip()[:80]
            if not ids:
                return self.send_json({"error": "no sheets given"}, 400)
            with pr.lock:
                n = 0
                for sid in ids:
                    s = pr.sheet(sid)
                    if s is None:
                        continue
                    if book:
                        s["book"] = book
                    else:
                        s.pop("book", None)
                    n += 1
                if book and name:
                    books = dict(pr.meta.get("books") or {})
                    books[book] = name
                    pr.meta["books"] = books
                pr.save_meta()
            return self.send_json({"ok": True, "sheets": n, "book": book})

        if head == "sheet" and len(rest) == 2:
            s = pr.sheet(rest[1])
            if s is None:
                return self.send_json({"error": "no such sheet"}, 404)
            if method == "POST":
                d = self.body_json()
                with pr.lock:
                    for k in ("label", "name", "source"):
                        if k in d:
                            s[k] = str(d[k])
                    if "done" in d:
                        s["done"] = bool(d["done"])
                    if "rot" in d:
                        s["rot"] = int(d["rot"]) % 4
                    # ⚠️ Kept on the sheet beside its turn, and NOT in
                    # outlines.json: a masked-off region can be drawn again in
                    # a moment, while an outline cannot, and the three stores
                    # that keep their own history are the three that cannot be
                    # rebuilt (fault 49).
                    if "skip" in d:
                        s["skip"] = sheet_skips({"skip": d["skip"]})
                    pr.save_meta()
                return self.send_json({"ok": True, "sheet": s})
            if method == "DELETE":
                with pr.lock:
                    gone = remove_sheets(pr, [s["id"]], bool(query.get("pieces")))
                return self.send_json(dict({"ok": True}, **gone))

        # ⭐️⭐️ A WHOLE BOX AT ONCE. The designer, 25 August 2026: "I'd like to be able
        # to remove a full set of imported sheets in one click (after a
        # confirmation). The [two of these books] are irrelevant here."
        # Thirty sheets removed one × at a time is thirty confirmations, and
        # somebody will stop reading them by the fourth — which is worse for
        # the one that matters than a single question that says everything.
        # ⚠️ It is the same removal, not a second one that will drift from it
        # (fault 24): both doors call `remove_sheets()`.
        if head == "book" and len(rest) == 2 and method == "DELETE":
            ids = [x["id"] for x in pr.sheets if pr.book_of(x["id"]) == rest[1]]
            if not ids:
                return self.send_json({"error": "no such set of sheets"}, 404)
            with pr.lock:
                gone = remove_sheets(pr, ids, bool(query.get("pieces")))
                books = dict(pr.meta.get("books") or {})
                if books.pop(rest[1], None) is not None:
                    pr.meta["books"] = books      # nothing left to call anything
                    pr.save_meta()
            return self.send_json(dict({"ok": True}, **gone))

        # ⭐️ The shape of a piece already cut. The outline it came off is
        # still on file, so this lifts the line that was drawn rather than
        # tracing it back out of the finished picture.
        if head == "shape" and len(rest) == 2 and method == "POST":
            d = self.body_json()
            made = shape_of_cut_piece(pr, rest[1], str(d.get("name") or "").strip()[:80])
            if isinstance(made, str):
                return self.send_json({"error": made}, 400)
            shapes = shelf_keep(self.registry, made, pr.id,
                                pr.meta.get("name") or pr.id)
            return self.send_json({"ok": True, "shape": made, "shapes": shapes})

        if head == "outlines":
            if len(rest) == 1 and method == "GET":
                return self.send_json(pr.outlines())
            if len(rest) == 2:
                sid = rest[1]
                if method == "GET":
                    return self.send_json(pr.outlines().get("sheets", {}).get(sid) or {})
                if method == "PUT":
                    d = self.body_json()
                    s = pr.sheet(sid)
                    if s is None:
                        return self.send_json({"error": "no such sheet"}, 404)
                    with pr.lock:
                        book = pr.outlines()
                        rec = {"pieces": d.get("pieces") or [], "draft": d.get("draft"),
                               "guides": d.get("guides") or [], "dpi": d.get("dpi") or 0,
                               "stamp": int(d.get("stamp") or now_ms()),
                               "w": s.get("w"), "h": s.get("h"), "label": s.get("label")}
                        # ⚠️⚠️ A SAVE THAT CHANGES NOTHING MUST NOT MAKE THE
                        # SHEET STALE. `stamp` is the whole of how the room
                        # decides a sheet has been outlined again since its cut
                        # (cut_state), and every such sheet goes back into
                        # *Cut every outlined sheet* — so a save carrying the
                        # identical work but a newer stamp puts a finished
                        # sheet in the queue for ever.
                        #
                        # The designer, 3 September 2026: "it said 67 sheets
                        # needed cutting... but I expected 66. I think there
                        # may be a bug with the core box components, because
                        # when I tried to 'put that set by' it noted there was
                        # 1 sheet outlined (even though all 11 sheets have been
                        # cut and finished with)." It was core-01, and it had
                        # been silently re-cut on every run: the editor mends
                        # repeated ink colours as a sheet loads, that sheet has
                        # 17 outlines against a palette of 12, so the repeat is
                        # unavoidable and it "mended" and saved every time.
                        # Fifteen of that game's sheets were in the same state.
                        #
                        # ⭐️ This is fault 49's rule — "a save that changes
                        # nothing must keep nothing" — arriving on staleness
                        # rather than on the history. The editor's end is
                        # mended too, but this is the guard that holds however
                        # a pointless save arrives.
                        was = (book.get("sheets") or {}).get(sid) or {}
                        same = all(was.get(k) == rec[k]
                                   for k in ("pieces", "draft", "guides", "dpi"))
                        if same and was.get("stamp"):
                            rec["stamp"] = was["stamp"]
                        book.setdefault("sheets", {})[sid] = rec
                        pr.save_outlines(book)
                    # ⚠️ so that closing the room knows somebody is at work
                    LAST_SAVE["at"] = time.time()
                    LAST_SAVE["what"] = s.get("label") or sid
                    return self.send_json({"ok": True, "pieces": len(rec["pieces"])})

        if head == "suggest" and len(rest) == 2 and method == "GET":
            sid = rest[1]
            if not pr.sheet(sid):
                return self.send_json({"error": "no such sheet"}, 404)
            cache = os.path.join(pr.p("cache"), sid + ".suggest.json")
            got = read_json(cache, None)
            # ⚠️ A CACHED DRAFT OUTLIVES THE CODE THAT MADE IT. The automatic
            # pass was made worth using on 25 August 2026 (rectangles fitted as
            # rectangles, and each outline saying whether it is straight or
            # curved) — and every sheet already drafted would have gone on
            # being offered yesterday's answer, for ever, with nothing to say
            # so. Bump this whenever the drafting changes.
            if got is not None and got.get("v") != SUGGEST_VERSION:
                got = None
            # ⭐️ A MASKED-OFF REGION IS PART OF THE QUESTION, so it is part of
            # what the kept answer is an answer TO. Without this the draft made
            # before the mask was drawn would be served for ever, and the tool
            # would look as though it had done nothing at all — which is fault
            # 58's shape, half working reading as broken.
            skips = sheet_skips(pr.sheet(sid))
            if got is not None and (got.get("skip") or []) != skips:
                got = None
            if got is None:
                rgb = np.asarray(Image.open(pr.sheet_png(sid)).convert("RGB"))
                if skips:
                    # ⚠️ Painted with the sheet's own colour rather than cut
                    # out, so the ground reads as paper right across it: a hole
                    # of black would be the biggest piece on the sheet.
                    rgb = rgb.copy()
                    ground = sheetlib.flat_colour(rgb)
                    for x1, y1, x2, y2 in sheet_skips(pr.sheet(sid), rgb.shape):
                        rgb[y1:y2, x1:x2] = ground
                mask = None
                for cand in (os.path.join(pr.p("masks"), sid + "-starter.png"),):
                    if os.path.exists(cand):
                        mask = cand
                got = {"v": SUGGEST_VERSION, "skip": skips,
                       "suggested": suggest_outlines(rgb, mask, pr.dpi)}
                write_json(cache, got)
            return self.send_json(got)

        if head == "cut" and len(rest) == 2 and method == "POST":
            # ⭐️ `only` names ONE outline, by its position in the sheet's list —
            # mending a piece should cut that piece. See cut_sheet(), which
            # falls back to the whole sheet whenever that would not be safe.
            d = self.body_json()
            only = d.get("only")
            try:
                only = int(only) if only is not None else None
            except (TypeError, ValueError):
                only = None
            try:
                return self.send_json(dict(ok=True, **cut_sheet(pr, rest[1], only)))
            except RuntimeError as exc:
                return self.send_json({"error": str(exc)}, 400)

        if head == "export" and method == "POST":
            # A big project is hundreds of pieces to turn, crop and write, so
            # it runs as a job with a count, like the import and the cut do.
            # ⭐️ `set` names one box of sheets to write on its own.
            d = self.body_json()
            want = str(d.get("set") or "").strip()
            if want and want not in [b["id"] for b in pr.books()]:
                return self.send_json({"error": "no such set of sheets"}, 400)
            job = start_job("Writing the export folder",
                            lambda prog: export_project(pr, prog, want or None))
            return self.send_json(job)

        if head == "cut-all" and method == "POST":
            # ⚠️⚠️ SHEETS ALREADY CUT ARE SKIPPED. This read "every sheet with
            # an outline on it" and so re-cut a whole 161-sheet game to get at
            # 22 new ones. ⭐️ `sheets` holds it to the ones the person is
            # looking at — "just cut the ones I'm looking at within the current
            # import" — and an old page that sends none still gets the skipping.
            # See waiting_to_cut(), which is the one rule.
            d = self.body_json()
            only = d.get("sheets")
            todo = pr.waiting_to_cut(only if isinstance(only, list) else None)
            if not todo:
                return self.send_json({"error": "Nothing is waiting to be cut."}, 400)

            def run(progress):
                out = {}
                for i, sid in enumerate(todo, 1):
                    progress(i - 1, len(todo), "cutting %s (%d of %d)" % (sid, i, len(todo)))
                    try:
                        out[sid] = len(cut_sheet(pr, sid)["made"])
                    except RuntimeError as exc:
                        out[sid] = str(exc)
                progress(len(todo), len(todo), "done")
                return out
            job = start_job("cut every outlined sheet", run)
            return self.send_json({"job": job["id"], "sheets": todo})

        if head == "pieces" and method == "GET":
            # ⚠️ WHATEVER IS IN THE SPARE FOLDER IS SET ASIDE, whether or not
            # anything ever wrote it down — see adopt_spares(). This is where
            # the screen is drawn from, so this is where the two are made to
            # agree, and it writes nothing unless they disagree.
            with pr.lock:
                pr.adopt_spares()
            idx = pr.index().get("pieces", {})
            man = pr.manifest().get("pieces", {})
            # a piece set aside is still one of this game's pieces: it is in
            # neither the index nor the folder in play, so it is asked for by
            # name or it drops off the screen altogether
            stems = sorted(set(idx) | set(pr.piece_files()) | pr.spare_stems())
            sizes = {s["id"]: (s.get("w"), s.get("h")) for s in pr.sheets}
            # ⚠️ WORKED OUT HERE, NOT IN THE PAGE. Which pieces have lost
            # their sheet decides what a delete button sweeps, and a second
            # copy of that rule in JavaScript would eventually disagree with
            # this one — over the one action in the room that destroys a
            # piece. See lost_pieces() and fault 95.
            lost = set(lost_pieces(pr))
            out = []
            for st in stems:
                meta = idx.get(st, {})
                mm = pr.piece_stats(st, meta.get("dpi"),
                                    sizes.get(meta.get("sheet")), meta.get("box")) or {}
                # ⚠️ A piece that runs off the edge of the sheet is only
                # PART of a piece, so its measurements are a half-truth and a
                # guess made from them would be a confident lie. No guess.
                guess = None if mm.get("edge") else guess_kind(
                    mm.get("w_in"), mm.get("h_in"), mm.get("cover"))
                out.append({"stem": st, "sheet": meta.get("sheet", ""),
                            "lost": st in lost,
                            "guess": guess,
                            "w_in": mm.get("w_in"), "h_in": mm.get("h_in"),
                            "hash": mm.get("hash"), "cover": mm.get("cover"),
                            "rgb": mm.get("rgb"), "bits": mm.get("bits"),
                            "edge": mm.get("edge", False),
                            "ink_rgb": meta.get("ink_rgb"),
                            "outline": self._outline_no(pr, st, meta),
                            "data": man.get(st, {})})
            # ⭐️ the SETS as well as the components: a dropdown of three
            # hundred components is unusable unless it can say which box each
            # one belongs to, and the sets are named in the checklist's own
            # store rather than on the components themselves.
            wb = pr.wanted()
            return self.send_json({"pieces": out, "types": pr.meta.get("types") or {},
                                   "kinds": KINDS, "wanted": wb.get("items", []),
                                   "groups": wb.get("groups", [])})

        # ⚠️⚠️ THE ONE PLACE, BESIDES REMOVING A SHEET, THAT REALLY DELETES A
        # CUT PIECE — and it is deliberately the narrowest door in the room.
        # The designer, 1 September 2026: "how do I remove all the pieces…
        # I can't see any other way to do it." There was no other way: a box's
        # removal asks about its pieces, a single sheet's × never did, and once
        # the sheet was gone the pieces were unreachable.
        # ⚠️ It sweeps ONLY what lost_pieces() names — never a joined piece,
        # whose sheet is empty by design, and never a file the index does not
        # know, which may belong to a game's own repository. It will not take a
        # stem the caller merely asks for.
        # ⭐️ THE NAME IS NOT THROWN AWAY: it goes to `retired`, the same as a
        # name whose piece disappears across a re-cut. Somebody who deletes
        # pieces has not asked to forget what they were called.
        if head == "pieces" and len(rest) == 2 and rest[1] == "lost" and method == "POST":
            with pr.lock:
                stems = lost_pieces(pr)
                if not stems:
                    return self.send_json(
                        {"error": "Nothing here has lost its sheet. Pieces made "
                                  "by joining two others, and files the room did "
                                  "not cut, are left alone on purpose."}, 400)
                idx = pr.index()
                man = pr.manifest()
                kept = 0
                for st in stems:
                    was = (man.get("pieces") or {}).pop(st, None)
                    if was and (was.get("name") or was.get("component")):
                        man.setdefault("retired", {})[st] = was
                        kept += 1
                    idx.get("pieces", {}).pop(st, None)
                    for path in (pr.piece_path(st), pr.spare_path(st)):
                        if os.path.exists(path):
                            os.remove(path)
                pr.save_index(idx)
                pr.save_manifest(man)
            return self.send_json({"ok": True, "removed": len(stems), "names_kept": kept})

        if head == "pieces" and len(rest) == 2 and rest[1] == "aside" and method == "POST":
            # ⭐️ Setting several aside at once is what makes the look-alike
            # finder useful: keep one counter, put the other nineteen away in
            # one press. ⚠️ IT DELETES NOTHING. The pieces are moved into the
            # store's `spare` folder, where the hand-over does not look, and
            # everything the manifest knows about them is kept. `aside: false`
            # brings them straight back.
            d = self.body_json()
            stems = [str(x) for x in (d.get("stems") or [])]
            aside = d.get("aside", True) is not False
            with pr.lock:
                moved = pr.set_aside(stems, aside)
            return self.send_json({"ok": True, "moved": moved, "aside": aside})

        # ⭐️ THIRTY-TWO CARDS, ONE COMPONENT, ONE PRESS. The designer, 24 August
        # 2026: "I'd like a bulk apply function - if I can select all 32 cards
        # in a deck, I should be able to apply the correct card deck label to
        # them all in one go." Dragging a deck's name onto thirty-two pieces
        # one at a time is the same work thirty-two times.
        #
        # ⚠️ A NAME SOMEBODY TYPED IS NEVER OVERWRITTEN — only a blank is
        # filled, exactly as one piece at a time does it. A bulk action is
        # where a wrong rule does the most damage before anybody notices.
        if head == "pieces" and len(rest) == 2 and rest[1] == "link" and method == "POST":
            d = self.body_json()
            stems = [str(x) for x in (d.get("stems") or [])]
            wid = str(d.get("wanted") or "").strip()
            # ⭐️ a whole deck's back in one press: the back is another piece,
            # and "" means leave whatever each of them already has alone
            back = str(d.get("back") or "").strip()
            item = None
            if wid:
                item = next((i for i in (pr.wanted().get("items") or [])
                             if i.get("id") == wid), None)
                if item is None:
                    return self.send_json({"error": "no such component"}, 400)
            with pr.lock:
                man = pr.manifest()
                linked, named = 0, 0
                for st in stems:
                    cur = man["pieces"].setdefault(st, {})
                    if d.get("wanted") is not None:
                        if wid:
                            cur["wanted"] = wid
                        else:
                            cur.pop("wanted", None)
                    if back:
                        cur["back"] = back
                    # ⭐️ and failing that, the back the component itself says
                    # it has — see inherit_back()
                    inherit_back(item, cur)
                    linked += 1
                    if item and not (cur.get("name") or "").strip():
                        cur["name"] = item.get("name") or ""
                        if item.get("kind") and not cur.get("kind"):
                            cur["kind"] = item["kind"]
                        named += 1
                    if not cur:
                        man["pieces"].pop(st, None)
                if stems:
                    pr.save_manifest(man)
            return self.send_json({"ok": True, "linked": linked, "named": named,
                                   "back": back,
                                   "component": (item or {}).get("name", "")})

        # ⭐️⭐️ TWO PIECES LAID TOGETHER AND MADE ONE. The designer, 26 August
        # 2026, of a spine scanned across two pages: "I have a component (the
        # spine) which extends over 2 pages. I need a way to stick them
        # together" — and then, having done it once by hand: "ensure it is
        # backed into the platform - I have a new use for something like it
        # immediately... ensuring that corridor pieces interlock neatly."
        #
        # ⭐️ Note the two uses, because they shape the tool: one JOINS and the
        # other only LOOKS. Laying two pieces against each other to see whether
        # their edges meet is the commoner of the two and writes nothing at
        # all, so joining is a button on the end of it rather than its purpose.
        if head == "pieces" and len(rest) == 2 and rest[1] == "join" and method == "POST":
            d = self.body_json()
            a, b = str(d.get("a") or ""), str(d.get("b") or "")
            name = str(d.get("name") or "").strip()
            try:
                dx, dy = int(d.get("dx") or 0), int(d.get("dy") or 0)
            except (TypeError, ValueError):
                return self.send_json({"error": "the offset must be two whole numbers"}, 400)
            if a == b or not a or not b:
                return self.send_json({"error": "two different pieces, please"}, 400)
            here = set(pr.piece_files()) | pr.spare_stems()
            for st in (a, b):
                if st not in here:
                    return self.send_json({"error": "no such piece: " + st}, 400)
            # ⚠️ A NAME IS ASKED FOR, because a joined piece belongs to no
            # sheet and so has no number to be found by. The same rule as the
            # checklist learnt from cut pieces (fault 72): the room makes the
            # thing and the person says what it is.
            if not name:
                return self.send_json({"error": "give the joined piece a name first"}, 400)
            ia = Image.open(pr.piece_file(a)).convert("RGBA")
            ib = Image.open(pr.piece_file(b)).convert("RGBA")
            x0, y0 = min(0, dx), min(0, dy)
            w = max(ia.width, dx + ib.width) - x0
            h = max(ia.height, dy + ib.height) - y0
            if w > 60000 or h > 60000:
                return self.send_json({"error": "that offset makes a picture too big to write"}, 400)
            out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            out.alpha_composite(ia, (-x0, -y0))
            out.alpha_composite(ib, (dx - x0, dy - y0))
            crop = out.getbbox()
            if crop:
                out = out.crop(crop)
            with pr.lock:
                taken = set(pr.piece_files()) | pr.spare_stems()
                base = "joined_" + file_slug(name, "piece", 40).replace("-", "_")
                stem, n = base + "_00", 0
                while stem in taken:
                    n += 1
                    stem = "%s_%02d" % (base, n)
                out.save(pr.piece_path(stem), "PNG", optimize=True)
                dpi = 0
                idx = pr.index()
                for st in (a, b):
                    dpi = dpi or (idx["pieces"].get(st) or {}).get("dpi")
                # ⚠️ `sheet` is left EMPTY on purpose. Naming a real sheet here
                # would put this piece in that sheet's `old` set, and the next
                # cut of it drops every index entry belonging to the sheet —
                # so a re-cut would quietly lose the joined piece's record.
                idx["pieces"][stem] = {"w": out.width, "h": out.height, "sheet": "",
                                       "dpi": dpi or pr.dpi, "cut_at": now_ms(),
                                       "joined_from": [a, b], "offset": [dx, dy]}
                pr.save_index(idx)
                man = pr.manifest()
                cur = man["pieces"].setdefault(stem, {})
                cur["name"] = name
                cur["note"] = ("joined from %s and %s" % (a, b))
                pr.save_manifest(man)
            # ⚠️ NOTHING IS DELETED. The two halves are SET ASIDE, which is
            # what the room does everywhere else (fault 19) and is undone from
            # the Pieces page — or a join made in the wrong place would throw
            # away the only copies of both.
            moved = pr.set_aside([a, b], True) if d.get("aside", True) else 0
            mm = pr.measure_piece(stem, dpi or pr.dpi) or {}
            return self.send_json({"ok": True, "stem": stem, "name": name,
                                   "w": out.width, "h": out.height,
                                   "w_in": mm.get("w_in"), "h_in": mm.get("h_in"),
                                   "aside": moved})

        if head == "pieces" and len(rest) == 2 and rest[1] == "kind" and method == "POST":
            # ⭐️ Accepting the room's guess for a whole run of pieces at once —
            # "call these 42 counters" — in one press and one write.
            # ⚠️ IT WILL NOT OVERWRITE A KIND SOMEBODY HAS ALREADY SET. The
            # room only ever fills a blank; a decision already made is a
            # decision, and this is a bulk action where a mistake would be
            # spread over hundreds of pieces before anybody noticed.
            d = self.body_json()
            stems = [str(x) for x in (d.get("stems") or [])]
            kind = str(d.get("kind") or "").strip()
            if not kind:
                return self.send_json({"error": "no kind given"}, 400)
            with pr.lock:
                man = pr.manifest()
                n = 0
                for st in stems:
                    cur = man["pieces"].setdefault(st, {})
                    if cur.get("kind"):
                        continue
                    cur["kind"] = kind
                    n += 1
                if n:
                    pr.save_manifest(man)
            return self.send_json({"ok": True, "set": n, "kind": kind})

        if head == "manifest":
            if len(rest) == 1 and method == "GET":
                return self.send_json(pr.manifest())

            # ⭐️ EVERYTHING THIS PIECE HAS BEEN CALLED, TAKEN OFF IT. The designer,
            # 24 August 2026: "give me a single button when viewing any single
            # piece to remove all the metadata (name, component, kind etc) —
            # just strip back to all those fields being unfilled." A piece
            # named in the wrong place, or filled in from the wrong row of a
            # contents list, is quicker to start again than to unpick field by
            # field.
            #
            # ⚠️ WHAT IT DOES NOT TOUCH, on purpose: `spare` (this piece is set
            # aside), `alike` (it is one of several designs of a component) and
            # `fine` (its flags have been looked at and waved through).
            # Those are not what the piece IS, they are decisions about its
            # place in the game, made from other screens, and a person clearing
            # a name is not asking to undo them. The picture and the outline
            # are not touched by anything here.
            if len(rest) == 2 and method == "DELETE":
                with pr.lock:
                    man = pr.manifest()
                    cur = man["pieces"].get(rest[1])
                    if cur is None:
                        return self.send_json({"error": "no such piece"}, 404)
                    kept = {k: v for k, v in cur.items()
                            if k in ("spare", "alike", "fine")}
                    had = sorted(k for k in cur if k not in kept)
                    if kept:
                        man["pieces"][rest[1]] = kept
                    else:
                        man["pieces"].pop(rest[1], None)
                    pr.save_manifest(man)
                return self.send_json({"ok": True, "cleared": had,
                                       "piece": kept})
            if len(rest) == 2 and method == "PUT":
                d = self.body_json()
                with pr.lock:
                    man = pr.manifest()
                    cur = man["pieces"].get(rest[1], {})
                    # ⭐️ `alike` marks a piece as one of several DESIGNS of the
                    # same component — the two player marker cards, the twelve
                    # movement templates with a different player's badge in the
                    # corner. Every piece in such a group carries the same
                    # token. It lives on the piece rather than in a list of its
                    # own so that it follows the piece across a re-cut, like
                    # the name does.
                    # ⭐️ `back` — the piece that is the BACK of this one.
                    # The designer, 24 August 2026: "when I'm in the process of
                    # cutting a deck of cards, how do I set the correct back to
                    # them? Note that it's not always the same back within the
                    # same set." A back is not a property of a card, it is
                    # ANOTHER PIECE: cut it once and every card in the deck
                    # points at it, so a set with three different backs is
                    # three pieces and no special case.
                    # ⭐️ `fine` — the room's own worries about this piece
                    # that the person has looked at and waved through. The designer,
                    # 24 August 2026: "some of the pieces I've cut are flagged
                    # as RUNS OFF THE SHEET. That's a reasonable thing to flag,
                    # but I don't see a way to remove that flag (because it
                    # doesn't matter)." A flag that cannot be answered is not a
                    # question, it is a stain: it sits on the piece for ever
                    # and the "worth a look" list never empties, so the list
                    # stops being read at all. It holds the flag keys, space
                    # separated, and lives on the piece so it follows it across
                    # a re-cut exactly as the name does.
                    for k in ("id", "name", "type", "kind", "use", "note", "hold",
                              "wanted", "alike", "back", "fine"):
                        if k in d:
                            v = str(d[k]).strip()
                            if v:
                                cur[k] = v
                            else:
                                cur.pop(k, None)
                    # ⭐️ `copies` — how many of this piece the game needs.
                    # The designer, 24 August 2026: "in the one of the card decks, one of
                    # the cards (one of them) needs to appear x20, whereas
                    # the other 12 are unique." The room's rule is unchanged —
                    # ONE of each design is cut, because a picture repeats for
                    # nothing — but the game reading the manifest has to be
                    # told that this one design is wanted twenty times, and
                    # until now there was nowhere to write that down.
                    # ⭐️ LINKING A CARD TO A DECK GIVES IT THE DECK'S BACK.
                    # The whole point of saying it once — see inherit_back(),
                    # which is the one copy of this rule.
                    if str(d.get("wanted") or "").strip():
                        item = next((i for i in (pr.wanted().get("items") or [])
                                     if i.get("id") == str(d["wanted"]).strip()), None)
                        inherit_back(item, cur)
                    if "copies" in d:
                        try:
                            c = int(d["copies"])
                        except (TypeError, ValueError):
                            c = 0
                        if c > 1:
                            cur["copies"] = min(c, 9999)
                        else:
                            cur.pop("copies", None)
                    # ⭐️⭐️ ANY ANGLE, NOT JUST A QUARTER TURN. The designer,
                    # 3 September 2026, on cards cut from photographs: "the
                    # ability to drag to rotate a cut piece - just flipping
                    # through 90 degrees is too crude when I may need to
                    # rotate a piece by just a few degrees to level it."
                    # ⚠️ A tenth of a degree is the grain. It is fine enough
                    # to level a card by eye — a tenth of a degree across a
                    # 3.5in card is six thousandths of an inch, under the
                    # thickness of the printed line — and coarse enough that
                    # the number in the box is one somebody can read and type
                    # back. `turned()` has always rotated by any angle; only
                    # this door insisted on whole quarters.
                    if "rotate" in d:
                        try:
                            r = round(float(d["rotate"]) % 360.0, 1)
                        except (TypeError, ValueError):
                            r = 0.0
                        if r:
                            # a whole number stays a whole number, so a
                            # quarter turn does not become "90.0" in the file
                            cur["rotate"] = int(r) if r == int(r) else r
                        else:
                            cur.pop("rotate", None)
                    if cur:
                        man["pieces"][rest[1]] = cur
                    else:
                        man["pieces"].pop(rest[1], None)
                    pr.save_manifest(man)
                return self.send_json({"ok": True, "piece": cur})
            if len(rest) == 2 and method == "DELETE":
                # ⭐️ This was the one-piece version of binning, and it deleted
                # too. Nothing in the room throws a cut piece away now: it is
                # set aside, and the same call puts it back.
                with pr.lock:
                    moved = pr.set_aside([rest[1]], True)
                return self.send_json({"ok": True, "moved": moved, "aside": True})

        # ⭐️⭐️ THE CHECK AGAINST THE CONTENTS LIST, at the end of the job.
        # Two ways to ask for the same findings: as data, for the page in the
        # room, and as the printable report that also goes into the export.
        if head == "review":
            if len(rest) == 1 and method == "GET":
                return self.send_json(pr.cut_review())
            if len(rest) == 2 and rest[1] == "print" and method == "GET":
                # ⭐️ the served copy knows the way back to the project page, so
                # every piece it names is a link; the exported copy does not.
                return self.send(200, review_page(
                    pr, pr.meta.get("game") or pr.meta.get("name") or "this game",
                    home="/p/%s/" % urllib.parse.quote(pr.id)))

        if head == "wanted":
            if len(rest) == 1 and method == "GET":
                return self.send_json(pr.wanted_status())
            if len(rest) == 1 and method == "PUT":      # the whole list
                d = self.body_json()
                with pr.lock:
                    w = pr.wanted()
                    for k in ("items", "groups", "note", "kinds"):
                        if k in d:
                            w[k] = d[k]
                    w["items"] = [{a: b for a, b in (it or {}).items()
                                   if a not in WORKED_OUT}
                                  for it in (w.get("items") or [])]
                    pr.save_wanted(w)
                return self.send_json(pr.wanted_status())
            if len(rest) == 2 and rest[1] == "import" and method == "POST":
                d = self.body_json()
                added = import_wanted_text(pr, str(d.get("text") or ""),
                                           str(d.get("group") or "core"),
                                           bool(d.get("each")),
                                           str(d.get("group_name") or ""),
                                           str(d.get("group_book") or ""))
                return self.send_json(dict(added=added, **pr.wanted_status()))

        # ⭐️⭐️ WHICH PIECE IS THE BACK OF THIS COMPONENT. The designer, 26
        # August 2026: "ALSO match should include an item for the relevant back
        # of each deck." A back is another PIECE (fault 46) and a deck of
        # thirty-two cards all point at the same one — so it is said ONCE,
        # about the deck, rather than thirty-two times about the cards.
        if head == "wanted" and len(rest) == 2 and rest[1] == "back" and method == "POST":
            d = self.body_json()
            wid = str(d.get("id") or "").strip()
            stem = str(d.get("stem") or "").strip()
            gave = 0
            with pr.lock:
                w = pr.wanted()
                item = next((i for i in (w.get("items") or [])
                             if i.get("id") == wid), None)
                if item is None:
                    return self.send_json({"error": "no such component"}, 400)
                # ⚠️ a stem nothing answers to would be a back pointing at a
                # piece that is not there — worse than no back at all
                if stem and stem not in (set(pr.piece_files()) | pr.spare_stems()):
                    return self.send_json({"error": "no such piece"}, 400)
                if stem:
                    item["back"] = stem
                else:
                    item.pop("back", None)
                pr.save_wanted(w)
                man = pr.manifest()
                if stem:
                    # ⭐️ THE DRAG IS THE DECISION, so the piece really is
                    # marked a card back — it is what makes the "only pieces
                    # marked as a card back" narrowing (fault 51) able to find
                    # it afterwards. Half of this working would read as broken.
                    man["pieces"].setdefault(stem, {})["kind"] = "card back"
                    for st, v in man["pieces"].items():
                        if st != stem and v.get("wanted") == wid \
                           and inherit_back(item, v):
                            gave += 1
                pr.save_manifest(man)
            return self.send_json(dict(ok=True, back=stem, gave=gave,
                                       **pr.wanted_status()))

        # ⭐️⭐️ the checklist learnt from what has been cut — see
        # learn_from_pieces(). The GROUPING is done in the page, off the very
        # same look-alike rule the review uses (fault 24: there is one of it),
        # so what arrives here is stems, a name and a decision.
        if head == "wanted" and len(rest) == 2 and rest[1] == "learn" and method == "POST":
            d = self.body_json()
            groups = d.get("groups") or []
            if not isinstance(groups, list) or not groups:
                return self.send_json({"error": "nothing to learn from"}, 400)
            if len(groups) > 500:
                return self.send_json({"error": "too many groups at once"}, 400)
            made, linked = learn_from_pieces(pr, groups)
            if not made:
                return self.send_json({"error": "every group needs a name and "
                                                "at least one piece"}, 400)
            return self.send_json(dict(added=made, linked=linked,
                                       **pr.wanted_status()))

        if head == "wanted" and len(rest) == 2 and rest[1] == "split" and method == "POST":
            d = self.body_json()
            got = split_wanted_item(pr, str(d.get("id") or ""), d.get("names") or [])
            if isinstance(got, str):
                return self.send_json({"error": got}, 400)
            made, moved = got
            return self.send_json(dict(made=made, moved=moved, **pr.wanted_status()))

        if head == "wanted" and len(rest) == 2 and rest[1] == "confirm" and method == "POST":
            # Every wanted item with exactly one unlinked piece whose name
            # matches becomes a link — the guess made firm, in one press.
            st = pr.wanted_status()
            with pr.lock:
                man = pr.manifest()
                n = 0
                for it in st["items"]:
                    # ⭐️ A DECK IS THE ONE CASE WHERE MANY MATCHES ARE RIGHT.
                    # For an ordinary component, one piece whose name matches
                    # and no other is the only safe answer — two matches mean
                    # the room does not know which. But a deck of twenty-four
                    # damage cards WANTS twenty-four pieces, all answering to
                    # the same component, so every one that matches belongs to
                    # it and tying them up by hand is twenty-four drags.
                    deck = it.get("need", 1) > 1
                    if it["state"] not in ("probably", "part"):
                        continue
                    take = it.get("guesses") or []
                    if not deck and len(take) != 1:
                        continue
                    for stem in take:
                        cur = man["pieces"].setdefault(stem, {})
                        if cur.get("wanted"):
                            continue
                        cur["wanted"] = it["id"]
                        n += 1
                if n:
                    pr.save_manifest(man)
            return self.send_json(dict(confirmed=n, **pr.wanted_status()))

        if head == "hook" and len(rest) == 2 and method == "POST":
            for h in pr.meta.get("hooks") or []:
                if h.get("id") == rest[1]:
                    cmd = h.get("cmd") or []
                    cwd = h.get("cwd") or pr.path
                    try:
                        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                                           timeout=int(h.get("timeout") or 900))
                        return self.send_json({"ok": r.returncode == 0, "rc": r.returncode,
                                               "out": (r.stdout + "\n" + r.stderr)[-8000:]})
                    except (OSError, subprocess.TimeoutExpired) as exc:
                        return self.send_json({"ok": False, "out": str(exc)})
            return self.send_json({"error": "no such hook"}, 404)

        # ⭐️ WHAT THE ROOM HAS PUT ASIDE, AND PUTTING ONE BACK. A safety net
        # nobody can reach is not a safety net — see `keep_a_copy`.
        if head == "history" and len(rest) == 1 and method == "GET":
            out = {}
            folder = pr.history_dir()
            for key in ("outlines", "manifest", "wanted"):
                mine = []
                for f in sorted(os.listdir(folder) if os.path.isdir(folder) else []):
                    if not (f.startswith(key + "-") and f.endswith(".json")):
                        continue
                    path = os.path.join(folder, f)
                    try:
                        blob = read_json(path, {})
                        if key == "wanted":
                            says = "%d components" % len(blob.get("items") or [])
                        elif key == "manifest":
                            says = "%d pieces named" % len([
                                1 for v in (blob.get("pieces") or {}).values()
                                if (v.get("name") or "").strip()])
                        else:
                            says = "%d outlines" % sum(
                                len(v.get("pieces") or [])
                                for v in (blob.get("sheets") or {}).values())
                    except Exception:                      # noqa: BLE001
                        says = "unreadable"
                    mine.append({"file": f, "when": os.path.getmtime(path),
                                 "size": os.path.getsize(path), "says": says})
                mine.reverse()                             # newest first
                out[key] = mine
            return self.send_json({"kept": out, "where": pr.history_dir(),
                                   "how_many": Project.KEEP_HISTORY})

        if head == "history" and len(rest) == 2 and rest[1] == "restore" and method == "POST":
            d = self.body_json()
            key = str(d.get("key") or "")
            name = os.path.basename(str(d.get("file") or ""))
            if key not in ("outlines", "manifest", "wanted"):
                return self.send_json({"error": "there is no such store"}, 400)
            if not (name.startswith(key + "-") and name.endswith(".json")):
                return self.send_json({"error": "that is not a copy of %s" % key}, 400)
            path = os.path.join(pr.history_dir(), name)
            if not os.path.exists(path):
                return self.send_json({"error": "that copy is not there any more"}, 404)
            blob = read_json(path, None)
            if blob is None:
                return self.send_json({"error": "that copy cannot be read"}, 400)
            with pr.lock:
                # ⭐️ the copy being replaced is itself kept, so putting one
                # back is not a one-way door either
                {"outlines": pr.save_outlines, "manifest": pr.save_manifest,
                 "wanted": pr.save_wanted}[key](blob)
            return self.send_json({"ok": True, "restored": name, "key": key})

        if head == "reveal" and method == "POST":
            d = self.body_json()
            what = str(d.get("what") or "project")
            # ⭐️ a set is written into a folder of its own, so the button
            # that opens it has to be told which one (fault 24: one rule for
            # the folder's name, in export_project, and this asks for it)
            out = export_dir(pr, str(d.get("set") or "").strip() or None)
            path = {"project": pr.path, "pieces": pr.p("pieces"),
                    "sheets": pr.p("sheets"),
                    "export": out}.get(what, pr.path)
            os.makedirs(path, exist_ok=True)
            return self.send_json({"ok": open_folder(path), "path": path})

        return self.send_json({"error": "no such call"}, 404)

    @staticmethod
    def _outline_no(pr, stem, meta):
        """Which outline on its sheet a piece was cut to, counting from one,
        as the Cutting Table numbers them — so a bad cut can be sent back
        to exactly the line that made it."""
        rgb = meta.get("ink_rgb")
        sid = meta.get("sheet")
        if not rgb or not sid:
            return 0
        want = "#%02X%02X%02X" % tuple(rgb)
        book = pr.outlines().get("sheets", {})
        for n, pc in enumerate((book.get(sid) or {}).get("pieces") or [], 1):
            if INKS[int(pc.get("ink", 0)) % len(INKS)].upper() == want:
                return n
        return 0


# ⚠️⚠️ THE ONE PLACE IN THE ROOM THAT REALLY DELETES, and it is called from
# two doors: one sheet's × and a whole box at once. Everything else in here
# sets things aside rather than destroying them (fault 19) — but a sheet that
# should never have been imported has nothing worth keeping, and its OUTLINES
# are the work, so this is the one action that can lose real work.
#
# ⭐️ What makes it safe enough to offer: `outlines.json` keeps its last sixty
# copies automatically (fault 49), so the WORK survives a box removed by
# mistake even though the scans have to be imported again — and the page says
# exactly that in the question it asks, rather than the comfortable version.
# ⚠️ Do not let that sentence drift into "Settings will put it back": the
# sheet records and the scan files go, and a promise the room cannot keep is
# worse than no promise.
#
# ⚠️ The cut pieces are NOT touched unless asked. A piece is a finished thing
# in its own right; the sheet it came off is only where it came from, and
# nothing else in the room throws a piece away.
# ⚠️ The caller holds `pr.lock`.
def remove_sheets(pr, ids, with_pieces=False):
    ids = [sid for sid in ids if pr.sheet(sid) is not None]
    if not ids:
        return {"sheets": 0, "outlines": 0, "pieces": 0}
    book = pr.outlines()
    drawn = sum(len((book.get("sheets", {}).get(sid) or {}).get("pieces") or [])
                for sid in ids)
    pr.meta["sheets"] = [x for x in pr.sheets if x["id"] not in ids]
    pr.save_meta()
    for sid in ids:
        book.get("sheets", {}).pop(sid, None)
    pr.save_outlines(book)
    for sid in ids:
        for path in (pr.sheet_png(sid),
                     os.path.join(pr.p("cache"), sid + ".jpg"),
                     os.path.join(pr.p("thumbs"), sid + ".jpg"),
                     os.path.join(pr.p("cache"), sid + ".suggest.json"),
                     os.path.join(pr.p("masks"), sid + ".png")):
            if os.path.exists(path):
                os.remove(path)
    took = 0
    if with_pieces:
        idx = pr.index()
        for st in [k for k, v in idx.get("pieces", {}).items() if v.get("sheet") in ids]:
            idx["pieces"].pop(st, None)
            for path in (pr.piece_path(st), pr.spare_path(st)):
                if os.path.exists(path):
                    os.remove(path)
            took += 1
        pr.save_index(idx)
    return {"sheets": len(ids), "outlines": drawn, "pieces": took}


# ⭐️⭐️ THE PIECES WHOSE SHEET HAS GONE — AND, MUCH MORE IMPORTANTLY, THE
# ONES THAT ONLY LOOK LIKE THEM.
#
# The designer, 1 September 2026: "how do I remove all the pieces, 'remove this
# set' doesn't clear the cut pieces, and I can't see any other way to do it."
# Quite right: removing a box asks a second question about its pieces, but the
# single sheet's × never did, and once the sheet is gone its pieces are
# orphans with no route to them at all. Nothing in the room could delete them.
#
# ⚠️⚠️ THREE DIFFERENT THINGS SIT UNDER "Not off any sheet this project knows",
# and only ONE of them may ever be swept:
#   • a piece whose sheet was removed — its `sheet` names an id the game no
#     longer has. That is this list.
#   • a JOINED piece — `sheet` is deliberately EMPTY, because it came off two
#     sheets and naming either would let the next re-cut drop its record
#     (fault 89). Sweeping these would destroy the one copy of somebody's
#     hand-made piece.
#   • a file the index knows nothing about — and `paths.pieces` may point
#     inside a GAME's own repository (fault 39), so these are very likely not
#     the room's to delete at all.
# One rule, in one place, because a second copy of it would eventually sweep
# one of the other two. See fault 95.
def lost_pieces(project):
    """Stems whose recorded sheet is an id this project no longer has."""
    live = {s["id"] for s in project.sheets}
    out = []
    for st, meta in (project.index().get("pieces") or {}).items():
        sid = meta.get("sheet") or ""
        if sid and sid not in live:          # empty sheet = joined, never swept
            out.append(st)
    return sorted(out)


def inherit_back(item, cur):
    """⭐️ A DECK'S BACK BELONGS TO THE DECK, so a card linked to the deck takes
    it. The designer, 26 August 2026: "match should include an item for the
    relevant back of each deck." Say once which piece is the back of these
    thirty-two cards and every one of them points at it — including the ones
    linked afterwards, which is the half that would otherwise silently not
    happen.

    ⚠️ IT FILLS A BLANK ONLY. A card given a back of its own keeps it: a set
    can have more than one back (fault 46), and a rule spread over a whole deck
    is exactly where a confident wrong answer does most damage (fault 43).

    ⚠️ ONE OF IT, because TWO doors link a piece to a component — the drag on
    the Match board (PUT /manifest/<stem>) and the bulk bar (POST
    /pieces/link) — and a guard only one of them remembered would be fault 14
    for the umpteenth time.
    """
    back = str((item or {}).get("back") or "").strip()
    if back and not str(cur.get("back") or "").strip():
        cur["back"] = back
        return True
    return False


def new_wanted(have, name, kind, group, qty, each):
    """One line of a checklist, made the same way wherever it comes from.

    ⚠️ THREE THINGS NOW MAKE COMPONENTS — a pasted contents list, a line split
    into its parts, and a group of cut pieces named in one go — and an id made
    three ways is fault 24 waiting to happen: two of them would agree and the
    third would quietly file its components somewhere nothing else looks.
    `have` is the ids already taken, and is added to."""
    iid = (kind or "other") + "_" + slug(name, 40).replace("-", "_")
    base, n = iid, 1
    while iid in have:
        n += 1
        iid = "%s_%d" % (base, n)
    have.add(iid)
    return {"id": iid, "name": name, "kind": kind or "other", "group": group,
            "qty": str(qty), "each": bool(each),
            "source": "", "where": "",
            "match": "(?i)" + re.escape(str(name).split("(")[0].strip()),
            "notes": ""}


def import_wanted_text(pr, text, group, each=False, group_name=None, group_book=None):
    """Lines like `26 Damage counters`, `Turning template x2`, `Long range ruler`,
    or `9 | Large templates | template` become wanted items.

    ⭐️ THE SET IS MADE HERE IF IT IS NEW. The designer, 25 August 2026: "how do I add
    a separate contents list for core as opposed to [the supplement]?" — by
    pasting one box's list at a time into a set of its own. A set the room has
    never heard of would otherwise arrive as a bare id on every component and
    no name anywhere, which reads as a fault rather than as a new box.
    """
    added = []
    with pr.lock:
        w = pr.wanted()
        groups = w.setdefault("groups", [])
        if group and not any(g.get("id") == group for g in groups):
            new = {"id": group, "name": (group_name or "").strip()[:80] or group}
            # ⭐️ WHICH BOX OF SHEETS THIS SET ANSWERS TO, when somebody has
            # said so outright by picking it. Fault 51 has to infer that from
            # the links already made, which is fine once there are some and
            # useless before — and a person saying it is better evidence than
            # anything the room can work out.
            if (group_book or "").strip():
                new["book"] = str(group_book).strip()[:80]
            groups.append(new)
        have = {it.get("id") for it in w["items"]}
        for raw in text.splitlines():
            line = raw.strip().strip("-•*· ").strip()
            if not line:
                continue
            kind = "other"
            if "|" in line:
                bits = [b.strip() for b in line.split("|")]
                qty = bits[0] if bits and bits[0] else "1"
                name = bits[1] if len(bits) > 1 else line
                if len(bits) > 2 and bits[2]:
                    kind = bits[2]
            else:
                m = re.match(r"^(\d+)\s*[x×]?\s+(.+)$", line)
                m2 = re.match(r"^(.+?)\s*[x×]\s*(\d+)$", line)
                if m:
                    qty, name = m.group(1), m.group(2)
                elif m2:
                    name, qty = m2.group(1), m2.group(2)
                else:
                    qty, name = "1", line
            low = name.lower()
            for k in ("counter", "template", "ruler", "card", "deck", "tile", "board", "token", "chart"):
                if k in low:
                    kind = k
                    break
            # ⭐️ said once for the whole list, because a contents list pasted
            # in is usually all one sort — a page of decks, or a page of
            # counters. Each line can still be changed after.
            item = new_wanted(have, name, kind, group, qty,
                              bool(each) and str(qty).strip() not in ("", "1"))
            w["items"].append(item)
            added.append(item)
        pr.save_wanted(w)
    return added


# ⭐️⭐️ THE CHECKLIST LEARNT FROM WHAT IS CUT — the inverse of Match, and the
# answer for a game whose contents list nobody has typed out, which is most
# games. Naming is the expensive part of this whole business and it is
# expensive because it comes from OUTSIDE the room: "3rd party lists etc, or
# rules manuals which may be tricky to comprehend". The pieces themselves are
# already here, already measured and already grouped by the look-alike hash
# the review uses — so twenty identical damage counters can become one line of
# the checklist in one typing, and a deck of thirty-two can become one line
# with all thirty-two tied to it.
#
# ⚠️⚠️ THE ROOM PROPOSES THE GROUPS; WHAT THEY ARE CALLED IS A JUDGEMENT AND
# STAYS THE PERSON'S. The same rule as the kinds (fault 25), the look-alikes
# (fault 18) and the splitting (fault 34): nothing here writes a name by
# itself, and a group nobody names is not added.
#
# ⚠️ AND `each` IS THEIRS TOO (fault 36). The room can see how many DESIGNS a
# group holds, which is real evidence a printed contents list never has — so
# it offers an answer — but "one is enough, unless every one is different" is
# still a decision about what the game needs, not about what was cut.
def learn_from_pieces(pr, groups):
    """Turn named groups of cut pieces into checklist lines, with the pieces
    tied to them. Returns (the lines made, how many pieces were linked)."""
    made, linked = [], 0
    with pr.lock:
        w = pr.wanted()
        w.setdefault("items", [])
        sets = w.setdefault("groups", [])
        man = pr.manifest()
        book = man.setdefault("pieces", {})
        have = {it.get("id") for it in w["items"]}
        for g in groups:
            name = str(g.get("name") or "").strip()[:120]
            stems = [str(x) for x in (g.get("stems") or [])]
            if not name or not stems:
                continue                    # unnamed is unasked-for
            gid = str(g.get("group") or "").strip()
            if gid and not any(x.get("id") == gid for x in sets):
                made_set = {"id": gid, "name": str(g.get("group_name") or gid)[:80]}
                # ⭐️ which BOX of sheets this set answers to, where the person
                # picked one — fault 64. Without it the room is back to
                # inferring that from the links (fault 51), which is no help
                # at all until there are some.
                if str(g.get("group_book") or "").strip():
                    made_set["book"] = str(g["group_book"]).strip()[:80]
                sets.append(made_set)
            item = new_wanted(have, name, str(g.get("kind") or "").strip(),
                              gid, len(stems), bool(g.get("each")))
            w["items"].append(item)
            made.append(item)
            # ⚠️ A NAME SOMEBODY TYPED IS NEVER OVERWRITTEN, here as anywhere
            # else — only a blank is filled. This is a bulk action, where a
            # wrong rule is spread over hundreds of pieces before anybody looks.
            # ⭐️ And where a group holds several DESIGNS, the pieces are
            # numbered: thirty-two cards all called "Damage card" are exactly
            # what fault 34 is about — whatever reads the manifest afterwards
            # cannot tell one from another. The page says so before the press.
            wide = len(str(len(stems)))
            for n, st in enumerate(stems, 1):
                cur = book.setdefault(st, {})
                cur["wanted"] = item["id"]
                if not (cur.get("name") or "").strip():
                    cur["name"] = ("%s %0*d" % (name, wide, n)) if g.get("number") else name
                if item["kind"] and item["kind"] != "other" and not cur.get("kind"):
                    cur["kind"] = item["kind"]
                linked += 1
        if made:
            pr.save_wanted(w)
            pr.save_manifest(man)
    return made, linked


def split_wanted_item(pr, iid, names):
    """One line of a contents list broken into the components it actually
    stands for. Returns (the new items, how many pieces followed) or a plain
    sentence saying why not.

    ⭐️ The designer, 23 August 2026, on a game's supplements: the contents list
    "only gives generic descriptions of [the] cards belonging to the factions
    the supplements bring to the game" — one line naming a player's ship
    templates where the box actually holds three differently named ships.

    ⚠️ This is the difference between a QUANTITY and a SET OF DESIGNS, and the
    room could not tell them apart. Twenty-six damage counters are one design
    printed twenty-six times — you cut ONE, and the row is right to be one
    row. Three movement templates are three different pieces of card that a
    printed contents list happened to sum up in one line. Only a person knows
    which is which, so the room does not guess: it offers the split and takes
    the names.

    Everything downstream then falls out. Match gives each piece its OWN name
    rather than the same name three times, which is what the game reading the
    manifest needs; and if the pieces were already named by hand, each new
    component's match pattern finds its own piece and *Confirm the likely
    links* ties them up in one press."""
    names = [str(n).strip()[:120] for n in (names or []) if str(n).strip()]
    if len(names) < 2:
        return "give at least two names, one for each component"
    if len(names) > 200:
        return "that is more components than one line of a contents list can stand for"
    with pr.lock:
        w = pr.wanted()
        items = w.get("items") or []
        at = next((i for i, it in enumerate(items) if it.get("id") == iid), -1)
        if at < 0:
            return "that component is not on the list any more"
        parent = items[at]
        have = {it.get("id") for it in items}
        made = []
        for name in names:
            kind = parent.get("kind") or "other"
            base = kind + "_" + slug(name, 40).replace("-", "_")
            new_id, n = base, 1
            while new_id in have:
                n += 1
                new_id = "%s_%d" % (base, n)
            have.add(new_id)
            made.append({"id": new_id, "name": name, "kind": kind,
                         "group": parent.get("group", ""), "qty": "1",
                         "source": parent.get("source", ""),
                         "where": parent.get("where", ""),
                         # ⭐️ where it came from, so the generic line it was
                         # broken out of is not lost
                         "from": parent.get("name", ""),
                         "match": "(?i)" + re.escape(name.split("(")[0].strip()),
                         "notes": parent.get("notes", "")})
        items[at:at + 1] = made
        w["items"] = items
        pr.save_wanted(w)

        # ⚠️ A PIECE ALREADY TIED TO THE OLD LINE WOULD BE LEFT POINTING AT
        # NOTHING. It follows to the first of the new components — which may
        # be the wrong one, so the person is told how many moved and where.
        man = pr.manifest()
        moved = 0
        for stem, v in (man.get("pieces") or {}).items():
            if v.get("wanted") != iid:
                continue
            v["wanted"] = made[0]["id"]
            # only a name the room put there itself is overwritten; one
            # somebody typed is theirs
            if (v.get("name") or "") == (parent.get("name") or ""):
                v["name"] = made[0]["name"]
            moved += 1
        if moved:
            pr.save_manifest(man)
    return made, moved


# ------------------------------------------------------- opening the room

# What the "the room is closed" page tells the person to do next. main() puts
# the true answer here once it knows whether there is a launcher to name.
HOW_TO_OPEN = ["Open it again by running cutting_room.py."]

LAUNCHER_NAME = "Cutting Room.command"

# ⭐️ THE ONE WITHOUT A TERMINAL WINDOW. The designer, having been given a
# press to quit the room and a press to start it again: "a simpler way to open
# and quit. I don't like terminal at the best of times." Opening was the last
# of the three that still showed one. A .app bundle is a FOLDER — an
# Info.plist and a shell script — so it can be written by the same code that
# already works out where this copy was cloned to, and it opens with no window
# at all.
APP_NAME = "Cutting Room.app"
APP_EXEC = "cutting-room"                       # Contents/MacOS/<this>
APP_ICON = "cutting-room.icns"
# ⚠️ Written into the Info.plist and read back before anything is replaced, so
# the install can tell ITS OWN bundle from something else that happens to be
# called the same thing. The bundle is rebuilt whole (there is nothing in it
# anybody would edit), and replacing a stranger's app whole would be the worst
# thing in this file.
APP_ID = "org.cuttingroom.launcher"
# ⚠️ Somewhere to put the room's words, because a window that does not exist
# cannot show them. The Mac's own place for it, so Console can read it.
APP_LOG = "~/Library/Logs/Cutting Room.log"

# ⚠️ The launcher is GENERATED, never committed: it has to carry the path this
# copy was cloned to, and that path is different for everybody. It is also the
# only file in the whole tool that knows where anything is.
LAUNCHER = """#!/bin/sh
# The Cutting Room. Made by "python3 cutting_room.py --install-launcher";
# remake it if you move the folder it points at.
#
# Close the room from the room itself — there is a link on its front page —
# and this window will say so and can then be closed.
cd %(here)s || exit 1
echo "Opening the Cutting Room..."
# ⚠️ The browser is opened HERE rather than by the room's own --open, so that
# both launchers obey the one --browser setting instead of two.
( sleep 2; %(browser)s "http://127.0.0.1:%(port)d/" >/dev/null 2>&1 ) &
%(python)s cutting_room.py --port %(port)d%(home)s
echo ""
echo "The Cutting Room is closed. You can close this window."
"""

# The same job with no window on it. Three things make it different from the
# .command above, and each of them is a fault waiting if it is left out:
#
# ⚠️ THE ROOM IS LET GO OF, not waited for. A .app that stays running is an
#    app the Finder thinks is already open, so the SECOND double-click — the
#    one somebody makes when they have closed the browser tab and want it back
#    — would quietly do nothing at all. So this script starts the room, waits
#    only until it is answering, opens the browser and gets out of the way.
#    Every later double-click finds the room already up and just opens a tab.
# ⚠️ A FAILURE MUST BE SEEN. With no window there is nowhere for a missing
#    numpy or a moved folder to appear, and silence reads as a broken button
#    (fault 58). If the room does not come up, this says so in a dialog with
#    the room's own last words in it.
# ⚠️ AND THE ROOM'S WORDS ARE KEPT. Everything it prints goes to the log, and
#    the log is rolled over before it can eat a disk.
APP_SCRIPT = """#!/bin/sh
# The Cutting Room. Made by "python3 cutting_room.py --install-launcher";
# remake it if you move the folder it points at.
#
# Close the room from the link on its own front page. There is no window here
# to close: this script has done its work by the time the browser opens.
here=%(here)s
port=%(port)d
url="http://127.0.0.1:%(port)d/"
log=%(log)s

mkdir -p "$(dirname "$log")"
# a day of cutting is a lot of lines; keep one old log and start a fresh one
if [ -f "$log" ] && [ "$(wc -c < "$log")" -gt 2000000 ]; then
  mv -f "$log" "$log.1"
fi
touch "$log"

answering() {
  /usr/bin/curl -fsS -o /dev/null --max-time 2 "$url" 2>/dev/null
}

if ! answering; then
  echo "" >> "$log"
  echo "--- $(date): opening the Cutting Room" >> "$log"
  # let go of it: the room outlives this script, which is the whole point
  ( cd "$here" && exec %(arch)s%(python)s cutting_room.py --port "$port"%(home)s ) >> "$log" 2>&1 &
  room=$!
  waited=0
  while [ "$waited" -lt 60 ]; do
    answering && break
    kill -0 "$room" 2>/dev/null || break
    sleep 0.5
    waited=$((waited + 1))
  done
fi

if answering; then
  # ⚠️ NOT a bare `open`: that hands the tab to whichever browser profile the
  # Mac happens to think is current, and somebody with a work profile and a
  # personal one does not want their games landing in the work one. Whatever
  # --browser was told at install time is what opens it.
  %(browser)s "$url" >/dev/null 2>&1
  exit 0
fi

# ⚠️ fault 58: half working reads as broken, and nothing at all reads as
# broken hardest. Say what happened, in the room's own words.
/usr/bin/osascript <<APPLESCRIPT
set itsWords to do shell script "tail -n 12 " & quoted form of "$log"
display dialog "The Cutting Room could not open." & return & return & itsWords & return & return & "The whole of what it said is in:" & return & "$log" with title "The Cutting Room" buttons {"OK"} default button 1 with icon caution
APPLESCRIPT
exit 1
"""

# ⚠️⚠️ AN APP MAY NOT READ YOUR OWN FOLDERS UNTIL YOU SAY SO, AND A ROOM
# STARTED FROM A TERMINAL NEVER HAD TO ASK. macOS keeps Documents, Desktop and
# Downloads behind a permission; a room run from a terminal quietly borrows the
# Terminal's, which is why this never came up until the launcher became an app
# of its own. Without it the room started perfectly and then answered
# "Operation not permitted" for the folder its projects live in — fault 58's
# shape, working right up to the moment it matters.
# ⚠️ These strings are not decoration: they are the SENTENCE in the box macOS
# puts up, and an app that asks without one can be refused before anybody is
# asked anything. Say what the room wants and why, in the room's own voice.
WHY_IT_ASKS = ("The Cutting Room keeps your games, your scans and the pieces "
               "you cut in this folder, so it needs to read and write there.")

# ⚠️ LSUIElement: no Dock icon, and that is deliberate. A Dock icon carries a
# Quit that kills the room without asking, and the room asks before it closes
# because a table may be holding an edit not yet written down (fault 21). The
# only doors out stay the ones that ask.
INFO_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>Cutting Room</string>
  <key>CFBundleDisplayName</key><string>Cutting Room</string>
  <key>CFBundleIdentifier</key><string>%(id)s</string>
  <key>CFBundleExecutable</key><string>%(exec)s</string>
  <key>CFBundleIconFile</key><string>%(icon)s</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSUIElement</key><true/>
  <key>NSDocumentsFolderUsageDescription</key><string>%(why)s</string>
  <key>NSDesktopFolderUsageDescription</key><string>%(why)s</string>
  <key>NSDownloadsFolderUsageDescription</key><string>%(why)s</string>
  <key>NSRemovableVolumesUsageDescription</key><string>%(why)s</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>LSArchitecturePriority</key><array><string>%(arch)s</string></array>
</dict>
</plist>
"""


def room_icon(px=1024):
    """The launcher's picture: a piece cut out of a sheet.

    ⭐️ Drawn rather than committed. A binary in the repository is a thing
    nobody can read the change to, and Pillow is already here — so the icon is
    made at install time along with the rest of the bundle, in the room's own
    colours, and there is nothing to keep in step.

    It is drawn big and shrunk, so the 32-pixel one is a photograph of the
    large one rather than a separate small drawing that would drift from it.
    """
    big = 1024
    im = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    panel, edge = (20, 27, 35, 255), (38, 49, 61, 255)
    paper, brass = (220, 227, 235, 255), (201, 162, 39, 255)
    d.rounded_rectangle([76, 76, 948, 948], radius=210, fill=panel, outline=edge, width=8)
    d.rounded_rectangle([200, 260, 824, 764], radius=18, fill=paper)
    # the pieces: holes in the sheet, so the ground shows through them
    d.rounded_rectangle([446, 336, 716, 688], radius=44, fill=panel, outline=brass, width=14)
    d.ellipse([256, 396, 406, 546], fill=panel, outline=brass, width=14)
    if px != big:
        im = im.resize((px, px), Image.LANCZOS)
    return im


def icns_bytes():
    """Pack the icon into an .icns, by hand.

    ⚠️ `iconutil` would do this, and it is not always on the machine — it is
    one of the names that belongs to the developer tools, so on a Mac without
    them it is a stub that asks you to install Xcode. The room must not need
    anything installed, so the container is written here: it is a header and
    a length in front of each picture, and macOS takes a PNG for every one of
    these types.
    """
    order = [(b"ic11", 32), (b"ic12", 64), (b"ic07", 128), (b"ic13", 256),
             (b"ic08", 256), (b"ic14", 512), (b"ic09", 512), (b"ic10", 1024)]
    big = room_icon(1024)
    parts = []
    for kind, px in order:
        buf = io.BytesIO()
        (big if px == 1024 else big.resize((px, px), Image.LANCZOS)).save(buf, "PNG")
        data = buf.getvalue()
        parts.append(kind + struct.pack(">I", len(data) + 8) + data)
    body = b"".join(parts)
    return b"icns" + struct.pack(">I", len(body) + 8) + body


def launcher_python():
    """Which python the launcher should name.

    ⚠️ sys.executable is a real path, and on a Mac that is often deep inside
    the command line tools — a path that moves when Xcode is updated, taking
    the launcher with it. /usr/bin/python3 is the STABLE name for the same
    interpreter, so it wins whenever it can do the job. Whether it can is
    asked, not assumed.
    """
    stable = "/usr/bin/python3"
    if os.path.exists(stable) and stable != sys.executable:
        try:
            ok = subprocess.run([stable, "-c", "import numpy, PIL"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=30).returncode == 0
        except Exception:                      # noqa: BLE001
            ok = False
        if ok:
            return stable
    return sys.executable or "python3"


def native_arch():
    """How to run python as this machine's own architecture, if it must be said.

    ⚠️⚠️ THE FINDER DOES NOT LAUNCH AN APP THE WAY A SHELL DOES. Written
    without this, the bundle came up under Rosetta on an Apple silicon Mac —
    LaunchServices chose x86_64 for an unsigned bundle that had not said
    otherwise — and numpy, which is built for one architecture only, refused
    to load: "incompatible architecture (have 'arm64', need 'x86_64')". The
    same script run from a terminal worked perfectly, which is exactly the
    sort of difference that never gets found by reading.

    So the architecture is said twice, and they are not two copies of one
    rule: the Info.plist states a PREFERENCE, and this states a FACT that
    holds however the bundle was started.
    """
    here = platform.machine()
    if sys.platform == "darwin" and os.path.exists("/usr/bin/arch") and here:
        return "/usr/bin/arch -%s " % here
    return ""


DEFAULT_BROWSER = "/usr/bin/open"

# ⚠️⚠️ macOS KEEPS APPS OUT OF THESE, AND WILL NOT EVEN ASK. An app bundle may
# read anything on the disk except Documents, Desktop and Downloads — and for
# a bundle whose executable is a script it does not put up the "would like to
# access" box at all, it simply refuses. So a room whose projects live in one
# of them starts perfectly from the app and then answers "Operation not
# permitted" for its own folder, which is fault 58's shape exactly. Nothing in
# the room can grant itself the permission, so all it can do is SAY SO at the
# moment the launcher is written, while somebody is there to read it.
# ⚠️ It is not a refusal: the launcher is still written. Somebody may well
# have granted the permission by hand, and a tool that will not do as it is
# told because it suspects trouble is worse than one that warns.
KEPT_FROM_APPS = ("Documents", "Desktop", "Downloads")


def home_argument(home):
    """The --home to bake into a launcher, if one was asked for."""
    return (" --home " + shlex.quote(os.path.abspath(os.path.expanduser(home)))) if home else ""


def home_kept_from_apps(home):
    """Is this home somewhere macOS will not let an app read? Say which."""
    path = os.path.abspath(os.path.expanduser(home or DEFAULT_HOME))
    for name in KEPT_FROM_APPS:
        top = os.path.join(os.path.expanduser("~"), name)
        if path == top or path.startswith(top + os.sep):
            return name
    return None


def install_folder(where):
    folder = os.path.abspath(os.path.expanduser(where or "~/Desktop"))
    if not os.path.isdir(folder):
        sys.exit("no folder at %s" % folder)
    return folder


def ours(app):
    """Is this bundle one the room wrote? Read it, do not assume."""
    try:
        with open(os.path.join(app, "Contents", "Info.plist")) as fh:
            return APP_ID in fh.read()
    except OSError:
        return False


def install_app(where, port, home=None, browser=None):
    """Write the double-clickable app that opens the room with no window."""
    folder = install_folder(where)
    path = os.path.join(folder, APP_NAME)
    if os.path.exists(path) and not ours(path):
        sys.exit("There is already something called %s in %s and it is not "
                 "one of ours.\nNothing has been touched. Move it aside, or "
                 "name another folder." % (APP_NAME, folder))
    # ⚠️ Built beside the real name and moved into place, so a bundle that is
    # half written is never a bundle anybody can press. The same reasoning as
    # the export folder: replaced WHOLE or not at all.
    making = path + ".being-made"
    shutil.rmtree(making, ignore_errors=True)
    macos = os.path.join(making, "Contents", "MacOS")
    resources = os.path.join(making, "Contents", "Resources")
    os.makedirs(macos)
    os.makedirs(resources)
    script = os.path.join(macos, APP_EXEC)
    with open(script, "w") as fh:
        fh.write(APP_SCRIPT % {"here": shlex.quote(HERE),
                               "python": shlex.quote(launcher_python()),
                               "arch": native_arch(),
                               "port": port,
                               "home": home_argument(home),
                               "browser": browser or DEFAULT_BROWSER,
                               "log": shlex.quote(os.path.expanduser(APP_LOG))})
    os.chmod(script, 0o755)
    with open(os.path.join(making, "Contents", "Info.plist"), "w") as fh:
        fh.write(INFO_PLIST % {"id": APP_ID, "exec": APP_EXEC, "icon": APP_ICON,
                               "arch": platform.machine(), "why": WHY_IT_ASKS})
    with open(os.path.join(resources, APP_ICON), "wb") as fh:
        fh.write(icns_bytes())
    shutil.rmtree(path, ignore_errors=True)
    os.rename(making, path)
    sign(path)
    return path, None


def sign(app):
    """Give the bundle an identity of its own, if this Mac can.

    ⚠️ macOS remembers "you said this app may read your Documents" against the
    app's SIGNATURE. An unsigned bundle is remembered by a weaker mark that
    changes whenever the bundle is rebuilt — so the permission would be
    forgotten every time the launcher was made again, and the room would go
    back to answering "Operation not permitted" with nothing to say why.
    An ad-hoc signature costs nothing and is stable for a given bundle.

    ⚠️ It is an IMPROVEMENT, never a requirement: `codesign` belongs to the
    developer tools and is not on every Mac, and the room must not need
    anything installed. If it cannot be done, the app still works — macOS just
    asks again after a rebuild.
    """
    if sys.platform != "darwin" or not os.path.exists("/usr/bin/codesign"):
        return False
    try:
        return subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", app],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=60).returncode == 0
    except Exception:                          # noqa: BLE001
        return False


def install_command(where, port, home=None, browser=None):
    """Write the plain shell launcher — the one that shows a window."""
    folder = install_folder(where)
    path = os.path.join(folder, LAUNCHER_NAME)
    body = LAUNCHER % {"here": shlex.quote(HERE),
                       "python": shlex.quote(launcher_python()),
                       "home": home_argument(home),
                       "browser": browser or DEFAULT_BROWSER,
                       "port": port}
    kept = None
    if os.path.exists(path) and open(path).read() != body:
        # Never overwrite somebody's own launcher without leaving it behind.
        kept = path + ".was"
        shutil.copy2(path, kept)
    with open(path, "w") as fh:
        fh.write(body)
    os.chmod(path, 0o755)
    return path, kept


def install_launcher(where, port, terminal_window=False, home=None, browser=None):
    """Write a double-clickable launcher that knows where this copy lives.

    ⚠️ ONE door, because this is the only place in the whole tool that works
    out where this copy was cloned to and which python can run it. A second
    place knowing that is a second place to be wrong when the folder moves.
    """
    if sys.platform == "darwin" and not terminal_window:
        return install_app(where, port, home, browser)
    return install_command(where, port, home, browser)


def launcher_on_the_desktop():
    """The launcher this machine has, if it has one — for the closed page."""
    for folder in ("~/Desktop", "~", "/Applications"):
        for name in (APP_NAME, LAUNCHER_NAME):
            # ⚠️ The app first: where somebody has both, it is the one to press.
            path = os.path.join(os.path.expanduser(folder), name)
            if os.path.exists(path):
                return path
    return None


# -------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--home", default=DEFAULT_HOME, help="where projects live")
    ap.add_argument("--open", action="store_true", help="open the browser once up")
    ap.add_argument("--register", help="register an existing project folder and exit")
    ap.add_argument("--install-launcher", nargs="?", const="~/Desktop", metavar="FOLDER",
                    help="write a double-clickable launcher (default: the Desktop) and exit")
    ap.add_argument("--browser", metavar="COMMAND",
                    help="with --install-launcher: the command that opens the browser, "
                         "the address added on the end. The default hands it to whatever "
                         "the Mac thinks is current, which on a machine with a work "
                         "profile and a personal one may not be the one you want.")
    ap.add_argument("--terminal-window", action="store_true",
                    help="with --install-launcher: write the old shell launcher, "
                         "which opens a Terminal window and shows what the room says. "
                         "Useful when the room will not start.")
    args = ap.parse_args()

    if args.install_launcher:
        # ⚠️ --home is passed on only if it was actually asked for, so a
        # launcher written without one goes on using the room's own default
        # rather than freezing today's answer into a file on the Desktop.
        chosen_home = args.home if args.home != DEFAULT_HOME else None
        path, kept = install_launcher(args.install_launcher, args.port,
                                      args.terminal_window, chosen_home, args.browser)
        print("Launcher written to %s" % path)
        if kept:
            print("The one that was there is kept at %s" % kept)
        print("Double-click it to open the Cutting Room.")
        if path.endswith(".app"):
            print("No Terminal window: it opens the room and then gets out of the way.")
            print("Whatever the room says goes to %s" % os.path.expanduser(APP_LOG))
            # ⚠️ Two launchers side by side is a question nobody should have to
            # answer, so say which is which rather than leaving both unexplained.
            old_one = os.path.join(os.path.dirname(path), LAUNCHER_NAME)
            if os.path.exists(old_one):
                print("The older %s is still beside it and still works; "
                      "you can throw it away." % LAUNCHER_NAME)
            # ⚠️⚠️ The one thing that makes a perfectly built launcher useless.
            kept_out = home_kept_from_apps(chosen_home)
            if kept_out:
                print("")
                print("⚠️  Your projects are in your %s folder, and macOS does not"
                      % kept_out)
                print("    let an app read that — it refuses without even asking.")
                print("    The room will open and then say \"Operation not permitted\".")
                print("    Move the folder somewhere else and write the launcher again")
                print("    with --home, or use --terminal-window instead.")
        print("Close the room from the link on its own front page.")
        return

    reg = Registry(args.home)
    if args.register:
        path = os.path.abspath(os.path.expanduser(args.register))
        if not os.path.exists(os.path.join(path, "project.json")):
            sys.exit("no project.json in %s" % path)
        reg.register(path)
        print("registered", path)
        return

    # the template's anchors are checked at start, not at the first click
    table_template()

    Room.registry = reg
    launcher = launcher_on_the_desktop()
    HOW_TO_OPEN[0] = ("Double-click %s to open it again."
                      % os.path.basename(launcher)) if launcher else \
                     ("Open it again by running cutting_room.py in %s." % HERE)
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Room)
    except OSError:
        # already running — just open it
        print("the Cutting Room is already open on port %d" % args.port)
        if args.open and sys.platform == "darwin":
            subprocess.Popen(["open", "http://127.0.0.1:%d/" % args.port])
        return
    httpd.daemon_threads = True
    Room.httpd = httpd
    url = "http://127.0.0.1:%d/" % args.port
    print("The Cutting Room is open at %s   (projects: %s)" % (url, reg.home))
    print("Close it from the link on its own front page — no need for this window.")
    if not launcher:
        print("(For a double-clickable launcher: python3 cutting_room.py --install-launcher)")
    if args.open and sys.platform == "darwin":
        threading.Timer(0.6, lambda: subprocess.Popen(["open", url])).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    # ⭐️ THE RELAUNCH, and it is the LAST thing the old process does: the
    # socket is closed, so the new room can take the port, and `execv` puts
    # the new one in this same window under this same command. It never
    # returns — anything after it belongs to a room that was only closed.
    if RELAUNCH["asked"]:
        print("The Cutting Room is starting again…")
        sys.stdout.flush()
        # ⚠️ WITHOUT `--open`, however it was started. The launcher on the
        # desktop opens a browser when it runs, which is right the first time
        # and wrong now: the tab that pressed the button is sitting there
        # waiting to reload itself, and a second tab is a small mess somebody
        # then has to tidy up.
        again = [a for a in sys.argv[1:] if a != "--open"]
        # the script by its real path, so a cwd that has moved cannot matter
        os.execv(sys.executable,
                 [sys.executable, os.path.join(HERE, "cutting_room.py")] + again)
    print("The Cutting Room is closed.")


if __name__ == "__main__":
    main()
