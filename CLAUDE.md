# The Cutting Room / Cutting Table — project guide for Claude

**One tool, two ways in.** `cutting_room.py` is a local web app — the whole
workshop, from importing a game's scans to knowing what is still to cut.
`cutting_table.py` bakes the same editor into a single self-contained HTML file
that works offline from a `file://` URL. The editor itself,
`cutting_table.tpl.html`, is shared by both and must stay that way.

**Public, MIT.** It grew out of
one game's own project and is deliberately
separate from it: nothing here knows about any particular game.

⚠️⚠️ **KEEP IT GENERIC. This is the constraint on everything.** The designer, 22
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

## Picking the work up

⭐️ **No prompt should be needed to start a session, and none should be
relied on.** The designer's instruction, 22 August 2026: *"the house rules should be
contained in the readmes in the repo, not a prompt."* A prompt is lost the
moment the chat is closed; this file is not. So everything about how to work
here lives in these documents, and *"carry on with the Cutting Room"* is a
complete brief. If a session ever needs a rule that is not written down, the
fix is to write it down here, not to put it in the next prompt.

1. **Read this file, then `BACKLOG.md`.** BACKLOG's *NOW* section is the live
   list and its ⭐️ marks what is next. The designer's most recent words outrank it.
2. **Take ONE thing and see it through** — code, documents, checks, commit,
   push. Say which you have taken and why before starting. Half a feature and
   a stale document is worse than not having begun.
3. **Run `check/check.sh` before you start as well as after.** Before, so you
   know whether you broke it or found it broken; after, so you know. It needs
   no arguments and finds its own Python.
4. **Finish by leaving the documents true**, which is the item below that gets
   forgotten first. A check count, a "next up", a feature described as
   proposed when it is built — each of those misleads the next session, and
   the next session is usually a different one that believes them.

---

## Working with the designer

- **The person who uses this is the person who designed it**, and is **not a
  programmer**. Claude makes every engineering decision. Explain what a change
  does, never how it is coded, unless they ask.
- **Their eye is the instrument.** They have caught more real faults from looking at
  the thing than any check has: the outlines that never left the browser, the
  cut pieces missing from the sheet thumbnails, the page margins being trimmed
  off, and the editor stealing their typing. When they say something looks wrong,
  it is wrong.
- Git: commit and push after each verified chunk, without being asked. Plain
  English messages that say what was wrong and why the fix is the fix.
- ⚠️⚠️ **NOTHING HERE NAMES A GAME, A PUBLISHER OR A PERSON.** Not in the
  code, not in a comment, not in an example, not in a check's test data. The
  names crept in the first time through the *explanations* — a rule is easier
  to justify with the real cardboard that taught it — and taking them out
  again took three passes, of which the third found one that had wrapped
  across a line break and so was invisible to a search. `check/check.sh` fails
  on any of them now, reading each file with the line breaks taken out.
  ⭐️ Write *"one game has two player marker cards"* rather than naming it. The
  measurement is the evidence; the name never was.
  ⭐️ **And no pronouns for the person either** — they/them. Nobody's are
  written down here, and a document with no name in it should not still say he.
- ⚠️ **This repository is PUBLIC and holds the TOOL ONLY.** Never commit a
  game's sheets, a baked HTML page (the sheets are inside it), a cut piece, or
  anything out of a `Cutting Room` project folder. `.gitignore` is written to
  keep them out and should stay that way.
- **Keep these documents current, every session:**
  - `GUIDE.md` — ⭐️ **the walk-through**: the six steps in order, with
    pictures, for somebody who has never seen the room. It is the thing to
    hand the designer. ⚠️ It **lifts from `ROOM.md` and must not duplicate it** —
    ROOM.md is the reference and wins where they disagree (fault 24). Its
    pictures are made by `docs/make_guide_pictures.sh` off the DEMONSTRATION
    sheet, so re-run that when a screen changes.
  - `ROOM.md` — the manual, every screen and every button.
  - `BACKLOG.md` — the live list: what is done, what is next, what is known
    to be missing.
  - `README.md` — the public front page. It is what a stranger reads first.
  - `CLAUDE.md` — this file.

---

## Status (24 August 2026)

The room is **built and in daily use** on two games, and 24 August was a day of
the designer cutting a real game with it and saying what was wrong — twenty-one
separate pieces of work, most of them their words verbatim in the faults below —
and then, at the end, **the check against the contents list** they had asked for
by name. One
game: 161 sheets, **221 components on the checklist**, cards and counters being
cut and named in earnest. Another: 21 sheets imported.

⭐️ **What that day was mostly about**: a game is not a heap of sheets, it is a
**box and its supplements**, and the room kept making them work a sheet at a
time. Sheets, Pieces, Match and the Checklist all group by box now, all fold,
and all remember. See faults 37, 41 and 42 — the same complaint arriving three
times because the first two fixes were made where it was reported rather than
where it belonged.

⚠️⚠️ **And the day's hard lesson: the room lost two of their components.** A
stale row handler removed the wrong one (fault 45), and what got them back was
git, which they do not use. Everything that cannot be rebuilt now keeps its own
history (fault 49). *Read fault 45 before touching any list that saves as you
type.*

⭐️⚠️ **And the day's second lesson: a list nobody can shorten is a list
nobody reads.** Three of their complaints were the same complaint — a flag that
could not be cleared, a dropdown of 221 pieces, a dropdown of a few hundred
components. See faults 50 and 51. **Whenever the room puts a list in front of
somebody, ask what makes it shorter.**

⭐️ **What is expensive is naming, not cutting.** The designer, having cut a sheet:
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

1. ⭐️ **A user guide, written properly.** There is a first cut of one, made
   from this day's work; BACKLOG says what it should become.
2. **A lighter ground** — *"I'd like to consider some different displays (eg
   white background rather than the black)."* Read the reason the ground is
   dark before changing it; it is written in the editor's `:root` block.
3. **No terminal window at all** — a minimal `.app` bundle. All that is left
   of *"a simpler way to open and quit"*: opening, quitting and **starting it
   again** are all a press on the page now (24 August), so what remains is
   only that the window exists at all.
4. ⭐️ **A way in from the report to the piece** — `?tab=pieces&piece=<stem>`.
   The report names pieces by their stem and cannot open them, and it is the
   same door a game engine would want in order to say *this one is wrong*.

Built that day, in order:

1. **The room itself** — projects, import, the served editor, cut, name, and
   the checklist.
2. **Match** — drag a component's name onto the piece it is.
3. **The UX pass** — five steps across the top, sheet filters and search, a
   first-run welcome, a proper empty state for the checklist.
4. **Post-cut review** — flags, look-alikes, keep-one-bin-the-rest.
5. **Drag and drop** — the whole window, and whole folders.

**22 August**, first thing: *"it now runs VERY slowly when manipulating a
sheet when cutting, all jerky. COMPLETELY unusable."* They were right, and it
was not subtle — during a two-second drag the browser painted **one frame**.
Two faults, both of which only show at the size of a real game; they are
numbers 11 and 12 below. It paints 120 frames in the same drag now. There is
a `check/check.sh` since, which goes red on both if they ever come back.

**Later the same day**, the designer cut with it for real and sent back five things,
all of which were right and all of which are fixed: a phantom error on every
drag in Match, a turn that did not turn the thumbnail beside it, a NAME field
that looked redundant because the two ways of setting it disagreed, counts
that never moved as they worked, and — the interesting one — the look-alike
finder proposing to bin the second player marker card. **Similar is not the
same as duplicate**; see fault 18. Chasing the re-cut test they had asked for
turned up a name that could lie in wait for the next piece cut in its place,
and writing the message about *that* re-broke the whole editor twice over in
the way fault 6 warns about.

---

## ⚠️ The faults that shaped it — do not undo these

Every one of these was real, and most were found by *looking at the thing*
rather than by reading the code.

1. ⚠️⚠️ **THE WORK WAS IN THE BROWSER.** The baked Cutting Table kept outlines
   in `localStorage` and the only way out was a *Save a copy* button nobody had
   told the designer about. They outlined four sheets; they never reached the game and
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
    where the designer could not see it at all. The fix is *one line* —
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
    files, and complained, *after* the link had been made. The designer: *"always
    seems to serve an error code (even though it also appears to work!)"*.
    A guard that some of a set of handlers share is a guard that will be
    forgotten by one of them.
15. 🖼 **A ROTATION LIVES IN THE MANIFEST, SO EVERY PICTURE MUST APPLY IT.**
    The cut PNG is never rewritten — a re-cut and the look-alike hash both
    depend on the file being exactly what came off the sheet. Four places draw
    a piece; two applied the turn and two did not, so turning a piece turned
    the big picture and not the row beside it, and the designer did it again thinking
    it had been refused. They go through one function now. *A quarter turn
    also swaps width and height*, so a turned picture must be held to the
    shorter side of its box or it is clipped.
16. 🧮 **TWO WAYS IN MUST DO THE SAME THING.** Dragging a component onto a
    piece filled its name in; choosing the same component from the dropdown
    did not. A piece linked that way read "(unnamed)" everywhere and step 4
    counted it as still to do for ever. The designer: *"NAME seems redundant?"* —
    it was not redundant, the two routes simply disagreed.
17. ⏱ **A COUNT WORKED OUT BY THE SERVER IS STALE THE MOMENT YOU CHANGE
    ANYTHING.** The five steps and their counts were read once at load, so
    naming a piece left "6 of 7 named" sitting there. Same complaint as the
    thumbnail that would not turn: *the screen does not show what you just
    did, so you doubt it took and do it again.*
18. 🎴 **SIMILAR IS NOT THE SAME AS DUPLICATE.** The look-alike finder knew
    two answers — bin the spares, or unrelated — and one game has two player
    marker cards (one per player) and twelve movement templates differing only in
    the player's badge. Those are **designs of one component** and all of them
    are wanted. There is a third answer now, and the mark lives on the piece
    so it survives a re-cut.

19. ⚠️ **NOTHING IN THE ROOM DELETES A CUT PIECE.** The designer: *"Binning a piece
    shouldn't be destructive — it should be merely to hide a piece from the
    main manifest. eg there are two identical terrain tiles. The game only needs
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
    answered **501 Unsupported method**. The designer would have seen the project page
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

22. ⚠️⚠️ **WHAT LEAVES THE ROOM IS SOMEBODY ELSE'S WORK.** The designer, 22 August
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
    it had five rules; **tried against 79 real pieces the designer had
    already cut and named, two of them were wrong**:
    - **ruler** called two TERRAIN TILES rulers — 1.89 × 6.79in, long and thin,
      but ragged blobs filling three quarters of their box. A ruler is a
      printed strip, so it must be **solid** (`cover > 0.90`).
    - **tile** spoke exactly once in 79 pieces and called a turn template a
      tile. **The rule is gone.** A 2in square is not only ever one thing.
    - and it was silent about the player marker cards, because a publisher in
      1993 did not buy standard card stock. A card is held in the hand, so
      its **proportions** give it away where its measurements do not.
    It speaks about 28 of the 79 now and is right about all 28.
    ⭐️ **And it no longer offers *token* for a round chit.** The designer, shown the
    result: *"not sure I know the difference between a token and a counter
    tbh!"* — there is not a firm one, `kind` decides only which heading a
    piece sits under, and a rule that hands somebody a distinction they
    cannot make has failed at the only thing this code is for.
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
    size. The designer: *"the size of a shape is agnostic, surely, as I can just
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
    PRESSES.** The designer, 23 August 2026: *"I don't, for example, have any idea
    what 'straight to the table' means on the project selection screen, so a
    hover tool or just in line text popup or whatever explaining what all the
    features and buttons do would be very helpful. And that's not just for me,
    obviously!"* They had been using the room for two days. **Every button now
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
    CANNOT TELL YOU WHICH IT MEANT.** The designer, 23 August 2026: *"in [one game]
    the contents of the supplements only gives generic descriptions of ship
    cards belonging to the players the supplements bring to the game"* — one
    line naming a player's movement templates where the box holds three ships,
    each with a name of its own.
    Two different things arrive as one line with a number on it:
    **26 damage counters** is one design printed twenty-six times — you cut
    ONE, and one row is right — while **3 movement templates** is three different
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

35. ⭐️ **THE LIST OPENS ON THE WORK, NOT ON EVERYTHING.** The designer, 23 August
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
    twenty-six identical damage counters and the game repeats one for ever, so
    `26 Damage counters` wants **one** piece cut — that is the rule the whole
    room is built on and it has not changed. But `24 Damage cards` is
    twenty-four DIFFERENT pieces of card, and one of them is not the deck.
    Both arrive as one line with a number on it, and **nothing in a printed
    contents list tells them apart**, so each line carries `each` and the
    person sets it: *one is enough* or *all different*. The designer, 23 August 2026:
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
    The designer, 23 August 2026, having had it in Match: *"I want the same ability
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

38. ⭐️⚠️ **THE PAGES ARE READ FRESH; THE PYTHON IS NOT.** The designer, 23 August
    2026, pressing a button built that same afternoon: *"bug — trying to split
    the [a player's] movement templates… when I press 'Split it' I get a 'no such call'
    error."* Nothing was wrong with the split. Their room had been open for
    hours: `room/*.html` and `room/*.js` are sent off the disk on every
    request, so the **new button was there**, while the Python is whatever was
    loaded when the process started, so the **route behind it was not**. A
    running program cannot re-read itself.
    ⚠️ The damage is that it looks like a broken button rather than an old
    room, and the person cannot tell. So the room now compares its own source
    against the clock it started at (`stale_code()`, `/api/health`) and every
    page carries a plain banner when they disagree: *close the room and open
    it again*. ⭐️ **Expect this every time a session adds an endpoint while
    the designer has the room open** — and now the room says so instead of them
    finding out through a button that appears to be broken.

39. ⚠️⚠️ **A SET IS NOT "THE ROWS THAT HAPPEN TO SIT TOGETHER".** The designer, 23
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

40. ⭐️ **YOU CANNOT JUDGE A PIECE AT FORTY-SIX PIXELS.** The designer, 23 August
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
    The designer, 24 August 2026: *"in Match, I should have the option to limit the
    display… to pieces cut from either core or one of the supplements…
    otherwise I get served with 200+ objects from across the whole game when
    I'm just trying to rationalise one supplement or something."* The board
    could be held to one sheet or to the whole game and nothing between, and
    the thing being worked through is neither. The same control now offers the
    **box** first and its sheets under it, worked out from the sheet id the
    way the Sheets page works it out, so the two pages agree what a box is.

42. ⭐️⚠️ **A GAME IS WORKED THROUGH A BOX AT A TIME, NOT A SHEET AT A TIME.**
    The designer, 24 August 2026, an hour after the same fix landed on Match: *"the
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
    The designer, 24 August 2026, all in one message:
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
    The designer, 24 August 2026: *"BUG - adding a new component does not work, so
    far as I can tell - I just tried to create a new Reward
    counter, typed in the name, clicked add, and nothing happened."*
    It had worked perfectly. The component was on the disk and its row was in
    the table — inside a set they had **folded away**, so the one thing they were
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
    LIST UNDER THEM.** The designer, 24 August 2026: *"removing a piece in the
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

46. ⭐️ **A CARD'S BACK IS ANOTHER PIECE, NOT A PROPERTY OF THE CARD.** The designer,
    24 August 2026: *"when I'm in the process of cutting a deck of cards, how
    do I set the correct back to them? Note that it's not always the same back
    within the same set."* Cut the back once and let every card point at it:
    a set with three different backs is three pieces and no special case
    anywhere. `back` holds the other piece's stem; the export turns it into
    the file name that piece was written as, because a stem means nothing to
    anybody reading the inventory. A whole deck takes its back in one press
    from the same bar that gives them their component.

47. ⭐️ **ONE DESIGN, CUT ONCE, WANTED TWENTY TIMES.** The designer, 24 August 2026:
    *"in the one of the card decks, one of the cards (one of them) needs to
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
    (fault 45) threw two of the designer's components away. What got them back was
    that their project folder happens to live inside a git
    repository — and told they might commit it more often they said, exactly
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

50. ⭐️⚠️ **A FLAG THAT CANNOT BE ANSWERED IS NOT A QUESTION, IT IS A STAIN.**
    The designer, 24 August 2026: *"some of the pieces I've cut are flagged as RUNS
    OFF THE SHEET. That's a reasonable thing to flag, but I don't see a way to
    remove that flag (because it doesn't matter), and I don't mind about the
    overrun."*
    ⚠️ The damage is not the nuisance, it is what it does to the list. *Worth
    a look* is a list of **things to deal with**; a flag nothing can clear
    means it never empties, so after a week it is never opened — **and the
    next flag on it, the one that really is a bad outline, is never seen
    either.** A sheet scanned edge to edge flags half its pieces quite
    correctly and quite uselessly. So every worry the room raises about a
    piece now has an answer, and for these three the answer is a person saying
    *That is fine*. `fine` on the piece holds the flag keys waved through, so
    it **follows the piece across a re-cut** exactly as a name does — or every
    answer would come back the next time the sheet was cut, which is fault 19
    again.
    ⭐️ The look-alike flag is not in that set: it has answers of its own. And
    *no name* is answered by naming.
    ⚠️ ONE list — `WORRIES` in `project.html` — because these keys are known
    in four places: the test that raises them, the words on the chip, the
    sentence in the bar, and the *Worth a look* filter. That is **fault 24 for
    the fifth time**.

51. ⭐️⭐️ **A LIST OF TWO HUNDRED IS NOT A LIST.** The designer, 24 August 2026, of
    two different dropdowns in one message: *"helpful if a card back element
    can be flagged as such, and then ONLY card backs appear in the ITS BACK
    dropdown, or that really is an exhaustive process"*, and *"I really do
    think those menus could be better rationalised tbh, if I'm working with
    one supplement's elements, there doesn't seem to be a need to include all
    the possible choices for the core and the other boxes."* Both lists were
    right and both were unusable: that game is 221 pieces and a few hundred
    components, and a `<select>` of that length is a haystack.
    - **Its back** narrows to the pieces marked as one. A back is not a
      property of a card, it is another PIECE (fault 46), so what it needed
      was a way of saying what SORT of piece it is — and that is what `kind`
      has always been for. `card back` is a kind now. ⚠️ Nothing guesses it:
      the room cannot see the back of a card, and a wrong back spread over a
      deck of thirty-two in one press is fault 25's confident wrong answer.
      ⚠️ And the narrowing gives up rather than showing an empty list, or
      somebody who has never marked a back meets a dropdown with nothing in it
      and no way of knowing why.
    - **This is the component…** puts the piece's own box first. That is
      **fault 42 again** — a game is worked through a BOX at a time — arriving
      at the last place in the room that still treated the whole game as one
      flat list.
    ⭐️ The part worth keeping: **nothing says which set a box of sheets
    answers to.** A component belongs to a `group` the person named ("the
    supplement"); a piece comes off a sheet whose id begins with a box
    ("plague-07"). Rather than ask, or match names and be clever, the room
    **learns it from the links already made** — a hundred pieces off this book
    linked to components in that set is better evidence than any rule about
    names — and falls back to the plain reading where nothing is linked yet.
    ⚠️ **It ORDERS; it does not hide.** A piece cut from a supplement may
    perfectly well be a core component that was reprinted, and a dropdown that
    had quietly dropped it would leave no way to say so at all. Each band says
    how many it holds, so the length is never a surprise.

52. ⭐️⭐️ **A DECK COUNTED AS ONE CARD READS AS DONE ON THE FIRST CARD CUT.**
    The end-of-job report the designer asked for by name was written, and then run
    over the real game — and it found something no reasoning had: **nine of
    that game's twelve decks** had never been set to *all different*, so each
    of them wanted ONE piece. A thirty-two-card deck with one card cut would
    have shown as accounted for, and the box as complete when it is not. That
    is fault 36's whole subject, and nothing in the room had ever said so.
    ⚠️⚠️ **And the rule is the KIND, not the number.** `26 Damage counters` has
    exactly the same shape — a quantity of twenty-six wanting one piece — and
    is exactly RIGHT, because one design is printed twenty-six times. Written
    to include `card` as well as `deck` and read against the real list, the
    finding count went from nine to twenty **and all eleven it added were
    wrong**: the two PLAYER MARKER cards are two designs of one component (fault 18),
    and the nine *anti-flyer armament card* lines are one card printed twice.
    ⭐️ That is habit 2 below earning its keep for the second time: reading the
    game's own data changed this rule twice in ten minutes.
    ⚠️ And the report says all of this and **fixes none of it** — the same rule
    as the kinds, the look-alikes and the splitting.
    ⚠️ With no contents list at all, every piece answers to nothing on it —
    which is not a finding, it is the absence of a list. The report says that
    instead of printing 221 names under a heading that reads as a fault. *The
    checklist is optional and must not quietly become compulsory.*

53. ⚠️⚠️ **A FAILING COMMAND IN AN EXIT TRAP, UNDER `set -e`, ENDS THE TRAP
    AND TAKES THE RUN'S EXIT STATUS WITH IT.** `check/check.sh` answered **1**
    on a run in which all 313 checks came out right and the green line printed.
    Its trap was `[ -n "$ROOM_PID" ] && kill "$ROOM_PID" 2>/dev/null; rm -rf
    "$TMP"` — and the `kill` fails **routinely**, because the last section of
    the file closes the room *from the room*, so the process has usually gone
    already. Two costs, the second worse than the first: a clean run reported
    failure, **and `rm -rf` never ran**, so every such run left its throwaway
    66-sheet game behind in `/tmp`. Two were sitting there.
    ⭐️ It was found by the exit status disagreeing with the report, which is
    the only reason it was ever going to be found: nothing in the output was
    wrong. *An exit code that lies teaches you to stop reading it.*
    `|| true` on both commands, and no bare `&&` in a trap.

54. ⚠️⚠️ **ON THE DISK IS NOT IN THE REPOSITORY.** The guide's eight pictures
    were written, looked at, referenced by name — and `.gitignore` was keeping
    every one of them out, because the rule that lets pictures into `docs/` is
    `!docs/*.png` and they live one level down in `docs/guide/`. The check
    written for exactly this asked `os.path.exists`, which was true here and
    would have gone on being true for ever, over a guide that showed a stranger
    eight broken images. It asks **git** now.
    ⭐️ The general form, and it is worth reading twice: **a check that asks the
    easy question in place of the real one is worse than no check**, because it
    is a green light over the fault. "Is the file there?" was easy; "is the
    file where a reader will look for it?" was the question.

55. ⚠️⚠️ **A NAME THAT WRAPS ACROSS A LINE BREAK IS INVISIBLE TO A SEARCH.**
    Taking one game's names out of this repository took three passes. The
    first took out the publisher and the products; the second the component
    names; and a search after the second still came up clean while a two-word
    name sat in `CLAUDE.md` with the line ending between its two words. An
    ordinary search cannot see it, and neither can a person reading down a
    list of matches, because it is not in the list.
    ⭐️ So the check reads every file **with the line breaks taken out**, and it
    is the only reason the last one was found.
    ⚠️ Its first run reported the repository as riddled with all twenty-seven
    forbidden words: it had found **its own list**, which is written in one of
    the files it searches. The list is cut out of whatever file carries it —
    and only the list, so a name really written into that file is still caught.
    ⭐️ The general shape, worth more than this instance: **a check whose
    subject includes the check itself needs to say so, or it reports its own
    definition as the problem.**

56. ⭐️⭐️ **A DECK OF THIRTEEN DESIGNS CAN BE A DECK OF THIRTY-TWO CARDS.**
    The designer, 24 August 2026: *"I need to finalise a deck. It contains 13
    different cards, one of which has 20 copies — thus 32 cards in total. I
    have marked the 20x component, but [the deck] reads — relatively
    justifiably — 13 of 32. How do I fix given the deck is technically
    complete?"*
    Both halves of the answer were already in the room and neither was
    speaking to the other. `each` says this line's thirty-two cards are not
    one design printed thirty-two times (fault 36); `copies` on a piece says
    the game wants **this** design twenty times (fault 47) — and the checklist
    counted **pictures** where the quantity means **cards**, so a deck that
    really was finished could never reach its own number and the box could
    never read as done. A cut piece now **fills as many of the wanted quantity
    as the game wants of it**.
    ⚠️ Fault 47's warning stands and is not weakened: these are still two
    questions. Nothing is cut twice, **nothing guesses `copies`**, and taking
    the mark off puts the deck straight back to 3 of 24 — a check tries
    exactly that. All this stops is the room asking for pieces that would be
    identical to ones it already has.
    ⭐️ And the count says what it is made of — *3 pieces, repeated to fill
    it* — because **32 of 32** over thirteen pictures reads as a miscount to
    the person who cut them.
    ⚠️ The worked-out counts (`state`, `need`, `got`, `cut_pieces`…) are
    stripped where the list is **saved** now, rather than by the page: that
    list of names was written out in the page and again in its check, so a new
    count would have been forgotten by one of them and written to disk as
    though somebody had answered it. **Fault 24, sixth time.**

57. ⚠️⚠️ **A DROPDOWN BUILT ONCE IS A DROPDOWN THAT GOES STALE — AND IT READS
    AS A SHORT LIST, NOT AS AN OLD ONE.** The designer, 24 August 2026: *"I have
    marked 6 different elements as card backs. When I do 'choose several at
    once' only one of those backs appears in the backs dropdown. It should
    contain the other card backs so I can batch add it (or I have to go
    through every card manually)."*
    The bulk bar's two lists were each rebuilt only when **the answer to a
    different question** changed: the backs list when the narrowing switched
    on or off, the components list when the box being shown changed. So the
    backs list was built at the moment the first back was marked and never
    again, and the components list would have missed a component added while
    the bar was open — **fault 44's subject**, the thing you have just made
    being the one thing that is hidden. Nothing errored; both simply went on
    offering yesterday, and the person is left doing by hand the very work the
    bar exists to save.
    ⭐️ The rule: **a list is rebuilt from what it is MADE OF, not from what
    prompted it.** `fillSelect()` builds the options and puts them up if they
    differ from what is up — and restores the choice already made, or
    replacing the markup would quietly blank it (fault 48's family).

58. ⚠️⚠️⚠️ **SETTING A PIECE ASIDE HALF WORKED, EVERY TIME, AND HALF WORKING
    IS WORSE THAN NOT WORKING.** The designer, 24 August 2026: *"setting pieces
    aside seems pretty temperamental — I just tried to get rid of multiple
    copies of [one piece], but didn't seem to work, either in bulk when
    suggested, or individually when selected in #pieces."*
    The file moved into `pieces/spare/` every single time. What did not happen
    was the **writing down**: `set_aside()` marked the piece only `if st in
    book` — only if the manifest already had an entry for it — and **a
    duplicate you want rid of is precisely the piece nobody has bothered to
    name**, so it has no entry at all. The room draws the Pieces list from the
    manifest, so the piece came back on screen undimmed, unflagged and
    apparently untouched. Press it again and nothing happened at all, because
    the file had already gone. **Reading the designer's own project found three
    pieces sitting in exactly that state** — in the spare folder, with nothing
    anywhere saying so. Habit 2 again.
    ⚠️ And it was not only cosmetic: a re-cut reads that mark to put the piece
    straight back into the spare folder, so an unmarked spare would have been
    **handed back to the game** the next time its sheet was cut. Fault 19's
    whole subject, arriving by a door nobody had tried.
    ⭐️⭐️ The rule, and it is worth more than the fix: **the folder is the
    truth; the mark is only the record of it.** `adopt_spares()` makes the
    record agree with the folder — where the list is read, and again before a
    re-cut sweeps the folder and destroys the evidence. A piece dropped into
    `spare/` by hand is set aside, and the designer's three repair themselves the
    moment they open the Pieces list.
    ⚠️ The room also **said it had worked whatever happened**: the press
    flashed *"Set aside. Nothing was deleted."* even when the room refused,
    and said nothing at all when no answer came. A message that cannot fail
    teaches you to stop reading it (fault 53's lesson about exit codes, in the
    interface this time).
    ⭐️ And the missing door: getting rid of *several* copies was only ever
    possible from the look-alike bar, which appears only when the room has
    spotted the resemblance itself. The *choose several at once* bar sets the
    ticked pieces aside now, and offers to bring them back when they already
    are.

59. ⭐️⭐️ **THE ROOM STARTS ITSELF AGAIN, BECAUSE THE ADVICE WAS RIGHT AND THE
    ERRAND WAS THE PROBLEM.** The designer, 24 August 2026, having been told twice
    in one day to close the room and open it again: *"is there a way to build a
    relaunch button into the browser tab it uses somehow?"* Fault 38's banner
    says exactly what to do and then sends somebody who *"[doesn't] like
    terminal at the best of times"* to go and find a Terminal window to do it
    in. So the banner carries the button that does it, and so does the top bar
    of every page. `os.execv` in `main()` — same window, same port, same
    command, **new process**, which is the whole point, because a running
    program cannot re-read itself.
    ⚠️ **A RELAUNCH THAT CANNOT COME BACK IS A QUIT.** The button is pressed
    at exactly the moment the code has just changed — which is exactly the
    moment it might not parse — and once the old process has gone there is
    nothing to fall back to. `code_that_will_not_start()` reads and compiles
    the new code **before** anything is stopped, and a room that would not
    start again refuses to stop, saying which file and which line.
    ⚠️ **The same guard as closing, and only one of it.** A restart is a close
    with a promise attached, so a table holding an edit not yet written down
    holds this door exactly as it holds the other (fault 21). Two copies of
    that question would drift, and the one that drifted would be the one that
    lost the work — so `ask()` in `close.js` is one function and only its last
    line differs.
    ⚠️ **"It answers" is not "it came back".** The old room answers perfectly
    well for the half second before it goes, so the page waits for a room
    reporting a **different** `started` before it reloads.
    ⚠️ And it strips `--open` from the arguments on the way through: the
    launcher opens a browser when it starts, which is right the first time and
    wrong now — the tab that pressed the button is sitting there waiting to
    reload itself, and a second tab is a mess somebody has to tidy up.
    ⭐️ The exec is the **last thing the old process does**, in the main
    thread, after `serve_forever` has returned and the socket is closed —
    doing it from the request's own thread races the main thread's tidying up,
    and whichever won, the room might simply be gone.

60. ⭐️⭐️ **A FROZEN WORD CANNOT ANSWER "HAS IT STALLED?", AND THAT IS THE
    ONLY QUESTION ANYBODY ASKS DURING A WAIT.** The designer, 24 August 2026,
    importing from a link: *"status says 'Fetching...' but would be much more
    useful if that were an actual progress bar or at the very least something
    a little more animated so i can see if it's stalled."*
    The room already had a job with progress on it — the rendering step counts
    pages as they land (fault 8) — but the **download** was one `r.read()`, a
    single blocking call with nothing to report and nothing to look at. So it
    is read in pieces and counted: a bar that fills where the size is known
    and creeps where it is not, the size that has arrived, the seconds since
    it began, and ⭐️ **when nothing the room says has changed for ten seconds,
    it says so in as many words** — which is what somebody is really asking,
    and the room is better placed to notice it than they are.
    ⚠️ **`read1`, not `read`.** `read(n)` waits until it has all n bytes, so
    the count jumps in lumps and sits perfectly still between them — the very
    thing being fixed. `read1` hands back whatever has arrived.
    ⚠️ The messages already said their own counts in words (*"rendered page 3
    of 40"*) and the page appended *"(3/40)"* to them as well. The numbers go
    to the **bar** now and the words are left alone.
    ⭐️⭐️ And what they were actually importing found a second thing: **a
    Google Doc is not a file, it is a thing Google will make a file out of.**
    A document, sheet or slide deck has no download at its own address — the
    link opens the editor, and what comes back to anything else asking is the
    editor's own web PAGE. So the room was reporting a perfectly well shared
    document as *not shared* (fault 9's rule, quite correctly applied to the
    wrong situation). Asked to `export?format=pdf`, the same document comes
    back as a PDF. ⚠️ Only the plain `/d/<id>` form: a **published** link
    (`/d/e/<id>/pub`) is a different address with no export behind it, and
    quietly rewriting it would break a link that works.

61. ⚠️⚠️ **A BUTTON THAT READS A CONTROL THAT IS NOT THERE DOES NOTHING AT
    ALL, AND SAYS NOTHING EITHER.** The designer, 25 August 2026: *"I have the
    contents list for the core box, pasted it into the checklist field, but
    the 'Add them' button doesn't seem to do anything."*
    It read `#wImportEach` — the tick that says *these are all different*
    (fault 36) — and **that control had never existed in the page**. Reading
    `.checked` off `null` throws, the handler stops on that line, and the
    press does nothing whatsoever: no request, no message, no error anybody
    would see. The list sits there looking ignored.
    ⚠️⚠️ **And every check the room had went through the API**, which worked
    perfectly the whole time. That is **fault 54's rule** — a check that asks
    the easy question in place of the real one is worse than no check, because
    it is a green light over the fault. The real question was never "does
    `/wanted/import` work?", it was "does the button work?". There is a check
    that presses the button now, and putting the fault back turns six of them
    red.
    ⭐️ The other half of the same message — *"how do I add a separate contents
    list for core as opposed to [the supplement]?"* — was that a set could not
    be made from that panel at all, only from a component's own Set box. It
    can now, and **the room writes the new set down**: the id went onto every
    pasted component while the NAME lived only in the page, so the next load
    showed a bare id where a box's name should be. (`saveWantedAll()` had the
    same hole: it sent the components and not the sets they belong to.)

62. ⭐️⭐️ **A SHEET IS NAMED AFTER THE FILE IT ARRIVED IN, AND NOBODY NAMES
    THEIR SCANS WELL.** The designer, 25 August 2026: *"Ability to rename imported
    sections (I've imported two separate sets of things into the project, the
    first is the core box, the second [a supplement]). I need to rename them
    from their current file names (which are lots of nonsense)."*
    A box is a sheet id with the page number taken off (fault 42), and a sheet
    id is made from the file — so a game imported from a folder of scans is
    filed, and displayed, under whatever the scanner called it. A box can be
    given a name now, from its heading on Sheets, and every list in the room
    calls it that: the headings, the *Show* lists on Pieces and Match, the
    sheet cards, and the rail on the cutting table.
    ⚠️⚠️ **THE ID IS NEVER TOUCHED, and that is the whole design.** Pieces are
    named from the sheet id (`core_p03_00`), the outlines are filed under it,
    and a game reading the manifest knows pieces by it. This writes down what
    the box is CALLED. **Renaming what other things are keyed by is how work
    gets lost** — so the label in `project.json` is left exactly as it was as
    well, and clearing the name puts every sheet straight back to its file
    name.
    ⚠️ A label somebody typed themselves is left alone: only a label that is
    still the file's own name is swapped, which is what the slug test in
    `sheet_title()` is for.
    ⚠️ The Sheets page built its own heading out of the id while every other
    list asked `bookLabel()` — so a renamed box would have gone on being
    called by its file name everywhere else. **Fault 24, sixth time.**

63. ⭐️⭐️ **A WHOLE BOX OUT AGAIN, IN ONE PRESS — AND ONE QUESTION THAT SAYS
    EVERYTHING.** The designer, 25 August 2026: *"I'd like to be able to remove a full
    set of imported sheets in one click (after a confirmation). The [two of
    these books] are irrelevant here."* Thirty sheets taken out one × at a
    time is thirty questions, and **nobody reads the fourth** — which is worse
    for the one that matters than a single question that says the lot.
    ⚠️⚠️ This is **the one thing in the room that really deletes** (fault 19
    is the rule everywhere else), and what it deletes includes OUTLINES, which
    are the work. So the question says what goes, what stays, and what can be
    got back — and the second of those is asked separately: **cut pieces are
    kept unless somebody says otherwise**, because nothing else in the room
    throws a piece away.
    ⚠️⚠️ **And it says only what is TRUE about getting it back.** The first
    wording said Settings would put it back, which is half a lie: the outlines
    are kept in the room's history (fault 49) but the sheet records and the
    scans themselves are gone, so the scans have to be imported again. **A
    promise the room cannot keep is worse than no promise** — the check reads
    that sentence, so it cannot quietly drift into the comfortable version.
    ⭐️ One `remove_sheets()`, called by both doors — one sheet's × and a whole
    box — because a second copy of a deletion is a second copy that will drift
    (fault 24).

64. ⭐️⭐️ **A SET OF COMPONENTS TAKES ITS NAME FROM THE BOX OF SHEETS IT
    BELONGS TO.** The designer, 25 August 2026, minutes after naming their boxes: *"the
    +add a new box should surely take its cue from the headings I've provided
    in #import? Otherwise how will it differentiate?"* Quite so. The room had
    just been given those names and was asking for them again, by hand,
    hoping the two would match — a set called *Terror in the Dark* and a box
    of sheets called *Terror in the Dark* with nothing at all between them.
    Every set picker now offers **the game's boxes**, by the names given them,
    and picking one is the whole job.
    ⭐️⭐️ And it answers a question the room had been **inferring**: fault 51
    works out which set a box of sheets answers to from the links already
    made, which is good evidence once there are links and no help at all
    before. A person picking the box says it outright, so the group carries
    `book` and `boxSet()` believes that first. The ordering is right from the
    first component, before a single piece has been linked.
    ⚠️ It still only ORDERS — fault 51's rule is untouched, and a piece cut
    from one box may perfectly well be another box's component.

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
                         code than the page — see fault 38 — and the button in
                         that banner that STARTS THE ROOM AGAIN, in the same
                         window at the same port, which is what makes fault 38
                         a press rather than an errand. `/api/relaunch`;
                         `os.execv` in main(), after the socket is closed.
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
docs/make_guide_pictures.sh  photographs the room for GUIDE.md — a throwaway
                         game in a home of its own, on a port of its own, off
                         the demonstration sheet. ⚠️ Never point it at a real
                         project: opening a sheet SAVES.
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
| `pieces/spare/` | pieces **set aside** — the second identical terrain tile. The hand-over globs `pieces/` and does not recurse, so this folder is how a piece is kept without being handed over | yes |
| `pieces/index.json` | where each piece came from: sheet, box, ink | yes |
| `manifest.json` | what each piece IS: name, kind, note, turn, component, **its back** (another piece), **how many copies the game needs** | ⭐️ **NO** |
| `wanted.json` | the checklist | ⭐️ **NO** |
| `cache/` | thumbnails, suggestions, piece statistics | yes |
| `export/` | ⭐️ what leaves the room: the pictures, the inventory, the contact sheet, the printable checklist, the cut files, and **the cut checked against the contents list** — as a page to print and as JSON for whatever ingests the pieces | yes, whole, every time |
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
check/check.sh          # 391 checks, about a minute
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

It runs the **end-of-job check against the contents list** on a bench built
for it — a deck three cards into twenty-four, a counter that is done, and one
cut piece answering to nothing — and the two checks that matter most are the
ones about it keeping QUIET: that a counter printed twenty-six times is **not**
reported as a deck counted short (fault 52), and that a game with no contents
list **says so** rather than reporting every piece it has as an orphan.

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

### ⭐️ Two habits that have each caught a real fault

**1. Try the teeth of a new check before believing it.** Put the fault back and
watch it go red, then take it out again. This has been done three times and
found a blunt check twice: the silence rules in `guessing_the_kind.py` stayed
green when the tile rule was widened to swallow whole boards, because every
case in them happened to be settled by a *different* rule. A check that has
never failed has not been shown to work.

**2. ⭐️⭐️ READ THE REAL GAME'S DATA BEFORE TRUSTING YOUR OWN REASONING.**
`guess_kind()` was written from first principles and looked entirely sensible.
Run over the 79 real pieces the designer had already cut and named, **two of its
five rules were wrong** — it called two terrain tiles rulers, and the one thing it
ever called a tile was a turn template. No amount of thinking would have found
that; ten minutes of reading would, and did. See fault 25.

⚠️ **Reading is not the same as pointing a check at it.** The measurements are
already sitting in the project's own `cache/stats.json`, the
names in the game's own manifest, and reading those with a
throwaway script touches nothing. **Never write, never serve it, never open a
browser at it** — see the warning below, which is about exactly that. When a
rule is about what real cardboard is like, the real cardboard is on the disk.

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
