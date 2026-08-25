#!/usr/bin/env python3
"""Reading a printed component sheet: labelling, separating, drafting.

The one hard fact about cutting components off a scanned sheet is that
colour alone cannot do it. On a terrain sheet the sea painted *inside* a
piece is the same blue as the flat sheet it is printed on, so a flood of
the background walks in through a lagoon and severs the piece. Keying out
the blue eats the surf. Tracing the printed die-cut line fails because
the hairline vanishes wherever it crosses dark painting.

So the outline is drawn by hand once, in the Cutting Table, and this
module does everything either side of that: the colour flood that drafts
a first attempt to correct, and the labelling that reads a finished mask
layer back as one region per piece.

Needs numpy and Pillow.
"""
import math
from collections import Counter, deque

import numpy as np
from PIL import Image, ImageFilter

Image.MAX_IMAGE_PIXELS = None

DPI = 300
BG_TOLERANCE = 40       # how far a pixel may sit from the flat sheet colour
WHITE = 242             # the paper margin counts as background too
SEAL = 1                # shrink the free space before flooding, so the flood
                        # cannot squeeze through a hairline gap
MIN_PIECE_IN = 0.25     # anything smaller in both directions is scanner dirt
MAX_SHEET_FRACTION = 0.85   # anything bigger than this is the scan's frame
FIELD_FRACTION = 0.015      # a flat expanse this big is the sheet, not a piece

# ⭐️⭐️ WHAT THE AUTOMATIC PASS IS FOR, and the numbers that decide it. The
# designer, 25 August 2026: "I'm also finding the auto-cutting quite strangely
# inaccurate... the dwarf sail sheet I uploaded felt like it should be very
# easy, blocky colourful shapes, but I basically had to redo the entire
# thing... there should be — given these are pieces of board games — a general
# thought that most shapes will be regular (squares, circles, rectangles)."
# Quite so. A traced ring is the right answer for a coastline and the wrong
# answer for a counter: what a counter wants is four corners.
SUGGEST_TOL = 7.0       # sheet px a traced outline may cut a corner by
SUGGEST_INSET = 6       # sheet px an outline starts inside the printed edge
SMOOTH_SPAN = 6         # ring points averaged either side before thinning
RECT_FILL = 0.93        # of its own smallest box, before a blob IS a rectangle
DISC_LOW = 0.88         # how much of its own circle a disc must really fill
DISC_HIGH = 1.12
ROUND_BAND = 0.05       # how far off its radius a point still counts as round
ROUND_SHARE = 0.85      # how much of the ring must be, before a blob IS round
TRIM_PCT = 0.25         # per cent of pixels ignored at each end of a measure
FIELD_STEP = BG_TOLERANCE / 2.0    # how far the ground may change, cell to cell
FIELD_FLAT = BG_TOLERANCE / 2.0    # how mixed a cell may be and still be ground
SNAP_DEG = 2.0          # a scan is never straight; a printed square is

STARTER_GROW = 14       # how far a starter shape is grown past the artwork
STARTER_COLOURS = [(255, 60, 60), (60, 220, 90), (255, 210, 40), (90, 160, 255),
                   (255, 120, 220), (120, 240, 240), (255, 150, 40), (170, 120, 255),
                   (110, 255, 160), (240, 240, 240), (255, 90, 140), (60, 120, 200)]

def shift_or(m):
    """Grow a mask by one pixel in the four directions."""
    out = m.copy()
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def shift_and(m):
    """Shrink a mask by one pixel in the four directions."""
    out = m.copy()
    out[1:, :] &= m[:-1, :]
    out[:-1, :] &= m[1:, :]
    out[:, 1:] &= m[:, :-1]
    out[:, :-1] &= m[:, 1:]
    return out


def flat_colour(rgb):
    """The single colour the sheet is printed on, ignoring paper white."""
    small = rgb[::4, ::4].reshape(-1, 3)
    keep = ~((small[:, 0] > WHITE) & (small[:, 1] > WHITE) & (small[:, 2] > WHITE))
    small = small[keep]
    if not len(small):
        return np.array([255, 255, 255])
    q = (small // 6 * 6)
    counts = Counter(map(tuple, q))
    return np.array(counts.most_common(1)[0][0])


def label(mask):
    """Connected components, four-connected, by run-length union-find.

    Returns (labels, count). `labels` is int32, 0 where the mask is off and
    1..count inside a component. Fast enough on a whole 300dpi sheet."""
    h, w = mask.shape
    parent = [0]

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    rows = []
    pad = np.zeros(w + 2, np.int8)
    prev_s = prev_e = np.empty(0, np.int64)
    prev_l = []
    for y in range(h):
        pad[1:w + 1] = mask[y]
        d = np.diff(pad)
        starts = np.flatnonzero(d == 1)
        ends = np.flatnonzero(d == -1)
        lab = [0] * len(starts)
        j = 0
        for i in range(len(starts)):
            s, e = starts[i], ends[i]
            while j < len(prev_s) and prev_e[j] <= s:
                j += 1
            k = j
            while k < len(prev_s) and prev_s[k] < e:
                if lab[i] == 0:
                    lab[i] = find(prev_l[k])
                else:
                    union(lab[i], prev_l[k])
                k += 1
            if lab[i] == 0:
                parent.append(len(parent))
                lab[i] = len(parent) - 1
        rows.append((starts, ends, lab))
        prev_s, prev_e, prev_l = starts, ends, lab

    remap = np.zeros(len(parent), np.int32)
    nxt = 0
    for i in range(1, len(parent)):
        r = find(i)
        if remap[r] == 0:
            nxt += 1
            remap[r] = nxt
        remap[i] = remap[r]

    out = np.zeros((h, w), np.int32)
    for y, (starts, ends, lab) in enumerate(rows):
        row = out[y]
        for i in range(len(starts)):
            row[starts[i]:ends[i]] = remap[lab[i]]
    return out, nxt


def outside(near, blob):
    """The true outside of every piece: the flat sheet, flooded in from the
    border, with the hand-drawn blobs standing as walls."""
    free = near & ~blob
    for _ in range(SEAL):
        free = shift_and(free)
    lab, n = label(free)
    if not n:
        return np.zeros_like(near)
    edge = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    keep = np.zeros(n + 1, bool)
    keep[np.unique(edge[edge > 0])] = True
    # Some sheets are printed inside a ruled frame, so the flat field never
    # reaches the paper margin and nothing seeds it from the border. The
    # field is in any case far the largest expanse of the one flat colour,
    # so take any large expanse of it as background too. Where shapes have
    # been drawn they are already excluded, so a piece's own lagoon — which
    # is the same blue — cannot be caught by this.
    sizes = np.bincount(lab.reshape(-1), minlength=n + 1)
    keep |= sizes >= near.size * FIELD_FRACTION
    keep[0] = False
    out = keep[lab]
    for _ in range(SEAL):
        out = shift_or(out)
    return out & near & ~blob


def within(mask, k):
    """Everything inside k pixels of the mask."""
    out = mask.copy()
    for _ in range(k):
        out = shift_or(out)
    return out


def label_shapes(ink, colour):
    """One label per drawn shape. Shapes are separated by being apart, or by
    being drawn in different colours — so two that overlap still come out as
    two pieces if they are different colours."""
    if colour is None:
        return label(ink)
    q = (colour.astype(np.int16) // 48)
    key = (q[:, :, 0] * 36 + q[:, :, 1] * 6 + q[:, :, 2]) * ink
    out = np.zeros(ink.shape, np.int32)
    total = 0
    for v in np.unique(key[ink]):
        lab, n = label(ink & (key == v))
        if not n:
            continue
        out[lab > 0] = lab[lab > 0] + total
        total += n
    return out, total


def keep(lab, n, shape):
    """Turn labelled regions into pieces, binning scanner dirt and the scan's
    own frame."""
    h, w = shape
    sizes = np.bincount(lab.reshape(-1), minlength=n + 1)
    limit = h * w * MAX_SHEET_FRACTION
    min_px = int(MIN_PIECE_IN * DPI)
    min_area = (MIN_PIECE_IN * DPI * 0.8) ** 2
    pieces = []
    for i in range(1, n + 1):
        if sizes[i] < min_area or sizes[i] > limit:
            continue
        m = lab == i
        ys, xs = np.nonzero(m)
        box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        if (box[2] - box[0]) < min_px and (box[3] - box[1]) < min_px:
            continue
        if (box[2] - box[0]) > w * 0.95 and (box[3] - box[1]) > h * 0.95:
            continue                 # the scan's own frame, not a component
        pieces.append({"mask": m, "box": box, "px": int(sizes[i])})
    return pieces


def local_field(rgb, bg, cell=32):
    """⭐️⭐️ THE SHEET COLOUR AS IT FALLS ON THIS SHEET, corner by corner.

    A flat sheet colour plus a tolerance is right for a PDF rendered at true
    size and wrong for anything anybody ever scanned or photographed: the
    light falls off across the glass, and one corner of the paper ends up
    forty units from the other. The flood then finds that corner is not
    "background" — so it becomes a piece, and the fringe of it lying against a
    real piece is joined ONTO that piece, which is where the odd bulges and
    the extra nodes came from.

    So the ground is measured in cells across the sheet and grown outwards
    from the paper it certainly is, a cell at a time. What comes back is a
    picture of the ground the pieces lie on, to compare each pixel against
    instead of one number.

    ⚠️ Two things keep the ground from walking onto a piece, and both were
    learnt by watching it do so:
      · **a step, not a distance.** "Anything within twice the tolerance of
        the sheet colour" swallowed a big pale board whole — it sat 85 units
        away with the limit at 80, so half its cells counted as paper, the
        field took the board's own colour, and the board vanished off the
        sheet. Each step out may be half a tolerance, which is far more than
        lighting does in a tenth of an inch and nowhere near a printed edge.
      · **a cell must be of ONE colour.** A cell lying across an edge is half
        ground and half piece, and where an edge runs nearly level with the
        paper — the long side of a rectangle a few degrees off true — there is
        a whole row of such cells, each a little more piece than the last. The
        ground crept up that ramp in steps of eight and ate four fifths of the
        piece. A cell that is not all one colour is not ground and cannot be
        stepped through.

    ⚠️ If there is no ground to measure — no flat expanse anywhere, or nothing
    but ground — this gives up and says so, rather than inventing one."""
    h, w, _ = rgb.shape
    thin_by = 4                       # every fourth pixel is plenty to average
    step = max(1, cell // thin_by)
    small = rgb[::thin_by, ::thin_by].astype(np.float32)
    gy, gx = small.shape[0] // step, small.shape[1] // step
    if gy < 3 or gx < 3:
        return None
    blocks = small[:gy * step, :gx * step].reshape(gy, step, gx, step, 3)
    mean = blocks.mean(axis=(1, 3))
    spread = np.sqrt(blocks.var(axis=(1, 3)).sum(axis=2))
    flat = spread <= FIELD_FLAT
    known = flat & ((((mean - bg.astype(np.float32)) ** 2).sum(axis=2))
                    <= float(BG_TOLERANCE) ** 2)
    if not known.any() or known.all():
        return None
    for _ in range(gx + gy):
        grew = False
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            was = np.roll(np.roll(known, dy, 0), dx, 1)
            val = np.roll(np.roll(mean, dy, 0), dx, 1)
            if dy == 1:
                was[0] = False
            elif dy == -1:
                was[-1] = False
            if dx == 1:
                was[:, 0] = False
            elif dx == -1:
                was[:, -1] = False
            out = (was & ~known & flat &
                   (((mean - val) ** 2).sum(axis=2) <= FIELD_STEP ** 2))
            if out.any():
                known |= out
                grew = True
        if not grew:
            break
    field = mean.copy()
    unknown = ~known
    # under a piece, the paper is whatever the paper either side of it is:
    # fill the holes from their edges inwards, a ring at a time
    for _ in range(gx + gy):
        if not unknown.any():
            break
        tot = np.zeros_like(field)
        cnt = np.zeros((gy, gx), np.float32)
        have = (~unknown).astype(np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh = np.roll(np.roll(field, dy, 0), dx, 1)
            sk = np.roll(np.roll(have, dy, 0), dx, 1)
            if dy == 1:
                sk[0] = 0
            elif dy == -1:
                sk[-1] = 0
            if dx == 1:
                sk[:, 0] = 0
            elif dx == -1:
                sk[:, -1] = 0
            tot += sh * sk[:, :, None]
            cnt += sk
        fillable = unknown & (cnt > 0)
        if not fillable.any():
            break
        field[fillable] = tot[fillable] / cnt[fillable][:, None]
        unknown &= ~fillable
    got = Image.fromarray(np.clip(field, 0, 255).astype(np.uint8))
    return np.asarray(got.resize((w, h), Image.BILINEAR), dtype=np.int16)


def separate(rgb, blob, colour):
    """Every piece on the sheet, as a full-resolution mask.

    With a hand-drawn mask layer, each drawn shape IS a piece: the shape is
    used as a cookie cutter and whatever is printed underneath is kept,
    whatever its colour. That is the only thing that works on the terrain
    sheets, where the sea painted inside a piece is the same blue as the
    sheet it is printed on and no amount of colour logic can tell the two
    apart. Without a mask layer, fall back to flooding the flat sheet colour
    in from the border, which is right for sheets whose pieces sit on a
    clearly different background."""
    h, w, _ = rgb.shape
    bg = flat_colour(rgb)

    if blob is not None:
        lab, n = label_shapes(blob, colour)
        return keep(lab, n, (h, w)), bg, True

    a = rgb.astype(np.int16)
    # ⚠️ against the ground AS IT FALLS ON THIS SHEET, not against one number
    # for the whole of it — see local_field()
    ground = local_field(rgb, bg)
    if ground is None:
        near = ((a - bg) ** 2).sum(axis=2) <= BG_TOLERANCE ** 2
    else:
        # ⚠️⚠️ AND NEVER FURTHER FROM THE SHEET'S OWN COLOUR THAN THIS. The
        # ground drifts with the light, and in the dark corner of a badly lit
        # scan it drifts TOWARDS a pale piece — a light grey board on cream
        # sat 105 units from the sheet colour in the middle and 47 in the
        # corner, so the corner ate it. Following the light is worth having;
        # following it onto the printing is not. Whatever the ground is doing
        # locally, a pixel this far from the colour the sheet is printed in is
        # a piece.
        near = (((a - ground) ** 2).sum(axis=2) <= BG_TOLERANCE ** 2) & \
               (((a - bg) ** 2).sum(axis=2) <= (BG_TOLERANCE * 2) ** 2)
    near |= ((a[:, :, 0] >= WHITE) & (a[:, :, 1] >= WHITE) & (a[:, :, 2] >= WHITE))
    out = outside(near, np.zeros((h, w), bool))
    lab, n = label(~out)
    return keep(lab, n, (h, w)), bg, False


def fill_holes(mask):
    lab, n = label(~mask)
    if not n:
        return mask
    edge = np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])
    hole = np.ones(n + 1, bool)
    hole[np.unique(edge[edge > 0])] = False
    hole[0] = False
    return mask | hole[lab]


# ------------------------------------------------ the automatic first attempt
#
# ⭐️⭐️ THREE THINGS MADE THE AUTOMATIC PASS NOT WORTH USING, and only one of
# them was the tracing. The designer, 25 August 2026: "whilst the general shapes
# were OK-ish, the platform added a load of additional nodes and made some of
# the shapes look pretty odd. Easy fix for me to remove those nodes and
# straighten lines, but it means that the auto cutting pass is essentially
# pointless." All three are answered here and in `outline_of()` below.


def contour(mask):
    """Moore-neighbour tracing: the outline of a filled shape as a ring."""
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return []
    h, w = mask.shape
    y0 = int(ys.min())
    x0 = int(xs[ys == y0].min())
    step = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    def on(x, y):
        return 0 <= x < w and 0 <= y < h and mask[y, x]

    start = (x0, y0)
    ring = [start]
    here = start
    back = 4
    limit = 8 * int(mask.sum()) + 64
    for _ in range(limit):
        found = False
        for k in range(1, 9):
            d = (back + k) % 8
            nxt = (here[0] + step[d][0], here[1] + step[d][1])
            if on(nxt[0], nxt[1]):
                back = (d + 4) % 8
                here = nxt
                found = True
                break
        if not found:
            break
        if here == start:
            break
        ring.append(here)
    return ring


def thin(pts, tol):
    """Douglas-Peucker, iterative."""
    if len(pts) < 3:
        return list(pts)
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    work = [(0, len(pts) - 1)]
    while work:
        lo, hi = work.pop()
        if hi <= lo + 1:
            continue
        ax, ay = pts[lo]
        bx, by = pts[hi]
        vx, vy = bx - ax, by - ay
        L = vx * vx + vy * vy
        worst, at = 0.0, -1
        for i in range(lo + 1, hi):
            px, py = pts[i]
            t = ((px - ax) * vx + (py - ay) * vy) / L if L else 0.0
            t = 0.0 if t < 0 else (1.0 if t > 1 else t)
            d = math.hypot(px - (ax + t * vx), py - (ay + t * vy))
            if d > worst:
                worst, at = d, i
        if worst > tol:
            keep[at] = True
            work.append((lo, at))
            work.append((at, hi))
    return [pts[i] for i in range(len(pts)) if keep[i]]


def smooth_ring(ring, span=SMOOTH_SPAN):
    """⭐️ THE JITTER OF A SCAN IS NOT A CORNER. A printed edge on a real scan
    wanders a pixel or two either way — halftone, JPEG blocks, the softness of
    the press — and Douglas-Peucker cannot tell that wander from a feature, so
    it plants a node at every bump bigger than its tolerance. Averaging the
    ring round each point first is what turns a hundred nodes along one
    straight edge into two. It moves nothing that matters: over a span this
    short a real corner survives, and the outline is inset anyway."""
    n = len(ring)
    if n < 4 * span + 4:
        return list(ring)
    out = []
    for i in range(n):
        sx = sy = 0.0
        for j in range(i - span, i + span + 1):
            p = ring[j % n]
            sx += p[0]
            sy += p[1]
        k = 2 * span + 1
        out.append((sx / k, sy / k))
    return out


def hull_of(pts):
    """The convex hull, Andrew's monotone chain."""
    p = sorted(set((float(x), float(y)) for x, y in pts))
    if len(p) < 3:
        return p

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2 and cross(out[-2], out[-1], q) <= 0:
                out.pop()
            out.append(q)
        return out

    lower = half(p)
    upper = half(reversed(p))
    return lower[:-1] + upper[:-1]


def smallest_box(hull, xs, ys, trim=TRIM_PCT):
    """The smallest rectangle round a blob, at any angle — rotating calipers
    over the hull's own edges, since a smallest box always lies along one.

    ⚠️ MEASURED WITH THE OUTLIERS TRIMMED OFF, and that is the whole reason
    this works on a real scan. A perfect 300-pixel square with SIX stray
    pixels of JPEG ringing at one corner has a smallest box of 314 by 316, so
    it fills only 91% of it and is not recognised as a square at all — which
    is exactly what was happening. The extent is taken at a fraction of a
    percent in from each end instead of at the furthest pixel, so a handful of
    speckles cannot decide the shape of a piece.

    Returns (area, along, across, u0, u1, v0, v1)."""
    best = None
    seen = set()
    n = len(hull)
    for i in range(n):
        ax, ay = hull[i]
        bx, by = hull[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey)
        if L < 1e-9:
            continue
        # a rectangle has four sides at right angles, so directions a quarter
        # turn apart are the same question asked twice
        key = round((math.degrees(math.atan2(ey, ex)) % 90.0) * 2)
        if key in seen:
            continue
        seen.add(key)
        u = (ex / L, ey / L)
        v = (-u[1], u[0])
        us = xs * u[0] + ys * u[1]
        vs = xs * v[0] + ys * v[1]
        u0, u1 = np.percentile(us, (trim, 100.0 - trim))
        v0, v1 = np.percentile(vs, (trim, 100.0 - trim))
        area = float((u1 - u0) * (v1 - v0))
        if area > 0 and (best is None or area < best[0]):
            best = (area, u, v, float(u0), float(u1), float(v0), float(v1))
    return best


def regular_outline(m, ring, inset, inner=None):
    """⭐️⭐️ A COUNTER IS NOT A COASTLINE. The designer's own reasoning, 25 August
    2026, and it is right: "given these are pieces of board games... most
    shapes will be regular (squares, circles, rectangles)". Where a blob
    really is one of those, say so — four corners for a rectangle, a ring for
    a circle — rather than handing back a traced approximation with a node
    everywhere the scan happened to wobble.

    ⚠️ IT ONLY SPEAKS WHEN THE SHAPE SETTLES IT, which is fault 25's rule
    about guessing kinds arriving on geometry. A triangle, an island, a
    hexagon or an L-shaped board fills nothing like its own box, and is traced
    as before. Silence is the right answer more often than any shape is.
    ⚠️ A CIRCLE MUST HAVE A SQUARE BOX. A flat-topped hexagon fills 0.75 of
    its box and a circle 0.785 — four percent apart, which is nothing — so the
    only thing keeping a hexagon from being handed back as an oval is that its
    box is half again as wide as it is tall. Ovals are left to the tracing."""
    px = int(m.sum())
    if px <= 0 or len(ring) < 12:
        return None
    hull = hull_of(ring)
    if len(hull) < 3:
        return None
    ys, xs = np.nonzero(m)
    if len(xs) > 6000:                      # enough to place an edge to a pixel
        step = len(xs) // 6000 + 1
        xs, ys = xs[::step], ys[::step]
    xs = xs.astype(np.float64)
    ys = ys.astype(np.float64)
    box = smallest_box(hull, xs, ys)
    if not box or box[0] <= 0:
        return None
    area, u, v, u0, u1, v0, v1 = box
    wide, tall = u1 - u0, v1 - v0
    fill = px / area

    def at(a, b):
        return [a * u[0] + b * v[0], a * u[1] + b * v[1]]

    if fill >= RECT_FILL and wide > 3 * inset and tall > 3 * inset:
        # ⭐️ A SCAN IS NEVER QUITE STRAIGHT AND A PRINTED SQUARE ALWAYS IS.
        # Within a degree or two of the paper's own axes, take the axes: an
        # outline a hair off true is one the person straightens by hand, which
        # is exactly the work they said they were having to redo.
        ang = math.degrees(math.atan2(u[1], u[0])) % 90.0
        if min(ang, 90.0 - ang) <= SNAP_DEG:
            x0, x1 = np.percentile(xs, (TRIM_PCT, 100.0 - TRIM_PCT))
            y0, y1 = np.percentile(ys, (TRIM_PCT, 100.0 - TRIM_PCT))
            if (x1 - x0) * (y1 - y0) <= area * 1.06:
                x0, x1 = float(x0) + inset, float(x1) - inset
                y0, y1 = float(y0) + inset, float(y1) - inset
                if x1 - x0 > 4 and y1 - y0 > 4:
                    return {"pts": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                            "curve": False}
        a0, a1 = u0 + inset, u1 - inset
        b0, b1 = v0 + inset, v1 - inset
        if a1 - a0 > 4 and b1 - b0 > 4:
            return {"pts": [at(a0, b0), at(a1, b0), at(a1, b1), at(a0, b1)],
                    "curve": False}

    # ⚠️⚠️ A CIRCLE IS ASKED ABOUT ITS RADIUS, AND ASKED OF THE INSET RING.
    # Measured against a box the answer moves with the trimming above — a
    # disc's furthest pixels are its sparsest, so trimming takes more off a
    # circle than off a square and it stops looking like a circle at all.
    # Its own radius does not care: every point of a circle is the same
    # distance from the middle, and nothing else on a sheet is (a hexagon
    # wanders 13%, a square 41%).
    # ⭐️ And it must be the INSET ring, which was the whole difficulty. Where
    # a printed edge runs level with the pixel grid — the very top and bottom
    # of a circle — a soft edge crosses the threshold along a hundred and
    # thirty pixels at once, so a scanned disc has a one-pixel flange at each
    # of its four tangents. Fifteen per cent of the traced ring sat 14 pixels
    # out because of it, and no percentile could tell that from a real bump.
    # A pixel of flange does not survive being taken in six.
    if inner is None or len(inner) < 12:
        return None
    cx = sum(q[0] for q in inner) / float(len(inner))
    cy = sum(q[1] for q in inner) / float(len(inner))
    rs = np.hypot(np.array([q[0] for q in inner], dtype=np.float64) - cx,
                  np.array([q[1] for q in inner], dtype=np.float64) - cy)
    # ⚠️⚠️ AND IT IS ASKED AS "HOW MUCH OF THIS RING IS A CIRCLE?", not as
    # "how far does it wander?". A real scan leaves blotches of not-quite-
    # background stuck to a piece — noise and JPEG mush that the flood cannot
    # tell from printing — and ONE such wing, nine per cent of the ring, puts
    # the furthest point thirteen pixels out and sinks any test made of
    # extremes. Nine tenths of a circle is still a circle; nothing else on a
    # sheet has nine tenths of its edge at one distance from its middle (a
    # hexagon manages seven tenths, a square under a half).
    # ⭐️ and the middle is found from the points that agree, not from all of
    # them: a blotch stuck to one side drags the centroid towards itself, so
    # the circle it is measured against is the wrong circle. Two rounds is
    # enough — the first throws the blotch out, the second measures properly.
    rx = np.array([q[0] for q in inner], dtype=np.float64)
    ry = np.array([q[1] for q in inner], dtype=np.float64)
    mid = float(np.median(rs))
    for _ in range(2):
        fit_in = np.abs(rs - mid) <= mid * ROUND_BAND * 2.0
        if fit_in.sum() < len(rs) * 0.5:
            break
        cx, cy = float(rx[fit_in].mean()), float(ry[fit_in].mean())
        rs = np.hypot(rx - cx, ry - cy)
        mid = float(np.median(rs[fit_in]))
    share = float(np.mean(np.abs(rs - mid) <= mid * ROUND_BAND))
    if mid > 3 * inset and share >= ROUND_SHARE \
            and DISC_LOW <= px / (math.pi * (mid + inset) ** 2) <= DISC_HIGH:
        n = 16
        return {"pts": [[cx + math.cos(k * 2 * math.pi / n) * float(mid),
                         cy + math.sin(k * 2 * math.pi / n) * float(mid)]
                        for k in range(n)], "curve": True}
    return None


def outline_of(m, inset=SUGGEST_INSET, tol=SUGGEST_TOL):
    """One blob of a sheet as an outline with nodes on it.

    ⭐️ AND IT SAYS WHETHER IT IS STRAIGHT OR CURVED. Every suggested outline
    used to be handed to the editor as a CURVE, so a four-node rectangle was
    drawn as a Bézier through its corners: the edges bowed out, the corners
    rounded off, and the piece came out visibly wrong — "made some of the
    shapes look pretty odd". A coastline wants a curve and a counter does not,
    and only the thing that traced it knows which this is."""
    px = int(m.sum())
    ring = contour(m)
    if len(ring) < 12:
        return None
    # ⚠️ start a touch inside the printed edge; it is easier to push a node out
    # than to notice one sitting on the cut line
    e = m
    for _ in range(inset):
        e = shift_and(e)
    if not e.any():
        return None
    inner = contour(e)
    if len(inner) < 12:
        return None
    fit = regular_outline(m, ring, inset, inner)
    if fit:
        return fit
    pts = thin(smooth_ring(inner), tol)
    if len(pts) < 3:
        return None
    return {"pts": [[float(p[0]), float(p[1])] for p in pts], "curve": True}


def starter(rgb, path):
    """A first draft of the mask layer, built from whatever the colour flood
    can manage on its own: every fragment grown a little so nearly-touching
    fragments run together, insides filled, and each shape given its own
    colour. Something to stretch and correct rather than a blank canvas.

    Always built from the colour flood, never from a previous cut, so that
    re-running the tool cannot feed its own output back to itself."""
    h, w, _ = rgb.shape
    union = np.zeros((h, w), bool)
    for p in separate(rgb, None, None)[0]:
        union |= p["mask"]
    grown = union
    for _ in range(STARTER_GROW):
        grown = shift_or(grown)
    grown = fill_holes(grown)
    # round the outline off, the way a die cut is rounded
    soft = np.asarray(Image.fromarray((grown * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(12))) >= 110
    lab, n = label(soft)
    out = np.zeros((h, w, 4), np.uint8)
    for i in range(1, n + 1):
        c = STARTER_COLOURS[(i - 1) % len(STARTER_COLOURS)]
        m = lab == i
        if m.sum() < (MIN_PIECE_IN * DPI * 0.8) ** 2:
            continue
        out[m] = (c[0], c[1], c[2], 255)
    Image.fromarray(out, "RGBA").save(path)
    print("   starter mask layer -> %s  (%d shapes)" % (path, n))
