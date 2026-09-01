#!/bin/sh
# Photograph the room, for the guide.
#
# ⚠️⚠️ IT NEVER TOUCHES A REAL PROJECT. It builds a throwaway game out of the
# demonstration sheet, in a home of its own, on a port of its own — the same
# rule as check/check.sh, and for the same reason: opening a sheet in the
# editor SAVES, so pointing a browser at somebody's real cutting folder writes
# to the one store that cannot be rebuilt.
#
# ⭐️ And that is also why the pictures may go in a PUBLIC repository: nothing
# in them is anybody's artwork. The demonstration sheet is drawn by
# demo/make_demo_sheet.py out of nothing.
#
#     docs/make_guide_pictures.sh        # writes docs/guide/*.png
#
# Run it again whenever the room's screens change; a guide illustrated with
# last month's screens is worse than one with no pictures at all.
set -e
cd "$(dirname "$0")/.."

PORT=${PORT:-8811}
SHOTS="docs/guide"
CHROME=${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}

PY=python3
if ! $PY -c "import numpy, PIL" > /dev/null 2>&1; then PY=/usr/bin/python3; fi
if ! $PY -c "import numpy, PIL" > /dev/null 2>&1; then
  echo "needs a python with numpy and Pillow"; exit 1
fi
if [ ! -x "$CHROME" ]; then
  echo "no Chrome at $CHROME — set CHROME to where it lives"; exit 1
fi

TMP=$(mktemp -d /tmp/cutting-guide.XXXXXX)
ROOM_PID=""
# ⚠️ `|| true` on both, and no bare `&&`: a failing command in an EXIT trap
# under `set -e` ends the trap, takes the exit status with it and leaves the
# temporary folder behind. See CLAUDE.md 53.
clear_up() {
  if [ -n "$ROOM_PID" ]; then kill "$ROOM_PID" 2>/dev/null || true; fi
  rm -rf "$TMP" || true
}
trap clear_up EXIT INT TERM

mkdir -p "$SHOTS"
$PY demo/make_demo_sheet.py > /dev/null

# ---- a small game: a core box of three sheets and one supplement, so the
#      pictures show the room grouping a game the way a real one arrives
$PY - "$TMP" <<'PY'
import json, os, shutil, sys
tmp = sys.argv[1]
bed = os.path.join(tmp, "home", "demo")
os.makedirs(os.path.join(bed, "sheets"))
sheets = []
for sid, label in (("core-01", "Core box, sheet 1"), ("core-02", "Core box, sheet 2"),
                   ("core-03", "Core box, sheet 3"), ("extras-01", "Supplement, sheet 1")):
    shutil.copyfile("demo/demo-sheet.png", os.path.join(bed, "sheets", sid + ".png"))
    sheets.append({"id": sid, "label": label, "name": "a demonstration sheet",
                   "w": 1800, "h": 2400})
json.dump({"id": "demo", "name": "The Demonstration Game", "game": "nothing real",
           "dpi": 300, "notes": "", "paths": {}, "hooks": [], "sheets": sheets},
          open(os.path.join(bed, "project.json"), "w"), indent=1)


def box(x, y, w, h):
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


# drawn round what is actually printed on the demonstration sheet: the
# whirlpool, two islands, a reef, and the top row of counters
pieces = [
    {"pts": box(1050, 300, 550, 550), "ink": 0, "curve": False, "name": ""},
    {"pts": box(165, 165, 915, 915), "ink": 1, "curve": False, "name": ""},
    {"pts": box(905, 1175, 655, 655), "ink": 2, "curve": False, "name": ""},
    {"pts": box(135, 1325, 595, 595), "ink": 3, "curve": False, "name": ""},
]
for col in range(6):
    pieces.append({"pts": box(126 + col * 260, 2056, 248, 248),
                   "ink": 4 + (col % 2), "curve": False, "name": ""})
json.dump({"tool": "cutting-table", "version": 2,
           "sheets": {"core-01": {"pieces": pieces}}},
          open(os.path.join(bed, "outlines.json"), "w"), indent=1)
json.dump({"projects": [bed]}, open(os.path.join(tmp, "home", "projects.json"), "w"))
PY

echo "opening the room on port $PORT, with a home of its own"
$PY cutting_room.py --port "$PORT" --home "$TMP/home" > "$TMP/room.log" 2>&1 &
ROOM_PID=$!
i=0
while [ $i -lt 60 ]; do
  if curl -s -o /dev/null --max-time 1 "http://127.0.0.1:$PORT/api/projects"; then break; fi
  sleep 0.5
  i=$((i + 1))
done

API="http://127.0.0.1:$PORT/api/p/demo"
curl -s -o /dev/null -X POST -H "Content-Type: application/json" -d '{}' "$API/cut/core-01"

# ---- name some of it, so the pictures show a job part done rather than an
#      empty room, which is what a guide's reader is trying to picture
$PY - "$PORT" <<'PY'
import json, sys, urllib.request
port = sys.argv[1]
API = "http://127.0.0.1:%s/api/p/demo" % port


def call(path, body, method="POST"):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method=method)
    return json.load(urllib.request.urlopen(req))


call("/wanted/import", {"text": "The Whirlpool\n2 Islands\nThe Reef\n"
                                "18 Damage counters\nThe rule book\n2 Range rulers",
                        "group": "core"})
call("/wanted/import", {"text": "The Deep Island\n6 Storm counters", "group": "extras"})
pieces = json.load(urllib.request.urlopen(API + "/pieces"))["pieces"]
# ⚠️ in READING ORDER, which is the order the pieces are cut and numbered in
# — the big island first, then the whirlpool beside it. Named the other way
# round the pictures show a whirlpool labelled as an island, and a guide whose
# pictures do not match its words is worse than one with none.
names = ["The Great Island", "The Whirlpool", "The Deep Island", "The Reef",
         "Damage counter — SUNK", "Damage counter — BLAZE", "Damage counter — CREW"]
kinds = ["terrain", "terrain", "terrain", "terrain", "counter", "counter", "counter"]
for p, name, kind in zip(sorted(pieces, key=lambda x: x["stem"]), names, kinds):
    call("/manifest/" + p["stem"], {"name": name, "kind": kind}, "PUT")
call("/wanted/confirm", {})
PY

# ⚠️ CHROME DOES NOT COME BACK ON ITS OWN HERE, and macOS has no `timeout`.
# Every page in the room keeps a heartbeat going — it has to, because the room
# cannot see a browser tab and must not be closed over the top of an unsaved
# edit (CLAUDE.md 21) — so `--virtual-time-budget` never runs out and the first
# screenshot hung the whole run for six minutes with the picture already
# written. So: take the shot in the background, wait for the FILE, and stop it.
shot() {
  rm -f "$SHOTS/$1.png"
  "$CHROME" --headless=new --disable-gpu --user-data-dir="$TMP/ch" \
    --window-size="$3" --virtual-time-budget=6000 \
    --screenshot="$SHOTS/$1.png" "$2" > /dev/null 2>&1 &
  ch=$!
  i=0
  while [ $i -lt 60 ]; do
    if [ -s "$SHOTS/$1.png" ]; then break; fi
    sleep 0.5
    i=$((i + 1))
  done
  sleep 1
  kill "$ch" 2>/dev/null || true
  pkill -f "user-data-dir=$TMP/ch" 2>/dev/null || true
  wait "$ch" 2>/dev/null || true
  if [ -s "$SHOTS/$1.png" ]; then
    echo "  wrote $SHOTS/$1.png"
  else
    echo "  WRONG nothing came out for $1"
  fi
}

echo "photographing the room"
shot "1-the-front-page"  "http://127.0.0.1:$PORT/"                        1500,1000
shot "2-the-sheets"      "http://127.0.0.1:$PORT/p/demo/?tab=sheets"      1500,1100
shot "3-the-table"       "http://127.0.0.1:$PORT/p/demo/table#core-01"    1500,1050
shot "4-the-pieces"      "http://127.0.0.1:$PORT/p/demo/?tab=pieces"      1500,1250
shot "5-match"           "http://127.0.0.1:$PORT/p/demo/?tab=match"       1500,1150
shot "6-the-checklist"   "http://127.0.0.1:$PORT/p/demo/?tab=wanted"      1500,1100
# ⭐️ two pieces named in the address, or the picture is an empty light table
# and shows nothing about what the tool is for. See ?fit= on the project page.
shot "7-fit-together"    "http://127.0.0.1:$PORT/p/demo/?tab=fit&fit=core_p01_04,core_p01_05" 1500,1150
shot "8-take-it-away"    "http://127.0.0.1:$PORT/p/demo/?tab=export"      1500,1200
shot "9-the-check"       "http://127.0.0.1:$PORT/api/p/demo/review/print" 1200,1400

echo "done — $SHOTS"
