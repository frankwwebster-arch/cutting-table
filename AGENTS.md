# The Cutting Room / Cutting Table — project guide for Codex

**One tool, two ways in.** `cutting_room.py` is a local web app — the whole
workshop, from importing a game's scans to knowing what is still to cut.
`cutting_table.py` bakes the same editor into a single self-contained HTML file
that works offline from a `file://` URL. The editor itself,
`cutting_table.tpl.html`, is shared by both and must stay that way.

**Public, MIT.** github.com/frankwwebster-arch/cutting-table. It grew out of
one game's own project and is deliberately
separate from it: nothing here knows about any particular game.

⚠️⚠️ **KEEP IT GENERIC. This is the constraint on everything.** Frank, 22
August 2026: *"the cutting tool should remain relatively generic — not every
user is going to be building their own version of [a game] to play on a computer!
Output format is important."* The room's product is **a folder of named,
measured, transparent-background component pictures with an inventory beside
them** — and that is wanted by far more people than the one building a game
engine: Tabletop Simulator and Tabletopia mods, VASSAL modules, reprinting a
missing counter at true size, cutting replacement chipboard on a craft cutter,
archiving an out-of-print box. **Any step shaped like a particular game belongs
in that game's own repository**, the way a game's hand-over scripts do.
When a feature could be built either here or there, it goes there.

---

## Working with Frank

- Frank is the user and the designer, and is **not a programmer**. Codex makes
  every engineering decision. Explain what a change does, never how it is
  coded, unless he asks.
- **His eye is the instrument.** He has caught more real faults from looking at
  the thing than any check has: the outlines that never left the browser, the
  cut pieces missing from the sheet thumbnails, the page margins being trimmed
  off, and the editor stealing his typing. When he says something looks wrong,
  it is wrong.
- Git: commit and push after each verified chunk, without being asked. Plain
  English messages that say what was wrong and why the fix is the fix.
- ⚠️ **This repository is PUBLIC and holds the TOOL ONLY.** Never commit a
  game's sheets, a baked HTML page (the sheets are inside it), a cut piece, or
  anything out of a `Cutting Room` project folder. `.gitignore` is written to
  keep them out and should stay that way.
- **Keep these documents current, every session:**
  - `ROOM.md` — the manual, written for somebody who has never seen it.
  - `BACKLOG.md` — the live list: what is done, what is next, what is known
    to be missing.
  - `README.md` — the public front page. It is what a stranger reads first.
  - `AGENTS.md` — this file.

---

## Status (24 August 2026)

The room is **built and in daily use** on two games, and 24 August was a day of
Frank cutting a real game with it and saying what was wrong — fifteen separate
pieces of work, most of them his words verbatim in the faults below. One
game: 161 sheets, **221 components on the checklist**, cards and counters being
cut and named in earnest. Another: 21 sheets imported.

⭐️ **What that day was mostly about**: a game is not a heap of sheets, it is a
**box and its supplements**, and the room kept making him work a sheet at a
time. Sheets, Pieces, Match and the Checklist all group by box now, all fold,
and all remember. See faults 37, 41 and 42 — the same complaint arriving three
times because the first two fixes were made where it was reported rather than
where it belonged.

⚠️⚠️ **And the day's hard lesson: the room lost two of his components.** A
stale row handler removed the wrong one (fault 45), and what got them back was
git, which he does not use. Everything that cannot be rebuilt now keeps its own
history (fault 49). *Read fault 45 before touching any list that saves as you
type.*

⭐️ **What is expensive is naming, not cutting.** Frank, having cut a sheet:
*"naming is always going to be the fiddly bit here as it will tend to rely on
3rd party lists etc, or rules manuals which may be tricky to comprehend."* The
room cuts a sheet in one press; what a piece is *called* comes from outside it.
Weigh any future work against that: a feature that removes a step from naming
is worth more than one that speeds up cutting.

⭐️⭐️ **KEEP IT GENERIC — the constraint on everything.** See the top of this
file. The room's product is a plain folder of named, measured pictures, and
step 6 (*Take it away*) is what proves it. Anything shaped like a particular
game belongs in that game's own repository.

**Next up, in this order** — and BACKLOG's *NOW* is the live list:

1. ⭐️⭐️ **Check the cut against the contents list, at the end.** Frank asked
   for it by name on 24 August: a report, read once before the pieces leave
   the room, saying what is missing, what is half-done, and — the part the
   room cannot do at all yet — **which cut pieces answer to nothing on the
   list**. The shape of the work is written out in BACKLOG.
2. ⭐️ **A user guide, written properly.** There is a first cut of one, made
   from this day's work; BACKLOG says what it should become.
3. **A lighter ground** — *"I'd like to consider some different displays (eg
   white background rather than the black)."* Read the reason the ground is
   dark before changing it; it is written in the editor's `:root` block.
4. **No terminal window at all** — a minimal `.app` bundle. All that is left
   of *"a simpler way to open and quit"*.

Built that day, in order:

1. **The room itself** — projects, import, the served editor, cut, name, and
   the checklist.
2. **Match** — drag a component's name onto the piece it is.
3. **The UX pass** — five steps across the top, sheet filters and search, a
   first-run welcome, a proper empty state for the checklist.
4. **Post-cut review** — flags, look-alikes, keep-one-bin-the-rest.
5. **Drag and drop** — the whole window, and whole folders.

**22 August**, first thing: *"it now runs VERY slowly when manipulating a
sheet when cutting, all jerky. COMPLETELY unusable."* He was right, and it
was not subtle — during a two-second drag the browser painted **one frame**.
Two faults, both of which only show at the size of a real game; they are
numbers 11 and 12 below. It paints 120 frames in the same drag now. There is
a `check/check.sh` since, which goes red on both if they ever come back.

**Later the same day**, Frank cut with it for real and sent back five things,
all of which were right and all of which are fixed: a phantom error on every
drag in Match, a turn that did not turn the thumbnail beside it, a NAME field
that looked redundant because the two ways of setting it disagreed, counts
that never moved as he worked, and — the interesting one — the look-alike
finder proposing to bin the second Wizard Marker card. **Similar is not the
same as duplicate**; see fault 18. Chasing the re-cut test he had asked for
turned up a name that could lie in wait for the next piece cut in its place,
and writing the message about *that* re-broke the whole editor twice over in
the way fault 6 warns about.

---

## ⚠️ The faults that shaped it — do not undo these

Every one of these was real, and most were found by *looking at the thing*
rather than by reading the code.

1. ⚠️⚠️ **THE WORK WAS IN THE BROWSER.** The baked Cutting Table kept outlines
   in `localStorage` and the only way out was a *Save a copy* button nobody had
   told Frank about. He outlined four sheets; they never reached the game and
   had to be read back out of Chrome's LevelDB by hand.
   **The room saves to the project a moment after every edit.** The browser's
   copy is the backup now, not the original. *Never reintroduce a
   browser-only store.*
2. ⌨️ **TYPING IS NOT A SHORTCUT.** The editor's single-key tools are bound to
   the window and the rail has a name box on it, so typing a piece's name went
   Rectangle, Ellipse, Adjust, Outline on the way past and Backspace deleted a
   node. `typing(ev)` in `cutting_table.tpl.html` stands the shortcuts down
   inside any field. *Any new global key handler needs the same guard.*
3. 🖼 **A CSS GRID WITH A `max-height` SIZES ITS OWN ROWS TO FIT IT.** 70px rows
   for 193px cells, every piece clipped to a coloured band. `grid-auto-rows:
   max-content`. Two wrong guesses preceded measuring it in the browser.
4. 🖼 **A PERCENTAGE `max-height` AGAINST AN `aspect-ratio` HEIGHT MAY NOT
   RESOLVE**, so a thumbnail was sized by width alone and every portrait sheet
   lost its foot. `object-fit: contain`.
5. 🖼 **A FLEX COLUMN ALWAYS HAS A SHRINKABLE CHILD.** Pin the picture and the
   caption vanishes; pin the caption and the picture collapses. Block flow has
   no such problem and the cells use it.
6. 🔤 **AN UNTERMINATED STRING KILLS THE WHOLE PAGE**, silently, with a working
   server behind it. Extract the `<script>` and `node --check` it after every
   edit — the one-liner is in *Verifying* below.
7. 🧮 **A LOOK-ALIKE HASH NEEDS COLOUR.** At 8×8 grey it called NO MOVEMENT and
   NO FIRING the same counter. 12×12 (144 bits) **plus** mean RGB, and all
   three of size, pattern and colour must agree.
8. 📄 **ONE `pdftoppm` RUN, NOT ONE PER PAGE.** A page at a time re-parses a
   twenty-megabyte book every time — ten seconds a page. One run, and count
   the files as they land for progress.
9. 🌐 **A PRIVATE DRIVE LINK RETURNS A SIGN-IN PAGE WITH HTTP 200**, which
   would otherwise be filed as a perfectly valid, perfectly useless HTML
   sheet. Refuse an HTML answer to a request for a document.
10. 📁 **`readEntries()` RETURNS AT MOST 100 ENTRIES** and must be called until
    it returns none, or a dropped folder of 200 scans silently imports 100.
11. ⚠️⚠️ 🖼 **A GRID COLUMN SIZES ITSELF TO ITS WIDEST CONTENT AND WILL NOT GO
    BELOW IT.** `.shell` was `display: grid` with its column left implicit.
    The sheet rail puts one tab per sheet in a row; at 161 sheets that row is
    **sixteen thousand pixels wide** — so the column was, so every row of the
    page was, so the stage was, **and the canvas takes its size from the
    stage**. A window showing 1200 pixels was clearing and repainting a
    16111 × 861 picture on every twitch of the hand: 55MB a frame, one frame
    in two seconds, and the piece ledger shoved off the side of the screen
    where Frank could not see it at all. The fix is *one line* —
    `grid-template-columns: minmax(0, 1fr)`. Any flex or grid child holding a
    list that can grow needs `min-width: 0` or the same treatment.
12. 🖼 **A SHEET'S PICTURE IS FETCHED WHEN IT REACHES THE TABLE, NOT AT LOAD.**
    The editor armed `new Image()` for every sheet the moment the page
    opened. Fine for the four sheets a baked page carries, ruinous for 161:
    147MB down the wire and **seven gigabytes** of unpacked pixels asked of
    the browser. `armSheet()` holds three at a time — the one being worked on
    and the two before it. *Never go back to arming them all.*

13. ⚠️ **THE SERVED EDITOR IS NOT THE TEMPLATE, AND ONLY THE TEMPLATE WAS
    BEING PARSED.** `TABLE_PATCHES` splices Python string literals into the
    editor, and **Python unescapes them before the page ever sees them** — so
    a `\n` written for JavaScript arrives as a REAL newline, ends the string
    it is in, and kills the whole editor silently with a working server behind
    it. That is fault 6 by a door it had not used before: the template on disk
    parsed perfectly the entire time. It bit twice in five minutes — once in
    the message being written, and once in the comment warning about it.
    *Write no backslash escapes inside `TABLE_PATCHES`,* and `check.sh` now
    parses what the room actually **serves**.
14. 🖼 **THREE OF FOUR HANDLERS ASKED; THE FOURTH DID NOT.** The whole window
    is a file-drop target so a dropped PDF cannot navigate the page away.
    `dragenter`, `dragover` and `dragleave` all checked that the drag carried
    **Files**; `drop` did not. So dragging a component's name onto a piece —
    one thing on the page onto another — was taken for a file import, found no
    files, and complained, *after* the link had been made. Frank: *"always
    seems to serve an error code (even though it also appears to work!)"*.
    A guard that some of a set of handlers share is a guard that will be
    forgotten by one of them.
15. 🖼 **A ROTATION LIVES IN THE MANIFEST, SO EVERY PICTURE MUST APPLY IT.**
    The cut PNG is never rewritten — a re-cut and the look-alike hash both
    depend on the file being exactly what came off the sheet. Four places draw
    a piece; two applied the turn and two did not, so turning a piece turned
    the big picture and not the row beside it, and Frank did it again thinking
    it had been refused. They go through one function now. *A quarter turn
    also swaps width and height*, so a turned picture must be held to the
    shorter side of its box or it is clipped.
16. 🧮 **TWO WAYS IN MUST DO THE SAME THING.** Dragging a component onto a
    piece filled its name in; choosing the same component from the dropdown
    did not. A piece linked that way read "(unnamed)" everywhere and step 4
    counted it as still to do for ever. Frank: *"NAME seems redundant?"* —
    it was not redundant, the two routes simply disagreed.
17. ⏱ **A COUNT WORKED OUT BY THE SERVER IS STALE THE MOMENT YOU CHANGE
    ANYTHING.** The five steps and their counts were read once at load, so
    naming a piece left "6 of 7 named" sitting there. Same complaint as the
    thumbnail that would not turn: *the screen does not show what you just
    did, so you doubt it took and do it again.*
18. 🎴 **SIMILAR IS NOT THE SAME AS DUPLICATE.** The look-alike finder knew
    two answers — bin the spares, or unrelated — and one game has two wizard
    marker cards (one per player) and twelve ship templates differing only in
    the fleet's flag. Those are **designs of one component** and all of them
    are wanted. There is a third answer now, and the mark lives on the piece
    so it survives a re-cut.

19. ⚠️ **NOTHING IN THE ROOM DELETES A CUT PIECE.** Frank: *"Binning a piece
    shouldn't be destructive — it should be merely to hide a piece from the
    main manifest. eg there are two identical ice fields. The game only needs
    to store one, even though it could be placed twice in an actual game."*
    A piece is **set aside**: moved to `pieces/spare/`, its manifest entry kept
    and marked `spare`. ⭐️ **The move is the whole mechanism** — anything
    reading the store globs the folder and does not recurse, so a spare is
    invisible to it without the room having to know anything about who is
    reading, which is the separation this repository is built on. The mark
    follows the piece across a re-cut exactly as a name does, or every re-cut
    would hand the game back the duplicates you had just put away. *Only
    deleting a whole sheet deletes pieces, and it says so.*

20. ⚠️⚠️ 🌐 **A POST THAT DOES NOT READ ITS BODY POISONS THE NEXT REQUEST.**
    The browser keeps one connection and sends request after request down it.
    *Cut this sheet* posts `{}` and the cut handler never read it, so those two
    bytes stayed in the socket and the **next** request on that connection was
    read starting from them: the room saw the request line `{}GET /p/...` and
    answered **501 Unsupported method**. Frank would have seen the project page
    come up blank after a cut, at random, depending on which connection the
    browser happened to reuse.
    ⭐️ **It had been there all along and could not be seen**, because
    `log_message()` **crashed on the very error it was reporting** —
    `send_error` logs an `HTTPStatus`, not a string, and `"/api/" in
    HTTPStatus` raises. The crash killed the connection, so the browser quietly
    tried again on a clean one and it all appeared to work. Fixing the logger
    is what made the fault visible; `check.sh` went red on the Match board
    within the minute.
    The fix is **fault 14's lesson again** — a guard only *some* of a set of
    handlers remember is a guard one of them will forget — so reading the body
    is no longer each handler's job. `route()` reads it once, for every
    request, wanted or not. *Never read `self.rfile` in a handler.*

21. ⚠️ **CLOSING THE ROOM IS FAULT 1 BY ANOTHER DOOR.** The room saves a moment
    after every edit, so stopping the server at the wrong moment throws that
    moment away. The room can see its own jobs but **cannot see a browser
    tab**, so every open cutting table says hello every eight seconds and says
    whether it is holding an edit not yet written down. `/api/close` names what
    is in flight and refuses until the person says otherwise. *A quit that does
    not ask is a quit that loses work.*

22. ⚠️⚠️ **WHAT LEAVES THE ROOM IS SOMEBODY ELSE'S WORK.** Frank, 22 August
    2026: *"some kind of warning that this is personal use, copyright in all
    things you cut is not your own — a real disclaimer. Don't share cut pieces
    etc etc."* Up to the export the pieces sit in one person's folder; after
    it they are a tidy, named, portable set that is trivially easy to put
    somewhere public without thinking about it. So the notice **travels with
    the folder** — in its README, in a `COPYRIGHT.txt` of its own because a
    README is the first thing anybody stops reading, and at the foot of every
    page meant to be printed — as well as being stated plainly above the
    button. `COPYRIGHT_NOTICE` in `cutting_room.py` is the one wording;
    `check.sh` checks all three places carry it. *Never let a new way out of
    the room be built without it.*

23. 🖼 **`hidden` DOES NOT HIDE A BUTTON.** `button, .btn` set `display:
    inline-block`, and a plain `display` rule beats the browser's own
    `[hidden] { display: none }`, so a button marked hidden in the markup sat
    there in plain sight. `[hidden] { display: none !important }` in
    `room.css` fixes it for everything at once.

24. ⚠️ **A SET OF NAMES WRITTEN OUT TWICE WILL DISAGREE WITH ITSELF.** The
    project page listed its tabs once for showing them and again, as a chain
    of `if`s, for reading the address. Adding a sixth tab to one and not the
    other meant the tab existed and its button worked, but a link straight to
    it quietly landed on Sheets. **That is fault 14 for the third time** — and
    fault 20 was the same shape again. Whenever the same set has to be known
    in two places, make it one list.

25. ⭐️ **A GUESS IS ONLY WORTH MAKING WHERE THE SHAPE REALLY SETTLES IT.**
    `guess_kind()` offers a kind from a piece's printed size — naming is the
    expensive part, and a measurement is free. Written from first principles
    it had five rules; **tried against 79 real pieces Frank had
    already cut and named, two of them were wrong**:
    - **ruler** called two ICE FIELDS rulers — 1.89 × 6.79in, long and thin,
      but ragged blobs filling three quarters of their box. A ruler is a
      printed strip, so it must be **solid** (`cover > 0.90`).
    - **tile** spoke exactly once in 79 pieces and called a turn template a
      tile. **The rule is gone.** A 2in square is not only ever one thing.
    - and it was silent about the wizard cards, because a publisher in
      1993 did not buy standard card stock. A card is held in the hand, so
      its **proportions** give it away where its measurements do not.
    It speaks about 28 of the 79 now and is right about all 28.
    ⚠️ **The offer must stay an offer** — nothing writes a kind by itself, a
    kind already set is never overwritten, and the bulk accept fills blanks
    only. Somebody working down a list of three hundred pieces will take a
    confident wrong answer without looking, which is why **silence is the
    right answer far more often than any particular kind is**. Fourteen of
    the checks in `check/guessing_the_kind.py` are about keeping quiet.

26. ⚠️⚠️ **A CHECK CAN CHECK CODE IT IS NOT LOOKING AT.** Python decides a
    compiled copy of a module is stale from the source's **size** and its
    modification time **in whole seconds** — so an edit that changes one
    digit and lands in the same second as the last one is invisible. Trying
    the teeth of a new check, the source read `0.10`, the code actually
    running read `0.60`, and the checks came out green on both. On a Mac the
    system python keeps that cache in `~/Library/Caches/com.apple.python/`,
    where nobody would think to look. `check.sh` sets `PYTHONPYCACHEPREFIX`
    to a folder inside its own temporary directory, so a run cannot read a
    stale one and throws its own away.

27. 🔤 **INSIDE A TEMPLATE LITERAL, `\s` IS JUST `s`.** The browser checks
    send expressions to Chrome as text in backticks, and a `replace(/\s+/g,
    " ")` written there arrived as `replace(/s+/g, " ")` — quietly scrubbing
    every letter s out of the page's own words before they were read. Two of
    the three checks using it passed anyway, which is how it went unnoticed.
    That is **fault 6's family again**: an escape that means one thing where
    it is written and another where it is used. Double them.

28. ⚠️ **A BUTTON THAT PUTS SOMETHING IN YOUR HAND MAKES THE NEXT PRESS PUT
    IT DOWN.** *Keep this shape* first picked the shape up as well as keeping
    it, on the reasoning that somebody keeping a shape means to use it. So
    the row arrived on the shelf already lit — and the first press on it,
    which is what everybody does, **toggled it off**. The check found it
    within a minute of being written: two clicks on the sheet, no pieces.
    Keeping and carrying are two acts; a button does one of them.

29. 🖼 **A GRID DECLARED FOR TWO CHILDREN WRAPS THE THIRD, SILENTLY.** The
    shelf row was `minmax(0, 1fr) auto` and grew a third control — the star
    for this game — so the × dropped onto a line of its own underneath every
    row. Nothing errored, nothing measured wrong, and it was found by
    **looking at a screenshot**, which is fault 3's family and the reason
    that habit is in this file twice.

30. ⚠️ **A SIZE IS NOT A SHAPE, AND A SHAPE IS NOT A SCALE.** The shelf
    first kept a shape *at* its printed size and laid it down only at that
    size. Frank: *"the size of a shape is agnostic, surely, as I can just
    scale a shape whilst retaining its shape?"* — quite so, and the same
    outline serves a game that prints its door an inch and a half wide and
    one that prints it two. But the fix is **not** to let a piece be forced
    to a size: a sheet is at whatever scale it is at, so a 4-inch outline
    laid on artwork printed 3.7 inches wide cuts a right-sized box round the
    wrong picture. Three separate things, and each has its own control now:
    the **shape** (kept), the **size** it is laid at (an offer — typed, or
    dragged out), and the **sheet's scale** (worked back from a shape whose
    true size is known, which is the only one of the three that makes pieces
    from different boxes match).

31. ⭐️⚠️ **A CONTROL THAT DOES NOT SAY WHAT IT DOES IS A CONTROL NOBODY
    PRESSES.** Frank, 23 August 2026: *"I don't, for example, have any idea
    what 'straight to the table' means on the project selection screen, so a
    hover tool or just in line text popup or whatever explaining what all the
    features and buttons do would be very helpful. And that's not just for me,
    obviously!"* He had been using the room for two days. **Every button now
    carries a plain sentence** — `data-tip`, or an ordinary `title`, which
    `room/tips.js` takes over so the same words are never written twice — and
    `check.sh` fails, by name, on a button that carries neither. That check is
    the point of the entry: the ones that existed were easy to fix, and the
    next one is the one to stop.

32. 🖼 **A THING THAT GOES ON EVERY PAGE MUST CARRY ITS OWN PAINT.** The tip
    bubble was styled in `room/room.css`, which the room's pages share — and
    the cutting table does not load, because it is one self-contained file so
    that it still works opened off a disk. On the table the bubble came out as
    an unstyled strip of text a page wide at the bottom of the window:
    switched on, correct, and invisible. The script carries its own stylesheet
    now, in colours that fall back where the page does not define them.
    ⭐️ It was found by **measuring the bubble rather than believing the flag
    that said it was showing** — the check asked "is it on?", got yes, and the
    screenshot showed nothing.

33. ⚠️ **A WATCHER THAT WATCHES FOR CHANGES WILL SEE ITS OWN.** *Explain
    everything* writes a line under each control, and a `MutationObserver`
    puts lines under controls a page builds later. Without a flag between
    them, writing the lines woke the watcher, which rewrote the lines, for
    ever — eight times a second until the tab was closed.

34. ⭐️⚠️ **A QUANTITY IS NOT A SET OF DESIGNS, AND A PRINTED CONTENTS LIST
    CANNOT TELL YOU WHICH IT MEANT.** Frank, 23 August 2026: *"in [one game]
    the contents of the supplements only gives generic descriptions of ship
    cards belonging to the factions the supplements bring to the game"* — one
    line naming a faction's ship templates where the box holds three ships,
    each with a name of its own.
    Two different things arrive as one line with a number on it:
    **26 wound counters** is one design printed twenty-six times — you cut
    ONE, and one row is right — while **3 ship templates** is three different
    pieces of card. The room believed the list, so Match could only give all
    three pieces the SAME name, and a game reading the manifest afterwards
    cannot tell them apart. A checklist line can now be **split into the
    components it really stands for**, one row and one name each. ⚠️ Only a
    person knows which lines are which, so the room offers and never decides —
    the same rule as the kinds and the look-alikes.
    ⭐️ And the careful part: pieces already tied to the old line follow to the
    first of the new components rather than being left pointing at nothing,
    and **a name somebody typed themselves is never overwritten** — only a
    name the room put there itself.

35. ⭐️ **THE LIST OPENS ON THE WORK, NOT ON EVERYTHING.** Frank, 23 August
    2026: *"the default view should be 'To outline', not 'All'… Otherwise I
    waste time wading through lots of cut and filed sheets before I find my
    next sheet to cut."* A hundred and sixty-one sheets, and the ones already
    dealt with are the ones in the way. The sheet filter now opens on **To
    outline** and is **remembered per game**, because two games are at
    different stages.
    ⚠️ And *finished with* beats *nothing outlined on it*: a sheet ticked as
    done drops out of the work still to do even though it has no outlines,
    because all it held was duplicates — *"it shouldn't appear in the 'To
    outline' view"*. The tick is the only thing that can know that.
    ⭐️ A consequence worth keeping: the commonest empty list is now a **good**
    one, so it says *"Nothing left to outline in this game"* rather than *"No
    sheet matches that"*, which would read as a fault.

36. ⭐️⚠️ **ONE IS ENOUGH, UNLESS EVERY ONE IS DIFFERENT.** A sheet prints
    twenty-six identical wound counters and the game repeats one for ever, so
    `26 Wound counters` wants **one** piece cut — that is the rule the whole
    room is built on and it has not changed. But `24 Damage cards` is
    twenty-four DIFFERENT pieces of card, and one of them is not the deck.
    Both arrive as one line with a number on it, and **nothing in a printed
    contents list tells them apart**, so each line carries `each` and the
    person sets it: *one is enough* or *all different*. Frank, 23 August 2026:
    *"build checklist counting deck against quantity — it's then my
    responsibility to ensure I have the correct number of cards to fill each
    deck."*
    ⚠️⚠️ **And the count must be asked BEFORE the guess.** Written the other
    way round — "does any piece's name match?" first — a deck of twenty-four
    with **nothing cut** read as *probably cut* because three pieces happened
    to be called *Damage card 01* and up, and the whole checklist showed
    **100%**. A guess may only speak for a whole component when there are
    enough of it to go round. Its teeth were tried: put the order back and two
    checks go red.
    ⭐️ A deck is also the one place where **many name matches are right**, so
    *Confirm the likely links* ties up every matching piece for a deck where
    for an ordinary component it insists on exactly one.

37. ⭐️ **EVERY LIST IN THE ROOM FOLDS, AND THERE IS ONE MECHANISM FOR IT.**
    Frank, 23 August 2026, having had it in Match: *"I want the same ability
    to collapse and expand core/expansions/extras etc throughout the platform
    (eg in Checklist, sheets, match, pieces etc) - it's super helpful."* A
    game and its supplements are one long list on every page, and the box
    being worked through is somewhere down the middle of it.
    ⚠️ **Four lists that each grew their own folding would drift apart** — one
    remembering and another not, one with its arrow the wrong way round. That
    is fault 24 for the fourth time, so there is a single `Fold` in
    `project.html` and each list only says what its headings and members are.
    ⭐️ The trick that let one mechanism serve a grid of cards, a table of
    rows, a column of pieces and a drag-and-drop list without rebuilding any
    of them: **members are hidden where they stand** — `data-fold="<group>"`
    on the row, `hidden` toggled on it — rather than being moved inside a
    wrapper. And a search always overrules a fold, or a component would hide
    inside a folded set while you were searching for it by name.

38. ⭐️⚠️ **THE PAGES ARE READ FRESH; THE PYTHON IS NOT.** Frank, 23 August
    2026, pressing a button built that same afternoon: *"bug — trying to split
    the [faction] ship templates… when I press 'Split it' I get a 'no such call'
    error."* Nothing was wrong with the split. His room had been open for
    hours: `room/*.html` and `room/*.js` are sent off the disk on every
    request, so the **new button was there**, while the Python is whatever was
    loaded when the process started, so the **route behind it was not**. A
    running program cannot re-read itself.
    ⚠️ The damage is that it looks like a broken button rather than an old
    room, and the person cannot tell. So the room now compares its own source
    against the clock it started at (`stale_code()`, `/api/health`) and every
    page carries a plain banner when they disagree: *close the room and open
    it again*. ⭐️ **Expect this every time a session adds an endpoint while
    Frank has the room open** — and now the room says so instead of him
    finding out through a button that appears to be broken.

39. ⚠️⚠️ **A SET IS NOT "THE ROWS THAT HAPPEN TO SIT TOGETHER".** Frank, 23
    August 2026: *"on #pieces the collapse/expand mechanic is going awry, just
    not working correctly, seems to be segmenting the core box over and
    over."*
    Every folding list started a new heading whenever the group of the row it
    was on differed from the row before — which is only grouping if a set's
    rows are already adjacent. On **Pieces** they are not: pieces are sorted by
    their own name, and a piece **file the index knows nothing about** has no
    sheet at all, so it sorts into the middle of a sheet's run and cuts it in
    two. ⭐️ A game project's `paths.pieces` may point into that game's own
    repository, so anything else living in that folder is one of these.
    ⚠️ And it is worse than untidy: both halves carry the **same fold id**, so
    each heading claims every row of that set — the counts are wrong on both,
    and folding one hides rows sitting under the other.
    The fix is *gather first, render second*, in one `gather()` all three
    lists use. It was latent on the other two as well: a component added by
    hand goes on the **end** of the list whatever set it belongs to, so the
    checklist and Match would have shown that set twice. ⭐️ Teeth tried — put
    the adjacency grouping back and four checks go red, showing the heading
    repeated and the counts double-claiming the same rows.
    ⭐️ A piece with no sheet also had an **empty** heading, which reads as a
    fault in itself. It says *Not off any sheet this project knows* now.

40. ⭐️ **YOU CANNOT JUDGE A PIECE AT FORTY-SIX PIXELS.** Frank, 23 August
    2026: *"if platform is suggesting '[n] pieces look like this one' it's
    incredibly difficult to see them in the tiny viewport it provides - can
    you make them appear larger/preview on hover (I don't want to click away
    to another page) just to make it easier to see if there is any
    differentiation?"* The room asks the hardest question it ever asks — are
    these the same piece printed twice, or two designs of one component? — and
    gave a stamp-sized picture to answer it from, when the whole answer is a
    flag in one corner. The tiles are twice the size now and hovering one
    shows it at 360px under the pointer.
    ⚠️ The preview uses the piece's **full picture**, not the thumbnail it is
    standing on: a thumbnail blown up is exactly as useless as a thumbnail.
    And such a picture must carry **no `title`**, or `tips.js` takes it over
    and puts a text bubble on top of the picture.
    ⭐️ Its check failed twice for reasons that were not the code: a hover
    dispatched with the left button named on it is a DRAG, and Chrome never
    delivers it as a hover; and the thumbnail sat 1496 pixels down a 963-pixel
    window, so the pointer was aimed into empty space. Scroll it into view and
    hover with no button.

41. ⭐️ **A SUPPLEMENT IS THIRTY SHEETS, SO "ONE SHEET" IS THE WRONG GRAIN.**
    Frank, 24 August 2026: *"in Match, I should have the option to limit the
    display… to pieces cut from either core or one of the supplements…
    otherwise I get served with 200+ objects from across the whole game when
    I'm just trying to rationalise one supplement or something."* The board
    could be held to one sheet or to the whole game and nothing between, and
    the thing being worked through is neither. The same control now offers the
    **box** first and its sheets under it, worked out from the sheet id the
    way the Sheets page works it out, so the two pages agree what a box is.

42. ⭐️⚠️ **A GAME IS WORKED THROUGH A BOX AT A TIME, NOT A SHEET AT A TIME.**
    Frank, 24 August 2026, an hour after the same fix landed on Match: *"the
    Pieces view is now pretty useless, and very frustrating to use. I don't
    want to go sheet by sheet, I'm much more likely to want to see core or
    supplement pieces - the random sheet numbers are not
    useful."* A hundred and sixty-one sheet numbers are not a list anybody can
    choose from, and *sheet 27* is not a thing anybody thinks in. Pieces now
    gathers by **box** by default and its *Show* list offers each box with its
    sheets underneath.
    ⚠️ Note the shape of this one: the same complaint arrived twice in a day
    about two different pages, because the fix was made where it was reported
    rather than where it belonged. There is one `bookOf()` now and Sheets,
    Pieces and Match all use it — **if a fourth list ever groups by sheet, it
    is probably wrong.**

43. ⭐️ **THREE THINGS A PERSON NAMING THREE HUNDRED PIECES ASKS FOR.**
    Frank, 24 August 2026, all in one message:
    - *"give me a single button when viewing any single piece to remove all
      the metadata (name, component, kind etc) - just strip back to all those
      fields being unfilled."* **Start this piece again** empties every box at
      once. ⚠️ It leaves `spare` and `alike` alone and says so: those are
      decisions about the piece's place made from other screens, and somebody
      clearing a name is not asking to undo them.
    - *"I'd like a bulk apply function - if I can select all 32 cards in a
      deck, I should be able to apply the correct card deck label to them all
      in one go."* **choose several at once** puts a tick on every row, with
      *all shown* / *none*, and one press gives them all the same component.
      ⚠️ It fills blanks only — a name somebody typed is never overwritten,
      which matters most in a bulk action, where a wrong rule is spread over
      hundreds of pieces before anybody looks.
    - *"if a piece has been marked as cut with a green tick… can you make it
      appear on hover over the green CUT pill?"* A tick is a claim about a
      piece, so the claim now shows the piece it was made from.
    ⚠️ The tick boxes went in and vanished: the row appended the checkbox and
    then set its `innerHTML`, which threw it away — the bar said *20 pieces
    ticked* over a list with no ticks on it. Anything added to a row must go
    in **after** its markup.

44. ⚠️⚠️ **A FOLD MUST NEVER SWALLOW SOMETHING YOU JUST ASKED FOR.**
    Frank, 24 August 2026: *"BUG - adding a new component does not work, so
    far as I can tell - I just tried to create a new Chaos Experience Reward
    counter, typed in the name, clicked add, and nothing happened."*
    It had worked perfectly. The component was on the disk and its row was in
    the table — inside a set he had **folded away**, so the one thing he was
    watching for was hidden the instant it appeared. A fold is a way of not
    looking at what you are done with; it must never be a way of losing what
    you have just made.
    So `Fold.open()` exists and **every way of adding a row calls it**: adding
    one component, pasting a list, and splitting a component into its parts.
    The add also says where the new row went and brings it into view, marked
    for a moment, because a list of two hundred should not have to be searched
    for the thing just added to it.
    ⭐️ Worth remembering the shape of this: a feature that hides things will
    eventually hide the wrong thing, and the person will report the OTHER
    feature as broken.

45. ⚠️⚠️ **A ROW'S HANDLERS MUST WORK BY ID, BECAUSE A SAVE REPLACES THE
    LIST UNDER THEM.** Frank, 24 August 2026: *"removing a piece in the
    checklist doesn't work - verify that."* It was worse than not working: it
    **removed the wrong component**. `saveWantedAll()` puts the room's answer
    back into `wantedData` and does NOT re-render — it must not, because it
    fires as you type and re-rendering would take the box away from under
    you. So every row on screen was left holding an item object that is no
    longer in the list: `indexOf(it)` gave −1, and `splice(-1, 1)` took the
    **last** component off instead of the one whose × was pressed. Edit a
    name, then remove something, and a different component was quietly thrown
    away. Every handler on a checklist row now looks its item up by **id**,
    which is the only thing about a row that survives a save.

46. ⭐️ **A CARD'S BACK IS ANOTHER PIECE, NOT A PROPERTY OF THE CARD.** Frank,
    24 August 2026: *"when I'm in the process of cutting a deck of cards, how
    do I set the correct back to them? Note that it's not always the same back
    within the same set."* Cut the back once and let every card point at it:
    a set with three different backs is three pieces and no special case
    anywhere. `back` holds the other piece's stem; the export turns it into
    the file name that piece was written as, because a stem means nothing to
    anybody reading the inventory. A whole deck takes its back in one press
    from the same bar that gives them their component.

47. ⭐️ **ONE DESIGN, CUT ONCE, WANTED TWENTY TIMES.** Frank, 24 August 2026:
    *"in the Chaos Magic deck, one of the cards (the Power card) needs to
    appear x20, whereas the other 12 are unique. How do we manage that?"* The
    room's rule does not change — one of each design is cut, because a picture
    repeats for nothing — but the game reading the manifest has to be told
    that this design is wanted twenty times, and there was nowhere to write it
    down. `copies` on the piece says so, and it travels in the inventory.
    ⚠️ Note which of the two questions each answers: the **checklist** counts
    what you have cut, and `copies` tells the game what to do with it. They
    are not the same number and must not be conflated.

48. ⚠️ **THE DEFAULT OF A BULK CONTROL MUST DO NOTHING, NOT UNDO SOMETHING.**
    The bulk bar's component list opened on *take the component off them*, so
    somebody using it only to set a deck's back would have unlinked the whole
    deck on the way past. It opens on *leave the component alone* now, and the
    request carries only what was actually chosen.

49. ⭐️⭐️⚠️ **THE ROOM KEEPS ITS OWN HISTORY, BECAUSE A BACKUP SOMEBODY HAS
    TO REMEMBER IS NOT A BACKUP.** On 24 August 2026 a bug of the room's own
    (fault 45) threw two of Frank's components away. What got them back was
    that his project folder happens to live inside a git
    repository — and told he might commit it more often he said, exactly
    right: *"I'm afraid this means nothing to me - it needs to be automated if
    it needs to happen."*
    So the three stores that **cannot be rebuilt** — `outlines.json` (the work
    itself), `manifest.json` (what every piece is called) and `wanted.json`
    (the checklist) — now keep the copy they replace, every time they are
    written, up to sixty each, in `<project>/history/`. Everything else in a
    project can be made again from the sheets and the outlines.
    ⚠️ **A save that changes nothing must keep nothing.** The room saves a
    moment after every edit and many of those carry identical content; sixty
    identical copies would push the real history off the end, which is the one
    thing the history exists to prevent. `save_store()` compares first and
    does nothing at all when nothing has changed.
    ⚠️ **And keeping history must never stop the work being saved** — a full
    disk loses the safety net, not the work.
    ⭐️ It is reachable without a terminal, which is the whole point: Settings
    lists what is kept, what was in each copy, and puts one back. The copy it
    replaces is kept too, so restoring is not a one-way door either.

---

## Architecture

```
cutting_room.py          the app: HTTP server, projects, import, cut, API
  room/home.html         the front page — projects, start a game
  room/project.html      one game: sheets, pieces, match, checklist, settings
  room/room.css          all the styling for both
  room/drop.js           dragging: whole window, whole folders. Shared.
  room/close.js          Close the Cutting Room, and the sign on the door.
                         Shared. ?closedsign=1 puts the sign up to be looked at.
                         ⭐️ Also the banner saying the room is running older
                         code than the page — see fault 38.
  room/tips.js           ⭐️ Every control says what it does. `data-tip` (or a
                         plain `title`, which it takes over) on ANY element.
                         Shared by both pages AND by the served table, and it
                         carries its own styling because the table does not
                         load room.css. check.sh fails on a button with
                         neither.
cutting_table.tpl.html   THE EDITOR. Shared by the room and the baked page.
cutting_table.py         bakes the editor + sheets into one offline HTML file
cut.py                   cuts pieces from a sheet + mask, standalone
sheets.py                the image work: flood, label, separate, draft
demo/make_demo_sheet.py  a pretend sheet, so the repo needs nobody's artwork
check/check.sh           everything that can be checked without a person
  check/in_the_browser.js  drives a real Chrome over a throwaway game
  check/guessing_the_kind.py  the size rules, and what they refuse to say
```

**The server is one file on purpose.** Standard library plus numpy and Pillow;
no framework, no build step, no `npm install`. It has to start from a
double-clicked `.command` on a Mac with nothing installed but Python.

### How the editor is served

`table_template()` reads `cutting_table.tpl.html` and applies `TABLE_PATCHES`
— a list of (old, new) exact-match string edits that turn the offline editor
into the served one: saving to the room, the Cut button, the room's sheets,
`+ Sheet` handing files to the server.

⚠️ **A patch whose anchor does not match RAISES, at start-up, loudly.** That is
deliberate: a silently unpatched editor would save nothing to disk, which is
fault 1 all over again. If you edit the template and the room refuses to start,
the message names the patch. Fix the anchor; do not delete the patch.

### A project

A folder with a `project.json` in it. `paths` may point each store anywhere:

```json
{"id": "boxgame", "name": "A Boxed Game", "dpi": 300,
 "paths": {"sheets": "sheets", "outlines": "../reference/outlines/x.json",
           "pieces": "../assets/cut/punched", "manifest": "../data/x.json",
           "wanted": "wanted.json"},
 "hooks": [{"id": "finish", "label": "Hand the pieces to the game",
            "cmd": ["/usr/bin/python3", "tools/finish_pieces.py"],
            "cwd": "/path/to/the/game"}],
 "sheets": [ ... kept by the room ... ]}
```

That is how a game's room writes straight into that game's own repository
and hands the finished pieces over with a button.

**The stores, and which of them matters:**

| file | what it is | rebuildable? |
|---|---|---|
| `outlines.json` | every outline on every sheet | ⭐️ **NO — this is the work** |
| `sheets/` | each sheet as a 300dpi PNG | yes, from the source PDFs |
| `masks/` | one flat colour per outline | yes, from the outlines |
| `pieces/` | the cut pieces | yes, from sheets + outlines |
| `pieces/spare/` | pieces **set aside** — the second identical ice field. The hand-over globs `pieces/` and does not recurse, so this folder is how a piece is kept without being handed over | yes |
| `pieces/index.json` | where each piece came from: sheet, box, ink | yes |
| `manifest.json` | what each piece IS: name, kind, note, turn, component, **its back** (another piece), **how many copies the game needs** | ⭐️ **NO** |
| `wanted.json` | the checklist | ⭐️ **NO** |
| `cache/` | thumbnails, suggestions, piece statistics | yes |
| `history/` | ⭐️ the last 60 copies of each of the three stores above that cannot be rebuilt, kept automatically before every save that changes anything — see fault 49 | it IS the rebuild |

⭐️ **One store is NOT in the project**, on purpose: `shapes.json` sits in the
room's home beside `projects.json`. That is the shelf of kept shapes, and its
being outside any one project is the whole feature — a door drawn for one
dungeon game is the same door in another. Each shape carries `stars`, the
list of project ids that have marked it as one of theirs, so *favourited per
project* and *searchable across projects* are the same list read two ways. Not
rebuildable, but cheap to redraw; the work it protects is time, not outlines.

### The cut, end to end

`outlines.json` → `paint_mask()` (the template's own Bézier, transcribed into
Python — change one and change both) → `sheets.label_shapes()` → `cut.cut()`
per piece → measured in inches → `pieces/index.json`.

⚠️ **Names follow their pieces across a re-cut.** Pieces are numbered in
reading order, so outlining one more near the top renumbers everything below
it and a name would quietly land on a neighbour. `cut_sheet()` matches new
pieces to old by their box (60% overlap) and rewrites the manifest keys.

### Piece statistics

`piece_stats()` — printed size, a 144-bit pattern hash, mean RGB, ink coverage,
and whether the piece runs off the sheet edge. Cached in `cache/stats.json`,
keyed on the file's mtime and a version number. **Bump the version when the
shape of the record changes** or stale records come back.

---

## Verifying

```sh
check/check.sh          # 273 checks, about a minute
```

That is the whole of it now. It parses every script, makes a **throwaway
66-sheet game** out of the demonstration sheet in a registry of its own — so
nothing you are working on is touched — serves it on a port of its own, and
drives a real Chrome over it: draws a rectangle, types a name whose every
letter is also a tool, and **reads the project's `outlines.json` off the disk**
to see that the work arrived. Then the offline baked page, the same way. It
wants Python with Pillow and numpy, Node 22+ (for its built-in `WebSocket`)
and Chrome; without the last two it does the parsing and says what it skipped.

It goes the whole way round: outline, name, save, **cut**, and the piece is
read back off the disk at its printed size in inches. It also checks that **a
POST leaves the connection fit for the request after it** (fault 20 — put that
one back and the check goes red on the first try), and finishes by **closing
the room from the room**: a table holding an unsaved edit holds the door shut
and is named, the door frees when that table goes, and the port really stops
listening. It then works the room's
own pages: a name dropped on a piece raises no complaint, and a turned piece
turns its picture everywhere without being clipped.

It breaks **one line of a contents list into the components it really
stands for** and follows what that does to the pieces already linked to it —
including the one that matters most, that a name somebody typed themselves is
left exactly as it was.

It checks that **every button on every page says what it does** — the one
that stops the next unexplained control, rather than the ones already fixed —
and, in the browser, that pointing at one really does explain it and that
*What does this do?* writes them all out without going round in circles.

It also works the **shelf of kept shapes**: a shape laid at twice its own
size and landing exactly twice as wide and twice as tall (the shape kept, not
squashed), a shape **telling a sheet what its scale really is** — ⭐️ its teeth
were tried, and the fault put back turns that check red on its own — a shape
taken off a piece **already cut** at the size the outline that made it says,
the API round trip on its own
(kept in inches, beside the projects rather than inside one, starred for the
game it was drawn in, starrable by another game without being taken from the
first, and every malformed shape refused with a sentence), and then the whole
thing by hand in the browser — a shape kept off one sheet, **laid down twice
on another**, read back off the disk at the printed size it was kept at, and a
shape belonging to a different game found by search and brought over with a
star.

`check/guessing_the_kind.py` is the measuring on its own — no browser and no
project, because `guess_kind()` is arithmetic. ⭐️ **Fourteen of its checks are
about the room saying NOTHING**, which is the half that matters: the rules that
recognise a card will not rot, but a future rule getting greedy would put a
confident wrong answer in front of somebody naming three hundred pieces. Its
teeth were tried and found blunt the first time — widening the tile rule to
swallow whole boards left every silence check green, because each of them
happened to be settled by a *different* rule. The fences round each band are
there now.

`check/names_across_a_recut.py` is the other half, and needs no browser — it is
the cut itself. **Names, and variant marks, following their pieces across a
re-cut** is the most delicate code in the room; twenty checks over a throwaway
game of its own, covering an outline added above the others, one removed from
the top, one removed from the BOTTOM, and a piece nudged. It found fault 13's
neighbour on its first outing.

⚠️ It parses **the editor the room serves**, not only the template on disk.
Those are different documents; see fault 13.

It has teeth, and that was tried rather than assumed: put fault 11 back and
nine checks go red, naming the elements doing the stretching; put fault 12
back and two go red.

⚠️ **It is not a substitute for looking.** Every fault in the list above was
found by eye first. The check is only there so the *same* ones cannot come
back quietly.

**Measuring, when something feels slow.** Headless Chrome does not raster
unless something is watching it, so it reports a serene 60fps whatever the
page is doing. `Page.startScreencast` makes it produce real frames, and the
frames that arrive are frames it actually painted — that is what turned
"feels jerky" into "one frame in two seconds". Drive it from Node over the
DevTools protocol the way `check/in_the_browser.js` does; nothing to install.

### By hand, when you want to see one thing

```sh
# does the Python parse, and do the editor patches still match?
python3 -c "import ast; ast.parse(open('cutting_room.py').read())"
python3 -c "import sys; sys.path.insert(0,'.'); import cutting_room as c; c.table_template(); print('patches ok')"

# 2. does each page's script parse? An unterminated string kills the page
#    silently, and the server knows nothing about it.
python3 - <<'PY'
import re
for f in ("room/home.html", "room/project.html"):
    open("/tmp/x.js","w").write(re.search(r"<script>(.*)</script>", open(f).read(), re.S).group(1))
    import subprocess; print(f, subprocess.run(["node","--check","/tmp/x.js"]).returncode)
PY
node --check room/drop.js

# 3. LOOK AT IT. This is the one that finds things.
open -a "Google Chrome" --args --headless=new --disable-gpu \
  --user-data-dir=/tmp/ch --window-size=1500,1050 --virtual-time-budget=11000 \
  --screenshot=/tmp/shot.png "http://127.0.0.1:8765/p/<id>/?tab=pieces"
# then read /tmp/shot.png. Console errors appear in the run's stderr.
```

**Debug hooks already in the code**, both harmless and both earning their keep:
`?probe=1` on the project page writes measured layout into `document.title`;
`?dropprobe=1` shows the drag curtain so it can be photographed.
`?tab=<name>` selects a tab without a fragment, which headless Chrome needs.

⚠️ **NEVER POINT A CHECK OR A BENCHMARK AT A REAL PROJECT.** Opening a sheet
in the editor *saves* — that is the whole point of fault 1 — so driving a
browser over a real project's folder writes to the one store that
cannot be rebuilt. It happened during this work: a benchmark drag on core-05
rewrote the sheet's metadata block. No outline was lost and the file was put
back, but the next one might not be so lucky. `check/check.sh` makes its own
game in its own registry for exactly this reason; anything else measuring the
editor must do the same.

⚠️ **macOS has no `timeout`.** Keep one on the PATH (a small shell
stand-in will do) when scripting Chrome.

---

## House style

- **Comments say WHY, at the point of the decision, and name the fault they
  came from.** Every ⚠️ in this codebase is a thing that actually went wrong.
- Prose in the interface, not jargon. "Nothing outlined yet", not "0 masks".
- ⭐️ **Every control says what it does, in one plain sentence.** A `data-tip`
  or a `title` on every button, link and field that is not self-evident —
  `room/tips.js` shows it on hover, and *What does this do?* writes them all
  out for a touch screen or for somebody who would rather read. **This is not
  optional and it is checked**: `check.sh` names any button that carries
  neither. Write it for somebody who has never seen the room, say what will
  HAPPEN, and where something is destructive or slow, say that.
- Never destroy without saying what will be destroyed and how to get it back —
  and prefer **not destroying**. Setting a piece aside moves it rather than
  deleting it, and a name whose piece is gone is put in `retired` rather than
  dropped. Deleting a whole sheet is the one place that really deletes, and it
  says so.
- Never guess on the user's behalf where the answer is a judgement. The
  look-alike finder proposes; it does not bin.
- British spelling throughout: colour, centre, licence (noun).
