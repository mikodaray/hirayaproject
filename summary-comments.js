// Comment boxes for each page group on summary.html.
// Drafts autosave in this browser. "Save" writes story-bible/commentary.json in the GitHub repo
// (needs a one time access token, see the Set up saving panel), so Claude can read the commentary there.
(function () {
  var REPO = "mikodaray/hirayaproject", PATH = "story-bible/commentary.json", BRANCH = "main";
  var LS = "hirayaCommentsV1", TK = "hirayaGhToken", SK = "hirayaSheetUrl", SHEET_URL = "https://script.google.com/macros/s/AKfycbz1Bih-S2BRZ2eWDeDN5bn8z2ptBj1MGFRVkvRL_3xRhywsCCWX1RQrIRefNwn3t5ps/exec";
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } }
  function lsDel(k) { try { localStorage.removeItem(k); } catch (e) {} }
  var local = {}; try { local = JSON.parse(lsGet(LS) || "{}") || {}; } catch (e) { local = {}; }
  var remote = {};
  var groups = [];
  var list = document.querySelector("ol.beats");
  if (!list) return;

  function sheetUrl() { return lsGet(SK) || SHEET_URL; }
  function persist() { lsSet(LS, JSON.stringify(local)); }
  function now() { return new Date().toISOString(); }
  function b64enc(s) { return btoa(unescape(encodeURIComponent(s))); }
  function b64dec(s) { return decodeURIComponent(escape(atob(s.replace(/\s/g, "")))); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  function token() { return lsGet(TK) || ""; }

  // toolbar
  var bar = el("div", "cm-bar");
  bar.innerHTML = '<p><strong>Your commentary.</strong> Write notes under any part of the story. Claude will read them from the repo and use them as input when you ask it to act on them.</p>';
  var btns = el("div", "cm-btns");
  var bAll = el("button", "btn", "Save all"), bCopy = el("button", "btn", "Copy all"), bDl = el("button", "btn", "Download"), bSet = el("button", "btn", "Set up saving");
  [bAll, bCopy, bDl, bSet].forEach(function (b) { b.type = "button"; btns.appendChild(b); });
  bar.appendChild(btns);
  var barStatus = el("p", "cm-status"); barStatus.setAttribute("aria-live", "polite"); bar.appendChild(barStatus);
  var setup = el("div", "cm-setup"); setup.hidden = true;
  setup.innerHTML = '<p><strong>One time setup, so the boxes can save to the repo.</strong></p><ol>' +
    '<li>On GitHub, open Settings, Developer settings, Personal access tokens, Fine grained tokens, Generate new token.</li>' +
    '<li>Repository access: only <b>mikodaray/hirayaproject</b>. Permissions: Contents, <b>Read and write</b>. Pick a short expiry, such as 30 days.</li>' +
    '<li>Paste the token below and press Save token. It stays only in this browser. Never send it to anyone, including Claude.</li></ol>' +
    '<p class="cm-warn">Every page under mikodaray.github.io shares this browser storage, so keep the token limited to this repo and let it expire.</p>';
  var inp = el("input"); inp.type = "password"; inp.autocomplete = "off"; inp.placeholder = "Paste token"; inp.setAttribute("aria-label", "GitHub token");
  var bSave = el("button", "btn", "Save token"), bDel = el("button", "btn", "Remove token");
  bSave.type = bDel.type = "button";
  var row = el("div", "cm-row"); row.appendChild(inp); row.appendChild(bSave); row.appendChild(bDel); setup.appendChild(row);
  var sp = el("p"); sp.innerHTML = "<strong>Google Sheet.</strong> Already built in, every save updates a row per page group in the sheet. You can override the Web app URL below if you ever redeploy.";
  setup.appendChild(sp);
  var sinp = el("input"); sinp.type = "url"; sinp.placeholder = "https://script.google.com/macros/s/.../exec"; sinp.setAttribute("aria-label", "Google Sheet web app URL"); sinp.value = sheetUrl() || "";
  var sBtn = el("button", "btn", "Save sheet URL"), sDel = el("button", "btn", "Remove sheet URL"); sBtn.type = sDel.type = "button";
  var srow = el("div", "cm-row"); srow.appendChild(sinp); srow.appendChild(sBtn); srow.appendChild(sDel); setup.appendChild(srow);
  var setupStatus = el("p", "cm-status"); setup.appendChild(setupStatus);
  bar.appendChild(setup);
  list.parentNode.insertBefore(bar, list);

  // one box per group
  Array.prototype.forEach.call(list.children, function (li) {
    var a = li.querySelector("a.pages"); if (!a) return;
    var key = (a.getAttribute("href").split("#")[1] || a.textContent).replace(/\W+/g, "");
    var h = li.querySelector("h4");
    var g = { key: key, pages: a.textContent.trim(), title: h ? h.textContent.trim() : "" };
    var box = el("div", "cm");
    var id = "cm-" + key;
    var label = el("label", "", "Your commentary on " + g.pages.toLowerCase() + ": " + g.title); label.setAttribute("for", id);
    var ta = el("textarea"); ta.id = id; ta.rows = 3; ta.placeholder = "Add your notes, changes or ideas for this part of the story.";
    var r = el("div", "cm-row");
    var b = el("button", "btn", "Save"); b.type = "button";
    var st = el("span", "cm-status"); st.setAttribute("aria-live", "polite");
    r.appendChild(b); r.appendChild(st);
    box.appendChild(label); box.appendChild(ta); box.appendChild(r); li.appendChild(box);
    g.ta = ta; g.st = st; g.btn = b; groups.push(g);
    if (local[key]) ta.value = local[key].text || "";
    var timer;
    ta.addEventListener("input", function () {
      local[key] = { text: ta.value, updated: now(), dirty: true }; persist();
      st.textContent = "Draft saved in this browser, not in the repo yet.";
      clearTimeout(timer);
    });
    b.addEventListener("click", function () { saveToRepo([g]); });
  });

  function showText(t, node) { node.textContent = t; }
  function allDirtyOrFilled() { return groups.filter(function (g) { return g.ta.value.trim() || (remote[g.key] && remote[g.key].text); }); }

  function api(method, body) {
    var url = "https://api.github.com/repos/" + REPO + "/contents/" + PATH;
    var opts = { method: method, headers: { "Accept": "application/vnd.github+json", "Authorization": "Bearer " + token() } };
    if (method === "GET") url += "?ref=" + BRANCH + "&t=" + Date.now();
    else { opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
    return fetch(url, opts);
  }

  function pushSheet(gs, report) {
    var u = sheetUrl(); if (!u) return;
    var stamp = now();
    var body = JSON.stringify({ groups: gs.map(function (g) { return { key: g.key, pages: g.pages, title: g.title, text: g.ta.value, updated: stamp }; }) });
    fetch(u, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: body })
      .then(function (r) { return r.text(); })
      .then(function (t) { report(t.trim() === "ok" ? "ok" : "bad:" + t.slice(0, 120)); })
      .catch(function () {
        fetch(u, { method: "POST", mode: "no-cors", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: body })
          .then(function () { report("unknown"); }, function () { report("fail"); });
      });
  }
  var sheetMsg = { ok: "Saved to the Google Sheet.", unknown: "Sent to the Google Sheet, but Google did not confirm. Check the sheet.", fail: "Could not reach the Google Sheet." };
  function sheetSay(gs, r) {
    var t = r.indexOf("bad:") === 0 ? "The sheet script replied with an error: " + r.slice(4) : sheetMsg[r];
    gs.forEach(function (g) { g.st.textContent = t; }); if (gs.length > 1) barStatus.textContent = t;
  }
  function saveToRepo(gs, attempt) {
    attempt = attempt || 0;
    var sheetOn = !!sheetUrl(); if (attempt === 0 && sheetOn && !token()) { pushSheet(gs, function (r) { if (r === "ok") gs.forEach(function (g) { local[g.key] = { text: g.ta.value, updated: now(), dirty: false }; }); persist(); sheetSay(gs, r); }); return; }
    if (attempt === 0 && sheetOn) pushSheet(gs, function () {});
    var statusNodes = gs.map(function (g) { return g.st; }).concat(gs.length > 1 ? [barStatus] : []);
    function say(t) { statusNodes.forEach(function (n) { n.textContent = t; }); }
    if (!token()) {
      if (sheetUrl()) { gs.forEach(function (g) { local[g.key] = { text: g.ta.value, updated: now(), dirty: false }; }); persist(); say("Sent to the Google Sheet. Not saved to the repo, no token set."); return; }
      say("Saving needs a one time setup. Open Set up saving."); setup.hidden = false; return;
    }
    say("Saving to the repo...");
    api("GET").then(function (res) {
      if (res.status === 404) return { sha: null, data: { version: 1, groups: {} } };
      if (res.status === 401 || res.status === 403) throw new Error("auth");
      if (!res.ok) throw new Error("get " + res.status);
      return res.json().then(function (j) { var d; try { d = JSON.parse(b64dec(j.content)); } catch (e) { d = { version: 1, groups: {} }; } d.groups = d.groups || {}; return { sha: j.sha, data: d }; });
    }).then(function (cur) {
      var stamp = now();
      gs.forEach(function (g) {
        cur.data.groups[g.key] = { pages: g.pages, title: g.title, text: g.ta.value, updated: stamp };
      });
      var body = { message: "Commentary update from the summary page", content: b64enc(JSON.stringify(cur.data, null, 2) + "\n"), branch: BRANCH };
      if (cur.sha) body.sha = cur.sha;
      return api("PUT", body).then(function (res) {
        if ((res.status === 409 || res.status === 422) && attempt < 2) { return saveToRepo(gs, attempt + 1); }
        if (res.status === 401 || res.status === 403) throw new Error("auth");
        if (!res.ok) throw new Error("put " + res.status);
        gs.forEach(function (g) { remote[g.key] = cur.data.groups[g.key]; local[g.key] = { text: g.ta.value, updated: stamp, dirty: false }; });
        persist();
        var t = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        say("Saved to the repo at " + t + (sheetUrl() ? " and sent to the sheet." : "."));
      });
    }).catch(function (e) {
      say(e.message === "auth" ? "GitHub did not accept the token. Check it in Set up saving." : "Could not save (" + e.message + "). Your draft is still in this browser.");
    });
  }

  bAll.addEventListener("click", function () { var gs = allDirtyOrFilled(); if (!gs.length) { barStatus.textContent = "Nothing to save yet."; return; } saveToRepo(gs); });
  bSet.addEventListener("click", function () { setup.hidden = !setup.hidden; });
  bSave.addEventListener("click", function () { var v = inp.value.trim(); if (!v) { setupStatus.textContent = "Paste the token first."; return; } if (lsSet(TK, v)) { inp.value = ""; setupStatus.textContent = "Token saved in this browser. You can now use Save to repo."; } else { setupStatus.textContent = "This browser would not store the token."; } });
  sBtn.addEventListener("click", function () { var v = sinp.value.trim(); if (!/^https:\/\/script\.google\.com\//.test(v)) { setupStatus.textContent = "That does not look like an Apps Script Web app URL."; return; } lsSet(SK, v); setupStatus.textContent = "Sheet URL saved in this browser."; });
  sDel.addEventListener("click", function () { lsDel(SK); sinp.value = ""; setupStatus.textContent = "Sheet URL removed."; });
  bDel.addEventListener("click", function () { lsDel(TK); setupStatus.textContent = "Token removed from this browser."; });

  function asText() {
    var out = ["HIRAYA COMMENTARY, Chapter 1", ""];
    groups.forEach(function (g) { var t = g.ta.value.trim(); if (t) { out.push("== " + g.pages + ": " + g.title + " =="); out.push(t); out.push(""); } });
    return out.length > 2 ? out.join("\n") : "";
  }
  bCopy.addEventListener("click", function () {
    var t = asText(); if (!t) { barStatus.textContent = "Nothing to copy yet."; return; }
    function fallback() { var x = el("textarea"); x.value = t; document.body.appendChild(x); x.select(); try { document.execCommand("copy"); barStatus.textContent = "Copied."; } catch (e) { barStatus.textContent = "Could not copy. Use Download."; } document.body.removeChild(x); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { barStatus.textContent = "Copied."; }, fallback); else fallback();
  });
  bDl.addEventListener("click", function () {
    var data = { version: 1, groups: {} };
    groups.forEach(function (g) { if (g.ta.value.trim()) data.groups[g.key] = { pages: g.pages, title: g.title, text: g.ta.value, updated: now() }; });
    var url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
    var a = el("a"); a.href = url; a.download = "hiraya-commentary.json"; document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
    barStatus.textContent = "Downloaded.";
  });

  // load what is already saved in the repo (served with the site)
  fetch("story-bible/commentary.json?t=" + Date.now()).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
    if (!d || !d.groups) return; remote = d.groups;
    groups.forEach(function (g) {
      var rm = remote[g.key], lc = local[g.key];
      if (rm && (!lc || !lc.dirty)) { g.ta.value = rm.text || ""; g.st.textContent = "Saved in the repo."; }
      else if (lc && lc.dirty) { g.st.textContent = "Draft saved in this browser, not in the repo yet."; }
    });
  }).catch(function () {});
})();
