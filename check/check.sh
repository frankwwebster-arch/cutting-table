#!/bin/sh
# Everything about the Cutting Room that can be checked without a person
# looking at it. Run it from anywhere:
#
#     check/check.sh
#
# It parses the code, makes a throwaway game out of the demonstration
# sheet, serves it on a port of its own with a registry of its own — so
# nothing you are actually working on is touched — and then drives a real
# browser over it: draws a piece, names it, and looks on disk to see that
# the work arrived.
#
# It needs Python with Pillow and numpy (the room needs those anyway),
# Node 22 or later, and Google Chrome. Without Node or Chrome it does the
# parsing and says plainly that the rest was skipped.
set -e
cd "$(dirname "$0")/.."

PY=${PYTHON:-python3}
PORT=${PORT:-8799}
HERE=$(pwd)
TMP=$(mktemp -d /tmp/cutting-check.XXXXXX)

# The room needs numpy and Pillow. On a Mac the python that HAS them is often
# not the python that `python3` means, so rather than stopping with an import
# error, look for one that will do. Setting PYTHON yourself always wins.
if [ -z "$PYTHON" ] && ! $PY -c "import numpy, PIL" > /dev/null 2>&1; then
  for cand in /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
    if [ -x "$cand" ] && "$cand" -c "import numpy, PIL" > /dev/null 2>&1; then
      PY=$cand
      echo "note: python3 has no numpy, so these checks are using $PY"
      break
    fi
  done
fi

# ⚠️ PYTHON WILL HAPPILY CHECK CODE IT IS NOT LOOKING AT. It keeps compiled
# copies of a module and decides whether one is stale by the source's SIZE and
# its modification time IN WHOLE SECONDS — so an edit that changes one digit
# and lands in the same second as the last one is invisible, and every check
# below runs against the previous version of the room. That happened while
# this very file's teeth were being tried: the source read 0.10, the code
# running read 0.60, and the checks came out green on both. Worse, the system
# python on a Mac keeps that cache in ~/Library/Caches, where nobody would
# think to look for it. So the run gets a cache of its own, thrown away with
# everything else at the end, and cannot read a stale one.
export PYTHONPYCACHEPREFIX="$TMP/pycache"
ROOM_PID=""
SLOW_PID=""
# ⭐️ The run's verdict, declared here at the top rather than half way down.
# A block that said `|| code=1` before this was set had its answer wiped out by
# the `code=0` that used to sit in the middle of the file — so it could only
# fail by way of `set -e`, which stops the run dead and hides every check after
# it. One place, before anything can set it. (Fault 53's neighbour.)
code=0
# ⚠️⚠️ A FAILING COMMAND IN AN EXIT TRAP, UNDER `set -e`, ENDS THE TRAP AND
# TAKES THE WHOLE RUN'S EXIT STATUS WITH IT. This was found by the exit status
# disagreeing with the report: every one of 313 checks came out right, the
# green line printed, and `check/check.sh` still answered 1. The `kill` is what
# fails, and it fails ROUTINELY — the last section of this file closes the room
# FROM the room, so by the time the trap runs the process has usually gone
# already. Two costs, and the second is worse than the first: a clean run
# reported failure, and `rm -rf` never ran, so every such run left its
# throwaway game behind in /tmp. `|| true` on both, and no bare `&&`.
clear_up() {
  if [ -n "$ROOM_PID" ]; then kill "$ROOM_PID" 2>/dev/null || true; fi
  if [ -n "$SLOW_PID" ]; then kill "$SLOW_PID" 2>/dev/null || true; fi
  rm -rf "$TMP" || true
}
trap clear_up EXIT INT TERM

say() { printf "\n\033[1m%s\033[0m\n" "$1"; }

# ------------------------------------------------------------ the code parses
say "does the Python parse, and do the editor's patches still match?"
$PY -c "import ast; ast.parse(open('cutting_room.py').read())"
$PY -c "import ast; ast.parse(open('cutting_table.py').read())"
$PY -c "import ast; ast.parse(open('cut.py').read())"
$PY -c "import ast; ast.parse(open('sheets.py').read())"
$PY -c "import ast; ast.parse(open('check/names_across_a_recut.py').read())"
$PY -c "import ast; ast.parse(open('check/the_automatic_pass.py').read())"
# ⚠️ A patch whose anchor has drifted raises here rather than serving an
# editor that quietly saves nothing.
$PY -c "import sys; sys.path.insert(0,'.'); import cutting_room; cutting_room.table_template()"
echo "  ok   the room's Python parses and every editor patch still matches"

# ⚠️⚠️ A SECOND DEFINITION OF A NAME DOES NOT CLASH IN PYTHON, IT SILENTLY
# REPLACES THE FIRST — for the whole module, including code written hundreds
# of lines above it. `cutting_room.py` had two functions called `slug`, taking
# different second arguments, and every call in the file was reaching the
# second one whichever its author meant. It surfaced as a set of sheets
# called "40", which is what `slug(x, 40)` gives you when 40 lands in the
# parameter named `fallback`.
say "is anything in here defined twice?"
$PY - <<'PYTWICE' || code=1
import ast, sys
bad = []
for mod in ("cutting_room.py", "cutting_table.py", "cut.py", "sheets.py"):
    tree = ast.parse(open(mod, encoding="utf-8").read(), mod)
    seen = {}
    for node in tree.body:            # top level only: a method may share a name
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in seen:
                bad.append("%s: %s is defined at line %d and again at line %d"
                           % (mod, node.name, seen[node.name], node.lineno))
            seen[node.name] = node.lineno
    print(("  ok   " if not bad else "  WRONG ") +
          "nothing in %s is defined twice" % mod +
          ("" if not bad else "   — saw " + "; ".join(bad)))
    if bad:
        break
sys.exit(1 if bad else 0)
PYTWICE

# ⭐️ A GOOGLE DOC IS NOT A FILE, IT IS A THING GOOGLE WILL MAKE A FILE OUT OF.
# The designer, 24 August 2026, trying one: a document has no download at its own
# address, so what came back was the editor's web page — and the room reported
# a perfectly well shared document as unshared. Asked to EXPORT, the same
# document comes back as a PDF. No network here: this is which address the
# room decides to ask.
say "a link to a Google document is asked for as a PDF"
$PY - <<'PYDOC' || code=1
import sys
sys.path.insert(0, ".")
import cutting_room as c
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


for kind in ("document", "presentation", "spreadsheets"):
    link = "https://docs.google.com/%s/d/1AbCdEfGhIjKlMnOpQrStUv/edit?usp=sharing" % kind
    m = c.DOC_EXPORT.search(link)
    check("a Google %s link is recognised" % kind, bool(m), link)
    if m:
        check("and it is its id the room asks about",
              m.group(2) == "1AbCdEfGhIjKlMnOpQrStUv", m.group(2))
# ⚠️ A PUBLISHED link is a different address with no export behind it, and a
# plain Drive FILE already has a download of its own — neither is a document
# to be exported, and quietly rewriting either would break a link that works.
check("a published link is left exactly as it is",
      not c.DOC_EXPORT.search("https://docs.google.com/document/d/e/2PACX-1vAbCdEf/pub"))
check("and so is an ordinary Drive file link",
      not c.DOC_EXPORT.search("https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUv/view"))
sys.exit(1 if bad else 0)
PYDOC

# ⚠️ AN UNTERMINATED STRING KILLS A PAGE SILENTLY, with a working server
# behind it. Each page's script is pulled out and parsed on its own.
if command -v node > /dev/null 2>&1; then
  say "does every page's script parse?"
  $PY - "$TMP" <<'PY'
import re, sys, os
out = sys.argv[1]
pages = {
    "room/home.html": None, "room/project.html": None,
    "cutting_table.tpl.html": {"/*__SHEETS__*/": "[]", "/*__SUBJECT__*/": "x",
                               "/*__ROOM__*/": "{}", "/*__SAVED__*/": "{}",
                               "/*__BACK__*/": "/", "/*__TITLE__*/": "t"},
}
for page, fill in pages.items():
    src = open(page, encoding="utf-8").read()
    for hole, plug in (fill or {}).items():
        src = src.replace(hole, plug)
    js = re.search(r"<script>(.*)</script>", src, re.S).group(1)
    open(os.path.join(out, os.path.basename(page) + ".js"), "w").write(js)
print("   pulled the script out of", len(pages), "pages")
PY
  for f in "$TMP"/*.js; do node --check "$f"; done
  node --check room/drop.js
  echo "  ok   every page's script parses"

  # ⚠️ THE SERVED EDITOR IS NOT THE TEMPLATE. TABLE_PATCHES splices Python
  # strings into it, and a backslash escape in one of those is unescaped by
  # Python before the page ever sees it — so an intended \n arrives as a real
  # newline, ends the string it is in, and kills the editor silently with a
  # working server behind it. The template parsed perfectly the whole time.
  # This happened. Parse what is actually SERVED, not what is on disk.
  say "does the editor still parse AFTER the room has patched it?"
  $PY - "$TMP" <<'PY2'
import os, re, sys
sys.path.insert(0, ".")
import cutting_room
html = cutting_room.table_template()
for hole, plug in {"/*__SHEETS__*/": "[]", "/*__SUBJECT__*/": "x", "/*__ROOM__*/": "{}",
                   "/*__SAVED__*/": "{}", "/*__BACK__*/": "/", "/*__TITLE__*/": "t"}.items():
    html = html.replace(hole, plug)
js = re.search(r"<script>(.*)</script>", html, re.S).group(1)
open(os.path.join(sys.argv[1], "served-editor.js"), "w").write(js)
PY2
  node --check "$TMP/served-editor.js"
  echo "  ok   the editor the room serves parses too"
else
  echo "  -- no node, so the pages' scripts were not parsed"
fi

# ⚠️ NAMES FOLLOWING THEIR PIECES ACROSS A RE-CUT is the most delicate code
# in the room, and for a long time nothing exercised it. It needs no browser:
# it is the cut itself. Its own throwaway game, in a folder of its own.
say "do names follow their pieces when a sheet is cut again?"
$PY demo/make_demo_sheet.py > /dev/null
$PY check/names_across_a_recut.py

# ⭐️ Naming is the expensive part of the whole business, so the room offers a
# kind rather than asking for one. What matters most here is not that it knows
# a card — it is that it stays SILENT about everything a measurement cannot
# settle, because a confident wrong answer will be accepted without looking.
say "does the room guess a piece's kind from its size — and hold its tongue otherwise?"
$PY check/guessing_the_kind.py

# ⭐️⭐️ THE AUTOMATIC FIRST ATTEMPT AT A SHEET. The designer, 25 August 2026: "the
# auto cutting pass is essentially pointless" — it added nodes everywhere and
# bent straight edges into curves. Like the kinds above, what matters most is
# the half where it says nothing: a hexagon squared off is a confident wrong
# answer drawn over somebody's artwork. No browser and no project; it draws
# its own sheet, unevenly lit and speckled, out of the shapes a box really
# holds.
say "does the automatic pass draw the shape that is printed — and only where it is sure?"
$PY check/the_automatic_pass.py

# ⭐️⭐️ EVERY CONTROL SAYS WHAT IT DOES. The designer, 23 August 2026: "I don't, for
# example, have any idea what 'straight to the table' means on the project
# selection screen, so a hover tool or just in line text popup or whatever
# explaining what all the features and buttons do would be very helpful. And
# that's not just for me, obviously!"
#
# ⚠️ This is the check that stops the NEXT unexplained button, which is the
# whole point of writing it down rather than fixing the ones that exist today.
# A button with neither `data-tip` nor `title` fails here, by name.
say "does every button say what it does?"
$PY - <<'PY9'
import re, sys
sys.path.insert(0, ".")
import cutting_room

bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


# A handful genuinely do not need a sentence: a zoom + and −, a × that sits on
# the thing it removes. Anything else must speak.
FINE = {"zin", "zout", "zspin", "zfit"}

pages = {"the front page": open("room/home.html").read(),
         "the project page": open("room/project.html").read(),
         "the cutting table the room serves": cutting_room.table_template()}
for name, html in pages.items():
    body = re.sub(r"<script>.*?</script>", "", html, flags=re.S)
    bare = []
    for tag in re.findall(r"<button\b[^>]*>", body):
        if "data-tip" in tag or "title=" in tag:
            continue
        got = re.search(r'id="([^"]+)"', tag)
        if got and got.group(1) in FINE:
            continue
        bare.append(got.group(1) if got else tag[:50])
    check("every button on %s explains itself" % name, not bare, bare or "all of them")

# and the ones built by JavaScript, which is where the buttons a person meets
# most often actually come from
js = open("room/project.html").read() + open("room/home.html").read()
for want, where in ((r"data-tip[^>]*>Open<", "Open, on a project card"),
                    (r"Straight to the table", "Straight to the table"),
                    (r'id="fShape"[^>]*data-tip', "Keep the shape, on a cut piece"),
                    (r'id="fDel"[^>]*data-tip', "Set this piece aside")):
    check("%s explains itself" % where, re.search(want, js) is not None)

# ⭐️ the one the designer named, and it must say where it goes
m = re.search(r'data-tip="([^"]*)"[^>]*>Straight to the table', open("room/home.html").read())
m = m or re.search(r"Straight to the table", open("room/home.html").read())
tip = re.search(r"Skip the project page[^']*", open("room/home.html").read())
check("and it says what it skips, in plain words", tip is not None,
      (tip.group(0)[:60] + "…") if tip else "nothing")

sys.exit(1 if bad else 0)
PY9

# ⭐️ THE GUIDE IS SOMETHING THAT LEAVES THE ROOM, so it carries the notice
# like everything else that does (fault 22) — and a guide whose pictures are
# missing is worse than one with none, because every one of them shows as a
# broken image. ⚠️ The pictures are of the DEMONSTRATION sheet, drawn by the
# tool out of nothing: no game's artwork may ever appear in this repository.
# ⭐️⭐️ NOTHING HERE NAMES A GAME OR A PERSON, AND THIS IS WHAT KEEPS IT THAT
# WAY. The rule at the top of CLAUDE.md is that the room knows nothing about
# any one game; the names crept in anyway, in the explanations of WHY a rule is
# the way it is, because that is where the evidence for it came from. Taking
# them out afterwards took three passes and still missed one that had wrapped
# across a line break. So the checking is done here, once, on every file the
# repository actually holds — and it is the same shape as every other rule in
# this file: the point is not the ones already fixed, it is the next one.
#
# ⚠️ It searches the text with the LINE BREAKS TAKEN OUT, because that is how
# the last one hid: a two-word name with the line ending between the words is
# not that name at all as far as an ordinary search is concerned, and it sat
# there through two passes that were both looking straight at it.
say "nothing in here names a game, a publisher or a person"
$PY - <<'PY13' || code=1
import re
import subprocess
import sys

bad = []
# A publisher, its games, and the factions in them; and the owner's name. Add
# to this rather than arguing with it: a word here costs nothing, and a name
# in a public repository cannot be taken back once it is cloned.
FORBIDDEN = [
    "games workshop", "citadel", "white dwarf", "warhammer", "heroquest",
    "man o war", "man o' war", "manowar", "blood bowl", "necromunda",
    "gorkamorka", "battlefleet", "slaanesh", "khorne", "nurgle", "tzeentch",
    "skaven", "bretonnian", "waaagh", "plague fleet", "sea of blood",
    "sea of claws", "wizard marker", "chaos magic", "chaos experience",
    "frank", "webster",
]
files = [f for f in subprocess.run(["git", "ls-files"], capture_output=True,
                                   text=True).stdout.split()
         if not f.endswith(".png")]
for word in FORBIDDEN:
    where = []
    for f in files:
        try:
            t = open(f).read()
        except (OSError, UnicodeDecodeError):
            continue
        # ⚠️ THE LIST ITSELF IS NOT A BREACH OF THE LIST. Written without this,
        # the check found all twenty-six of its own words in its own source and
        # reported the repository as riddled with them. Cut the literal out of
        # whichever file carries it, and go on searching the rest of that file
        # — so a name really written in here is still caught.
        t = re.sub(r"FORBIDDEN = \[.*?\n\]", "", t, flags=re.S)
        flat = re.sub(r"[\s#*>|/_-]+", " ", t).lower()
        if word in flat:
            where.append(f)
    if where:
        bad.append(word)
        print("  WRONG %r is back, in %s" % (word, ", ".join(where)))
if not bad:
    print("  ok   no game, publisher or person is named anywhere in the %d "
          "files this repository holds" % len(files))
sys.exit(1 if bad else 0)
PY13

say "the guide, and its pictures"
$PY - <<'PY10' || code=1
import os
import re
import sys

bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


guide = open("GUIDE.md").read()
check("the guide says what a person actually does, step by step",
      all(w in guide for w in ("Get the scans in", "Draw round each piece",
                               "Cut", "Say what each piece is",
                               "Check what you have against the box",
                               "take it away")))
# ⚠️ the same three refusals as COPYRIGHT_NOTICE, in the guide's own words
# ⚠️ the SUBSTANCE of COPYRIGHT_NOTICE, not one sentence of it word for word:
# the guide says it in its own voice, and a check pinned to one phrasing would
# go red over a rewording rather than over the meaning going missing.
for phrase in ("yours to give away", "on the internet", "not lawyers"):
    check("the guide carries the copyright notice: %r" % phrase, phrase in guide)
shots = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", guide)
check("it has pictures at all", len(shots) >= 6, len(shots))
gone = [f for f in shots if not os.path.exists(f)]
check("and every one of them is really there", not gone, gone or "all of them")
# ⚠️⚠️ ON THE DISK IS NOT IN THE REPOSITORY. This check first asked only
# whether the files existed — and they did, while `.gitignore` was quietly
# keeping every one of them out: `!docs/*.png` does not reach `docs/guide/`.
# So the guide was perfect here and eight broken images to anybody who read it
# anywhere else, for ever, with a green check over it. Ask git.
import subprocess
try:
    tracked = set(subprocess.run(["git", "ls-files", "docs/guide"],
                                 capture_output=True, text=True,
                                 timeout=20).stdout.split())
except (OSError, subprocess.SubprocessError):
    tracked = None
if tracked is None:
    print("  ..   not a git checkout, so whether the pictures are committed "
          "cannot be told from here")
else:
    out = [f for f in shots if f.startswith("docs/") and f not in tracked]
    check("and every one is in the repository, not just on this disk",
          not out, out or "all of them")
check("the pictures can be made again, so they cannot rot unnoticed",
      os.access("docs/make_guide_pictures.sh", os.X_OK))
sys.exit(1 if bad else 0)
PY10

# ------------------------------------------------------- a throwaway game
if ! command -v node > /dev/null 2>&1; then
  echo ""
  echo "no node, so the browser checks were skipped."
  exit 0
fi
CHROME=${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}
if [ ! -x "$CHROME" ]; then
  echo ""
  echo "no Chrome at $CHROME, so the browser checks were skipped."
  echo "set CHROME to where it lives and run this again."
  exit 0
fi

say "a throwaway game, in a home of its own"
$PY demo/make_demo_sheet.py > /dev/null
$PY - "$TMP" <<'PY'
import json, os, shutil, sys
tmp = sys.argv[1]
bed = os.path.join(tmp, "home", "proving-ground")
os.makedirs(os.path.join(bed, "sheets"))
# two runs out of two pretend books, and one sheet on its own, which is
# how a real game's sheets arrive and what the rail has to make sense of
books = [("proving-ground-sheets", 40), ("second-book-of-tests", 25), ("odd-one-out", 1)]
sheets = []
for book, pages in books:
    for n in range(1, pages + 1):
        sid = "%s-%02d" % (book, n)
        shutil.copyfile("demo/demo-sheet.png", os.path.join(bed, "sheets", sid + ".png"))
        sheets.append({"id": sid, "label": "%s p.%d" % (book, n),
                       "name": "a pretend sheet", "w": 1800, "h": 2400})
json.dump({"id": "proving-ground", "name": "The Proving Ground",
           "game": "nothing real", "dpi": 300, "notes": "", "paths": {},
           "hooks": [], "sheets": sheets},
          open(os.path.join(bed, "project.json"), "w"), indent=1)
json.dump({"game": "nothing real", "note": "", "kinds": [], "groups": [], "items": []},
          open(os.path.join(bed, "wanted.json"), "w"), indent=1)
# a second game with no sheets at all, for the checklist work — so breaking a
# contents list apart cannot disturb the pieces the browser checks are naming
other = os.path.join(tmp, "home", "the-supplement")
os.makedirs(other)
json.dump({"id": "the-supplement", "name": "The Supplement", "game": "nothing real",
           "dpi": 300, "notes": "", "paths": {}, "hooks": [], "sheets": []},
          open(os.path.join(other, "project.json"), "w"), indent=1)
json.dump({"game": "nothing real", "note": "", "kinds": [], "groups": [], "items": []},
          open(os.path.join(other, "wanted.json"), "w"), indent=1)
json.dump({"pieces": {}}, open(os.path.join(other, "manifest.json"), "w"), indent=1)
# ⭐️ a third game, for taking a whole box of sheets out again: two books, one
# of them outlined, and nothing else in the run reading it — because that
# check DELETES, and it should not be able to spoil anything else.
spare = os.path.join(tmp, "home", "the-spare-room")
os.makedirs(os.path.join(spare, "sheets"))
spare_sheets = []
# ⚠️ THREE books, and the third is the browser's: the page presses the button
# for real further down, and the two checks must not be able to spoil each
# other — least of all when the browser is skipped for want of Chrome, which
# would otherwise change what this one counts.
for book, pages in (("keepers", 2), ("throwaways", 3), ("browser-fodder", 2)):
    for n in range(1, pages + 1):
        sid = "%s-%02d" % (book, n)
        shutil.copyfile("demo/demo-sheet.png", os.path.join(spare, "sheets", sid + ".png"))
        spare_sheets.append({"id": sid, "label": "%s p.%d" % (book, n),
                             "name": "", "w": 1800, "h": 2400})
json.dump({"id": "the-spare-room", "name": "The Spare Room", "game": "nothing real",
           "dpi": 300, "notes": "", "paths": {}, "hooks": [], "sheets": spare_sheets},
          open(os.path.join(spare, "project.json"), "w"), indent=1)
json.dump({"sheets": {"throwaways-01": {"pieces": [{"pts": [[0, 0], [10, 0], [10, 10]]},
                                                   {"pts": [[0, 0], [5, 0], [5, 5]]}],
                                        "stamp": 1}}},
          open(os.path.join(spare, "outlines.json"), "w"), indent=1)
json.dump({"projects": [bed, other, spare]},
          open(os.path.join(tmp, "home", "projects.json"), "w"), indent=1)
print("   %d sheets out of %d books" % (len(sheets), len(books)))
PY

say "baking the same editor into an offline page"
$PY cutting_table.py --images demo/demo-sheet.png demo/demo-sheet.png \
    --subject "The Proving Ground" --out "$TMP/baked.html" | tail -1

say "opening the room on port $PORT, with its own registry"
$PY cutting_room.py --port "$PORT" --home "$TMP/home" > "$TMP/room.log" 2>&1 &
ROOM_PID=$!
up=0
i=0
while [ $i -lt 60 ]; do
  if curl -s -o /dev/null "http://127.0.0.1:$PORT/api/projects"; then up=1; break; fi
  sleep 0.5
  i=$((i + 1))
done
if [ $up -eq 0 ]; then
  echo "the room never came up. Its log:"
  cat "$TMP/room.log"
  exit 1
fi
echo "  ok   the room is up"

# ⚠️⚠️ A POST MUST LEAVE THE CONNECTION FIT FOR THE NEXT REQUEST.
# The browser keeps one connection and sends request after request down it.
# A handler that answers a POST without reading the body leaves those bytes
# in the socket, and the next request is read starting from them: the browser
# asks for a page and the room sees the request line "{}GET /p/... " and
# answers 501 Unsupported method. "Cut this sheet" forgot, and the project
# page came up as an empty error page because of it — with nothing in the
# log, because the logger crashed on the very error it was reporting.
say "does a POST leave the connection fit for the request after it?"
curl -s -o "$TMP/posted.json" -H "Content-Type: application/json" -d "{}" \
     "http://127.0.0.1:$PORT/api/p/proving-ground/cut/no-such-sheet" \
     --next -o "$TMP/after-post.html" "http://127.0.0.1:$PORT/p/proving-ground/"
if grep -q 'id="mGrid"' "$TMP/after-post.html"; then
  echo "  ok   the page asked for after a POST is the page, not a 501"
else
  echo "  WRONG the request after a POST on the same connection was not the page:"
  head -5 "$TMP/after-post.html"
  exit 1
fi

# ⭐️ SHAPES KEPT, AND KEPT BESIDE THE PROJECTS RATHER THAN INSIDE ONE.
# The designer, 23 August 2026: "I will need to cut a number of pieces that are
# different, but also EXACTLY the same shape — I only want to create that
# shape mask ONCE… and perhaps use that between projects (eg one dungeon game
# and another)." So the shelf is a file in the room's home, in inches, and nothing
# a page sends it is believed.
say "the shelf of shapes: kept beside the projects, and shared by them"
$PY - "$TMP" "$PORT" <<'PY8'
import json, os, sys, urllib.error, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def ask(body):
    req = urllib.request.Request("http://127.0.0.1:%s/api/shapes" % port,
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        return 200, json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


code, first = ask({"what": "list"})
check("the shelf starts empty", first.get("shapes") == [], first.get("shapes"))

# a dungeon game's door: 2.05 x 1.02in, four corners
door = {"name": "door", "curve": False, "w": 2.05, "h": 1.02,
        "pts": [[0, 0], [2.05, 0], [2.05, 1.02], [0, 1.02]]}
code, kept = ask({"what": "keep", "shape": door,
                  "project": "proving-ground", "game": "The Proving Ground"})
one = (kept.get("shapes") or [{}])[0]
check("a shape can be kept", code == 200 and len(kept.get("shapes") or []) == 1, code)
check("it is kept in inches, not in one sheet's pixels",
      one.get("w") == 2.05 and one.get("h") == 1.02, [one.get("w"), one.get("h")])
check("and it says which game it was drawn in, so another one can tell",
      one.get("game") == "The Proving Ground", one.get("game"))
check("it is given a name of its own to be found by", bool(one.get("id")), one.get("id"))

# ⭐️ the whole point: the shelf is NOT inside the project
on_disk = os.path.join(tmp, "home", "shapes.json")
inside = os.path.join(tmp, "home", "proving-ground", "shapes.json")
check("the shelf is a file beside the projects, not inside one",
      os.path.exists(on_disk) and not os.path.exists(inside), on_disk)
check("and every project in the room is offered it",
      json.load(open(on_disk))["shapes"][0]["name"] == "door")

# ⚠️ It comes off a web page, so none of it is believed.
code, no = ask({"what": "keep", "shape": {"name": "x", "w": 1, "h": 1,
                                          "pts": [[0, 0], [1, 1]]}})
check("a shape with two nodes is refused, with a reason",
      code == 400 and "three nodes" in (no.get("error") or ""), no.get("error"))
code, no = ask({"what": "keep", "shape": {"name": "x", "w": 1, "h": 1,
                                          "pts": [[0, 0], [1, "seven"], [1, 1]]}})
check("a node that is not a number is refused, with a reason",
      code == 400 and "number" in (no.get("error") or ""), no.get("error"))
code, no = ask({"what": "keep", "shape": {"name": "x", "w": 0, "h": 1,
                                          "pts": [[0, 0], [1, 0], [1, 1]]}})
check("a shape of no size is refused, with a reason",
      code == 400 and (no.get("error") or ""), no.get("error"))
code, still = ask({"what": "list"})
check("and none of those reached the shelf", len(still.get("shapes") or []) == 1,
      len(still.get("shapes") or []))

# ⭐️ FAVOURITED PER PROJECT, SEARCHABLE BETWEEN THEM. The designer, 23 August 2026:
# "I'd like to be able to favourite specific shapes on a per project basis but
# have that library searchable between projects (eg in one game I can review
# shapes I favourited in another)." So the mark belongs to the project, not
# to the shape, and one shape can be marked by several at once.
check("a shape is one of its own game's from the moment it is drawn",
      one.get("stars") == ["proving-ground"], one.get("stars"))

quest = dict(door, name="quest door", w=1.5, h=1.5,
             pts=[[0, 0], [1.5, 0], [1.5, 1.5], [0, 1.5]])
code, both = ask({"what": "keep", "shape": quest,
                  "project": "another-game", "game": "A Dungeon Game"})
other = (both.get("shapes") or [{}])[0]
check("another game's shape sits on the same shelf",
      len(both.get("shapes") or []) == 2, len(both.get("shapes") or []))
check("but is not one of this game's until it is said to be",
      other.get("stars") == ["another-game"], other.get("stars"))

code, after = ask({"what": "star", "shape": {"id": other.get("id")},
                   "project": "proving-ground"})
now = [x for x in after.get("shapes") or [] if x.get("id") == other.get("id")][0]
check("starring it here does not take it from the game it came out of",
      sorted(now.get("stars") or []) == ["another-game", "proving-ground"],
      now.get("stars"))
code, after = ask({"what": "star", "shape": {"id": other.get("id")},
                   "project": "proving-ground"})
now = [x for x in after.get("shapes") or [] if x.get("id") == other.get("id")][0]
check("and the star comes off again without touching the other game's",
      now.get("stars") == ["another-game"], now.get("stars"))

for dead in (one, other):
    code, gone = ask({"what": "forget", "shape": {"id": dead.get("id")}})
check("a shape can be forgotten again", gone.get("shapes") == [], gone.get("shapes"))
check("and the file says so too", json.load(open(on_disk))["shapes"] == [])

sys.exit(1 if bad else 0)
PY8

say "and now, in a real browser"
mkdir -p "$TMP/shots"
# ⚠️ The rectangle the browser draws comes out an inch and a half square, and
# an inch and a half square is EXACTLY the shape the room refuses to guess
# about — a tile, a template, half a board, no way to tell. So the browser
# gets a counter of its own to press the offer on. It is dropped into the
# store at the start of that one section and taken away again at the end of
# it, so nothing before or after ever sees it.
$PY - "$TMP" <<'PY7'
import sys
from PIL import Image, ImageDraw
im = Image.new("RGBA", (188, 188), (0, 0, 0, 0))
ImageDraw.Draw(im).rectangle([0, 0, 187, 187], fill=(90, 130, 180, 255))
im.save(sys.argv[1] + "/a-counter.png")            # 0.63in square at 300dpi
# ⭐️ and a speck, for the flags. A piece the room is worried about is the only
# way to try the answer to a worry, and 0.2in square is "very small" by any
# reading. Dropped in for one section and taken away again, like the counter.
im = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
ImageDraw.Draw(im).rectangle([0, 0, 59, 59], fill=(180, 90, 90, 255))
im.save(sys.argv[1] + "/a-speck.png")              # 0.20in square at 300dpi
PY7
# ⭐️⭐️ A LINK THAT TAKES ITS TIME, so there is something to watch while it
# does. The designer, 24 August 2026, importing a document from a link: "status says
# 'Fetching...' but would be much more useful if that were an actual progress
# bar or at the very least something a little more animated so i can see if
# it's stalled." A file served instantly proves nothing about that, so this
# serves a real sheet a tenth at a time with a wait between each — the same
# shape as a slow link, and it takes about two and a half seconds.
SLOW_PORT=$((PORT + 3))
$PY - "$SLOW_PORT" <<'PYSLOW' > /dev/null 2>&1 &
import http.server, socketserver, sys, time
data = open("demo/demo-sheet.png", "rb").read()


class Trickle(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        step = max(1, len(data) // 10)
        for i in range(0, len(data), step):
            self.wfile.write(data[i:i + step])
            self.wfile.flush()
            time.sleep(0.25)

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(("127.0.0.1", int(sys.argv[1])), Trickle).serve_forever()
PYSLOW
SLOW_PID=$!

ROOM="http://127.0.0.1:$PORT" \
COUNTER="$TMP/a-counter.png" \
SPECK="$TMP/a-speck.png" \
SLOW_URL="http://127.0.0.1:$SLOW_PORT/a-slow-sheet.png" \
PROJECT="proving-ground" \
SHEETS=66 \
OUTLINES="$TMP/home/proving-ground/outlines.json" \
BED="$TMP/home/proving-ground" \
BAKED="$TMP/baked.html" \
SHOTS="$TMP/shots" \
CHROME="$CHROME" \
  node check/in_the_browser.js || code=$?

# the pictures are worth keeping when something has gone wrong
if [ $code -ne 0 ] && [ -d "$TMP/shots" ]; then
  keep=${TMPDIR:-/tmp}/cutting-check-shots
  rm -rf "$keep"; cp -R "$TMP/shots" "$keep"
  echo "the screenshots are in $keep — LOOK AT THEM."
fi

# ⭐️⭐️ A QUANTITY IS NOT A SET OF DESIGNS. The designer, 23 August 2026, on a game's
# supplements: "the contents of the supplements only gives generic
# descriptions of ship cards" — one printed line naming a player's ship
# templates where the box holds three differently named ships. Three real
# components — and until it is broken up, Match can only give all three pieces
# the same name, which is exactly what the game reading the manifest cannot
# make sense of.
say "one line of a contents list, broken into the components it stands for"
$PY - "$TMP" "$PORT" <<'PY10'
import json, os, sys, urllib.error, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
API = "http://127.0.0.1:%s/api/p/the-supplement" % port
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def call(path, body, method="POST"):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method=method)
    try:
        return 200, json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


code, w = call("/wanted/import", {"text": "3 Long movement templates\n26 Damage counters",
                                  "group": "core"})
line = [i for i in w["items"] if "Long movement" in i["name"]][0]
check("a printed contents list comes in as one line for the three of them",
      line["qty"] == "3", line["qty"])

# a piece cut and linked to that one line, the way Match leaves it
man = os.path.join(tmp, "home", "the-supplement", "manifest.json")
json.dump({"pieces": {
    "tmpl_00": {"name": "Long movement templates", "wanted": line["id"]},
    "tmpl_01": {"name": "the one I named myself", "wanted": line["id"]}}},
    open(man, "w"), indent=1)

code, d = call("/wanted/split", {"id": line["id"],
                                 "names": ["Long template A", "Long template B",
                                           "Long template C"]})
made = d.get("made") or []
check("it can be broken into the components it really stands for", len(made) == 3,
      [m["name"] for m in made])
check("each one is a component in its own right, wanted once",
      all(m["qty"] == "1" for m in made), [m["qty"] for m in made])
check("and each says which printed line it came out of",
      all(m.get("from") == "Long movement templates" for m in made),
      made[0].get("from") if made else "")
check("the line it came from is gone, so nothing is counted twice",
      not [i for i in d["items"] if i["name"] == "Long movement templates"])
check("and the rest of the list is left alone",
      [i["name"] for i in d["items"] if i["name"] == "Damage counters"] == ["Damage counters"])

# ⚠️ the pieces that were tied to the old line must not be left pointing at
# nothing — they follow, and the room says how many did
kept = json.load(open(man))["pieces"]
check("a piece already linked to it follows, rather than being left adrift",
      kept["tmpl_00"]["wanted"] == made[0]["id"], kept["tmpl_00"])
check("and the room says how many moved", d.get("moved") == 2, d.get("moved"))
check("its name follows too, since the room is the one that put it there",
      kept["tmpl_00"]["name"] == "Long template A", kept["tmpl_00"]["name"])
# ⭐️ THE CAREFUL ONE. A name somebody typed is theirs, and nothing may
# overwrite it — not even a tidy-up that is right about everything else.
check("but a name somebody typed themselves is left exactly as it was",
      kept["tmpl_01"]["name"] == "the one I named myself", kept["tmpl_01"]["name"])

# and now each piece can be told apart by the thing that reads the manifest
check("the pieces no longer share one name",
      kept["tmpl_00"]["name"] != kept["tmpl_01"]["name"])

code, no = call("/wanted/split", {"id": made[0]["id"], "names": ["only one"]})
check("splitting into one component is refused, with a reason",
      code == 400 and "at least two" in (no.get("error") or ""), no.get("error"))
code, no = call("/wanted/split", {"id": "no-such-thing", "names": ["a", "b"]})
check("splitting something that is not on the list is refused, with a reason",
      code == 400 and (no.get("error") or ""), no.get("error"))

# ⭐️ and the pay-off: a piece named by hand is FOUND by the component that was
# split out for it, so one press ties them together
json.dump({"pieces": {"tmpl_02": {"name": "Long template C"}}}, open(man, "w"), indent=1)
got = json.load(urllib.request.urlopen(API + "/wanted"))
hit = [i for i in got["items"] if i["name"] == "Long template C"]
check("a piece already named by hand is recognised by its new component",
      hit and hit[0]["state"] == "probably", hit[0]["state"] if hit else "no such item")
code, conf = call("/wanted/confirm", {})
check("and one press ties them together", conf.get("confirmed") == 1, conf.get("confirmed"))

sys.exit(1 if bad else 0)
PY10

# ⭐️⭐️ A DECK IS COUNTED; A COUNTER IS NOT. The designer, 23 August 2026: "build
# checklist counting deck against quantity — it's then my responsibility to
# ensure I have the correct number of cards to fill each deck." Both arrive as
# one line with a number on it and only a person can tell them apart, so the
# room asks rather than guessing — and the checks below are mostly about it
# not guessing.
say "counting a deck against its quantity, without counting a counter"
# ⚠️ `|| code=1` like every other block, not a bare run. Without it `set -e`
# kills the whole script on the first WRONG in here — so a single fault hid the
# hundred and twenty checks that come after it, and the run said nothing about
# whether THEY were still right. A check suite that stops at the first fault
# tells you about one thing when it could have told you about everything.
$PY - "$TMP" "$PORT" <<'PY11' || code=1
import json, os, sys, urllib.error, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
API = "http://127.0.0.1:%s/api/p/the-supplement" % port
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def call(path, body=None, method="POST"):
    req = urllib.request.Request(API + path,
                                 data=json.dumps(body or {}).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method=method)
    try:
        return 200, json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def by(items, name):
    return [i for i in items if i["name"] == name][0]


# start this game's list again, and give it four cards cut and named by hand
json.dump({"game": "nothing real", "note": "", "kinds": [], "groups": [], "items": []},
          open(os.path.join(tmp, "home", "the-supplement", "wanted.json"), "w"))
json.dump({"pieces": {"c00": {"name": "Damage card 01"}, "c01": {"name": "Damage card 02"},
                      "c02": {"name": "Damage card 03"}, "w00": {"name": "Damage counter"}}},
          open(os.path.join(tmp, "home", "the-supplement", "manifest.json"), "w"))

code, d = call("/wanted/import", {"text": "24 Damage card\n26 Damage counter",
                                  "group": "core", "each": True})
deck, counter = by(d["items"], "Damage card"), by(d["items"], "Damage counter")
check("a pasted list can be told its lines are decks",
      deck["need"] == 24 and counter["need"] == 26, [deck["need"], counter["need"]])

# ⚠️⚠️ THE COUNT COMES FIRST. Asking "does a piece's name match?" before "are
# there enough of them?" made a deck with NOTHING cut read as probably cut,
# and the whole checklist showed 100%.
check("a deck with nothing linked is not 'probably cut' because three names match",
      deck["state"] != "probably", deck["state"])
check("and the checklist does not call the game done", d["summary"]["pct"] == 0,
      d["summary"]["pct"])

code, d = call("/wanted/confirm")
deck, counter = by(d["items"], "Damage card"), by(d["items"], "Damage counter")
check("one press ties up every card of a deck whose name matches, not just one",
      d["confirmed"] == 4, d["confirmed"])
check("a deck with some of its cards cut says how many, and is not done",
      (deck["got"], deck["need"], deck["state"]) == (3, 24, "part"),
      [deck["got"], deck["need"], deck["state"]])
check("a part-filled deck is not counted as accounted for",
      d["summary"]["done"] == 0, d["summary"]["done"])
check("and the sum in actual pieces is given as well as in components",
      d["summary"]["pieces_cut"] == 4 and d["summary"]["pieces_wanted"] == 50,
      [d["summary"]["pieces_cut"], d["summary"]["pieces_wanted"]])

# ⭐️ AND THE RULE THE WHOLE ROOM IS BUILT ON IS UNTOUCHED: a sheet printing
# twenty-six identical counters wants ONE cut, because the game repeats it.
# ⚠️ SENT BACK WHOLE, exactly as the page sends it — worked-out fields and
# all. Taking them off is the ROOM's job now, in the one place that saves the
# list, and the check below reads the disk to see that it did.
items = d["items"]
for i in items:
    if i["name"] == "Damage counter":
        i["each"] = False
code, d = call("/wanted", {"items": items}, method="PUT")
counter = by(d["items"], "Damage counter")
check("a counter set back to 'one is enough' is done with one piece",
      (counter["got"], counter["need"], counter["state"]) == (1, 1, "cut"),
      [counter["got"], counter["need"], counter["state"]])
check("and the deck beside it is untouched by that",
      by(d["items"], "Damage card")["need"] == 24)

# ⭐️⭐️ ONE DESIGN, CUT ONCE, WANTED TWENTY TIMES — AND THE DECK IS FULL.
# The designer, 24 August 2026, of a deck of thirteen different cards one of which
# is printed twenty times, thirty-two cards in all: "I have marked the 20x
# component, but [the deck] reads — relatively justifiably — 13 of 32. How do
# I fix given the deck is technically complete?" `copies` on the piece already
# said the game wants that design twenty times; the checklist was not reading
# it, so a deck that really was complete could never reach its own quantity.
man_file = os.path.join(tmp, "home", "the-supplement", "manifest.json")
man = json.load(open(man_file))
man["pieces"]["c00"]["copies"] = 22
json.dump(man, open(man_file, "w"))
d = json.load(urllib.request.urlopen(API + "/wanted"))
deck = by(d["items"], "Damage card")
check("a card the game wants twenty-two times fills twenty-two of its deck",
      (deck["got"], deck["need"], deck["state"]) == (24, 24, "cut"),
      [deck["got"], deck["need"], deck["state"]])
check("and the deck still says how many pictures that is, as well as cards",
      deck["cut_pieces"] == 3, deck["cut_pieces"])
# ⚠️ THE TEETH, and the rule this must not break: nothing guesses `copies`,
# so with the mark taken off the deck is three cards into twenty-four again.
man["pieces"]["c00"].pop("copies")
json.dump(man, open(man_file, "w"))
d = json.load(urllib.request.urlopen(API + "/wanted"))
deck = by(d["items"], "Damage card")
check("and with the mark taken off it is three of twenty-four again, nothing guessed",
      (deck["got"], deck["state"]) == (3, "part"), [deck["got"], deck["state"]])

# ⚠️ the worked-out numbers must not be written into the file as though they
# were somebody's answer
kept = json.load(open(os.path.join(tmp, "home", "the-supplement", "wanted.json")))
check("nothing worked out is written back into the list on disk",
      not any(k in kept["items"][0]
              for k in ("need", "got", "cut_pieces", "state", "pieces", "guesses")),
      sorted(kept["items"][0].keys()))

# ⭐️⭐️ THE CHECK AGAINST THE CONTENTS LIST, AT THE END OF THE JOB. The designer, 24
# August 2026: "I want (once I've done my cutting work) to be able to run a
# verification check against the original component index - a secondary check
# to ensure we have every piece cut."
#
# This game is the right bench for it: a deck three cards into twenty-four, a
# counter that is done, and a piece named by hand that answers to nothing.
print("")
print("the cut checked against the contents list")
# ⚠️ A MANIFEST ENTRY IS NOT A CUT PIECE. The report counts the pieces that
# really exist — the same reading as the Pieces page, so the two cannot
# disagree about what is there — and this game was made with no sheets and no
# pieces at all, so it needs some. One picture each, and one of them answering
# to nothing on the list, which is the finding this whole section is about.
from PIL import Image
pdir = os.path.join(tmp, "home", "the-supplement", "pieces")
os.makedirs(pdir, exist_ok=True)
for stem in ("c00", "c01", "c02", "w00"):
    Image.new("RGBA", (300, 420), (120, 120, 160, 255)).save(os.path.join(pdir, stem + ".png"))
rv = json.load(urllib.request.urlopen(API + "/review"))
s = rv["summary"]
check("the room can be asked how the cut stands against the list",
      rv["has_list"] and s["components"] == 2, s)
part = [i for band in rv["sets"] for i in band["part"]]
check("a deck that is not full says how far off it is",
      any(i["got"] == 3 and i["need"] == 24 for i in part), part)
check("and it is NOT reported as missing, which would be a different job",
      not [i for band in rv["sets"] for i in band["missing"]],
      [i["name"] for band in rv["sets"] for i in band["missing"]])
# ⭐️⭐️ THE HALF THE ROOM COULD NOT DO AT ALL: a cut piece that answers to
# nothing on the list is either something the list forgot, a piece cut twice,
# or a piece cut from the wrong place. w00 is tied to the counter; c00-c02 are
# tied to the deck; the loose one is the finding.
json.dump({"pieces": {"c00": {"name": "Damage card 01"}, "c01": {"name": "Damage card 02"},
                      "c02": {"name": "Damage card 03"}, "w00": {"name": "Damage counter"},
                      "zz": {"name": "something nothing asked for"}}},
          open(os.path.join(tmp, "home", "the-supplement", "manifest.json"), "w"))
Image.new("RGBA", (300, 420), (160, 120, 120, 255)).save(os.path.join(pdir, "zz.png"))
code, d = call("/wanted/confirm")
rv = json.load(urllib.request.urlopen(API + "/review"))
loose = [o["stem"] for o in rv["orphans"]]
check("a cut piece that answers to nothing on the list is named",
      loose == ["zz"], loose)
check("and a piece that does answer to something is not",
      "w00" not in loose and "c00" not in loose, loose)

# ⭐️⭐️ A DECK COUNTED AS ONE CARD WILL READ AS DONE ON THE FIRST CARD CUT.
# Nine of one real game's twelve decks were in exactly that state, so a 32-card
# deck with one card cut would have shown the box as complete.
cur = json.load(urllib.request.urlopen(API + "/wanted"))
items = cur["items"]
for i in items:
    if i["name"] == "Damage card":
        i["each"] = False                       # a deck told one is enough
        i["kind"] = "deck"
    if i["name"] == "Damage counter":
        i["kind"] = "counter"                   # 26 of one design, quite right
code, d = call("/wanted", {"items": items}, method="PUT")
rv = json.load(urllib.request.urlopen(API + "/review"))
names = [x["name"] for x in rv["loose_decks"]]
check("a deck the list counts as one card is reported, before the totals are trusted",
      names == ["Damage card"], names)
# ⚠️⚠️ THE NOISE TEST, and the one that matters: "26 Damage counters" has the
# SAME shape — a quantity of 26 wanting one piece — and is exactly right,
# because one design is printed twenty-six times. Flag the number rather than
# the kind and every counter in the game becomes a finding.
check("but a counter printed twenty-six times is NOT, because one is enough",
      "Damage counter" not in names, names)

# ⭐️⭐️ WHAT IS BEING CUT NOW, AND WHAT WAS ONLY UPLOADED FOR LATER. The
# designer, 25 August 2026: "I find the overall checklist % isn't very helpful
# - would be preferable to have a % completion per set of files uploaded for
# cutting... I've decided to not yet cut some pieces which belong to advanced
# rule sets that I don't want to bring in the v1 of the game."
print("")
print("a figure for each set, and the sets put by for later")
code, d = call("/wanted/import", {"text": "Advanced marker\nAdvanced tile",
                                  "group": "advanced", "group_name": "The advanced rules",
                                  "group_book": "adv-scans"})
g = d["summary"]["groups"]
check("every set carries its own figure, not just the game",
      g["core"]["pct"] == 100 and g["advanced"]["pct"] == 0,
      [g["core"]["pct"], g["advanced"]["pct"]])
check("and the game as a whole is the two of them together",
      (d["summary"]["done"], d["summary"]["total"], d["summary"]["pct"]) == (2, 4, 50),
      [d["summary"]["done"], d["summary"]["total"], d["summary"]["pct"]])

# ⚠️ ONE SWITCH, NOT TWO: this set was made FROM a box of sheets, so it
# answers to that box — putting the box by is what puts the set by.
code, d = call("/later", {"key": "book:adv-scans", "later": True})
check("a box of sheets can be put by for later", d.get("later") == ["book:adv-scans"],
      d.get("later"))
d = json.load(urllib.request.urlopen(API + "/wanted"))
s2 = d["summary"]
check("the figure is then about what is being cut now, and reads 100%",
      (s2["live_done"], s2["live_total"], s2["live_pct"]) == (2, 2, 100),
      [s2["live_done"], s2["live_total"], s2["live_pct"]])
# ⚠️ TWO NUMBERS THAT DISAGREE IN SILENCE ARE WORSE THAN ONE BLUNT ONE (fault
# 67): the whole-game reading is still there and still true, and the page says
# what the difference between them is made of.
check("while the whole game still reads 2 of 4, and says what was left out",
      (s2["pct"], s2["later_total"], s2["later_sets"]) == (50, 2, 1),
      [s2["pct"], s2["later_total"], s2["later_sets"]])
check("and nothing is hidden — the components are still on the list",
      len(d["items"]) == 4, len(d["items"]))
rv = json.load(urllib.request.urlopen(API + "/review"))
check("the end-of-job report does not count a set put by as missing",
      not [i for band in rv["sets"] for i in band["missing"]],
      [i["name"] for band in rv["sets"] for i in band["missing"]])
check("but it names the set, with what it holds, rather than dropping it in silence",
      [(x["name"], x["total"]) for x in rv["put_by"]] == [("The advanced rules", 2)],
      [(x["name"], x["total"]) for x in rv["put_by"]])
check("and its own figure is over what is being cut now",
      (rv["summary"]["accounted"], rv["summary"]["components"],
       rv["summary"]["later_components"]) == (2, 2, 2), rv["summary"])

# ⚠️ THE TEETH. Bringing the set back must put every one of those figures
# straight back to what it was, or the mark is a one-way door.
code, d = call("/later", {"key": "book:adv-scans", "later": False})
d = json.load(urllib.request.urlopen(API + "/wanted"))
s2 = d["summary"]
check("bringing it back into the cutting counts it again, at once",
      (s2["live_total"], s2["live_pct"], s2["later_total"]) == (4, 50, 0),
      [s2["live_total"], s2["live_pct"], s2["later_total"]])
rv = json.load(urllib.request.urlopen(API + "/review"))
check("and the report asks for its components again",
      sorted(i["name"] for band in rv["sets"] for i in band["missing"])
      == ["Advanced marker", "Advanced tile"],
      sorted(i["name"] for band in rv["sets"] for i in band["missing"]))
code, d = call("/later", {"key": "advanced", "later": True})
check("a mark that says neither a box nor a set is refused in a sentence",
      code == 400 and "book:" in d.get("error", ""), d)

# ⚠️ WITH NO CONTENTS LIST, EVERY PIECE IS AN ORPHAN — which is not a finding,
# it is the absence of a list. The checklist has always been optional and this
# report must not quietly make it compulsory.
code, d = call("/wanted", {"items": [], "groups": []}, method="PUT")
rv = json.load(urllib.request.urlopen(API + "/review"))
check("a game with no contents list says so, instead of listing every piece",
      rv["has_list"] is False and rv["orphans"] == [], [rv["has_list"], len(rv["orphans"])])

# ⚠️ AND THE REPORT IS SOMETHING THAT LEAVES THE ROOM, so it carries the
# notice like everything else that does (fault 22).
page = urllib.request.urlopen(API + "/review/print").read().decode()
check("the printable report carries the copyright notice",
      "copyright" in page.lower(), page[:0])
check("and does not pretend to be printed at true size, having no pictures on it",
      "25&nbsp;mm" not in page)

sys.exit(1 if bad else 0)
PY11

# ⭐️⭐️ THE THREE FILES THAT CANNOT BE REBUILT KEEP THEIR OWN HISTORY. The designer,
# 24 August 2026, after a bug of the room's own threw two components away and
# git was what got them back: "I'm afraid this means nothing to me - it needs
# to be automated if it needs to happen." A safety net somebody has to
# remember to use is not a safety net.
say "the room keeps its own copies of what cannot be rebuilt"
$PY - "$TMP" "$PORT" <<'PY12'
import json, os, sys, urllib.error, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
API = "http://127.0.0.1:%s/api/p/the-supplement" % port
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def call(path, body=None, method="POST"):
    req = urllib.request.Request(API + path, data=json.dumps(body or {}).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method=method)
    try:
        return 200, json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


def kept():
    return json.load(urllib.request.urlopen(API + "/history"))


was = len(kept()["kept"]["wanted"])
code, d = call("/wanted/import", {"text": "A thing worth keeping", "group": "core"})
after = kept()
check("saving the checklist puts the copy it replaced aside",
      len(after["kept"]["wanted"]) == was + 1,
      [was, len(after["kept"]["wanted"])])
check("and each copy says what was in it",
      "components" in (after["kept"]["wanted"][0].get("says") or ""),
      after["kept"]["wanted"][0].get("says"))

# ⚠️ THE ROOM SAVES A MOMENT AFTER EVERY EDIT, and several of those carry the
# same content. Sixty identical copies would push the real history off the end,
# which is the one thing the history exists to prevent.
now = json.load(urllib.request.urlopen(API + "/wanted"))
items = [{k: v for k, v in i.items()
          if k not in ("pieces", "guesses", "state", "need", "got")}
         for i in now["items"]]
n0 = len(kept()["kept"]["wanted"])
items[0]["where"] = "a real change"
call("/wanted", {"items": items}, method="PUT")
n1 = len(kept()["kept"]["wanted"])
check("a real change keeps the copy it replaced", n1 == n0 + 1, [n0, n1])
call("/wanted", {"items": items}, method="PUT")
call("/wanted", {"items": items}, method="PUT")
n2 = len(kept()["kept"]["wanted"])
check("but saving the same thing again keeps nothing new", n2 == n1, [n1, n2])

# ⭐️ and it can be reached without a terminal
shelf = kept()["kept"]["wanted"]
oldest = shelf[-1]["file"]
code, r = call("/history/restore", {"key": "wanted", "file": oldest})
check("a copy can be put back", code == 200 and r.get("ok"), r)
check("and the one it replaced is kept too, so that is not a one-way door either",
      len(kept()["kept"]["wanted"]) > len(shelf), len(kept()["kept"]["wanted"]))

code, no = call("/history/restore", {"key": "wanted", "file": "../../../etc/passwd"})
check("a made-up file name is refused", code == 400, no.get("error"))
code, no = call("/history/restore", {"key": "sheets", "file": "sheets-1.json"})
check("and a store that is not one of the three is refused", code == 400, no.get("error"))

# ⭐️ the outlines are the work, so they are kept as well
book = json.load(urllib.request.urlopen(
    "http://127.0.0.1:%s/api/p/proving-ground/outlines" % port))
sid = sorted(book.get("sheets") or {})[0]
rec = book["sheets"][sid]
req = urllib.request.Request(
    "http://127.0.0.1:%s/api/p/proving-ground/outlines/%s" % (port, sid),
    data=json.dumps({"pieces": rec.get("pieces") or [], "dpi": rec.get("dpi") or 0,
                     "guides": []}).encode(),
    headers={"Content-Type": "application/json"}, method="PUT")
urllib.request.urlopen(req)
theirs = json.load(urllib.request.urlopen(
    "http://127.0.0.1:%s/api/p/proving-ground/history" % port))
check("the outlines are kept the same way, being the one thing nothing can rebuild",
      len(theirs["kept"]["outlines"]) >= 1,
      len(theirs["kept"]["outlines"]))

# ⚠️ THE ROOM HOLDS ITS OWN DOOR SHUT FOR THREE SECONDS AFTER A SAVE — that is
# fault 21, and it is right to. This block has just saved some outlines, so
# wait for that window to pass or the closing checks at the end of the run
# find a room that quite correctly refuses to close.
import time
time.sleep(3.5)

sys.exit(1 if bad else 0)
PY12

# ------------------------------------------------------ taking it away
# ⭐️ The way out has to be plain, and it has to carry the warning. The designer, 22
# August 2026: "the cutting tool should remain relatively generic"; and "some
# kind of warning that this is personal use, copyright in all things you cut is
# not your own — a real disclaimer."
say "taking the pieces out of the room"
curl -s -o "$TMP/export.json" -X POST -H "Content-Type: application/json" -d "{}" \
     "http://127.0.0.1:$PORT/api/p/proving-ground/export"
$PY - "$TMP" "$PORT" <<'PY5' || code=1
import csv, json, os, sys, time, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
jid = json.load(open(os.path.join(tmp, "export.json")))["id"]
for _ in range(120):
    time.sleep(0.25)
    st = json.load(urllib.request.urlopen("http://127.0.0.1:%s/api/jobs/%s" % (port, jid)))
    if st["state"] != "running":
        break
bad = []
def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % saw if saw != "" else ""))
    if not ok:
        bad.append(what)

check("the export finishes", st["state"] == "done", st.get("error") or st["state"])
root = (st.get("result") or {}).get("folder") or os.path.join(tmp, "home", "proving-ground", "export")
want = ["README.txt", "COPYRIGHT.txt", "inventory.csv", "inventory.json",
        "contact-sheet.html"]
missing = [f for f in want if not os.path.exists(os.path.join(root, f))]
check("the folder explains itself and carries the notice", not missing, missing or "all there")

# ⭐️ named by WHAT IT IS, and the turn baked in — the cut PNG never has it
pieces = sorted(f for f in os.listdir(os.path.join(root, "pieces")) if f.endswith(".png"))
check("the piece is named by what it is, not by where it was cut",
      pieces == ["a-piece-on-its-side.png"], pieces)

rows = list(csv.DictReader(open(os.path.join(root, "inventory.csv"))))
check("the spreadsheet has a row for it", len(rows) == 1, len(rows))
r = rows[0] if rows else {}
check("with its size in inches AND millimetres",
      bool(r.get("width_in")) and bool(r.get("width_mm")),
      {k: r.get(k) for k in ("width_in", "height_in", "width_mm", "height_mm")})
# the cut piece measured 1.51 x 1.43in; a quarter turn swaps them
check("and the turn is baked into what leaves the room",
      abs(float(r.get("width_in", 0)) - 1.43) < 0.03
      and abs(float(r.get("height_in", 0)) - 1.51) < 0.03,
      "%s x %s in" % (r.get("width_in"), r.get("height_in")))

# ⚠️ Collapse the whitespace first: the notice is wrapped for a text file, so
# a sentence that reads as one line may be two, and a check that does not
# allow for it goes red over a line break rather than over the meaning.
notice = " ".join(open(os.path.join(root, "COPYRIGHT.txt")).read().split())
check("the copyright notice says the important part in plain words",
      "NOTHING IN THIS FOLDER IS YOURS TO GIVE AWAY" in notice
      and "Do NOT put these pieces on the internet" in notice
      and "not legal advice" in notice)
check("and the README carries it too", "ABOUT COPYRIGHT" in open(os.path.join(root, "README.txt")).read())

# ⭐️⭐️ THE CHECK TRAVELS WITH THE PIECES. It is the last thing read before
# they leave the room, so it is no use only on a screen: the folder gets copied
# about. Twice over — once to read and print, once for a program, because
# whatever ingests these pieces wants the room's own account of what is missing
# rather than working it out again from the inventory.
for f in ("check-against-the-list.html", "check-against-the-list.json"):
    check("the check against the contents list goes into the folder: " + f,
          os.path.exists(os.path.join(root, f)))
rvj = json.load(open(os.path.join(root, "check-against-the-list.json")))
check("and the machine-readable one says which game it is about, and what it found",
      "game" in rvj and "summary" in rvj and "orphans" in rvj,
      sorted(rvj.keys()))
check("and the README names it, so nobody has to find it by accident",
      "check-against-the-list.html" in open(os.path.join(root, "README.txt")).read())
sheet = open(os.path.join(root, "contact-sheet.html")).read()
check("and so does the foot of every page meant to be printed",
      "somebody else&#x27;s copyright" in sheet or "somebody else's copyright" in sheet)
check("the contact sheet carries a ruler to catch a scaled printout", "25&nbsp;mm" in sheet)

# every sheet with outlines on it gets a cut file, and by now the browser has
# outlined a second one by laying a kept shape down on it — so name the sheet
# this checks rather than counting the folder
svgs = sorted(f for f in os.listdir(os.path.join(root, "laser")) if f.endswith(".svg"))
want = "proving-ground-sheets-01-cut.svg"
check("there is a cut file for each outlined sheet", want in svgs, svgs)
if want in svgs:
    svg = open(os.path.join(root, "laser", want)).read()
    # the demo sheet is 1800x2400 at 300dpi = 6x8 inches = 152.4 x 203.2 mm
    check("in millimetres, at the sheet's true size",
          'width="152.400mm"' in svg and 'height="203.200mm"' in svg,
          svg.split("width=")[1][:40] if "width=" in svg else svg[:60])
    check("with one closed path per piece", svg.count("<path ") == 1, svg.count("<path "))
sys.exit(1 if bad else 0)
PY5

# ------------------------------------------ closing the room, from the room
# Last of all, because it stops the server this whole section is talking to.
# ⚠️ The room must NOT close over the top of an edit that has not reached the
# disk. That is fault 1 by another door: the work is on disk or it is not
# work. So a table holding an unsaved edit is asked about, not overruled.
# ------------------------------------------- the room offering a kind
# ⭐️ the designer, 22 August 2026: "naming is always going to be the fiddly bit here
# as it will tend to rely on 3rd party lists etc." The measurement rules
# themselves are checked above without a browser; what is checked here is that
# the guess actually REACHES the page, and that accepting one writes to disk
# and cannot tread on an answer somebody has already given.
say "does the guess reach the page, and does accepting it stick?"
$PY - "$TMP" "$PORT" <<'PY6' || code=1
import json, os, sys, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
room = "http://127.0.0.1:%s" % port
bad = []


def check(what, right, saw=None):
    print(("  ok   " if right else "  WRONG ") + what +
          ("" if saw is None else "   — saw " + json.dumps(saw, ensure_ascii=False)))
    if not right:
        bad.append(what)


def get(where):
    return json.load(urllib.request.urlopen(room + where))


def post(where, body):
    req = urllib.request.Request(room + where, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


# ⚠️ The one piece the browser cut is an inch and a half square, which is a
# shape the room deliberately refuses to guess about. So this block brings its
# own counter, and takes it away again at the end.
import shutil
spare = tmp + "/home/proving-ground/pieces/zz_a_counter.png"
shutil.copyfile(tmp + "/a-counter.png", spare)
d = get("/api/p/proving-ground/pieces")
pieces = d["pieces"]
# start from a clean slate whatever the browser left behind, so this block
# says the same thing whether or not the browser checks ran before it
for p in pieces:
    if (p.get("data") or {}).get("kind"):
        urllib.request.urlopen(urllib.request.Request(
            room + "/api/p/proving-ground/manifest/" + p["stem"],
            json.dumps({"kind": ""}).encode(),
            {"Content-Type": "application/json"}, method="PUT"))
guessed = [p for p in pieces if p.get("guess")]
check("a measured piece is served with a kind offered for it",
      len(guessed) >= 1, [(p["stem"], p["guess"]["kind"]) for p in guessed])
if guessed:
    g = guessed[0]["guess"]
    check("and the offer says what it was made from, in inches",
          "in" in g.get("why", ""), g.get("why"))
    check("and the kind it offers is one the Kind box actually holds",
          g["kind"] in d["kinds"], g["kind"])
    stem = guessed[0]["stem"]
    r = post("/api/p/proving-ground/pieces/kind", {"stems": [stem], "kind": g["kind"]})
    check("accepting it sets the kind", r.get("set") == 1, r)
    man = json.load(open(tmp + "/home/proving-ground/manifest.json"))
    check("and the kind is on the piece in the manifest on disk",
          man["pieces"].get(stem, {}).get("kind") == g["kind"],
          man["pieces"].get(stem, {}))
    # ⚠️ THIS IS THE ONE THAT MATTERS. It is a bulk action: a mistake here is
    # spread over every piece in a game before anybody notices it. The room
    # fills a blank and never overwrites an answer.
    again = post("/api/p/proving-ground/pieces/kind", {"stems": [stem], "kind": "board"})
    man = json.load(open(tmp + "/home/proving-ground/manifest.json"))
    check("but it will not tread on a kind already set",
          again.get("set") == 0 and man["pieces"][stem]["kind"] == g["kind"],
          man["pieces"][stem]["kind"])
    check("a piece with a kind is no longer asked about",
          not [p for p in get("/api/p/proving-ground/pieces")["pieces"]
               if p["stem"] == stem and not (p.get("data") or {}).get("kind")])
    urllib.request.urlopen(urllib.request.Request(
        room + "/api/p/proving-ground/manifest/" + stem,
        json.dumps({"kind": ""}).encode(),
        {"Content-Type": "application/json"}, method="PUT"))
check("and the shape that settles nothing is passed over in silence",
      not [p for p in pieces if p["stem"] != "zz_a_counter" and p.get("guess")],
      [[p["w_in"], p["h_in"]] for p in pieces if p["stem"] != "zz_a_counter"])
os.remove(spare)
sys.exit(1 if bad else 0)
PY6

# ⭐️⭐️ A WHOLE BOX OF SHEETS OUT AGAIN, IN ONE PRESS. The designer, 25 August
# 2026: "I'd like to be able to remove a full set of imported sheets in one
# click (after a confirmation). The [two of these books] are irrelevant here."
# ⚠️ This is the one thing in the room that really deletes, so what it must
# NOT do is most of what is checked here.
say "taking a whole box of sheets out of a game"
$PY - "$TMP" "$PORT" <<'PY15' || code=1
import json, os, sys, urllib.error, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
API = "http://127.0.0.1:%s/api/p/the-spare-room" % port
bed = os.path.join(tmp, "home", "the-spare-room")
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def get():
    return json.load(urllib.request.urlopen(API))


def drop(book, pieces=False):
    req = urllib.request.Request(API + "/book/" + book + ("?pieces=1" if pieces else ""),
                                 method="DELETE")
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return json.load(e)


def book_of(sid):
    return sid.rsplit("-", 1)[0]


was = get()
check("the game has the two boxes this check is about",
      len([s for s in was["sheets"] if book_of(s["id"]) == "throwaways"]) == 3 and
      len([s for s in was["sheets"] if book_of(s["id"]) == "keepers"]) == 2,
      [s["id"] for s in was["sheets"]])
gone = drop("throwaways")
check("a whole box goes in one call, and says what went",
      gone.get("sheets") == 3 and gone.get("outlines") == 2, json.dumps(gone))
now = get()
check("and only that box went",
      not [s for s in now["sheets"] if book_of(s["id"]) == "throwaways"] and
      len([s for s in now["sheets"] if book_of(s["id"]) == "keepers"]) == 2,
      [s["id"] for s in now["sheets"]])
check("its scans are off the disk too, not left lying about",
      not any(f.startswith("throwaways") for f in os.listdir(os.path.join(bed, "sheets"))),
      sorted(os.listdir(os.path.join(bed, "sheets"))))
book = json.load(open(os.path.join(bed, "outlines.json")))
check("and the outlines drawn on them are out of the outline file",
      "throwaways-01" not in (book.get("sheets") or {}), sorted(book.get("sheets") or {}))
# ⭐️⭐️ AND THE WORK IS STILL RECOVERABLE, which is the only reason this is
# safe enough to offer at all: outlines.json is one of the three stores the
# room keeps its own copies of (fault 49), so the outlines survive a box
# removed by mistake even though the scans have to be imported again.
kept = json.load(urllib.request.urlopen(API + "/history"))
outs = (kept.get("kept") or {}).get("outlines") or []
check("the outlines that went are still in the room's own history",
      any("2 outlines" in (c.get("says") or "") for c in outs),
      [c.get("says") for c in outs])
# ⚠️ and a box that is not there is a plain answer, not a stack trace
check("a box the game does not have is refused in a sentence",
      "no such" in (drop("no-such-book").get("error") or ""), drop("no-such-book"))
sys.exit(1 if bad else 0)
PY15

# ⭐️⭐️ WHAT A BOX OF SHEETS IS CALLED. The designer, 25 August 2026: "Ability to
# rename imported sections... I need to rename them from their current file
# names (which are lots of nonsense)." A sheet id is made from the file it
# arrived in, and the box is that id with the page number taken off — so a
# game imported from a folder of scans is called whatever the scanner called
# it, everywhere in the room.
say "naming a box of sheets, without renaming anything underneath it"
$PY - "$PORT" <<'PY14' || code=1
import json, sys, urllib.request
port = sys.argv[1]
API = "http://127.0.0.1:%s/api/p/proving-ground" % port
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def get():
    return json.load(urllib.request.urlopen(API))


def name_it(book, name):
    req = urllib.request.Request(API + "/book/" + book, json.dumps({"name": name}).encode(),
                                 {"Content-Type": "application/json"}, method="POST")
    return json.load(urllib.request.urlopen(req))


def sheets_of(d, book):
    return [s for s in d["sheets"] if s["id"].startswith(book + "-")]


was = sheets_of(get(), "second-book-of-tests")
name_it("second-book-of-tests", "The Second Box")
now = get()
check("a box of sheets can be given a name of its own",
      (now.get("books") or {}).get("second-book-of-tests") == "The Second Box",
      now.get("books"))
mine = sheets_of(now, "second-book-of-tests")
check("and every sheet in it is called by it, page numbers kept",
      all(s["label"].startswith("The Second Box p.") for s in mine),
      [s["label"] for s in mine[:3]])
check("while the sheets in the other boxes are left alone",
      all(not s["label"].startswith("The Second Box")
          for s in now["sheets"] if not s["id"].startswith("second-book-of-tests-")),
      [s["label"] for s in now["sheets"][:2]])
# ⚠️⚠️ THE ID IS NEVER TOUCHED. A piece is named from its sheet's id, the
# outlines are filed under it, and a game reading the manifest knows pieces by
# it. A name is a label; renaming what other things are keyed by loses work.
check("and not one sheet id changed, which is what pieces are named from",
      [s["id"] for s in mine] == [s["id"] for s in was],
      [s["id"] for s in mine[:3]])
# ⚠️ and a label somebody typed themselves is not the file's name, so it stays
req = urllib.request.Request(API + "/sheet/second-book-of-tests-01",
                             json.dumps({"label": "The one with the map on it"}).encode(),
                             {"Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req)
after = [s for s in get()["sheets"] if s["id"] == "second-book-of-tests-01"][0]
check("a label somebody typed themselves is left exactly as it was",
      after["label"] == "The one with the map on it", after["label"])
# and it all goes back
name_it("second-book-of-tests", "")
back = get()
check("emptying the name puts every sheet back to its own file name",
      all(s["label"].startswith("second-book-of-tests")
          for s in sheets_of(back, "second-book-of-tests")
          if s["id"] != "second-book-of-tests-01"),
      [s["label"] for s in sheets_of(back, "second-book-of-tests")[:3]])
req = urllib.request.Request(API + "/sheet/second-book-of-tests-01",
                             json.dumps({"label": "second-book-of-tests p.1"}).encode(),
                             {"Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req)
sys.exit(1 if bad else 0)
PY14

# ⭐️⭐️ STARTING THE ROOM AGAIN, FROM THE ROOM. The designer, 24 August 2026: "is
# there a way to build a relaunch button into the browser tab it uses
# somehow?" — having been told twice in a day to close the room and open it
# again because it was running older code than its own pages. The room stops
# and starts itself in place: same window, same port, same command, NEW
# process. This runs before the closing section, which then closes the room
# that came back.
say "starting the room again, from the room"
$PY - "$TMP" "$PORT" <<'PY12' || code=1
import json, os, sys, time, urllib.error, urllib.request
tmp, port = sys.argv[1], sys.argv[2]
room = "http://127.0.0.1:%s" % port
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


def post(where, body=None):
    req = urllib.request.Request(room + where, json.dumps(body or {}).encode(),
                                 {"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        return json.load(e)


def get(where):
    return json.load(urllib.request.urlopen(room + where, timeout=4))


# ⚠️⚠️ A RESTART IS A CLOSE WITH A PROMISE ATTACHED, so it answers to the same
# guard: an edit not yet written down holds this door exactly as it holds the
# other one. Two guards would drift apart, and the one that drifted would be
# the one that lost the work.
post("/api/at-the-table", {"tab": "check-again", "project": "proving-ground",
                           "name": "The Proving Ground",
                           "sheet": "proving-ground-sheets-01",
                           "label": "proving-ground-sheets p.1", "dirty": True})
held = post("/api/relaunch")
check("an edit not yet written down holds the restart, as it holds the close",
      held.get("relaunching") is False and held.get("hold") is True, json.dumps(held))
check("and the room is still running, having refused",
      get("/api/health").get("ok") is True)
post("/api/at-the-table", {"tab": "check-again", "gone": True})

was = get("/api/health")["started"]
said = post("/api/relaunch")
check("with nothing in flight, the room says it is starting again",
      said.get("relaunching") is True and said.get("was") == was, json.dumps(said))
# ⚠️ IT IS A DIFFERENT ROOM OR IT IS NOTHING — the old one answers perfectly
# well for the half second before it goes, so "it answers" proves nothing.
now, waited = None, 0.0
while waited < 40:
    time.sleep(0.5)
    waited += 0.5
    try:
        now = get("/api/health")
    except Exception:
        continue                      # between the two rooms
    if now.get("started") and now["started"] != was:
        break
check("and a NEW room answers on the same address, by itself",
      bool(now) and now.get("started") not in (None, was),
      "%s -> %s after %ss" % (was, (now or {}).get("started"), waited))
check("with the same projects in it as before",
      any(p["id"] == "proving-ground" for p in get("/api/projects")["projects"]))
sys.exit(1 if bad else 0)
PY12

# ⚠️⚠️ A RELAUNCH THAT CANNOT COME BACK IS A QUIT. The button is pressed after
# the code has changed, which is exactly when the code might not parse — and
# there is nothing to fall back to once the old process has gone. So the new
# code is read before anything is stopped. No server here: it is one function
# and a folder with a broken file in it.
$PY - "$TMP" <<'PY13' || code=1
import json, os, sys
sys.path.insert(0, ".")
import cutting_room as c
bad = []


def check(what, ok, saw=""):
    print(("  ok   " if ok else "  WRONG ") + what + ("   — saw %s" % (saw,) if saw != "" else ""))
    if not ok:
        bad.append(what)


check("the code on the disk now would start, so the room would come back",
      c.code_that_will_not_start() is None, c.code_that_will_not_start())
was = c.HERE
try:
    pretend = os.path.join(sys.argv[1], "brokenroom")
    os.makedirs(pretend, exist_ok=True)
    for f in ("cutting_room.py", "sheets.py", "cut.py"):
        open(os.path.join(pretend, f), "w").write("def half_a_thing(:\n")
    c.HERE = pretend
    said = c.code_that_will_not_start()
finally:
    c.HERE = was
check("and code that would NOT start is refused before the room lets go",
      bool(said) and "cutting_room.py" in said, said)
sys.exit(1 if bad else 0)
PY13

say "closing the room, from the room"
hello() {
  curl -s -o /dev/null -X POST -H "Content-Type: application/json" -d "$1" \
       "http://127.0.0.1:$PORT/api/at-the-table"
}
hello '{"tab":"check-1","project":"proving-ground","name":"The Proving Ground","sheet":"proving-ground-sheets-01","label":"proving-ground-sheets p.1","dirty":true}'
curl -s -o "$TMP/close-held.json" -X POST -H "Content-Type: application/json" -d "{}" \
     "http://127.0.0.1:$PORT/api/close"
$PY - "$TMP/close-held.json" <<'PY3' || code=1
import json, sys
d = json.load(open(sys.argv[1]))
held = d.get("closed") is False and d.get("hold") is True
said = any("written down" in r.get("what", "") for r in d.get("reasons", []))
print(("  ok   " if held else "  WRONG ") + "an edit not yet written down holds the door shut")
print(("  ok   " if said else "  WRONG ") + "and the room says which sheet it is waiting for   — saw %s"
      % json.dumps([r.get("what") for r in d.get("reasons", [])]))
sys.exit(0 if (held and said) else 1)
PY3
if curl -s -o /dev/null --max-time 4 "http://127.0.0.1:$PORT/api/projects"; then
  echo "  ok   and the room is still open"
else
  echo "  WRONG the room closed anyway"; code=1
fi
# the tab goes away, and the door is free
hello '{"tab":"check-1","gone":true}'
curl -s -o "$TMP/close-done.json" -X POST -H "Content-Type: application/json" -d "{}" \
     "http://127.0.0.1:$PORT/api/close"
$PY - "$TMP/close-done.json" <<'PY4' || code=1
import json, sys
d = json.load(open(sys.argv[1]))
ok = d.get("closed") is True and bool(d.get("how"))
print(("  ok   " if ok else "  WRONG ") + "with the table shut, the room closes and says how to open it again   — saw %s"
      % json.dumps(d.get("how")))
sys.exit(0 if ok else 1)
PY4
i=0
gone=0
while [ $i -lt 20 ]; do
  if ! curl -s -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/api/projects"; then gone=1; break; fi
  sleep 0.5
  i=$((i + 1))
done
if [ $gone -eq 1 ]; then
  echo "  ok   the room really stopped — nothing is listening on $PORT"
else
  echo "  WRONG the room said it closed but is still listening"; code=1
fi

if [ $code -eq 0 ]; then
  printf "\n\033[32mall the room's own checks came out right too\033[0m\n"
fi
exit $code
