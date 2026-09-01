/* FIT TWO PIECES TOGETHER — lay one cut piece against another, see whether
   their edges meet, and join them into one if they are two halves of the same
   thing.

   ⭐️⭐️ WHY IT IS IN THE ROOM AT ALL. The designer, 26 August 2026, of a spine
   scanned across two pages: "I have a component (the spine) which extends over
   2 pages. I need a way to manually stick them together." That was done once by
   hand — and then, immediately: "ensure it is baked into the platform - I have
   a new use for something like it... ensuring that corridor pieces interlock
   neatly."

   ⭐️ THOSE ARE TWO DIFFERENT JOBS AND THE COMMONER ONE WRITES NOTHING. Asking
   "do these two edges meet?" is looking, not making — so this tool is a light
   table first, and *Join them into one piece* is a button on the end of it.
   Nothing here changes a piece until that button is pressed.

   ⚠️ It works in TRUE PIECE PIXELS throughout and multiplies by the zoom only
   when it draws. Holding the offset in screen pixels would lose precision every
   time the zoom changed, and the offset is the thing the whole tool produces.

   ⚠️ IT USES EACH PIECE'S FULL PICTURE, not its thumbnail — the question is
   whether two printed edges line up, and a thumbnail cannot answer it (fault
   40's lesson, that a stamp-sized picture is no use for a judgement). Only two
   are ever loaded at a time, which is the guard fault 12 asks for.
*/
window.FitPieces = (function () {
  "use strict";

  var api = "", base = "", pieces = [], onDone = null;
  var A = null, B = null;                 // { stem, w, h, img }
  var dx = 0, dy = 0, zoom = 1, step = 10, seamOn = true, ready = false;

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function inches(px, dpi) { return (px / (dpi || 300)).toFixed(2) + " in"; }

  /* ---------------------------------------------------------- the picker */

  function fill(sel, chosen) {
    var by = {}, order = [];
    pieces.forEach(function (p) {
      var k = p.book || "";
      if (!by[k]) { by[k] = []; order.push(k); }
      by[k].push(p);
    });
    order.sort();
    sel.innerHTML = '<option value="">choose a piece…</option>' +
      order.map(function (k) {
        return '<optgroup label="' + esc(k || "not off any sheet") + '">' +
          by[k].map(function (p) {
            return '<option value="' + esc(p.stem) + '"' +
              (p.stem === chosen ? " selected" : "") + ">" +
              esc((p.name ? p.name + " — " : "") + p.stem) + "</option>";
          }).join("") + "</optgroup>";
      }).join("");
  }

  /* ------------------------------------------------------------ the table */

  function load(which, stem, then) {
    if (!stem) { if (which === "a") A = null; else B = null; then(); return; }
    var im = new Image();
    im.onload = function () {
      var rec = { stem: stem, w: im.naturalWidth, h: im.naturalHeight, img: im };
      if (which === "a") A = rec; else B = rec;
      then();
    };
    im.onerror = function () { then(); };
    im.src = base + "/piece/" + encodeURIComponent(stem) + ".png";
    im.className = which === "a" ? "fpA" : "fpB";
    im.draggable = false;
    im.alt = which === "a" ? "the piece held still" : "the piece you move";
  }

  function stage() { return $("fpStage"); }

  function draw() {
    var st = stage(), table = $("fpTable");
    if (!A || !B) {
      st.innerHTML = "";
      $("fpFigs").hidden = true;
      $("fpEmpty").hidden = false;
      $("fpJoin").disabled = true;
      ready = false;
      return;
    }
    $("fpEmpty").hidden = true;
    $("fpFigs").hidden = false;
    $("fpJoin").disabled = false;
    if (!ready) {
      st.innerHTML = "";
      st.appendChild(A.img);
      st.appendChild(B.img);
      var line = document.createElement("div");
      line.id = "fpSeam";
      st.appendChild(line);
      ready = true;
    }
    var minX = Math.min(0, dx), minY = Math.min(0, dy);
    var maxX = Math.max(A.w, dx + B.w), maxY = Math.max(A.h, dy + B.h);
    function place(el, x, y, w, h) {
      el.style.left = ((x - minX) * zoom) + "px";
      el.style.top = ((y - minY) * zoom) + "px";
      el.style.width = (w * zoom) + "px";
      el.style.height = (h * zoom) + "px";
    }
    place(A.img, 0, 0, A.w, A.h);
    place(B.img, dx, dy, B.w, B.h);
    st.style.width = ((maxX - minX) * zoom) + "px";
    st.style.height = ((maxY - minY) * zoom) + "px";
    var seam = $("fpSeam");
    seam.style.left = ((dx - minX) * zoom) + "px";
    seam.style.height = ((maxY - minY) * zoom) + "px";
    seam.hidden = !seamOn;

    var dpi = (pieceOf(A.stem) || {}).dpi || 300;
    var over = A.w - dx;                   // positive: they overlap
    $("fpDx").textContent = dx;
    $("fpDy").textContent = dy;
    $("fpDxin").textContent = inches(dx, dpi);
    $("fpDyin").textContent = inches(dy, dpi);
    /* ⭐️ OVERLAP AND GAP ARE ONE NUMBER READ TWO WAYS, and which of them is
       showing tells you which job you are doing: two halves of a spine
       overlap, two corridor tiles that interlock should meet at nothing. */
    $("fpMeetWhat").textContent = over > 0 ? "Overlap" : over < 0 ? "Gap" : "They meet";
    $("fpMeet").textContent = over === 0 ? "0" : Math.abs(over);
    $("fpMeetin").textContent = over === 0 ? "edge to edge" : inches(Math.abs(over), dpi);
    $("fpMeet").className = over === 0 ? "good" : "";
    $("fpTot").textContent = (maxX - minX) + " × " + (maxY - minY);
    $("fpTotin").textContent = inches(maxX - minX, dpi) + " × " + inches(maxY - minY, dpi);
  }

  function pieceOf(stem) {
    return pieces.filter(function (p) { return p.stem === stem; })[0];
  }

  /* ⭐️ FIT AND CENTRE, and it is what the tool opens on. The designer, 26
     August 2026: "Better if they both start next to each other, centered in
     the window and I can then drag. Zoom only important once I've done a rough
     join." So the two start edge to edge with the whole of both in view. */
  function fit() {
    if (!A || !B) return;
    var table = $("fpTable"), pad = 36;
    var wide = Math.max(A.w, dx + B.w) - Math.min(0, dx);
    var tall = Math.max(A.h, dy + B.h) - Math.min(0, dy);
    zoom = Math.max(0.01, Math.min(4,
      Math.min((table.clientWidth - pad) / wide, (table.clientHeight - pad) / tall)));
    $("fpZoom").value = Math.round(zoom * 1000);
    $("fpZval").textContent = Math.round(zoom * 100) + "%";
    draw();
    centre();
  }
  function centre() {
    var t = $("fpTable"), st = stage();
    t.scrollLeft = (st.offsetWidth - t.clientWidth) / 2;
    t.scrollTop = (st.offsetHeight - t.clientHeight) / 2;
  }

  /* ------------------------------------------------------------ the wiring */

  function wire() {
    var table = $("fpTable");

    ["fpPickA", "fpPickB"].forEach(function (id, i) {
      $(id).addEventListener("change", function () {
        ready = false;
        load(i ? "b" : "a", this.value, function () {
          if (A && B && !dx && !dy) { dx = A.w; dy = 0; }   // edge to edge
          draw();
          fit();
        });
      });
    });

    // dragging B, in true piece pixels
    var down = false, ox = 0, oy = 0;
    table.addEventListener("pointerdown", function (e) {
      if (!B || e.target !== B.img) return;
      down = true; ox = e.clientX; oy = e.clientY;
      B.img.setPointerCapture(e.pointerId);
      B.img.classList.add("dragging");
      e.preventDefault();
    });
    table.addEventListener("pointermove", function (e) {
      if (!down) return;
      dx += Math.round((e.clientX - ox) / zoom);
      dy += Math.round((e.clientY - oy) / zoom);
      ox = e.clientX; oy = e.clientY;
      draw();
    });
    function up() { if (down) { down = false; if (B) B.img.classList.remove("dragging"); } }
    table.addEventListener("pointerup", up);
    table.addEventListener("pointercancel", up);

    /* ⚠️ The arrow keys stand down inside a field, exactly as the table's own
       shortcuts do (fault 2) — the name box for the joined piece is right
       there, and typing in it must not slide the picture about. */
    document.addEventListener("keydown", function (e) {
      if ($("tab-fit").hidden) return;
      var t = e.target || {};
      if (/^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName || "") || t.isContentEditable) return;
      var k = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
      if (!k || !A || !B) return;
      e.preventDefault();
      dx += k[0] * step; dy += k[1] * step;
      draw();
    });

    $("fpZoom").addEventListener("input", function () {
      // ⚠️ zoom about the middle of what is on screen, or whatever you were
      // studying slides off the edge every time you touch the slider
      var st = stage();
      var cx = (table.scrollLeft + table.clientWidth / 2) / Math.max(1, st.offsetWidth);
      var cy = (table.scrollTop + table.clientHeight / 2) / Math.max(1, st.offsetHeight);
      zoom = this.value / 1000;
      $("fpZval").textContent = Math.round(zoom * 100) + "%";
      draw();
      table.scrollLeft = cx * st.offsetWidth - table.clientWidth / 2;
      table.scrollTop = cy * st.offsetHeight - table.clientHeight / 2;
    });
    $("fpOp").addEventListener("input", function () {
      if (B) B.img.style.opacity = this.value / 100;
    });
    $("fpSteps").addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("button") : null;
      if (!t) return;
      step = +t.dataset.step;
      this.querySelectorAll("button").forEach(function (x) { x.classList.toggle("on", x === t); });
    });
    $("fpDiff").addEventListener("click", function () {
      if (!B) return;
      var on = B.img.style.mixBlendMode !== "difference";
      B.img.style.mixBlendMode = on ? "difference" : "normal";
      this.classList.toggle("on", on);
    });
    $("fpSeamBtn").addEventListener("click", function () {
      seamOn = !seamOn; this.classList.toggle("on", seamOn); draw();
    });
    $("fpEdge").addEventListener("click", function () {
      if (!A) return;
      dx = A.w; dy = 0; fit();
    });
    $("fpFit").addEventListener("click", fit);
    $("fpSwap").addEventListener("click", function () {
      var a = $("fpPickA").value, b = $("fpPickB").value;
      $("fpPickA").value = b; $("fpPickB").value = a;
      ready = false; dx = 0; dy = 0;
      load("a", b, function () { load("b", a, function () { dx = A ? A.w : 0; dy = 0; fit(); }); });
    });
    window.addEventListener("resize", function () { if (!$("tab-fit").hidden) centre(); });

    $("fpJoin").addEventListener("click", join);
  }

  /* ⚠️ THE ONE THING HERE THAT WRITES ANYTHING, and it says what it will do
     before it does it. Nothing is deleted: the two halves are SET ASIDE, which
     the Pieces page undoes (fault 19). */
  function join() {
    if (!A || !B) return;
    var name = $("fpName").value.trim();
    if (!name) {
      window.alert("Give the joined piece a name first — it belongs to no sheet, " +
                   "so its name is the only way you will find it again.");
      $("fpName").focus();
      return;
    }
    var aside = $("fpAside").checked;
    if (!window.confirm(
        "Make one new piece, “" + name + "”, out of " + A.stem + " and " + B.stem +
        ".\n\n" + (aside
          ? "The two halves are SET ASIDE — not deleted. They keep their names, stay " +
            "in the Pieces list dimmed, and the same button there puts them back."
          : "Both halves are left exactly where they are, so the same artwork will be " +
            "in the export twice.") +
        "\n\nNothing else changes.")) return;
    var b = $("fpJoin");
    b.disabled = true; b.textContent = "Joining…";
    fetch(api + "/pieces/join", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ a: A.stem, b: B.stem, dx: dx, dy: dy,
                             name: name, aside: aside })
    }).then(function (r) { return r.json(); }).then(function (j) {
      b.disabled = false; b.textContent = "Join them into one piece…";
      if (j.error) { window.alert(j.error); return; }
      window.alert("“" + j.name + "” made — " + j.w + " × " + j.h + " px" +
                   (j.w_in ? ", " + j.w_in + " × " + j.h_in + " in" : "") + ".\n\n" +
                   (j.aside ? "The two halves are set aside; nothing was deleted."
                            : "Both halves are still in play.") +
                   "\n\nIt is on the Pieces page under “" + j.name + "”.");
      if (onDone) onDone(j);
    }).catch(function (e) {
      b.disabled = false; b.textContent = "Join them into one piece…";
      window.alert("The join failed: " + e.message);
    });
  }

  /* --------------------------------------------------------------- opening */

  return {
    /* `list` is [{stem, name, book, dpi}]. Called every time the tab is
       opened, so a piece cut a moment ago is in the list. */
    open: function (opts) {
      api = opts.api; base = opts.base; pieces = opts.pieces || [];
      onDone = opts.onDone || null;
      if (!$("fpTable").dataset.wired) { wire(); $("fpTable").dataset.wired = "1"; }
      var wasA = $("fpPickA").value, wasB = $("fpPickB").value;
      fill($("fpPickA"), wasA);
      fill($("fpPickB"), wasB);
      if (A && B) { draw(); centre(); }
    }
  };
})();
