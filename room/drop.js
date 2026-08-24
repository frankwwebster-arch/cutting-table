/* Dropping things on the room.
 *
 * ⭐️ THE DESIGNER, 21 August 2026: "I honestly think a drag and drop upload function
 * is likely to be more useful" — more useful, that is, than pasting links at
 * it. They are right, and the reason is worth writing down: the files are already
 * on their disk. Drive and Dropbox both put a folder there, or hand you a ZIP;
 * the shortest path from that to a cut piece is to pick the folder up and drop
 * it on the page. A link is a detour round the machine you are sitting at.
 *
 * So this does three things the plain <input type=file> cannot:
 *
 *   1. THE WHOLE WINDOW IS THE TARGET. Dropping a PDF on a page that is not
 *      expecting it makes the browser NAVIGATE TO THE FILE and lose your work,
 *      which is a nasty way to learn where the drop zone was. Nothing here can
 *      do that any more.
 *   2. A FOLDER CAN BE DROPPED, and is walked to the bottom. That is the whole
 *      answer to "can I have my Drive folder?" — download it, drop it, done.
 *   3. IT SAYS WHAT IT WILL TAKE while you are still holding the mouse: how
 *      many files it can read, and what it is ignoring.
 *
 * Nothing here is specific to any one page: install() is handed a callback and
 * gets on with it.
 */
(function () {
  "use strict";

  var TAKE = /\.(pdf|png|jpe?g|tiff?|webp|bmp|gif|docx?|zip)$/i;

  /* A dropped folder arrives as a DIRECTORY ENTRY, not as files, and reading
     one is a small ceremony: readEntries() hands back at most a hundred at a
     time and you must keep asking until it hands back none. Miss that and a
     folder of two hundred scans quietly imports the first hundred. */
  function walk(entry, out, depth, then) {
    if (!entry || depth > 8) return then();
    if (entry.isFile) {
      entry.file(function (f) {
        if (TAKE.test(f.name) && !/^\./.test(f.name)) {
          f._path = entry.fullPath || f.name;
          out.push(f);
        }
        then();
      }, then);
      return;
    }
    if (!entry.isDirectory) return then();
    if (/^(__MACOSX|\.)/.test(entry.name)) return then();
    var reader = entry.createReader();
    var kids = [];
    (function more() {
      reader.readEntries(function (batch) {
        if (!batch.length) {
          var left = kids.length;
          if (!left) return then();
          kids.forEach(function (k) { walk(k, out, depth + 1, function () { if (!--left) then(); }); });
          return;
        }
        kids = kids.concat(Array.prototype.slice.call(batch));
        more();
      }, then);
    })();
  }

  /* Is this drag carrying files from outside the browser, or is it one thing
     on the page being dragged onto another? All four window handlers ask,
     because the answer decides whether any of this applies at all. */
  function carriesFiles(e) {
    var dt = e.dataTransfer;
    return !!dt && Array.prototype.indexOf.call(dt.types || [], "Files") >= 0;
  }

  function filesFrom(dt, then) {
    var items = dt.items;
    var canWalk = items && items.length && typeof items[0].webkitGetAsEntry === "function";
    if (!canWalk) {
      var plain = Array.prototype.slice.call(dt.files || []).filter(function (f) {
        return TAKE.test(f.name) && !/^\./.test(f.name);
      });
      return then(plain, Array.prototype.slice.call(dt.files || []).length - plain.length);
    }
    var entries = [];
    for (var i = 0; i < items.length; i++) {
      var e = items[i].webkitGetAsEntry();
      if (e) entries.push(e);
    }
    var out = [], left = entries.length;
    if (!left) return then([], 0);
    var dropped = Array.prototype.slice.call(dt.files || []).length;
    entries.forEach(function (e) {
      walk(e, out, 0, function () {
        if (--left) return;
        // sort so a book's pages arrive in order, and folders group together
        out.sort(function (a, b) {
          var x = (a._path || a.name).toLowerCase(), y = (b._path || b.name).toLowerCase();
          return x < y ? -1 : x > y ? 1 : 0;
        });
        then(out, Math.max(0, dropped - out.length));
      });
    });
  }

  /* The curtain that comes down over the whole window while something is
     being dragged over it. */
  function curtain() {
    var el = document.getElementById("dropCurtain");
    if (el) return el;
    el = document.createElement("div");
    el.id = "dropCurtain";
    el.innerHTML = '<div class="inner"><b id="dropCurtainTitle">Drop them anywhere</b>' +
                   '<span id="dropCurtainSub"></span></div>';
    document.body.appendChild(el);
    return el;
  }

  function install(opts) {
    var onFiles = opts.onFiles;
    // ⚠️ The title is asked for at DRAG TIME, not at install time. The page
    // installs this before it has heard back what the project is called, and
    // the curtain read "Drop them into …" for exactly as long as it took to
    // photograph it.
    var title = opts.title || "Drop them anywhere on this page";
    var depth = 0;

    function show(on) {
      var c = curtain();
      c.classList.toggle("on", on);
      if (on) {
        var t = (typeof title === "function") ? title() : title;
        document.getElementById("dropCurtainTitle").textContent = t || "Drop them anywhere on this page";
        document.getElementById("dropCurtainSub").textContent =
          "PDFs, scans, Word files with pictures in them, ZIPs — or a whole folder";
      }
    }

    // ⚠️ dragenter/dragleave fire for every element the pointer crosses, so a
    // plain toggle flickers the curtain the moment you move. Count instead.
    // A drag cannot be synthesised from outside the browser, so the curtain
    // is otherwise impossible to photograph. ?dropprobe=1 shows it.
    if (/[?&]dropprobe=1/.test(location.search)) setTimeout(function () { show(true); }, 400);

    window.addEventListener("dragenter", function (e) {
      if (!carriesFiles(e)) return;
      e.preventDefault();
      depth++;
      show(true);
    });
    window.addEventListener("dragover", function (e) {
      if (!carriesFiles(e)) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
    });
    window.addEventListener("dragleave", function (e) {
      if (!carriesFiles(e)) return;
      depth = Math.max(0, depth - 1);
      if (!depth) show(false);
    });
    window.addEventListener("drop", function (e) {
      // ⚠️ THE DESIGNER, 22 August 2026: dragging a component's name onto a piece in
      // Match "always seems to serve an error code (even though it also
      // appears to work!)". It did both. dragenter and dragover already asked
      // whether the drag carried FILES; this one did not, so a text/plain drag
      // inside the page — which is what Match is — bubbled up to the window,
      // was taken for a file import, found no files, and put up "Nothing was
      // dropped that the room can read." The link had already been made by
      // then. The window is the target for FILES ONLY; a drag between two
      // things on the page is none of its business.
      if (!carriesFiles(e)) return;
      e.preventDefault();
      depth = 0;
      show(false);
      var c = curtain();
      c.classList.add("on");
      document.getElementById("dropCurtainTitle").textContent = "Reading what you dropped…";
      document.getElementById("dropCurtainSub").textContent = "";
      filesFrom(e.dataTransfer, function (files, ignored) {
        c.classList.remove("on");
        if (!files.length) {
          window.alert(ignored
            ? "None of those " + ignored + " could be read. The room takes PDFs, PNG/JPEG/TIFF scans, Word files with pictures in them, and ZIPs."
            : "Nothing was dropped that the room can read.");
          return;
        }
        onFiles(files, ignored);
      });
    });
  }

  window.RoomDrop = { install: install, TAKE: TAKE };
})();
