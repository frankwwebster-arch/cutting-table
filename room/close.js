/* Closing the Cutting Room, from the Cutting Room.
 *
 * ⭐️ The designer, 22 August 2026: "a simpler way to open and quit. I don't like
 * terminal at the best of times." Quitting used to mean finding the Terminal
 * window the room was started from and closing it. They are already looking at
 * the room in a browser, so the room closes itself from here.
 *
 * ⚠️ Nothing here may cut a save short. Fault 1 — the fault this whole tool
 * exists because of — is work that stayed in the browser and never reached
 * the disk. So before it closes, the room is asked what is still in flight:
 * an import or a cut running on a thread, or a cutting table open in another
 * tab with an edit not yet written down. Anything holding is named, in plain
 * English, and the person decides.
 *
 * Shared by the front page and a project's page.
 */
(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* The room has gone. There is no server left to serve a page, so this page
     rewrites itself into the closed sign. */
  function closedSign(how) {
    document.title = "The Cutting Room is closed";
    var main = document.createElement("div");
    main.className = "closedroom";
    main.innerHTML =
      "<h1>The Cutting Room is closed.</h1>" +
      "<p>Everything you cut and everything you named is on the disk, where it was " +
      "all along. Nothing was kept in this browser.</p>" +
      "<p class=\"how\">" + esc(how || "Open it again by running cutting_room.py.") + "</p>" +
      "<p class=\"tiny muted\">This page is just a sign on the door — there is nothing " +
      "behind it now. You can close the tab.</p>";
    document.body.innerHTML = "";
    document.body.appendChild(main);
  }

  /* What is in flight, as a question a person can answer. */
  function ask(reasons) {
    var lines = reasons.map(function (r) { return "  • " + r.what; });
    var hold = reasons.some(function (r) { return r.hold; });
    return window.confirm(
      (hold ? "Something is still being written down:\n\n"
            : "The room is quiet, but this is still open:\n\n") +
      lines.join("\n") + "\n\n" +
      (hold ? "Closing now could lose it. Close the room anyway?"
            : "Close the Cutting Room?"));
  }

  function close() {
    fetch("/api/busy")
      .then(function (r) { return r.json(); })
      .then(function (b) {
        var reasons = b.reasons || [];
        if (reasons.length && !ask(reasons)) return null;
        return fetch("/api/close", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ force: reasons.length > 0 })
        }).then(function (r) { return r.json(); });
      })
      .then(function (j) {
        if (!j) return;
        if (j.error) { window.alert("The room could not close itself: " + j.error); return; }
        // It said it would go. Give the server the half-second it asked for,
        // then put the sign up — by which time there is nothing to fetch.
        if (j.closed) setTimeout(function () { closedSign(j.how); }, 700);
      })
      .catch(function () {
        // No answer at all almost always means it has already gone.
        closedSign("");
      });
  }

  function install() {
    var nav = document.querySelector("header.bar nav");
    if (!nav || nav.querySelector("#closeRoom")) return;
    var a = document.createElement("a");
    a.href = "#";
    a.id = "closeRoom";
    a.className = "closelink";
    a.textContent = "Close the Cutting Room";
    a.title = "Stop the room. Everything cut and named stays on the disk.";
    a.addEventListener("click", function (e) { e.preventDefault(); close(); });
    nav.appendChild(a);
  }

  /* ⭐️⚠️ A ROOM RUNNING YESTERDAY'S CODE MUST SAY SO.
     The designer, 23 August 2026, pressing a button built that afternoon: "when I
     press 'Split it' I get a 'no such call' error."

     They had left the room open for hours. Its pages are read off the disk on
     every request, so the new button was there; its Python is whatever was
     loaded when the process started, so the route behind the button was not.
     A running program cannot re-read itself, and nothing said so — the button
     simply looked broken.

     ⚠️ It is a BANNER, not a console message. The person who needs to read
     this is the one looking at the page, and the room has to be closed and
     opened again before anything built since will work. */
  function sayIfStale() {
    fetch("/api/health")
      .then(function (r) { return r.json(); })
      .then(function (j) {
        if (!j || !j.stale || document.getElementById("staleRoom")) return;
        var bar = document.createElement("div");
        bar.id = "staleRoom";
        bar.className = "staleroom";
        bar.innerHTML =
          "<b>This room is running older code than these pages.</b> " +
          "The Cutting Room has been updated since it was opened, and a page " +
          "is read fresh every time while the room itself is not — so a button " +
          "added since may answer <i>no such call</i>. " +
          "<b>Close the room and open it again</b> and it will work. " +
          "Nothing is at risk: everything cut and named is on the disk.";
        document.body.insertBefore(bar, document.body.firstChild);
      })
      .catch(function () { /* the room has gone; the closed sign covers that */ });
  }

  window.RoomClose = { install: install, close: close, sign: closedSign,
                       stale: sayIfStale };
  // ?closedsign=1 puts the sign up without closing anything, so it can be
  // photographed. The same trick as ?probe=1 and ?dropprobe=1.
  if (/[?&]closedsign=1/.test(location.search)) {
    setTimeout(function () { closedSign("Double-click Cutting Room to open it again."); }, 30);
  }
  function start() { install(); sayIfStale(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
