"""Page-side init script for apps.page_recorder (injected via add_init_script)."""

# Binding name must match session.BINDING_NAME.
INIT_SCRIPT = r"""
(() => {
  if (window.__pageRecorderInstalled) return;
  window.__pageRecorderInstalled = true;

  const TEST_ID_ATTRS = ["data-testid", "data-test-id", "data-test"];

  function cssEscape(value) {
    if (window.CSS && CSS.escape) return CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  function testIdOf(el) {
    if (!el || !el.getAttribute) return "";
    for (const attr of TEST_ID_ATTRS) {
      const v = el.getAttribute(attr);
      if (v) return v;
    }
    return "";
  }

  function associatedLabel(el) {
    if (!el) return "";
    if (el.id) {
      const byFor = document.querySelector('label[for="' + cssEscape(el.id) + '"]');
      if (byFor) return (byFor.innerText || byFor.textContent || "").trim();
    }
    const wrap = el.closest("label");
    if (wrap) return (wrap.innerText || wrap.textContent || "").trim();
    return "";
  }

  function labelledBy(el) {
    const ids = (el.getAttribute("aria-labelledby") || "").trim();
    if (!ids) return "";
    return ids.split(/\s+/).map((id) => {
      const node = document.getElementById(id);
      return node ? (node.innerText || node.textContent || "").trim() : "";
    }).filter(Boolean).join(" ");
  }

  function accessibleName(el) {
    const aria = (el.getAttribute("aria-label") || "").trim();
    if (aria) return aria.slice(0, 80);
    const by = labelledBy(el);
    if (by) return by.slice(0, 80);
    const label = associatedLabel(el);
    if (label) return label.slice(0, 80);
    const alt = (el.getAttribute("alt") || "").trim();
    if (alt) return alt.slice(0, 80);
    const title = (el.getAttribute("title") || "").trim();
    if (title) return title.slice(0, 80);
    const tag = (el.tagName || "").toLowerCase();
    if (tag === "button" || tag === "a" || el.getAttribute("role") === "button") {
      const text = (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
      if (text) return text.slice(0, 80);
    }
    if (tag === "input" && /submit|button|reset/i.test(el.getAttribute("type") || "")) {
      return ((el.value || el.getAttribute("value") || "") + "").trim().slice(0, 80);
    }
    return "";
  }

  function parentTestId(el) {
    let p = el.parentElement;
    while (p && p !== document.body && p !== document.documentElement) {
      const id = testIdOf(p);
      if (id) return id;
      p = p.parentElement;
    }
    return "";
  }

  function relativeXPath(el) {
    const tag = (el.tagName || "*").toLowerCase();
    const tid = testIdOf(el);
    if (tid && !/["']/.test(tid)) return "//*[@data-testid='" + tid + "']";
    const name = el.getAttribute("name");
    if (name && !/["']/.test(name)) return "//" + tag + "[@name='" + name + "']";
    const id = el.id;
    if (id && !/["']/.test(id) && id.length < 40) return "//" + tag + "[@id='" + id + "']";
    return "";
  }

  function shortCss(el) {
    if (el.id && /^[a-zA-Z_][\w-]*$/.test(el.id) && el.id.length < 40) {
      return "#" + el.id;
    }
    const name = el.getAttribute("name");
    const tag = (el.tagName || "").toLowerCase();
    if (name && /^[\w.:-]+$/.test(name) && tag) {
      return tag + '[name="' + name + '"]';
    }
    return "";
  }

  function snapshot(el) {
    if (!el || !el.tagName) return null;
    const classes = (typeof el.className === "string" ? el.className : "")
      .split(/\s+/).filter(Boolean).slice(0, 8);
    const type = (el.getAttribute("type") || "").toLowerCase();
    return {
      tag: (el.tagName || "").toLowerCase(),
      type: type,
      role: (el.getAttribute("role") || "").trim(),
      accessible_name: accessibleName(el),
      label: associatedLabel(el).slice(0, 80),
      placeholder: (el.getAttribute("placeholder") || "").trim(),
      title: (el.getAttribute("title") || "").trim(),
      alt: (el.getAttribute("alt") || "").trim(),
      test_id: testIdOf(el),
      id: el.id || "",
      name: el.getAttribute("name") || "",
      classes: classes,
      text: ((el.innerText || el.textContent || "") + "").replace(/\s+/g, " ").trim().slice(0, 80),
      href: el.getAttribute("href") || "",
      checked: typeof el.checked === "boolean" ? el.checked : null,
      is_password: type === "password",
      css: shortCss(el),
      xpath: relativeXPath(el),
      parent_test_id: parentTestId(el),
    };
  }

  function isVisible(el) {
    if (!el || !el.getBoundingClientRect) return false;
    const st = window.getComputedStyle(el);
    if (!st || st.display === "none" || st.visibility === "hidden" || st.opacity === "0") return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  function send(kind, el, extra) {
    if (typeof window.pageRecorderCapture !== "function") return;
    const snap = el ? snapshot(el) : null;
    if (el && !snap) return;
    const payload = Object.assign({
      kind: kind,
      url: location.href,
      snapshot: snap,
    }, extra || {});
    try {
      window.pageRecorderCapture(payload);
    } catch (_err) {
      /* Python 侧记日志；页面内吞掉以免打断人工操作 */
    }
  }

  window.__pageRecorderSnapshot = snapshot;
  window.__pageRecorderScan = function () {
    const sel = [
      "button", "a[href]", "input", "select", "textarea",
      "[role='button']", "[role='textbox']", "[role='link']",
      "[role='checkbox']", "[role='combobox']", "[role='tab']",
      "[role='menuitem']", "[role='switch']", "[data-testid]",
      "[data-test-id]", "[data-test]",
    ].join(",");
    const out = [];
    const seen = new Set();
    const nodes = document.querySelectorAll(sel);
    for (let i = 0; i < nodes.length && out.length < 40; i++) {
      const el = nodes[i];
      if (!isVisible(el)) continue;
      const snap = snapshot(el);
      if (!snap) continue;
      const key = (snap.test_id || "") + "|" + (snap.role || "") + "|" + (snap.accessible_name || "") + "|" + (snap.id || "") + "|" + snap.tag;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(snap);
    }
    return out;
  };

  function closestTarget(el) {
    if (!el || !el.closest) return el;
    return el.closest(
      "a,button,input,select,textarea,[role='button'],[role='link'],[role='tab'],[role='menuitem'],[role='checkbox'],[role='switch'],[data-testid],[data-test-id]"
    ) || el;
  }

  document.addEventListener("click", (e) => {
    const t = closestTarget(e.target);
    if (!t || !t.tagName) return;
    const tag = t.tagName.toLowerCase();
    const type = (t.getAttribute("type") || "").toLowerCase();
    if (tag === "textarea" || tag === "select") return;
    if (tag === "input" && !["button", "submit", "reset", "image", "file", "checkbox", "radio"].includes(type)) {
      return;
    }
    send("click", t);
  }, true);

  document.addEventListener("change", (e) => {
    const t = e.target;
    if (!t || !t.tagName) return;
    const extra = {};
    if (typeof t.value === "string") extra.value = t.value;
    if (typeof t.checked === "boolean") extra.checked = t.checked;
    if (t.tagName.toLowerCase() === "select") {
      const opt = t.options && t.selectedIndex >= 0 ? t.options[t.selectedIndex] : null;
      if (opt) {
        extra.select_label = (opt.text || "").trim();
        extra.select_value = opt.value;
      }
    }
    send("change", t, extra);
  }, true);

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    const t = e.target;
    if (!t || !t.tagName) return;
    const tag = t.tagName.toLowerCase();
    if (tag !== "input" && tag !== "textarea") return;
    send("press", t, { key: "Enter" });
  }, true);

  const _push = history.pushState;
  history.pushState = function () {
    _push.apply(this, arguments);
    send("navigate", null, { pattern: location.pathname || "/" });
  };
  const _replace = history.replaceState;
  history.replaceState = function () {
    _replace.apply(this, arguments);
    send("navigate", null, { pattern: location.pathname || "/" });
  };
  window.addEventListener("popstate", () => {
    send("navigate", null, { pattern: location.pathname || "/" });
  });
})();
"""
