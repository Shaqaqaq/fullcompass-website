// Full Compass website: the one script. It reads the update site's list of the latest versions
// (https://updates.fullcompass.co.uk/updates.json) and fills in the download details and release notes.
// Without it (no JavaScript, or the list can't be read) each page keeps its written fallback.
(function () {
  "use strict";

  var SITE = "https://updates.fullcompass.co.uk/";
  var LIST = SITE + "updates.json";
  var ICONS = { suite: "suite", accounts: "accounts", books: "books", businesstax: "business-tax", personaltax: "personal-tax", pay: "pay" };

  var wanted = document.querySelector("[data-fc]");
  if (!wanted || !window.fetch || !window.JSON) return;

  function all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function set(name, text) { all('[data-fc="' + name + '"]').forEach(function (el) { el.textContent = text; }); }

  function megabytes(bytes) { return (bytes / 1048576).toFixed(1) + " MB"; }

  function longDate(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "";
    var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    return d.getUTCDate() + " " + months[d.getUTCMonth()] + " " + d.getUTCFullYear();
  }

  // Only a plain installer name is linked: letters, digits, dots, dashes and underscores, ending .exe.
  function fileUrl(file) {
    var name = String(file || "").replace(/^files\//, "");
    return /^[A-Za-z0-9._-]+\.exe$/.test(name) ? SITE + "files/" + name : null;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function showSetup(m) {
    var s = m.setup, d = s && s.download;
    var url = d && fileUrl(d.file);
    if (!s || !url || typeof d.size !== "number" || !/^[0-9a-f]{64}$/.test(d.sha256 || "")) return;
    set("setup-version", s.version);
    set("setup-size", megabytes(d.size));
    set("setup-sha", d.sha256);
    set("setup-file", url.slice(url.lastIndexOf("/") + 1));
    all('[data-fc="setup-link"]').forEach(function (a) { a.href = url; });
  }

  function showReleases(m) {
    var box = document.querySelector('[data-fc="releases"]');
    if (!box || !Array.isArray(m.apps) || !m.apps.length) return;
    var list = el("ul", "releases");
    m.apps.forEach(function (app) {
      var li = el("li");
      var icon = ICONS[app.key];
      if (icon) {
        var img = el("img");
        img.src = "/assets/img/apps/" + icon + ".png";
        img.alt = "";
        img.width = 48;
        img.height = 48;
        li.appendChild(img);
      }
      var h = el("h3", null, app.name);
      h.appendChild(el("span", "ver", app.version));
      li.appendChild(h);
      li.appendChild(el("p", null, app.notes || "No changes beyond the version."));
      list.appendChild(li);
    });
    box.textContent = "";
    box.appendChild(list);
  }

  fetch(LIST, { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (signed) {
      var m = typeof signed.manifest === "string" ? JSON.parse(signed.manifest) : signed.manifest;
      if (!m) return;
      showSetup(m);
      showReleases(m);
      if (m.published) set("published", longDate(m.published));
      document.documentElement.classList.add("fc-live");
    })
    .catch(function () { /* keep the written fallback */ });
})();
