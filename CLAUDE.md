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

## Status (2 September 2026)

**2 September**: the designer, mid-way through cutting a real game's sheets:
*"Three keep coming up as blank... The numbering is also haywire - more cut
than I have outlined?"* The rogue pieces were **one and two pixels** of ink,
stranded by the fill of the tile beside them, and `keep()` has no floor at
all for a shape a person drew — so a single pixel was cut, numbered and
counted as a component. ⚠️⚠️ **See fault 96, and read the middle of it: the
first diagnosis was reasoned out of the source, was wrong, and cost the
designer an hour.** Their own `index.json` gave the answer at a glance. That
is habit 2, ignored because the code seemed to explain itself.

**1 September**: the designer, having cut and named every component in the
second game's core box and ticked every one of its seventeen sheets: *"There
should now be a way to move those (not out of sight) but just to ensure they
don't pop up anymore, no need for them to populate dropdowns, or the sheets
page anymore etc."* Built as **filing a set away**. ⭐️ See fault 91 — and note
that the room already had a mark for a box that is *not being cut*, and this
is the opposite one: a filed set **counts as done**, which is the whole reason
it could not be the same list.

**1 September, later**: the designer, given a project set up by hand for
600dpi scans: *"would be helpful if that was shown somewhere visually!"* ⚠️⚠️
It was not merely invisible — **the editor never learnt the project's scale at
all**, so every inch figure on the table was wrong for any project not at 300,
and a shape laid from the shelf came out the wrong size. See fault 93, and note
that the cut was right the whole time: **only the screen lied**, which is the
hardest kind of fault to see.

⚠️⚠️ **The same day, a check put a modal dialog on the designer's screen** in
the middle of their afternoon. See fault 92, which is worth more than the
feature: the guard was written on the copy of the launcher that was *expected
to fail*, and not on the copy expected to succeed.

⭐️ **Where it stands.** The room is built, checked by 729 checks, documented
end to end, and in daily use on two games. There is **nothing outstanding that
anybody has reported**: every item in BACKLOG's *NOW* is work chosen for its
worth rather than a complaint waiting to be answered.

⭐️⭐️ **27 August was the day the second game got large, and that is the theme
of everything below it.** The designer outlined seventeen sheets of it and the
cut took **eighteen minutes**; their scans turned out to be **170 megapixels
each**, twenty times anything the room had ever been tried on. Four different
costs in the cut scaled with *pieces × sheet area* and had been invisible until
then; one line was 85% of the whole thing. ⚠️ **The lesson is not about
numpy.** It is that a benchmark built on the demonstration sheet answers a
question nobody is asking, and that the real game's own `project.json` — sitting
on the disk, free to read — said in ten seconds what an afternoon of reasoning
would not have. That is habit 2, on a subject it had not been used for before.

⚠️ **And a tidying-up pass found the second game's INITIALS in two places** —
one of them this file's own account of fault 84. The forbidden-word list held
full names only. See fault 90: **an abbreviation is a name.**

⭐️ **The same day turned up three faults that only a big game could show**: a
piece covering 90% of its sheet was binned as the scanner's frame and the cut
said nothing (fault 85); every tall piece on the Match board had been quietly
clipped since the board was built (fault 87, which is fault 4 again); and the
checklist toggle appeared dead for two reasons at once, one of them a field the
page had started depending on the day before (fault 86 — ⭐️ **read that one
before adding any field to a payload**).

**27 August, last**: *"ensure it is backed into the platform - I have a new use
for something like it immediately… ensuring that corridor pieces interlock
neatly."* Built as **Fit together**, `room/fit_pieces.js`. ⭐️ See fault 89, and
note which of the two uses shaped it: *do these edges meet* writes nothing and
is asked far more often than *join these two*, so the tool is a light table
with a join button on the end rather than the other way about.

**27 August, after that**: *"If I'm mending a piece, it seems obvious that
default should be to just recut that specific piece no?"* Built — and the
control that says which piece you mean already existed. See fault 88, whose
whole weight is the **fallback**: cut one piece when the numbering has shifted
and the names land on the wrong pictures.

**27 August**: *"Pressed cut, and it is INCREDIBLY slow… it took 1081 seconds
to cut the 17 sheets."* ⭐️⭐️ Read their `project.json` and the reason was
immediate: their sheets are **170 megapixels**, twenty times anything this had
been tried on, and four separate costs scaled with *pieces × sheet area*. See
fault 84 — and note that it was made safe by **running the old code beside the
new one and comparing pixel for pixel**, which is the only honest way to speed
up the cut. 1081s → about 140s. In the same day: a piece covering 90% of a
sheet was binned as the scanner's frame and the cut said nothing (fault 85),
and the checklist toggle appeared dead for two reasons at once (fault 86, whose
second half was mine from the day before).

**26 August, last thing of all**: *"when something is a deck it should also
report that each component dropped is unique in the checklist ie '[n] needed'
rather than '1 needed'."* The room had been saying so in its own end-of-job
report and counting the other way. See fault 83 — ⭐️ and read the part about
`each: false`, which is a **stamp every component carries**, not an answer
anybody gave: the first version of this rule was correct, checked, green, and
could not have fired on a real list.

**26 August, later still**: *"in Checklist it's generally very apparent that
certain elements comprise more than one piece (eg a deck of cards). But this
isn't carried through to the Match drag and drop function."* Right, and the
room had known the right answer the whole time — Match was the one list asking
a cruder question of its own, in **two** places. See fault 82, whose careful
half is the back: *"match should include an item for the relevant back of each
deck."*

**26 August, later**: *"I think pressed 'cut every outlined sheet', next to
which it said '22 not cut yet'. But it then started cutting every single page I
have ever outlined in the entire game."* Right, and the room's own words had
been saying the correct thing the whole time while the code did something else.
See fault 81 — ⭐️ whose lesson is that **a sentence on a button is a claim
nothing is checking**, and this button had no check on it at all.

**26 August, the same day and the important half of it**: the app was built,
signed, and *correct in every particular* — and it **did not work**. macOS
keeps an app out of `Documents`, `Desktop` and `Downloads`, and for a bundle
whose executable is a script it does not even put up the box that asks: it
simply refuses. The designer's projects lived in `~/Documents/Cutting Room`, so
the room opened and then said *"Operation not permitted"* about its own folder.
See fault 80 — ⭐️ and note that **nothing but pressing it on a real machine
would ever have shown that**, which is this file's oldest lesson arriving on a
new subject. The folder moved; the launcher can be told where it is; and the
room now says so at the moment the launcher is written.

**26 August**: the last of *"a simpler way to open and quit. I don't like
terminal at the best of times."* Quitting and restarting were already a press
on the page; **opening still put a Terminal window on the screen**, and now it
does not — `--install-launcher` writes **`Cutting Room.app`**. See fault 79,
whose whole content is that **the Finder does not launch an app the way a
shell does**: the bundle came up under Rosetta and numpy would not load, while
the identical script run from a terminal worked perfectly every time.

**26 August, earlier**: *"I'd like to be able to just export a set of cut pieces, rather
than everything in one project folder."* Built — **Take away** offers the whole
game or one box of sheets, and a set goes into a folder of its own. See fault
78, whose careful part is that an export folder is replaced **whole**, so a set
written into `export/` would have silently destroyed the export of everything
else.

**25 August, and the other half of the same message**: *"one quick tool that
would be useful would be the ability to mask off a section of any given sheet,
so that it doesn't get run for suggestions."* Built — **Mask off**, `M`. See
fault 77, whose interesting part is that the kept draft had to learn what
question it was an answer to.

**25 August, after that**: *"the suggested outline feature is improved, still
rough though. It sometimes creates insanely small artefacts."* Right on both
counts — there was no floor under the automatic pass worth the name, and the
number that fixed it was **read off the designer's own 322 cut pieces** rather
than reasoned out. See fault 76, and note what it turned up: fault 71 shared
the tracing and left the **choosing** written out twice.

**25 August, last thing**: three keys, asked for in three messages — *"is there
(or can there be) a shortcut for duplicate piece please - needs to be a button
that won't trigger anything else though (maybe the + = key?)"* and *"also a
shortcut to delete the selected piece (x maybe?)"* and *"another shortcut for
work on this piece alone"*. All three were free, all three are bound, and see
fault 75 for the things that made them more than a line of code each.

**25 August, before that**: the designer, asked about the light ground that had
been first on the list since 22 August: *"I'm no longer certain a white
background view is worthwhile."* Agreed, and it came off — but there was a real
fault underneath the cosmetic one, and it is *NOW* item 2. See fault 74. What
was done instead was **a report you can act on**: every piece the end-of-job
check names now opens it. See fault 73.

**25 August, the first thing off the list**: *learn the checklist from what is
cut* — the inverse of Match, and the answer for a game whose contents list
nobody has typed out. See fault 72.

**25 August, later still**: *"the auto cutting pass is essentially pointless."*
Three faults, of which the loudest was one word — every suggested outline was
handed to the editor as a **curve**, so a rectangle was drawn as a Bézier
through its corners. See fault 71, and `check/the_automatic_pass.py`, whose
fourteen checks about **saying nothing** are the half that matters.

**25 August, later**: the designer, working with two boxes of one game imported and
only one of them being cut, on the figure at the top of the checklist: *"I find
the overall checklist % isn't very helpful."* A percentage over a whole game
answers a question nobody asks — see fault 68, which is the divide they asked
for in the same breath: **a set can be put by for later** and stops being
counted, and **every set carries its own figure**. In the same message: no way
to add a section to the checklist at all (fault 69).

**25 August** was a day of the designer importing rather than cutting, and every
complaint was about **sets of sheets**: twelve files that arrived as twelve sets
of one (fault 65), a box that could not be named or removed (faults 62 and 63),
a set of components that would not take its name from the box it belonged to
(fault 64), and *Add them* doing nothing at all because it read a tick box that
had never been in the page (fault 61). ⭐️ It also turned up **two functions
called `slug`** (fault 66) — a name silently replacing another for a whole
module, surfacing as a set of sheets called *40*. The day ended with the pieces
**held back** becoming a list you can open (fault 67).

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

⚠️⚠️ **WHAT IS NEXT IS IN `BACKLOG.md`, AND IT IS NOT WRITTEN HERE.** This
file used to carry its own numbered *next up* list beside BACKLOG's *NOW*, and
by 25 August the two disagreed: the first item here was a user guide that had
been built and photographed two days earlier. **That is fault 24, in the
documents rather than the code**, and it is the one this codebase warns about
most. So there is one list, it lives in `BACKLOG.md` under *NOW*, it is
numbered in the order the work is worth doing, and the answer to *what next* is
**the first thing on it**.

⭐️ **What does belong here is the rule the order was made with**, because a
list can be re-sorted and a rule cannot:

1. ⭐️⭐️ **Naming is what is expensive, not cutting.** A feature that removes a
   step from naming beats one that speeds up cutting, every time. It is said
   three times in this file and reading the real game's data has proved it
   twice.
2. **Then what the designer has asked for and not yet got** — an ask that keeps
   slipping behind cleverer work is an ask being quietly refused.
3. **Then what a stranger meets.** This repository is public and the room is
   for far more people than the one who commissioned it; a thing nobody can try
   without owning a board game first is a thing most people never see.
4. **Cosmetic last**, and never before something that is silently broken.

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

65. ⭐️⭐️ **FILES IMPORTED IN ONE GO ARE ONE SET.** The designer, 25 August 2026: *"I
    just imported 12 new files into the project, assuming they would all stay
    together as a single set of 12 sheets, but they've all turned into
    separate sets, which is highly inefficient. I think it is a reasonable
    view that files imported in one go will form a single set."*
    It is a reasonable view, and it was not what happened: a sheet's id is
    made from the file it arrived in, so twelve files made **twelve sets of
    one sheet each** — twelve headings, twelve entries in every *Show* list,
    and nothing to work through a box at a time with (fault 42, arriving from
    the other end).
    ⭐️ The name is taken from what the person has already said, in this order:
    **the folder they dropped**, then **the part of the file names they all
    share** (`sail-01`, `sail-02` → *sail*), and only failing both, the day it
    arrived. All of them can be renamed on the heading (fault 62).
    ⚠️ One file is left alone — it is its own set already, and a prefix would
    invent a heading for a single sheet. ⚠️ And a set that already has a name
    keeps it: dropping more sheets into an existing set must not rename it
    back to its file names.
    ⭐️⭐️ **And the ones that came in before that was true.** *Put these N into
    one set…* on Sheets gathers **the sheets shown** — so the search box is
    how they are chosen: type *sail*, see twelve, press once. It works by
    writing `book` on each sheet, so **not one id changes**: pieces are named
    from those ids and the outlines are filed under them. That also makes it
    undoable — the same press with an empty name puts them back in the sets
    their file names give them.
    ⚠️ `bookOf()` now asks the sheet first and falls back to the id, in the
    page and in the room. It is still ONE rule in each (fault 42).

66. ⚠️⚠️⚠️ **A SECOND DEFINITION OF A NAME DOES NOT CLASH IN PYTHON, IT
    SILENTLY REPLACES THE FIRST** — for the whole module, including code
    written hundreds of lines above it. `cutting_room.py` had **two functions
    called `slug`**: one at the top that makes an id, one further down that
    makes a readable file name, with different second parameters. Every
    `slug(...)` in the file was reaching the second one, whichever its author
    meant — so `slug(x, 40)`, written for *keep 40 characters*, was passing 40
    as the **fallback**.
    ⭐️ It surfaced as a set of sheets called **40**, which is the sort of
    thing you can stare at for a long time. The two really are different jobs
    and now say so: `slug()` makes an ID and drops a file extension,
    `file_slug()` makes a file name.
    ⚠️ Sheet ids made under the old shadowing kept the extension in them
    (`a-scan-pdf-01`) and those sheets are on people's disks, so
    `sheet_title()` accepts **either spelling** when deciding whether a label
    is still the file's own name.
    ⭐️ There is a check now: **nothing in any of the room's modules may be
    defined twice**, top level. It reads the AST of all four, and its teeth
    were tried by adding a second `slug` and watching it name both lines.

67. ⭐️⭐️ **A MARK YOU CAN PUT ON A PIECE AND NOT GET BACK OFF THE PILE IS A
    NOTE TO NOBODY.** The designer, 25 August 2026: *"I want a way to see, on
    #pieces, a list of every piece I have marked hold back — at the moment the
    only route to them is opening pieces one at a time or printing the whole
    check against the contents list."*
    *Hold back* had been writable for days and unreadable the whole time. It is
    the one mark on a piece the room never puts there itself — the artwork wants
    redoing, the rules are unclear — so it is written precisely when somebody
    means to come back to it, and coming back meant opening two hundred pieces
    or printing a report. **A chip that gathers them, and the reason printed on
    the row**, because a list of six pieces that all say nothing but *held back*
    is a list you still have to open six times.
    ⭐️ **And the count in the report is the door.** *1 piece held back* was a
    number with no route to the piece. The report's counts of held-back and
    unnamed pieces are links into that chip now — the first half of the *way in
    from the report to the piece* this file has had on its list. ⚠️ One
    `showPieceFilter()` does it, shared with the chips themselves, or the two
    ways of choosing a filter would drift apart (fault 24, seventh time), and it
    has to survive being called before the pieces have been fetched.
    ⚠️⚠️ **The hard part was that the two counts are not the same count.** Every
    chip on Pieces shows what is **set aside** along with the rest, dimmed —
    nothing on that page is ever out of sight, and a filter that quietly drops
    rows is fault 44's shape. The printed check counts the other way: a piece
    set aside is counted as set aside and as nothing else. Both readings are
    right, so the answer is neither to hide the pieces nor to change the report:
    **the list says what the difference is made of** — *2 pieces in all — 1 set
    aside*. Two numbers that disagree in silence is what a link between them
    would otherwise have created.
    ⭐️ And an empty list says **which** empty it is — *Nothing is being held
    back here* — for every chip, not only this one. The commonest empty list on
    this page is the good answer, and a blank page reads as a broken screen
    (fault 35's lesson, arriving on a different page).
    ⚠️ Its own check taught something too: a `querySelector(...).click()` on a
    control that is not there **throws inside the page, and the throw ended the
    whole browser section** — eighty checks after it never ran, the bench kept
    the piece the block had made, and four more checks went red for reasons that
    were nothing to do with them. Trying the teeth showed that, not the code.
    *Guard the click: a check that crashes reports one fault as six.*
    ⚠️ And the bench borrowed *whatever second piece it found* to be the
    held-and-set-aside one. There was no second piece, so the stem came out
    `undefined`, the room dutifully wrote a manifest entry under that name, and
    the check went red pointing at the page rather than at itself. It makes its
    own piece now.

68. ⭐️⭐️ **A PERCENTAGE THAT COUNTS WORK YOU HAVE DECIDED NOT TO DO CAN
    NEVER REACH 100, SO IT SAYS NOTHING.** The designer, 25 August 2026: *"I find
    the overall checklist % isn't very helpful — would be preferable to have a
    % completion per set of files uploaded for cutting. eg in [one game] I've
    decided to not yet cut some pieces which belong to advanced rule sets that
    I don't want to bring in the v1 of the game. Maybe I need a user-defined
    divide between live cutting and a sheet backlog/future cutting which I may
    have uploaded only for convenience?"*
    Both halves were right and they are one feature. **A set can be PUT BY**:
    it stays exactly where it is, nothing is deleted and nothing is hidden,
    and the room stops adding it up — its sheets leave *To outline*, its
    components leave the headline figure, and the end-of-job report lists it
    under *Sets put by for later* instead of as things missing. **And every
    set carries its own figure**, because the work is done a box at a time
    (fault 42) and so is the reading of it.
    ⭐️ This is **fault 50's lesson arriving on a number**: a list nobody can
    shorten is a list nobody opens, and a figure nobody can move is a figure
    nobody reads. The question to ask of anything the room counts is *what
    makes this reach 100?*
    ⚠️ **ONE SWITCH, NOT TWO.** A set of components made from a box of sheets
    — which is how they are normally made (fault 64) — answers to **that box**,
    so the button on the Sheets heading and the one on the Checklist heading
    press the same thing. `later` is a list of keys on the project:
    `book:<id>` for a box of sheets, `set:<id>` only for a set that has no box
    of its own. `group_later()` in the room and `groupLater()` in the page are
    the one rule each. Fault 24, for the eighth time.
    ⚠️ **And two numbers that disagree in silence are worse than one blunt
    one** (fault 67). The whole-game figure is still worked out and still
    true; the page leads with the live one and **says what the difference is
    made of** — *"Not counted here: 30 components in 1 set put by for later.
    The whole game is 44 of 221 (20%)."*
    ⚠️ Nothing is inferred. Fault 51 works out which box a set answers to from
    the links already made, for **ordering** — and its rule is that it orders
    and never hides. Using that guess to drop a set out of a count would break
    it, so only a `book` somebody has actually picked counts here.

69. ⭐️ **EVERY DOOR MADE A SET ON THE WAY PAST TO SOMETHING ELSE.** The designer, 25
    August 2026: *"very obvious quirk I just noticed - I cant see how to add a
    new section to the checklist (eg to add details of the new sail set I just
    uploaded and have started cutting)."* Quite so: a set could be made from a
    component's own **Set** box, or from the panel that pastes a whole
    contents list in — both of them on the way to doing something else — so
    somebody who wanted the **section** first had nowhere to press.
    **+ Add a set** is that door, and it offers **the boxes of sheets** first
    (fault 64), so the new sail set is sitting there by name.
    ⚠️ **An empty section would have been made, saved, and then invisible.**
    Every folding list in the room only draws a heading where there are rows
    under it — so the one thing they had just made would have been the one
    thing they could not see, which is **fault 44 exactly**. A set that is
    empty in the whole list is drawn anyway, and says what to do next.
    ⚠️ Only ever one that is empty in the *whole* list, never one the search
    or a filter has merely emptied, or every set would sprout a phantom
    heading the moment somebody typed in the find box.

70. ⚠️ **A CHECK THAT PRESSES THE THIRD BUTTON IN A ROW IS A CHECK THAT WILL
    PRESS THE WRONG ONE.** Two checks reached the *Remove this set* button as
    `querySelectorAll("button")[2]`, and adding *Put this set by* to that
    heading made them press the new button instead: three checks went red over
    code that was perfectly well, and one of them was about the room's only
    really destructive action. **A handle that is a position drifts; the words
    on the button are the thing being tested.** They find it by its text now.

71. ⭐️⭐️⚠️ **THE AUTOMATIC PASS WAS DRAWING EVERY PIECE AS A COASTLINE.** The
    designer, 25 August 2026: *"I'm also finding the auto-cutting quite strangely
    inaccurate — can we improve that somehow? the [one] sheet I uploaded felt
    like it should be very easy, blocky colourful shapes, but I basically had
    to redo the entire thing. There should be — given these are pieces of
    board games — a general thought that most shapes will be regular (squares,
    circles, rectangles), and will be strongly differentiated in colour terms
    from their background. Whilst the general shapes were OK-ish, the platform
    added a load of additional nodes and made some of the shapes look pretty
    odd. Easy fix for me to remove those nodes and straighten lines, but it
    means that the auto cutting pass is essentially pointless."*
    **Three separate faults, and only one of them was the tracing.** Each was
    found by drawing a sheet the way a real one arrives — unevenly lit,
    speckled, squashed through a JPEG — and watching what came back.
    - ⭐️⭐️ **EVERY SUGGESTION ARRIVED AT THE EDITOR AS A CURVE.**
      `addSuggested()` wrote `curve: true` on all of them, whatever they were,
      so a four-node rectangle was drawn as a **Bézier through its corners**:
      the sides bowed out and the corners rounded off. That is the whole of
      *"made some of the shapes look pretty odd"*, and it was one word.
      A suggested outline now says whether it is straight or curved, because
      **only the thing that traced it knows**. ⚠️ A page baked before this
      carries bare lists of points; those were always coastlines, so a list
      still means a curve.
    - ⭐️⭐️ **A COUNTER IS NOT A COASTLINE.** The designer's reasoning is
      right and the room now acts on it: where a blob really fills its own
      smallest box, it is handed back as **four corners** (snapped to the
      paper's axes when it is within two degrees of them, because a scan is
      never straight and a printed square always is); where its edge really is
      all one distance from its middle, as **a circle**. Everything else is
      traced as before. ⚠️ **It only speaks when the shape settles it** —
      fault 25's rule arriving on geometry. A hexagon fills 0.75 of its box
      and a circle 0.785, four per cent apart, so a circle must ALSO have a
      square box; ovals and hexagons are left to the tracing. Fourteen of the
      new check's twenty-nine are about it saying nothing.
    - ⭐️⭐️ **ONE FLAT COLOUR CANNOT BE THE GROUND OF A SCANNED SHEET.** The
      light falls off across the glass, so the far corner stopped counting as
      paper: it became a piece of its own, and the fringe of it lying against
      a real piece was **joined onto that piece**. That is where the extra
      nodes came from — put the fault back and a printed square comes back
      with **34 nodes and bent sides**. The ground is now measured in cells
      across the sheet and grown outwards from the paper it certainly is.
    ⚠️⚠️ **Two things keep that ground off the printing, and both were learnt
    by watching it walk on:** each step out may be **half a tolerance** (at a
    whole one, a pale board 85 units from the sheet colour was swallowed
    whole), and **a cell must be all one colour** (a rectangle a few degrees
    off true has a whole row of half-and-half cells along its top edge, and
    the ground crept up that ramp in steps of eight and ate four fifths of the
    piece). And whatever the ground does locally, a pixel more than twice the
    tolerance from the sheet's own colour is a piece.
    ⭐️ **Measure on the trimmed extent, not the furthest pixel.** A perfect
    300-pixel square with six pixels of JPEG ringing at one corner has a
    smallest box of 314 × 316 — it fills 91% of it and is not a square at all.
    Every extent is taken a quarter of a per cent in from each end. The same
    for the circle: it is asked *how much of this ring is at one radius* (nine
    tenths is a circle; a hexagon manages seven, a square under a half) rather
    than *how far does it wander*, because one blotch stuck to one side sinks
    any test made of extremes.
    ⭐️ **And the tracing itself is smoothed before it is thinned.** A printed
    edge on a real scan wanders a pixel or two either way, and Douglas-Peucker
    cannot tell that from a feature, so it planted a node at every bump.
    ⚠️ **One copy of all of it, in `sheets.py`.** `cutting_table.py` carried a
    second copy of the tracing and would have gone on drafting yesterday's
    outlines — fault 24, which would have bitten the moment this was written.
    ⚠️ **And the cached draft outlives the code that made it**: `/suggest`
    keeps its answer per sheet, so `SUGGEST_VERSION` is bumped whenever the
    drafting changes, or every sheet already drafted goes on being offered the
    old answer for ever with nothing to say so.
    ⭐️ Habit 1 earned its keep again: a morphological opening written to clean
    the speckled fringe turned out to earn **nothing** once the measures were
    made robust — the checks stayed green with it taken out — so it is not in
    the code. *A step no check can feel is a step nobody can maintain.*

72. ⭐️⭐️ **THE CHECKLIST LEARNT FROM WHAT IS CUT — the inverse of Match.**
    The first thing on BACKLOG's *NOW*, and it is there because **naming is
    the expensive part and it is expensive because it comes from outside the
    room**: *"3rd party lists etc, or rules manuals which may be tricky to
    comprehend."* A game with no contents list typed out — which is most
    games — had no way to keep score at all without somebody reading a manual
    first. But the pieces are already cut, already measured, and already
    grouped by the very look-alike hash the review uses, so **twenty identical
    counters become one line in one typing**, and a deck of thirty-two becomes
    one line with all thirty-two tied to it.
    ⚠️⚠️ **THE ROOM PROPOSES THE GROUPS AND NOTHING ELSE.** What a group is
    *called* is a judgement and stays the person's — fault 25 (the kinds),
    fault 18 (the look-alikes), fault 34 (splitting a line), and now this. A
    group nobody names **is not added**, the room refuses in a sentence rather
    than failing quietly, and a name somebody typed themselves is never
    overwritten. Both of those have teeth: break either and the checks go red.
    ⭐️ **What the room CAN see, and a printed contents list never can: how
    many DESIGNS a group holds.** Twenty pieces of one design is a counter
    printed twenty times and one is enough; twenty pieces of twenty designs is
    a deck and every one has to be cut. So *one is enough / all different*
    (fault 36) arrives with an answer already offered — ⚠️ as a **control**,
    because it is still a decision about what the game needs rather than about
    what was cut.
    ⭐️ **A group of several designs is numbered** — *Damage card 01, 02…* —
    because thirty-two pieces all called *Damage card* is fault 34's whole
    subject: whatever reads the manifest afterwards cannot tell one from
    another. The panel says so before the press.
    ⭐️ **And a name already typed is offered back.** Where every named piece
    in a group agrees, the box arrives filled in; where they disagree it stays
    empty, because two names in a group is a question and the room does not
    answer questions about what a thing is called.
    ⚠️ **The grouping is done in the PAGE**, off `alike()` and `sameSize()` —
    `sameSize()` was factored out of `alike()` for it, so there is still one
    rule for *"the same size"* rather than two that would drift (fault 24).
    What reaches the room is stems, a name and a decision.
    ⚠️ **And there is now one `new_wanted()`**, because three things make
    components — a pasted list, a line split into parts, and this — and an id
    made three ways is fault 24 waiting: two would agree and the third would
    file its components where nothing else looks.
    ⭐️ Its browser check was written believing an empty name box; the box was
    **already filled**, by the offer above, and the check went red over
    perfectly good code. *Looking at the thing is what showed it.*

73. ⭐️⭐️ **A REPORT THAT NAMES A PIECE AND CANNOT OPEN IT IS HALF A REPORT.**
    The end-of-job check against the contents list prints a `stem` on every
    line it finds — a piece answering to nothing on the list, a piece with no
    name, a piece held back — and there was no way from any of them to the
    piece. You read the name off the page and then hunted for it through two
    hundred rows, which is precisely the work the report exists to save. Half
    of the way in was built on 25 August (fault 67, the counts becoming links
    into a chip); this is the other half, **one piece at a time**.
    `?tab=pieces&piece=<stem>` on the project page opens it, and ⚠️ it is read
    in `fromHash`, **the one place the address is read**, rather than in a
    second chain of ifs (fault 24, and this file's most-repeated warning).
    ⭐️ A stem is the right handle because it is **the one name the room, the
    inventory and whatever ingests the pieces afterwards can all say** —
    `cut_from` in `inventory.csv` carries it — so *"this one is wrong, go and
    fix it"* is a link rather than a description.
    ⚠️⚠️ **THE HARD HALF IS THAT NOTHING MAY NARROW IT AWAY.** The Pieces list
    is held to a chip and to a box, and both stay put for as long as the page
    is open — so a piece asked for while a chip is on is sitting behind a
    narrowing chosen twenty minutes ago, and **the link would appear to do
    nothing at all**. That is fault 44 exactly: the one thing you asked for is
    the one thing hidden. `landOn()` clears the narrowing every time, rather
    than only on the fresh page load where it happens to be clear already.
    ⚠️ **And a piece the room has not got says so.** Quietly showing the first
    piece in the list instead would look for all the world as though the link
    had worked — fault 58's lesson, that half working is worse than not
    working.
    ⚠️ **The link acts once.** Left sitting in the address, every later hash
    change — pressing Pieces again after a look at Match — dragged you back to
    the same piece: a link that will not let go. It is taken out of the address
    as it is used, and the fragment left alone.
    ⚠️⚠️ **And only the copy the room SERVES carries a link.** The identical
    page is written into the export folder, which leaves the room and is meant
    to be read by somebody with no room running (fault 22) — a dead link to a
    local port sitting in somebody else's folder is worse than plain text. So
    `home` is passed by the route that serves it and by nothing else, and a
    check holds both halves.
    ⭐️ **A piece that answers to nothing also says how big it is**, in inches
    and millimetres. A size is very often the whole answer — a 0.6in square is
    a counter, a 2.5 × 3.5in rectangle is a card — and it costs nothing, being
    the same cached record the Pieces page reads.
    ⚠️ The report still **reports and fixes nothing** (fault 52). Its lines
    became doors; they did not become buttons.

74. ⭐️⭐️ **THE COSMETIC ASK HAD A REAL FAULT UNDERNEATH IT, AND THE ASK ITSELF
    DID NOT SURVIVE.** *A light ground* — *"I'd like to consider some different
    displays (eg white background rather than the black)"*, 22 August — sat
    first on the list for three days, and on 25 August the designer took it
    back: *"I'm no longer certain a white background view is worthwhile."* It
    went to *Ideas*, where a room-wide theme belongs: it costs one set of
    colour names read by both `room/room.css` and the editor's own `:root`
    (they hard-code one palette each, which is fault 24 waiting), a control,
    somewhere to remember it, and all eight guide pictures taken again — for a
    preference nobody had complained about since.
    ⭐️⭐️ **But the reading of it that was not cosmetic stayed.** A cut piece
    is a **transparent** picture, and it is shown on one hard-coded near-black
    (`#0A0F14`) in five places: the sheet card, the piece row, the Match cell,
    the look-alike tiles and the big preview. A pale card reads beautifully on
    that. **A dark counter's edge disappears into it** — and whether an outline
    clipped a corner is precisely the judgement fault 40 says the room must let
    somebody make. No one ground can be right for both, so the ground has to be
    a control: dark, light, or a chequer. That is *NOW* item 2, and the
    cutting table's own ground is deliberately not part of it.
    ⭐️ The general shape, worth more than this instance: **when an ask reads as
    a preference, look for the judgement it is getting in the way of.** The
    preference can be argued with; the judgement cannot.

75. ⭐️⚠️ **A SHORTCUT IS NOT THE SAME PRESS AS A BUTTON, IN TWO WAYS.** The
    designer, 25 August 2026, asked for `+` to duplicate the chosen piece and
    `X` to remove it. Both keys were free and the actions already existed —
    and the interesting part is neither of those.
    ⚠️ **A BUTTON THAT WOULD DO NOTHING GOES DIM; A KEY CANNOT.** `says()`
    disables *Duplicate* and *Delete* when no piece is chosen, so pressing
    them is self-explanatory. The same action on a key, with nothing chosen,
    did nothing whatever and said nothing either — which is exactly how
    somebody decides a new shortcut is broken (fault 58: silence reads as not
    working). Both now say what they would have acted on.
    ⚠️⚠️ **AND A DESTRUCTIVE THING ON ONE KEY MUST SAY HOW TO UNDO IT, IN THE
    SAME BREATH.** *Delete piece* is a deliberate press with a sentence on it;
    `X` is one finger and the piece simply vanishes. It says what went, that
    ⌘Z puts it back, and that nothing already cut is touched.
    ⭐️ **`X`, not Backspace, and the reason matters**: Backspace already means
    something else at this table — it drops picked NODES, or the last point of
    the outline being drawn — and **one key must not mean two things**, least
    of all when one of them destroys more than the other.
    ⭐️ And `=`/`+` sits BELOW the meta/ctrl guard in the handler, so ⌘= is
    still the browser's zoom and has not been quietly taken away.
    ⚠️ The delete is **one `deletePiece()`** now, called by the button and the
    key. It was written out twice for about a minute, which is fault 16 and
    fault 24 arriving on the one action in the editor that throws work away.
    ⭐️ *"Won't trigger anything else"* is the half the checks are pointed at,
    and it costs nothing: `typing(ev)` already stands the whole handler down
    inside a text field (fault 2). The check presses both keys in a note box
    and watches them do nothing but type.
    ⭐️⚠️ **The third key, `O` — *work on this one alone* — is the same lesson
    a third time and a fourth thing besides.** It hides every other outline,
    so on a sheet of forty counters it takes thirty-nine off the picture at a
    stroke and somebody who pressed it by accident is looking at an empty
    sheet. It says **hidden, not deleted**, and how to bring them back. ⚠️ And
    it is a **toggle**, undone by the same finger that did it — a key that
    could only switch the hiding ON would be fault 50's shape, a state nothing
    can clear. ⚠️ There were then **three** doors to it — the tick box, the
    key, and arriving from a link sent to mend one piece — so there is one
    `setSolo()` and all three go through it, or one of them would leave the
    tick box saying the opposite of what the sheet shows.

76. ⭐️⭐️ **THE AUTOMATIC PASS HAD NO FLOOR UNDER IT WORTH THE NAME, AND THE
    NUMBER THAT FIXED IT WAS READ OFF A REAL GAME.** The designer, 25 August
    2026: *"the suggested outline feature is improved, still rough though. It
    sometimes creates insanely small artefacts, which it should have the nous
    to manually remove before it presents its final suggestions."*
    ⚠️ **The test asked whether a blob was small in BOTH directions.** So a
    hairline crack between two counters — 1.3 inches long and four hundredths
    of an inch wide — was not small in both directions, cleared the area floor,
    and arrived on the sheet as a suggested piece. **The short side is the one
    that matters** and nothing was asking about it.
    ⚠️ **And the area floor was in the wrong units and seven times too low.**
    `(0.25 × 300 × 0.8)²` is 3600 pixels — four hundredths of a square inch.
    ⭐️⭐️ **Habit 2 settled both numbers in ten minutes.** The designer's own
    project has **322 cut pieces** with their sizes already in
    `cache/stats.json`: the smallest **short side** in the whole game is
    **0.28in** and the smallest **area** is **0.288 square inches**. So a floor
    at 0.25in and 0.05 square inches cannot drop anything that game holds, and
    the second is five times under its smallest piece. No amount of reasoning
    would have produced those; reading did, exactly as it did for the kinds
    (fault 25).
    ⚠️ **It is asked of the OUTLINE, not of the blob**, in printed inches,
    after the scaling — that is the thing being handed over, and `outline_of()`
    insets it by six pixels on the way past, which is what turns a scratch into
    nothing at all.
    ⚠️⚠️ **And it must NOT be part of `keep()`**, which the CUT uses as well: a
    thin outline somebody **drew** is a decision, and the room does not
    overrule those. This only refuses to make the suggestion in the first
    place.
    ⭐️⭐️ **Writing it turned up fault 71's other half.** That fault put the
    **tracing** in one place; the **choosing** — which blobs become
    suggestions — was still written out twice, in `cutting_room.py` and in
    `cutting_table.py`. So this rule would have reached the room and not the
    baked page, and an offline table would have gone on offering hairline
    cracks for ever with nothing to say why. There is one `trace_all()` now
    and both drafters call it. *A comment saying "one copy of the tracing" is
    not the same as one copy of the pass.*
    ⚠️ `SUGGEST_VERSION` bumped, or every sheet already drafted goes on being
    offered the old answer.

77. ⭐️⭐️ **A PART OF THE SHEET THE AUTOMATIC PASS IS TOLD TO LEAVE ALONE.**
    The designer, 25 August 2026: *"one quick tool that would be useful would
    be the ability to mask off a section of any given sheet, so that it doesn't
    get run for suggestions."*
    ⭐️ It is worth more than it looks. The flood is right about cards and
    counters on a plain ground and hopeless about a page of printed rules, a
    title panel, a bar of colour down the margin or the shadow the scanner cast
    down one edge — and **one** such region is enough to fill a sheet with
    suggestions nobody wants, which is the work the button exists to save. The
    person can see at a glance which part that is; **no measurement can**, and
    that is the whole argument for a tool rather than a cleverer rule.
    ⚠️⚠️ **THE KEPT DRAFT HAD TO LEARN WHAT QUESTION IT WAS AN ANSWER TO.**
    `/suggest` keeps its answer per sheet, so a mask drawn *after* a sheet had
    been drafted changed nothing whatever: the old suggestions were served for
    ever and the new tool looked as though it did nothing at all. That is fault
    58 — half working reads as broken — and the fix is that the cached record
    now carries the regions it was made with and re-drafts when they differ.
    ⭐️ Its teeth were tried, and it is the whole feature: take that one
    comparison out and *"the automatic pass then suggests nothing at all inside
    it"* goes red on its own.
    ⚠️ **IT MASKS THE SUGGESTIONS AND NOTHING ELSE.** Not a crop, not a delete.
    The scan is untouched, the cut pays it no attention, and an outline drawn
    inside one by hand is as good as any other — so a region put in the wrong
    place costs a **suggestion**, never a piece, which is why it needs no
    confirming and no undo of its own. It is painted with the sheet's own
    colour rather than cut out, because a hole of black would be the biggest
    piece on the sheet.
    ⚠️ **And it can be taken off by clicking it**, or it would be fault 50's
    shape — a mark nothing can clear — over a control that hides part of the
    sheet from the room.
    ⚠️ **The regions live on the sheet record, not in `outlines.json`.** A
    masked region can be drawn again in a moment; an outline cannot. The three
    stores that keep their own history are the three that cannot be rebuilt
    (fault 49), and this is not one of them.
    ⚠️⚠️ **The tool is not offered in a baked page at all.** An offline page's
    suggestions were worked out when it was made and there is no room behind it
    to ask again, so the control would quietly do nothing — fault 58 again, by
    the door of a feature that cannot work rather than one that is broken. ⚠️
    And `hidden` does not hide a button whose CSS sets `display` (fault 23,
    which this template had already been bitten by four times), so the check
    **measures the button** rather than believing the flag.

78. ⭐️⭐️ **ONE SET OUT OF THE GAME, RATHER THAN THE WHOLE PROJECT FOLDER.**
    The designer, 26 August 2026: *"I'd like to be able to just export a set of
    cut pieces, rather than everything in one project folder."*
    ⭐️ **A box is the right unit**, and it was already the room's own: Sheets,
    Pieces, Match and the Checklist all gather by it (fault 42), boxes can be
    named (fault 62), made in one go (fault 65) and put by (fault 68). A game
    of 161 sheets and four boxes wants one of them far more often than all
    four, so this is the normal case rather than a special one.
    ⚠️⚠️ **AN EXPORT FOLDER IS REPLACED WHOLE**, on purpose — a half-old export
    listing pieces that are no longer there would be worse than no export. So
    a set written into `export/` would have **destroyed the export of
    everything else**, silently, and been noticed only by somebody later
    hunting for a piece that used to be in it. Each set goes into
    `export-<set>/` of its own.
    ⚠️ **One rule for that folder's name** (`export_dir`), because two things
    ask: the writing of it, and the button that opens it afterwards. Two
    spellings would show one folder and fill another — and the PAGE must not
    work the name out either, which is why the project payload carries it.
    Fault 24 for the ninth time.
    ⭐️ **The check against the contents list goes with the set and is about
    the set** — its pieces, and only the checklist sections whose `book` was
    set outright (fault 64). ⚠️ Fault 51's inferred box is **not** used here:
    it orders and never hides, and using a guess to decide what a report is
    about would break that. ⚠️ And the headline figure had to be worked out
    again from the bands actually in the report, or a folder holding one set
    would have been headed *44 of 221*, which is a lie by arithmetic.
    ⚠️ **The checklist itself stays with the whole game.** A page headed *what
    is still to cut* listing three other boxes, sitting in a folder holding
    one, sends somebody hunting for pieces that were never meant to be there.
    ⚠️ **And the folder says it is part of something.** A set's README says
    plainly that this is one set out of the game and that the others are
    exported separately — otherwise anybody checking it against a printed
    contents list finds most of the game missing and concludes the room lost
    it.
    ⭐️⭐️ **Its check needed a second box before it meant anything.** Written
    against the bench as it stood — one box, one piece — every one of these
    checks passed over code that exported the lot and called it a set. That is
    **fault 54**, the easy question in place of the real one, and the bench now
    grows a piece in another box and puts itself back afterwards. Teeth tried:
    with the filter removed, three go red.

79. ⚠️⚠️ **THE FINDER DOES NOT LAUNCH AN APP THE WAY A SHELL DOES, AND
    NOTHING BUT LAUNCHING IT WILL SHOW YOU.** The last of the designer's *"a
    simpler way to open and quit. I don't like terminal at the best of
    times."* — `Cutting Room.app`, which opens the room with no window at all.
    ⚠️⚠️ **It came up under Rosetta.** LaunchServices chose **x86_64** for an
    unsigned bundle that had not said otherwise, and numpy — built for one
    architecture only — refused to load: *"incompatible architecture (have
    'arm64', need 'x86_64')"*. The identical script run from a terminal worked
    **perfectly, every time**, which is exactly the sort of difference that
    can only be found by pressing the thing. So the architecture is said
    twice, and those are not two copies of one rule: the Info.plist states a
    **preference**, and `/usr/bin/arch -<machine>` on the command states a
    **fact** that holds however the bundle was started.
    ⭐️⭐️ **AND IT LETS GO OF THE ROOM.** A bundle that stays running while the
    room runs is a bundle the Finder thinks is already open — so the **second**
    double-click, which is the one somebody makes when they have closed the tab
    and want the room back, would do **nothing at all**. The launcher starts
    the room, waits only until it answers, opens the browser and finishes;
    every later press finds the room up and opens a tab.
    ⚠️ **With no window there is nowhere for a failure to appear**, and silence
    reads as a broken button (fault 58). A room that will not start says so in
    a message box carrying the room's own last words, and everything it says
    goes to `~/Library/Logs/Cutting Room.log` — rolled over, because a day of
    cutting is a lot of lines.
    ⚠️ **No Dock icon** (`LSUIElement`), on purpose: a Dock icon carries a
    *Quit* that stops the room without asking what is half-finished, and fault
    21 is the whole reason the room asks.
    ⚠️ **It is rebuilt WHOLE and so must never rebuild something that is not
    its own** — the bundle is read before it is replaced, and an app of that
    name that the room did not write is refused with a sentence and left
    exactly as it was.
    ⭐️ The icon is **drawn** rather than committed (a binary in a repository is
    a change nobody can read), and the `.icns` is packed by hand rather than by
    `iconutil`, which belongs to the developer tools and is a stub on a Mac
    without them. *The room must not need anything installed.*
    ⭐️⭐️ **Two of its checks were changed by trying their teeth**, and both
    lessons outlive this feature: a reading of the script that asked whether it
    let go of the room stayed **green with the fault deliberately put back**, so
    it came out — and the fault that makes the launcher wait did not turn the
    section red at all, it **hung the whole run for ever**. ⚠️⚠️ **A check that
    hangs reports nothing**, which is worse than one that reports the wrong
    thing (fault 53's family). No press is waited on unboundedly now.

80. ⚠️⚠️⚠️ **macOS KEEPS AN APP OUT OF `Documents`, `Desktop` AND
    `Downloads` — AND WILL NOT EVEN ASK.** Fault 79's launcher was built,
    ad-hoc signed, given the four `NS...UsageDescription` sentences that are
    supposed to be the words in the permission box, and was **correct in every
    particular**. It did not work. The room came up, served its front page,
    and answered `PermissionError: Operation not permitted` for
    `~/Documents/Cutting Room` — the folder its projects live in.
    ⚠️⚠️ **There is no prompt to wait for.** For a bundle whose executable is
    a shell script running Apple's own python, macOS does not attribute the
    request to the app, so it never asks and simply refuses. `tccutil reset`
    on the bundle's identifier changed nothing. It is not a thing the room can
    fix from inside.
    ⭐️⭐️ **What settled it was two experiments, not reasoning.** First: an app
    that HOLDS ON to its child and one that LETS GO were refused identically,
    so fault 79's design was not the cause. Second: the same bundle reading
    `~/Projects` and a folder made in the home directory was allowed
    **instantly** — so it is those three folders and nothing else. Ten minutes
    of pressing it, against an afternoon of plausible theories about
    responsible processes.
    ⭐️ **The answer is where the projects live.** `~/Documents/Cutting Room` is
    a poor home on a modern Mac and always was; moved one level up, everything
    works with no permission, no System Settings and no prompt. So
    `--install-launcher` takes `--home`, and ⚠️ **the room says so at the
    moment the launcher is written**, while somebody is there to read it —
    which is the only thing it CAN do. ⚠️ It warns and still writes the
    launcher: somebody may have granted the permission by hand, and a tool
    that refuses to do as it is told because it suspects trouble is worse than
    one that warns.
    ⚠️ **The default home is left alone.** Changing `DEFAULT_HOME` would strand
    the projects of everybody who already has one.
    ⭐️⭐️ **And a bare `open` is not good enough either.** The designer, in the
    same breath: *"NEVER open it when I am using my work chrome profile."* A
    launcher that opens a browser hands the tab to whichever profile the Mac
    thinks is current, and somebody with a work account and a personal one
    wants their games in exactly one of them. So `--install-launcher` takes
    `--browser`, and ⚠️ **both launchers open the browser themselves** rather
    than one of them leaning on the room's `--open` — or the setting would hold
    for one door out and not the other (fault 24, tenth time).

81. ⚠️⚠️⚠️ **A BUTTON'S WORDS AND A BUTTON'S ACTION WERE WORKED OUT
    SEPARATELY, SO THEY DISAGREED — AND THERE WAS NO CHECK ON IT AT ALL.**
    The designer, 26 August 2026, having outlined 22 new sheets: *"I think
    pressed 'cut every outlined sheet', next to which it said '22 not cut
    yet'. But it then started cutting every single page I have ever outlined
    in the entire game. It should surely skip finished sheets? Or just cut
    the ones I'm looking at within the current import. Total waste of time and
    I don't like the though of any potential duplication of previously-prepared
    elements."*
    ⚠️⚠️ **Everything the room SAID was right and the room did something
    else.** The tip on the button said it cut every sheet that *"has not been
    cut yet"*; the note beside it counted exactly those and said *"22 not cut
    yet"*; and `/cut-all` behind them read `[s for s in sheets if outlines]` —
    no rule about `cut` anywhere in it. So a 161-sheet game went through the
    cutter to get at 22. That is **fault 16's shape** (two routes to one thing
    that disagree) over **fault 24's cause** (the same fact written out more
    than once): *waiting to be cut* was spelled out in FOUR places in the page
    — the Cut step's count, the *Cut* filter chip, the note, and nothing at
    all in the button's own handler — and a fifth time, differently, in the
    room.
    ⭐️ There is one `needsCut()` in the page and one `waiting_to_cut()` in the
    room now, and everything asks them.
    ⚠️⚠️ **AND THERE WAS NO CHECK ON THIS BUTTON WHATEVER** — not through the
    API, not in the browser, not a word in `ROOM.md`. That is why it could
    drift: nothing was holding the words to the action. It has fourteen now,
    and their teeth were tried — put the fault back and six go red, while
    *"every sheet ended up cut"* stays green, which is the guard against the
    cheap way to pass (skip everything and call it skipping).
    ⭐️⭐️ **A SHEET OUTLINED AGAIN SINCE ITS CUT IS WAITING TOO.** "Skip what
    is cut" written flatly would have been wrong in the other direction — you
    fix an outline, press the run button, and it does nothing, which is fault
    58 again. `stale` already existed and already coloured the sheet card; it
    is now part of the one rule, so correcting an outline puts that sheet back
    in the queue and nothing else with it.
    ⭐️⭐️ **"OR JUST CUT THE ONES I'M LOOKING AT" NEEDED NOTHING NEW.** The
    sheet list is already held to a box, a search and a filter (faults 35, 42,
    62, 65), so **the narrowing they have already made is the answer** — the
    button acts on the sheets shown and names its own number, which is the
    idiom *"Put these N into one set…"* had already established two inches to
    its left. ⚠️ The room INTERSECTS what the page names with what is really
    waiting rather than obeying it, because a page open for an hour may name a
    sheet another tab has since cut.
    ⚠️⚠️ **AND A NARROWING MAY NEVER BE SILENT.** The Sheets list opens on *To
    outline*, so somebody can be looking at a page showing none of the sheets
    that are waiting — and a button quietly doing less than they think is the
    whole of what went wrong here, from the other end. It says how many are
    waiting that this list is not showing, and how to reach them. Two numbers
    that disagree in silence, again — faults 67 and 68.
    ⭐️ The general shape, worth more than the fix: **when a control carries a
    sentence saying what it does, that sentence is a claim nothing is
    checking.** Fault 31 put a sentence on every button in the room; this is
    the first time one of them turned out to be a lie.

82. ⭐️⭐️⚠️ **MATCH ASKED A CRUDER QUESTION THAN THE CHECKLIST, SO A DECK
    LEFT THE LIST ON ITS FIRST CARD.** The designer, 26 August 2026: *"In
    Checklist it's generally very apparent that certain elements comprise more
    than one piece (eg a deck of cards). But this isn't carried through to the
    Match drag and drop function. ie if I mark one magic card as part of a
    deck, that then disappears from the left column, even though I might have
    numerous more cards to mark as part of that deck. The only way to get it
    back is to click 'show everything, including matched' which isn't a great
    experience. There should be a linkage between checklist and match that only
    marks a component as matched when user has dragged it onto the correct
    number of cards. ALSO match should include an item for the relevant back of
    each deck. These feel like obvous fixes to me."*
    ⚠️⚠️ **THE ROOM HAD KNOWN THE RIGHT ANSWER THE WHOLE TIME.**
    `wanted_status()` counts a deck against its quantity (fault 36) and lets
    one design fill as many cards as the game wants of it (fault 56). Match was
    the one list in the room that did not ask it — **twice**, in two different
    copies of a cruder rule:
    - `renderMatch()` dropped a component from the list on
      `(w.pieces || []).length > 0` — *anything linked means done*.
    - and `link()`, which keeps the two stores the page holds in step after a
      drag rather than fetching them again, **re-derived `state` itself** with
      the same crude rule — so even a correct filter would have been fed a
      wrong answer a millisecond later. ⭐️ The bulk bar had already worked
      this out and its comment says so in as many words: *"read the checklist
      back from the room rather than working it out here: whether a component
      is done depends on how many pieces a deck wants, which only the room
      knows."* One door had the lesson written on it and the other did not.
      **Fault 24, twelfth time.** `link()` reads it back from the room now, and
      there is no second copy of the rule in any language.
    ⭐️ **And the list says how far it has got** — *3 of 24*. A component that
    merely vanished answered none of the question the designer was actually
    asking of it.
    ⚠️ **The badge over Match counted something else again** — only components
    with nothing at all against them, while the column showed the part-done
    too. Two numbers disagreeing in silence (faults 67, 68); it counts what the
    column holds now.
    ⭐️⭐️ **A BACK IS A ROW, BECAUSE A BACK IS ANOTHER PIECE.** *"Match should
    include an item for the relevant back of each deck."* A back cannot be a
    name dragged onto a card — fault 46 settled that it is another PIECE — so
    the row is dragged the other way: drop **its back** onto the piece that is
    the back and the whole deck points at it.
    ⚠️ **The half that would otherwise silently not happen** is the cards
    linked *afterwards*. The back lives on the **component** (`back` on the
    wanted item) and a card linked to that component inherits it — ⚠️ filling
    a blank only, because a set can have more than one back, and ⚠️ through
    **one `inherit_back()`**, because two doors link a piece to a component
    (the Match drag and the bulk bar) and a guard only one of them remembers is
    fault 14 for the umpteenth time.
    ⭐️ **The drag is the decision**, so the piece really is marked `card back`
    — that is what lets the *only pieces marked as a card back* narrowing
    (fault 51) find it later. Half of this working would read as broken.
    ⚠️ **And it can be taken off**, or it is fault 50's shape: a mark nothing
    can clear, over a decision spread across thirty-two cards.
    ⭐️ **A component still needing a back stays on the list even when all its
    pieces are matched**, showing only the row that is left to do — or the last
    thing to do about a deck would be the one thing you could not see.
    ⭐️ Teeth tried on both copies of the rule, separately: put the filter back
    and the deck vanishes from the list; put `link()`'s own recompute back and
    the deck vanishes **on the drop**, which is precisely what was reported.
    ⚠️ Which components are offered a back row is a judgement: **kind `card` or
    `deck`, or anything wanting more than one piece.** The last of those is
    deliberately generous — a set of several different pieces may well be
    printed two-sided — and it costs one ignorable row, which goes away the
    moment the back is said.

83. ⭐️⭐️⚠️ **CALLING SOMETHING A DECK IS SAYING ITS CARDS ARE ALL
    DIFFERENT — AND `each: false` WAS NOT AN ANSWER, IT WAS A STAMP.**
    The designer, 26 August 2026: *"when something is a deck it should also
    report that each component dropped is unique in the checklist ie '[n]
    needed' rather than '1 needed'."*
    ⭐️ **The room had been asserting this and not acting on it.** Fault 52's
    end-of-job finding reports *a deck counted as one card* as something to fix
    — so the room already held that a component whose kind is `deck` with a
    quantity of thirty-two is thirty-two different cards. It said so in a
    report and then counted one. That is half a report, and the fix is to
    count it: `counts_each()` reads the kind where nobody has said otherwise.
    ⚠️ **This is not the room guessing.** `kind` is a word the person typed,
    and fault 36's rule — that nothing in a printed contents list tells a
    repeated design from a set of different ones — is untouched: the list still
    cannot tell, but *"deck"* can.
    ⚠️⚠️ **AND ONLY `deck`, WHICH IS EVIDENCE RATHER THAN REASONING.** Fault
    52 tried exactly this rule with `card` included and read it against the
    designer's real list: the findings went from nine to twenty and **all
    eleven it added were wrong**. That reading is what this rule rests on, and
    a check goes red if `card` is ever let in.
    ⚠️⚠️⚠️ **THE FAULT THAT NEARLY MADE THE WHOLE THING DO NOTHING.** Written
    first as *"`each` absent means read it from the kind"*, it was correct,
    checked, green — **and could never have fired on a real list.**
    `new_wanted()` stamps `each` onto every component it makes, from a pasted
    contents list, a split line or a group of cut pieces alike, so a real
    game's `wanted.json` is full of `false` that nobody ever chose. The check
    passed only because it had **popped the field first**, which no path in the
    room does. That is **fault 54** — the easy question in place of the real
    one — and it was caught by asking what a pasted list actually leaves
    behind. ⭐️ The check does not clear the field now; it asserts the field is
    *there*, which is the state every real list is in.
    ⭐️ So the person's press is recorded separately, as `each_said`. `each:
    true` is obeyed however it arose; `each_said` is the only thing that can
    mean *"one is enough, and I mean it"*. ⚠️ Which keeps the press
    reversible — a default that could not be pressed back would be fault 50's
    shape.
    ⭐️ **And a figure that settled itself has to be accountable**, so the row
    says *counted as a deck* under the button, in as many words.
    ⚠️ **`each_on` is sent BY THE ROOM**, not worked out again in the page: the
    word on the button and the number beside it come from one answer, or they
    would eventually disagree — and *"one is enough"* printed next to *0 of 32*
    is exactly the sort of nonsense fault 24 produces.
    ⚠️ **Fault 52's finding became a list of decisions rather than accidents.**
    The state it caught can no longer happen by accident, so the only way to
    reach it is to have pressed *one is enough* on a deck — which is a fair
    answer for a line called a deck that really is one piece. Its wording says
    so, and says there may be nothing to do: **a report that tells somebody off
    for a choice they made on purpose stops being read**, which is fault 50's
    lesson arriving on a page rather than a chip.

84. ⚠️⚠️⚠️ **THE CUT DID FULL-SHEET WORK PER PIECE, AND ON A REAL GAME'S
    SCANS THAT WAS EIGHTEEN MINUTES.** The designer, 26 August 2026: *"I have
    highlighted 17 pages of [the second game]'s components. Pressed cut, and it
    is INCREDIBLY slow"* — and then, *"finished, it took 1081 seconds to cut the 17 sheets."*
    ⭐️⭐️ **Habit 2 found it in ten minutes and no amount of reading the code
    would have.** Their project's own `project.json` says the sheets are
    **10909 × 15355** — a hundred and seventy megapixels each, twenty times the
    size anything here had been tried on. Every cost that scales with *pieces ×
    sheet area* was invisible at eight megapixels and ruinous at a hundred and
    seventy. **Measure on the real thing's dimensions, not on the demonstration
    sheet.**
    Four of them, in the order they cost:
    - ⚠️⚠️ **`np.unique(..., axis=0)` was 85% of the whole cut.** It lexsorts
      three columns of every pixel in a piece, to find the commonest ink under
      it — and it was handed a **whole-sheet** boolean besides. Packing the
      three channels into one number and asking a 1-D array is the identical
      answer **117 times faster**; cropping to the piece's own box first is
      another threefold. 87s a sheet became under 2.
    - ⚠️ **`label_shapes()` walked the whole sheet once per ink colour**, in a
      Python row loop, and built a `int16` copy three times the sheet's size to
      hold numbers that never exceed 215. It is uint8 now, each colour is
      labelled **in its own bounding box**, and `label()` skips rows with
      nothing in them (⚠️ resetting the run linkage across a gap, which is
      exact because a blank row cannot connect anything).
    - ⚠️ **`paint_mask()` made two full-sheet images per piece** — an L layer
      and an RGBA patch — and composited both across the entire sheet: 200MB of
      work for one counter. It draws in the polygon's own box now, which is the
      identical picture because the paste still happens in order.
    - ⚠️ **`keep()` called `np.nonzero` per piece** to take four numbers off
      two int64 arrays as long as the piece. Two boolean reductions give the
      same four, 34 times faster.
    ⭐️⭐️ **It was checked by DIFFERENCE, not by reasoning.** The old code was
    taken out of git and run beside the new one on six awkward sheets —
    overlapping pieces in the same ink and in different inks, curves, a piece
    against the edge, a piece drawn over another, a piece in the darkest ink
    (key 0, which the sentinel had to keep apart from the background), thin
    pieces with blank rows between them — and on the real demonstration sheet
    through the automatic pass. **Every answer identical, pixel for pixel.**
    That is the only honest way to speed up the most delicate code in the room.
    ⭐️ One sheet: 102.6s → 8.2s. Their seventeen: **1081s → about 140s.**

85. ⚠️⚠️ **A PIECE THAT FILLS THE SHEET IS STILL A PIECE, IF SOMEBODY DREW
    IT.** The designer, 26 August 2026: *"I have outlined the single large
    component on the sheet. But it won't cut. Is that a size constraint?"* It
    was. `keep()` bins anything covering more than 85% of the sheet as the
    scanner's own frame, and their board covered **90.3%** — so the cut ran,
    threw the one piece away, wrote an empty answer and **reported success**.
    ⭐️ **Fault 76 had already settled this principle at the other end of the
    scale** and said so in `sheets.py` in as many words: *"a thin outline
    somebody DREW is a decision, and the room does not overrule those… it is
    deliberately not part of `keep()`, which the CUT uses as well."* The floor
    got that treatment; the **ceiling never did**. `keep(..., drawn=True)` now
    means these shapes came from a person and none of the binning applies —
    and the automatic pass, which is what those guards are for, is unchanged.
    ⚠️ **And the silence was half the fault.** A cut that keeps nothing now
    says so, naming the sheet and how many outlines it had. Reporting success
    over an empty answer is fault 58 — half working reads as broken, and here
    there was nothing at all to read.
    ⭐️ Verified against the designer's own sheet, read-only: 0 pieces before,
    one piece of 22.7 × 44.5 inches after.

86. ⚠️⚠️⚠️ **A SAVE THAT REPLACES THE LIST THROWS AWAY EVERY EDIT MADE WHILE
    IT WAS IN FLIGHT.** The designer, 26 August 2026: *"I edited 'small
    room(6)' to note that it is 6 unique pieces… but despite it now showing 6,
    I cant seem to toggle that immediately… Hitting the toggle doesn't seem to
    do anything."*
    ⭐️ **Pressing a button in a row BLURS the box you were typing in**, so the
    box's own save goes out first and the press follows a moment later — two
    writes of the whole list in flight at once. `saveWantedAll()` ended with
    `wantedData = d`, so the **first** save's answer, carrying the list as it
    was *before* the press, arrived last and wiped the press out of the page's
    copy. Nothing was broken; the answer to an older question simply won.
    ⭐️ The room's answer is now **merged**, not swapped in: it refreshes only
    the fields the room works out and leaves everything a person typed alone.
    ⚠️ And the room **says which fields those are** (`worked_out` in the
    payload) rather than the page keeping a second copy of that list — fault
    24, with a saved store underneath it. Saves are also chained, one at a
    time.
    ⚠️⚠️ **AND A SECOND FAULT UNDERNEATH IT, WHICH WAS MINE FROM THE DAY
    BEFORE.** Fault 83 had the page read `each_on` — a field the room sends.
    **The pages are read fresh off the disk on every request and the Python is
    whatever was loaded when the room started** (fault 38), so a new page in
    front of an older room got `undefined` for every row: the button read *one
    is enough* on everything, and pressing it set `each` to the opposite of
    undefined — true — for ever, **so it never changed**. That is fault 58 by
    fault 38's door. `eachOn()` falls back to the stored value, so the control
    behaves exactly as it always did until the room is restarted. ⭐️ **Any
    future field this page reads from the room needs the same treatment**, and
    that is the general lesson: a page may not depend silently on a field a
    running room might not send yet.

87. ⚠️⚠️ **EVERY TALL PIECE ON THE MATCH BOARD HAD ITS FOOT CUT OFF, AND HAD
    ALL ALONG — FAULT 4, IN THE ONE PLACE IT HAD NOT BEEN LOOKED FOR.**
    The designer, 26 August 2026, first: *"some of the previews of the pieces
    in Match are too large for me to be able to fully see"*, and then, when
    the hover was made bigger: *"the hover pop up is too aggressive and large
    — all i need to see is the outer boundary of any piece which is slightly
    cropped within the preview square. I think a better solution is to show
    the full boundary of any cut piece in that preview, and then hover could
    be a small zoom."*
    ⭐️⭐️ **The second message was the right diagnosis and the first fix was
    the wrong one.** `.mcell .pic img` was `max-width: 92%; max-height: 92%` —
    and the percentage max-height **did not resolve**, so the picture was
    sized by its WIDTH alone. Measured in a real browser on a bench built with
    three shapes on purpose: a tall piece came out **239 pixels high in a
    118-pixel box** and a square one 131 — both with their feet cut off by the
    `overflow: hidden`. Only wide pieces ever fitted, which is why it read as
    "slightly cropped" rather than as obviously broken.
    ⚠️ That is **fault 4 verbatim** — *"a percentage `max-height` against an
    `aspect-ratio` height may not resolve, so a thumbnail was sized by width
    alone and every portrait sheet lost its foot"* — written down in August
    about the sheet cards, and this was the only percentage max-height left in
    the stylesheet. Pixels resolve where percentages do not; `object-fit:
    contain` makes it true for any shape.
    ⭐️ Making the hover enormous had **hidden** the real fault by working
    round it. The cell shows the whole piece now and the hover went back to
    being a small zoom, which is what was asked for.
    ⚠️ Its check measures FIVE cells and asserts one of them is taller than it
    is wide — a check that measured one square piece would have stayed green
    through the entire fault (fault 54). Teeth tried: put the percentage back
    and all five are reported clipped.
    ⭐️ Match had no hover preview at all before this; it now uses the same
    `data-big` the look-alike tiles have had since fault 40, so there is one
    mechanism rather than two.

88. ⭐️⭐️ **MENDING ONE PIECE CUTS THAT PIECE.** The designer, 26 August 2026:
    *"If I'm mending a piece, it seems obvious that default should be to just
    recut that specific piece no?"* Quite so — a sheet holds forty and
    thirty-nine of them were right.
    ⭐️ **The control that says which piece you mean already existed**: *work on
    this one alone* (fault 75). The mend link from the Pieces page turns it on,
    so that flow gets this without anybody choosing anything, and turning it
    off cuts the sheet as before. The button says which it will do.
    ⚠️⚠️ **THE WHOLE SHEET IS STILL PAINTED AND LABELLED, and that is not
    waste.** A piece's NUMBER is its position in reading order over every piece
    on the sheet — cut one outline on its own and it would be `_00` whatever it
    really is, which is precisely the renaming `cut_sheet` exists to prevent.
    What is saved is the cutting, measuring and writing of the other
    thirty-nine, which on a big scan is nearly all of the work.
    ⚠️⚠️ **AND IT FALLS BACK TO THE WHOLE SHEET THE MOMENT ANYTHING ELSE
    MOVED** — a different number of pieces, or this one past a neighbour in
    reading order. Then every number below it shifts and the names must follow.
    ⭐️ Teeth tried, and this is the entry's point: with the guard removed the
    checks show the names landing on the **wrong pieces** — the exact damage
    the re-cut machinery was built to stop. A fast path that quietly left the
    store inconsistent would be far worse than a slow one.
    ⚠️ **And it says which it did.** Asked for one piece and given the whole
    sheet, a silent answer would read as the button being ignored (fault 58).
    ⚠️ The sweep that makes a re-cut safe by starting from nothing is the one
    line the fast path must not run; the mended piece is removed by name
    instead. A piece that was set aside still goes back to the spare folder.

89. ⭐️⭐️ **TWO PIECES LAID AGAINST EACH OTHER — AND THE COMMONER USE OF IT
    WRITES NOTHING.** The designer, 26 August 2026, of a board scanned across
    two pages: *"I have a component (the spine) which extends over 2 pages. I
    need a way to manually stick them together… perhaps a one-off solution just
    for this?"* It was done once by hand — and then, within the hour: *"ensure
    it is backed into the platform - I have a new use for something like it
    immediately in my [second game] build (ensuring that corridor pieces
    interlock neatly)."*
    ⭐️⭐️ **THE SECOND ASK IS THE ONE THAT SHAPED THE TOOL.** *Do these two
    edges meet?* is looking, not making: it changes nothing, it is asked far
    more often than the other, and it wants a light table rather than a
    command. So **Fit together** is a light table first — two pieces, a drag,
    a zoom, a difference blend — and *Join them into one piece* is a button on
    the end of it. Nothing is written until that button is pressed.
    ⭐️ **Overlap and gap are one number read two ways**, and which of them is
    showing tells you which job you are doing: two halves of a spine overlap,
    two corridor tiles that interlock should meet at nothing at all.
    ⚠️ **NOTHING IS DELETED.** Joining sets the two halves aside (fault 19),
    which the Pieces page undoes — a join made in the wrong place must not
    throw away the only copies of both.
    ⚠️⚠️ **THE JOINED PIECE ANSWERS TO NO SHEET, ON PURPOSE.** Naming a real
    sheet in its index entry would put it in that sheet's set, and `cut_sheet`
    drops every index entry belonging to a sheet before it writes the new ones
    — so the next re-cut of that sheet would **quietly lose the joined piece's
    record**. It is left empty and the piece shows under *Not off any sheet
    this project knows*, which is the plain truth: it came off two.
    ⚠️ **It asks for a name and refuses without one.** A joined piece has no
    sheet and so no number to be found by; the name is the only handle. Same
    rule as the checklist learnt from cut pieces (fault 72) — the room makes
    the thing, the person says what it is.
    ⭐️ **The offset is held in TRUE PIECE PIXELS throughout** and multiplied by
    the zoom only when it draws. Holding it in screen pixels would lose
    precision every time the zoom changed, and the offset is the one thing the
    whole tool produces.
    ⚠️ **The arrow keys stand down inside a field** — the name box is on the
    same panel, and fault 2 is this codebase's oldest. A check presses an arrow
    key in that box and watches the picture not move.
    ⚠️ **The stage is laid out at its real, zoomed size rather than scaled with
    a CSS `transform`.** A transform leaves the scroller's idea of the size
    unchanged, so above 100% the piece you were not looking at slides out of a
    box that has not grown — *"the zoom was a bit flaky, the piece on the left
    kept vanishing"*, said of the throwaway version, and fixed here before it
    reached the room.
    ⭐️ It opens **edge to edge, fitted and centred**, because that is where
    both jobs start: *"Better if they both start next to each other, centered
    in the window and I can then drag. Zoom only important once I've done a
    rough join."*

90. ⚠️⚠️ **AN ABBREVIATION IS A NAME, AND THE LIST OF FORBIDDEN WORDS HELD
    ONLY FULL ONES.** Fault 55 took one game's names out of this repository in
    three passes and left a check that reads every file with the line breaks
    taken out. It has been green ever since — and on 27 August a tidying-up
    pass found the **second** game's three-letter abbreviation sitting in two
    places: a comment in `cutting_room.py` using it in an example file name,
    and, worse, **this file's own account of fault 84**, which quoted the
    designer verbatim.
    ⚠️ Note that this entry cannot spell the letters either — writing them here
    to explain them would put them back. That is **fault 55's rule about a
    check whose subject includes itself**, arriving in the prose rather than in
    the code: the only safe way to describe a forbidden word is not to use it.
    ⭐️ **Both were written by somebody who had those initials in front of them
    all day**, which is exactly how the first game's names got in. The list had
    the game's full name and would have caught it spelled out; three letters
    went straight past.
    ⚠️ So the list has the abbreviation now, and the rule to take from it is
    the one already at the top of this file, arriving by a new door: **add to
    that list rather than arguing with it.** A word there costs nothing; a name
    in a public repository cannot be taken back once it is cloned.
    ⭐️ It was found by grepping for the game's name while writing this session
    up — not by the check, which could not see it. *When a check has been green
    for a week, the thing to ask is what it cannot see.*

91. ⭐️⭐️ **A BOX THAT IS FINISHED IS NOT A BOX THAT IS PUT BY, AND THE
    DIFFERENCE IS THE COUNTING.** The designer, 1 September 2026, having cut
    and named every component in the second game's core box and ticked every
    one of its seventeen sheets: *"There should now be a way to move those (not
    out of sight) but just to ensure they don't pop up anymore, no need for
    them to populate dropdowns, or the sheets page anymore etc."*
    ⚠️⚠️ **THE OBVIOUS FIX WAS THE WRONG ONE.** The room already had a mark
    that takes a set out of the way — *put by for later* (fault 68) — and
    reaching for it would have been one line. But put by means **not cut yet**
    and is left out of every figure precisely because a percentage counting
    work you have decided not to do can never reach 100; a finished box marked
    that way would be reported by the end-of-job check as a box **nobody ever
    cut**, which is a lie about the very work the mark is celebrating. So
    `filed` is a second list beside `later`: the same key shape, the same
    route, and ⚠️ **one rule for which key a set answers to** (`group_key()` in
    the room, `groupMarkKey()` in the page), because two copies of that would
    drift and the one that drifted would be the one that marked the wrong box.
    ⭐️⭐️ **IT PUTS THINGS LAST; IT DOES NOT HIDE THEM.** That is fault 51's
    rule — *it ORDERS, it does not hide* — and it is what makes this safe:
    every list that narrows by box still offers a filed box, in a band of its
    own at the end, collapsed from a line per sheet to **one line**. A piece
    cut from a finished box is exactly the sort of thing somebody comes back
    for. On the Sheets page its sheets keep out of the views, and there are
    **two doors back**: a chip of its own, and a **search, which always
    overrules the filing** (fault 37's rule about folds, on a different
    mechanism).
    ⭐️ **THE ROOM OFFERS IT AT THE MOMENT IT IS EARNED.** It already knows
    whether every sheet is ticked and every piece named, so the button says so
    rather than waiting to be found. ⚠️ Still only an offer: a box may be as
    done as it is ever going to be, so a box that is not ready is filed anyway
    if the person says so — and the question **says what is outstanding**
    first. Fault 80's rule, that a tool which refuses because it suspects
    trouble is worse than one that warns.
    ⚠️ **AND FILING IS A CLAIM, SO THE END-OF-JOB CHECK GOES ON CHECKING IT** —
    the band says *filed away* and still asks for anything missing out of it.
    A mark that stopped the checking would bury the one thing it was hiding.
    ⚠️⚠️ **Two faults were mended on the way, and both were made by the feature
    itself.** The Sheets headings were drawn only when the list **shown** held
    more than one box — so filing the first of two boxes left one box shown,
    the headings vanished, and with them the only way to file the second or
    bring the first back: fault 50's shape (a mark nothing can clear),
    manufactured by the thing being built. They are decided by what the GAME
    holds now. And Match's *Show* list was built `if (sel.options.length <= 1)`
    — once, and never again — which is **fault 57 exactly** and would have gone
    stale the moment a box was filed with that board open. It goes through
    `fillSelect()` like the others.
    ⚠️ Its own first run turned up the fault this kind of filter always has:
    the new chip let every **other** sheet through as well, because a non-filed
    sheet fell past the new test and hit the `return true` at the bottom. The
    chip that exists to show what has been filed showed the whole game.
    ⭐️ Twenty new checks, ten through the room's own door and ten by pressing
    the buttons in a real browser — because a check through the API is a green
    light over a button that does nothing (fault 61).

92. ⚠️⚠️⚠️ **A CHECK PUT A MODAL DIALOG ON THE DESIGNER'S SCREEN, AND THE
    GUARD AGAINST IT HAD BEEN WRITTEN ON THE OTHER COPY.** On 1 September 2026
    the designer, working at their machine, got an alert box: *"The Cutting
    Room could not open."* It was not their room — it was `check/check.sh`.
    The launcher's last act when the room will not start is an `osascript
    display dialog` (fault 79), which is a real modal alert waiting for a real
    person to press OK. The checks press **two** copies of that launcher: a
    working one, and a deliberately broken one. The broken one had its dialog
    swapped for an `echo`, with a comment saying in as many words that *a check
    must not put a box on somebody's screen*. ⭐️ **The working copy did not,
    because nobody writes a guard for the case they are sure will not happen.**
    That is **fault 14** — a guard only some of a set remember — arriving in
    the checks rather than in the room. It is one substitution now (`NO_DIALOG`)
    and every copy takes it.
    ⚠️⚠️ **What made the working copy fail was a port collision inside the run
    itself.** The launcher section and the pretend slow download were both
    written as `PORT + 3`, four hundred lines apart, neither knowing about the
    other. They got away with it because the launcher's room is closed before
    the download starts — until a run that stopped half way left its trickle
    server on that port, and the next run's launcher could not bind. **Fault 24
    in arithmetic**: every port the run uses is declared in one place now.
    ⚠️ And the run that stopped half way was stopped with `kill -9`, which
    takes the exit trap with it — the trap is careful and correct (fault 53)
    and cannot run at all if the shell is not allowed to. *Stop a check run
    with TERM and wait for it; never `-9`.*
    ⭐️ The lesson worth keeping is the first one: **a check that assumes it
    will pass is a check that has not been written for the day it does not.**

93. ⭐️⭐️⚠️ **THE EDITOR NEVER LEARNT WHAT SCALE THE PROJECT WAS AT, AND
    THERE WAS NOWHERE TO SET IT ANYWAY.** The designer, 1 September 2026,
    having been given a project set up for 600dpi scans: *"can you confirm
    that I can now upload the files… and it's set to 600dpi - would be helpful
    if that was shown somewhere visually!"*
    ⚠️⚠️ **It was worse than not being shown.** `cutting_table.tpl.html`
    carried a bare `var DPI = 300` and **nothing ever told it otherwise** — so
    on a project at any other scale every inch figure on the table was wrong:
    the piece readout, the measuring tool, the millimetres in the laser SVG,
    and — the one that would have cost an evening — the **"Lay it at"** box, so
    a shape laid from the shelf at a typed size came out at the wrong number of
    pixels. ⭐️ The cut itself was always right, because that is done in the
    room at `project.dpi`. **Only the screen lied**, which is the hardest kind
    to catch: nothing errors, and the numbers are plausible.
    ⭐️ The fix is that `table_page()` already splices per-project values into
    the editor, so the scale goes through **that** door rather than becoming a
    second hard-coded copy. A baked offline page keeps the marker and still
    reads 300, which is right for a page made from a PDF rendered at true size.
    ⚠️⚠️ **AND THE PROJECT'S SCALE COULD NOT BE SET AT ALL.** A new project is
    hard-coded to 300 and there was no control anywhere, so a box of 600dpi
    scans could only be handled by measuring a line on **every sheet** with the
    ruler — twenty-two times, for the game that turned this up. There is a
    field in Settings now, and `POST /dpi`. ⚠️ A sheet's own measured scale
    still wins: that was measured on the sheet and is better evidence than a
    project-wide default.
    ⭐️⭐️ **IT IS SAID IN INCHES, NOT ONLY IN DOTS.** *"600 dpi"* cannot be
    checked by somebody holding a piece of card; *"at 600 dpi your widest sheet
    is 10.9 inches across"* can be checked against the thing itself in a
    second, and that is the only test of whether the number is right. The same
    reasoning as fault 73's orphan sizes.
    ⚠️ **Changing it re-measures every piece already cut**, so the question
    says so and says it concretely — *a piece recorded as 2 inches becomes
    1.00* — rather than in the abstract. Nothing is re-cut and no picture
    changes, and it says that too (fault 63's rule: say what goes, what stays,
    and only what is true).
    ⚠️⚠️ **WRITING THE COMMENT BROKE THE EDITOR, EXACTLY AS FAULT 6 SAYS IT
    WOULD.** The note explaining the new marker **contained the marker**, and
    its closing characters ended the block comment early — the rest of the
    comment became code and the whole editor stopped parsing. Caught by
    `check.sh`, which parses what the room **serves** (fault 13). *The only
    safe way to describe that marker is not to write it* — which is fault 55's
    rule about a check whose subject includes itself, arriving in a comment.
    ⭐️ Twelve checks through the room's door and four by pressing the button in
    a real browser (fault 61), and the one that holds the fault is neither the
    API nor the field: it is **reading `var DPI` out of the page the room
    actually serves.**

94. ⚠️⚠️ **AN IMPORT DECIDES WHAT IS NEW BY THE FILE NAME ALONE, SO A
    DIFFERENT SCAN UNDER A NAME YOU HAVE USED BEFORE REPLACES THIRTEEN SHEETS
    AND SAYS "13 SHEETS ADDED".** The designer, 1 September 2026: *"Tile
    Sheets.pdf was processed but isn't showing."*
    It had been processed, perfectly. `import_into()` takes a file whose name
    it has seen before as **a better scan of the same sheets** and replaces
    their pictures in place — keeping their ids, their labels, and their
    outlines — rather than making new ones. Nothing in the room said so, and
    the page reported the replaced sheets as *added*, so the sheet count did
    not move and it read as an import that had silently failed. It took an
    hour of comparing `added` timestamps against PNG mtimes to work out what
    had actually happened.
    ⭐️⭐️ **THE BEHAVIOUR IS RIGHT AND THE SILENCE WAS THE FAULT.** Replacing
    in place is exactly how somebody swaps a better scan in underneath
    outlines they have already drawn — which is a thing this very evening
    turned out to want. It cost an evening only because nothing said which of
    its two quite different jobs it had just done. **Fault 81's shape**: a
    sentence claiming something nothing was checking, and — as there — *there
    was no check on any of it*.
    ⚠️⚠️ **THE REAL DAMAGE IS THE OUTLINES.** An outline is filed under its
    sheet's id, so a replaced picture leaves the work lying over artwork it
    was never drawn on. The room cannot know whether the new scan is the same
    page laid out the same way — **only the person can** — so it says exactly
    how many outlines are on each replaced sheet and leaves the judgement with
    them (the same rule as the kinds, the look-alikes and the splitting).
    ⭐️ **And it is quiet when there is nothing to lose.** Replacing a sheet
    nobody has outlined is harmless, and a warning nobody needs is a warning
    that stops being read — fault 50's lesson, arriving on an alert.
    ⚠️ **ONE WORDING**, shared by the drop and the fetch-a-link box, because
    two copies would drift and the one that drifted would be the one that
    lied. Fault 24 again.
    ⭐️ Eleven checks, and the one that matters is that the same file name
    twice leaves the game with **two** sheets rather than four. ⚠️ Note they
    need a **PDF**: an image has no page number, so it is always its own new
    sheet and can never take this path — which is also the honest advice to
    anybody it bites.

95. ⭐️⭐️⚠️ **"NOT OFF ANY SHEET THIS PROJECT KNOWS" IS THREE DIFFERENT
    THINGS, AND ONLY ONE OF THEM MAY EVER BE SWEPT.** The designer, 1
    September 2026: *"how do I remove all the pieces, 'remove this set'
    doesn't clear the cut pieces, and I can't see any other way to do it."*
    There was no other way. Removing a **box** asks a second question about
    its cut pieces; the **single sheet's ×** said flatly *"(The cut pieces
    stay.)"* and offered no way to say otherwise — **though the route had
    taken `?pieces=1` the whole time**. That is fault 14 exactly: a choice
    only some of a set of doors offer. And once the sheet was gone its pieces
    were orphans that **nothing in the room could reach**.
    ⚠️⚠️ **THE OBVIOUS FIX WOULD HAVE DESTROYED TWO OTHER THINGS.** That
    heading gathers every piece with no sheet, and they are not alike:
    - a piece whose **sheet was removed** — its `sheet` names an id the game
      no longer has. This is the only one that may go.
    - a **JOINED** piece — `sheet` is deliberately **empty**, because it came
      off two sheets and naming either would let the next re-cut drop its
      record (fault 89). It is hand-made and there is one copy of it.
    - a **file the index never knew** — and `paths.pieces` may point inside a
      GAME's own repository (fault 39), so these are very likely not the
      room's to delete at all.
    ⭐️ So there is one `lost_pieces()`, in the room, and the page is **told**
    which pieces qualify rather than working it out — a second copy of that
    rule in JavaScript would eventually disagree with this one, over the one
    action in the room that destroys a piece. Fault 24, on the highest stakes
    it has yet turned up on.
    ⭐️⭐️ **Teeth tried, and the failure is the point**: drop the four
    characters `sid and` from the guard and four checks go red — one of them
    reporting `joined_thing.png` gone from the disk, which is precisely the
    damage.
    ⭐️ **The name is not thrown away**: it goes to `retired`, exactly as a
    name whose piece disappears across a re-cut does. Somebody deleting a
    piece has not asked to forget what it was called.
    ⚠️ **And asked again with nothing to do it refuses in a sentence** that
    says what it leaves alone — otherwise somebody looking at rows still on
    the screen is left wondering whether the button worked (fault 58).

96. ⚠️⚠️⚠️ **A PIECE OF CARDBOARD ONE PIXEL WIDE. AND THE FIRST DIAGNOSIS,
    MADE BY READING THE CODE, WAS WRONG.** The designer, 2 September 2026,
    having cut a real game's sheets: *"Three keep coming up as blank, even
    though when I 'mend on page' they clearly appear, and it seems I can cut
    them. The numbering is also haywire - more cut than I have outlined?"*
    Three sheets: 18 outlines and 19 pieces, 15 and 16, 4 and 5. The extra
    piece on each showed no size at all — *"?" × "?"* wherever a size should
    have been.
    ⭐️⭐️⭐️ **THE REAL FAULT WAS ONE LINE OF THEIR OWN `index.json`, AND
    HABIT 2 WOULD HAVE HAD IT IN TEN MINUTES.** The rogue pieces measured
    **1 × 2 pixels, 1 × 1 and 1 × 1** — specks of ink stranded inside the
    tile beside them, dropped by that tile's own fill where a curve through
    a sharp corner overshoots. `keep()` has NO floor at all for a shape a
    person drew (fault 85, quite rightly), so a single pixel was cut,
    numbered, filed and counted as a component, and `piece_stats()` had
    nothing in it to measure.
    ⚠️⚠️ **The first attempt at this was reasoned out of the source and cost
    the designer an hour**: `label()` being four-connected, a notched outline
    might pinch to a diagonal touch and read as two shapes. That is real,
    it is fixed (`_merge_corners()`), and **it was not what was happening** —
    the speck is nowhere near touching. Reading their `index.json` said so
    at a glance: a box of `[4612, 1288, 4613, 1290]` is not a tile. *This
    file has said since fault 25 that reading the real data beats reasoning,
    and it was not done first because the code seemed to explain it.*
    ⭐️ The fix is `_absorb_dust()`: a label under `DUST_PX` is absorbed into
    the nearest shape of its own colour — **the shape whose fill dropped it**
    — so nothing is refused and not one pixel is thrown away. ⚠️ **This is
    NOT fault 85's floor coming back.** That floor refused a PIECE for its
    size and must never return; this sits three orders of magnitude below any
    real one (the smallest ever cut is 0.288 square inches — a hundred
    thousand pixels at 600 dpi), and it merges rather than discards. A check
    holds the floor to that margin, and another cuts a deliberately small
    piece to prove fault 85 still stands.
    ⚠️ **ONE PLACE, both callers.** `label_shapes()` is what `cut_sheet()`
    and `cut.py`'s standalone cutter both call, so this reaches the offline
    table too without a second copy — fault 24's rule holding again.
    ⭐️ Verified against the designer's own three sheets, read-only: 19 → 18,
    5 → 4, and the sheet whose speck had already gone left at 15. Teeth
    tried on both halves — disable the merge and four checks go red; disable
    the absorbing and the speck is cut as a piece again.
    ⭐️ **A full re-cut is what clears rogue pieces already in a project** —
    it sweeps every piece for that sheet and rebuilds from the outlines. The
    single-piece mend deliberately does not (fault 88), which is why mending
    them looked as though it had done nothing.

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
  room/fit_pieces.js     ⭐️⭐️ FIT TWO PIECES TOGETHER — lay one cut piece
                         against another to see whether their edges meet (do
                         these corridor tiles interlock?) and, where they are
                         two halves of one thing scanned across two pages, join
                         them into a single piece. ⚠️ The looking writes
                         NOTHING; joining is a button on the end of it, and
                         sets the halves aside rather than deleting them.
                         `POST /pieces/join`. See fault 89.
  room/tips.js           ⭐️ Every control says what it does. `data-tip` (or a
                         plain `title`, which it takes over) on ANY element.
                         Shared by both pages AND by the served table, and it
                         carries its own styling because the table does not
                         load room.css. check.sh fails on a button with
                         neither.
cutting_table.tpl.html   THE EDITOR. Shared by the room and the baked page.
cutting_table.py         bakes the editor + sheets into one offline HTML file
cut.py                   cuts pieces from a sheet + mask, standalone
  (the launcher)         ⭐️ `--install-launcher` writes `Cutting Room.app` —
                         an Info.plist, a shell script and an icon drawn here
                         with Pillow. ⚠️ ONE place works out where this copy
                         was cloned to and which python can run it; a second
                         would be a second thing to be wrong when the folder
                         moves. `--terminal-window` writes the older launcher
                         that shows its working; `--home` says where the
                         projects are and `--browser` says what opens the tab.
                         See faults 79 and ⚠️⚠️ 80, which is the one that
                         decides whether any of it works at all.
sheets.py                the image work: flood, label, separate, draft — and
                         ⭐️ the AUTOMATIC PASS: `local_field()` (the ground as
                         it falls on this sheet), `outline_of()` and
                         `regular_outline()` (a rectangle drawn as a rectangle),
                         `trace_all()` (WHICH blobs become suggestions) and
                         `worth_offering()` (⭐️ the floor under it, in printed
                         inches, read off a real game — fault 76).
                         ⚠️ The room and the baked table both use these; there
                         is no second copy. Faults 71 and 76.
                         ⭐️ `label_shapes()` merges same-colour labels that
                         only touch at a corner (`_merge_corners()`) and
                         absorbs a speck of a few pixels into the shape whose
                         own fill dropped it (`_absorb_dust()`) — a piece one
                         pixel wide was being cut and counted. Fault 96.
demo/make_demo_sheet.py  a pretend sheet, so the repo needs nobody's artwork
docs/make_guide_pictures.sh  photographs the room for GUIDE.md — a throwaway
                         game in a home of its own, on a port of its own, off
                         the demonstration sheet. ⚠️ Never point it at a real
                         project: opening a sheet SAVES.
check/check.sh           everything that can be checked without a person
  check/in_the_browser.js  drives a real Chrome over a throwaway game
  check/guessing_the_kind.py  the size rules, and what they refuse to say
  check/the_automatic_pass.py  ⭐️ the first attempt at a sheet: the shapes it
                         draws, and — the half that matters — the ones it
                         refuses to call a rectangle or a circle. Draws its
                         own sheet, unevenly lit and speckled. See fault 71.
  check/one_outline_one_piece.py  ⭐️ a hand-drawn outline that pinches to a
                         single diagonal pixel is still ONE piece, not two —
                         `_merge_corners()`'s own check. See fault 96.
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
| `export-<set>/` | ⭐️ the same, for ONE box of sheets taken away on its own — a folder per set, because an export is replaced whole and a set written into `export/` would destroy it. See fault 78 | yes, whole, every time |
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
check/check.sh          # 729 checks, about a minute
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

⚠️ It also holds the launcher to the two settings that decide whether it is
any use: that a home macOS will keep an app out of is **recognised and said
out loud** (and that a folder merely beginning with the same letters is not),
that the warning is a warning and still writes the launcher, and that a
launcher told where the projects are and which browser to open carries both —
in the app and in the plain one alike.

It presses **the launcher that opens the room with no terminal window**: the
bundle is the right shape, says which architecture to run as — ⭐️ the fault
that only launching it could find — carries an icon that is a real `icns`, and
refuses to replace an app of that name it did not write. Then it is **pressed**,
because a bundle of the right shape that does not open the room is fault 54: it
starts the room and lets go of it, a second press opens another tab rather than
a second room, a room that will not start **says so** instead of nothing at
all, and a room opened this way still closes from its own front page. ⚠️ Three
lines are changed in a copy first, and only three — the browser, the room's
`--home`, and the log — because a check must not reach out of its own sandpit.

It works the **three keys at the table**: `+` lays another copy of the chosen
piece down and hands it to Adjust ready to be dragged, `X` takes it off again
and says in the same breath how to put it back, `O` works on it alone and says
the others are **hidden, not deleted** before the same key brings them back —
and, the half that was asked for, **none of them fires while you are typing**.

It follows **the report's way in to a piece**: the served report links every
stem it prints and says what an orphan measures, the copy that leaves the room
carries no link at all, and — in the browser — a link naming one piece opens
that piece, **opens it from behind a chip that was hiding it**, drops the piece
out of the address so it does not keep pulling you back, and says so plainly
when the piece is not there rather than opening a different one.

It breaks **one line of a contents list into the components it really
stands for** and follows what that does to the pieces already linked to it —
including the one that matters most, that a name somebody typed themselves is
left exactly as it was.

It works the **list of pieces held back**: the chip gathers them, the reason
is printed on each row, a piece both set aside and held back stays on the list
dimmed with the count saying how many of it are those, the report's *N pieces
held back* is a link that opens that chip, and letting the piece go empties the
list again and says which empty it is.

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

It takes **one set away on its own**: a set the game does not have is refused,
a set is written into a folder of its own, the whole game's folder is still
there beside it, the pieces from another box are left out — ⭐️ which needed the
bench to grow a second box before it meant anything (fault 54) — the inventory
and the README say which set it is and that the others are exported separately,
and the whole game's checklist does not travel with it while the check against
the contents list does. Then in the browser: the way out offers the whole game
or one set, choosing one names the folder it will go into, and **pressing the
button writes that set's folder** rather than the game's.

It works **masking a part of a sheet off**: the whole sheet masked suggests
nothing, taking the mask off puts every suggestion back — which is the check
that holds the kept draft to knowing what it was an answer to — a nonsense
region and one too small to mean anything are dropped, and what survives is
written down on the sheet rather than merely answered. Then in the browser,
because a check through the API is a green light over a button that does
nothing (fault 61): the tool is in the served table, `M` puts it in hand, a box
dragged on the sheet **reaches the room's own file**, the table says nothing was
deleted, clicking the box takes it off again — and the baked offline page does
not offer the tool at all, measured rather than believed.

It holds **calling something a deck** to what that means: a component whose
kind is `deck` wants all of its cards with nobody pressing anything, and says
so — while ⚠️ **a line of CARDS still wants one**, which is the noise test
fault 52's reading of the real game settled, and so does a counter printed
twenty-six times. ⭐️ It starts from what a pasted contents list really leaves
behind — `each` stamped `false` on every line — rather than clearing the field
first, which is the difference between checking this rule and checking a state
no game is ever in. And the press that overrules it sticks, is written down,
and is not confused with the stamp.

It works **a deck on the Match board**: a deck of 24 is not settled by one
card or by two, while a counter printed 26 times still is on the first; the
deck's back is said once and reaches every card already linked, and every card
linked afterwards; a card given a back of its own keeps it; the back can be
taken off again; and a back naming a piece the game has not got is refused.
Then in the browser, because the fault was a list that emptied itself: a
part-marked deck is **still there** with *4 of 24* on it, carries a row for its
back, records that back when the row is dropped on a piece — and, the one that
matters, **dropping a card on the deck leaves it on the list, one further on**,
without the page being reloaded.

It works **fitting two pieces together**: a join with no name is refused, so is
a piece joined to itself and one the game has not got; two pieces are written
out as one and measured in inches; ⚠️ the two halves are **set aside, not
deleted**, and keep their names; and the joined piece answers to **no sheet**,
which is what stops a later re-cut dropping its record. Then in the browser:
the tool offers this game's pieces, choosing two lays them **edge to edge** and
says they meet, the arrow keys open a **gap** and the figure changes its own
name to say so, ⚠️ an arrow key inside the name box types instead of moving the
picture, and *edge to edge* puts them back.

It works **mending one piece**: cutting one outline writes that piece and
leaves its neighbour's picture untouched, both names exactly where they were —
and ⚠️ when the mend shifts the numbering the room cuts the **whole sheet**
instead and says so, with every name following its own piece. Teeth tried:
take the guard away and the checks catch the names landing on the wrong
pieces.

It works **filing a finished box away**: the mark is written, and ⚠️ **not one
figure moves** — which is the check the whole feature turns on, because a
filed set is done and counts as done where a set put by comes out of the
reckoning; the end-of-job report goes on asking for what is missing out of it
and says *filed away* on the band; the two marks are two lists and neither
press disturbs the other; and a mark naming neither a box nor a set is
refused. Then in the browser, because the fault to stop is a button that does
nothing (fault 61): the heading **offers** it, a box that is not finished
**says what is outstanding** and refusing that question changes nothing at
all, filing takes its sheets out of the views, the page **says how many that
is and where they went**, the chip and a **search** both reach them again, the
list that narrows the pieces by box collapses it to one line in a band of its
own — ⚠️ still there, not dropped — and bringing it back out puts every sheet
in front of you again.

It works **cutting a run of sheets**: asked for the lot, the room takes only
the sheets not cut yet; with nothing left it refuses in a sentence rather than
doing the game again; a sheet outlined AGAIN since its cut is waiting again;
and told which sheets are being looked at it does those and no others — while
ignoring one another tab has since cut and one the game has not got. ⚠️ And
*every sheet ended up cut*, or the cheap way to pass all of that is to skip
everything. Then in the browser, because the fault was that the button's words
and its action disagreed: the button **names the number it will act on**, says
how many it is skipping as already done, says how many are waiting that the
list is not showing, and pressing it cuts the sheet it named and leaves the
other one waiting.

It gives the automatic pass a **grubby scan** — a hairline crack, a speck and
a scratch across the glass, each of which cleared every test the room used to
have — and holds it to both halves at once: not one of them is offered, **and**
every piece really printed on the sheet is still found, because the cheap way
to pass the first is to raise the floor until real counters go too.

`check/the_automatic_pass.py` is the **first attempt at a sheet** on its own —
no browser and no project, because it is arithmetic over a picture. It draws
its own sheet out of the shapes a box really holds (square, rectangle, circle,
oval, two hexagons, a triangle, a coastline, a crooked rectangle, a rounded
counter, a big pale board) and prints it the way a scan really arrives:
unevenly lit, speckled with noise, squashed through a JPEG. ⭐️ **Fourteen of
its twenty-nine checks are about it refusing to fit a shape** — a hexagon
squared off is a confident wrong answer drawn over somebody's artwork.
Its teeth were tried on all three faults of number 71: take the regular fits
out and ten go red, take the local ground out and three go red (naming a
printed square that comes back with 34 nodes and bent sides).

`check/guessing_the_kind.py` is the measuring on its own — no browser and no
project, because `guess_kind()` is arithmetic. ⭐️ **Fourteen of its checks are
about the room saying NOTHING**, which is the half that matters: the rules that
recognise a card will not rot, but a future rule getting greedy would put a
confident wrong answer in front of somebody naming three hundred pieces. Its
teeth were tried and found blunt the first time — widening the tile rule to
swallow whole boards left every silence check green, because each of them
happened to be settled by a *different* rule. The fences round each band are
there now.

`check/one_outline_one_piece.py` is `label_shapes()`'s own check, no browser
and no project: hand-built masks, the same way the checks above test `keep()`
and `guess_kind()` directly. ⭐️ Its teeth were tried on both halves — make
`_merge_corners()` a no-op and four go red; make `_absorb_dust()` a no-op and
a speck of one pixel is cut as a piece again. ⚠️ **The half that matters is
the noise test**: a genuinely small piece somebody drew is still cut, and the
floor is held to a fraction of the smallest piece a real game has held, or
this becomes fault 85 all over again.

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
