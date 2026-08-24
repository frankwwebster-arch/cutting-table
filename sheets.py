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
    near = (((a - bg) ** 2).sum(axis=2) <= BG_TOLERANCE ** 2) | \
           ((a[:, :, 0] >= WHITE) & (a[:, :, 1] >= WHITE) & (a[:, :, 2] >= WHITE))
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
