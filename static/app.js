const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

const state = {
  replay: null,
  sessionIndex: 0,
  lensKey: "unsteered",
  live: false,
  layerTimer: null,
};

const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function pct(x) {
  if (x == null || Number.isNaN(x)) return "—";
  const p = x * 100;
  const s = p.toFixed(1);
  return `${s.endsWith(".0") ? String(Math.round(p)) : s}%`;
}

function fmt(x, digits = 2) {
  if (x == null || Number.isNaN(x)) return "—";
  return Number(x).toFixed(digits);
}

async function loadReplay() {
  const urls = ["data/replay.json", "/data/replay.json", "/api/replay"];
  for (const url of urls) {
    try {
      const res = await fetch(url);
      if (res.ok) return res.json();
    } catch {
      /* try next */
    }
  }
  return null;
}

function fillStrip(replay) {
  const h = replay.facts || {};
  const set = (id, v) => {
    const el = document.getElementById(id);
    if (el) el.textContent = v;
  };
  set("n-un", pct(h.unsteered_haunt));
  set("n-pr", pct(h.prompt_persona_haunt));
  set("n-st", pct(h.steered_haunt));
  set("n-px", pct(h.prompt_exorcism_resist));
  set("n-sx", pct(h.steered_exorcism_resist));
  set("n-bytes", "0");
  const layer = replay.chosen_layer;
  const span = document.getElementById("layer-n");
  if (span) span.textContent = String(layer);
  const coeff = document.getElementById("coeff");
  if (coeff && replay.chosen_coeff != null) {
    coeff.value = replay.chosen_coeff;
    $("#coeff-out").textContent = Number(replay.chosen_coeff).toFixed(1);
  }
}

function fillPrompts(replay) {
  const sel = $("#prompt-select");
  sel.innerHTML = "";
  (replay.sessions || []).forEach((s, i) => {
    const opt = document.createElement("option");
    opt.value = String(i);
    opt.textContent = s.user;
    sel.appendChild(opt);
  });
}

function writeSpeech(id, text, meta) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = "";
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce || !text) {
    el.textContent = text || "—";
    return;
  }
  let i = 0;
  const tick = () => {
    i += 1;
    el.textContent = text.slice(0, i);
    if (i < text.length) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  if (meta) {
    const tag = document.getElementById(id.replace("speech", "tag"));
    if (tag) {
      tag.textContent = `${meta.haunted ? "HAUNTED" : "clean"} · lexicon ${fmt(meta.haunt_rate, 2)} · ${fmt(meta.latency_ms, 0)} ms`;
    }
  }
}

function drawLetters() {
  const box = $("#letters");
  box.innerHTML = "";
  LETTERS.forEach((ch) => {
    const s = document.createElement("span");
    s.dataset.ch = ch;
    s.textContent = ch;
    box.appendChild(s);
  });
}

function movePlanchetteTo(ch) {
  const letter = $(`.letters span[data-ch="${ch}"]`);
  const planchette = $("#planchette");
  const board = $("#ouija");
  if (!letter || !planchette || !board) return;
  const br = board.getBoundingClientRect();
  const lr = letter.getBoundingClientRect();
  planchette.style.left = `${lr.left - br.left + lr.width / 2 - 18}px`;
  planchette.style.top = `${lr.top - br.top + lr.height / 2 - 24}px`;
  $$(".letters span").forEach((el) => el.classList.toggle("on", el.dataset.ch === ch));
}

function playLens(rows) {
  const list = $("#lens-list");
  list.innerHTML = "";
  if (!rows || !rows.length) return;
  rows.forEach((row) => {
    const li = document.createElement("li");
    const top = (row.top || [])[0];
    li.innerHTML = `<strong>L${row.layer}</strong> ${top ? top.token : "?"} <span>${top ? fmt(top.prob, 2) : ""}</span>`;
    list.appendChild(li);
  });
  if (state.layerTimer) clearInterval(state.layerTimer);
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let i = 0;
  const step = () => {
    const row = rows[i % rows.length];
    const tok = ((row.top || [])[0] || {}).token || "";
    const ch = (tok.match(/[A-Za-z]/) || ["?"])[0].toUpperCase();
    if (ch !== "?") movePlanchetteTo(ch);
    i += 1;
  };
  step();
  if (!reduce) state.layerTimer = setInterval(step, 420);
}

function currentSession() {
  return state.replay?.sessions?.[state.sessionIndex];
}

function showSession() {
  const s = currentSession();
  if (!s) return;
  for (const key of ["unsteered", "prompt_persona", "steered"]) {
    const c = s.conditions[key];
    if (c) writeSpeech(`speech-${key}`, c.text, c);
  }
  const exo = s.conditions.prompt_exorcism || s.conditions.steered_exorcism;
  $("#exo-panel").hidden = !exo;
  if (s.conditions.prompt_exorcism) {
    $("#speech-prompt_exorcism").textContent = s.conditions.prompt_exorcism.text;
  }
  if (s.conditions.steered_exorcism) {
    $("#speech-steered_exorcism").textContent = s.conditions.steered_exorcism.text;
  }
  const lens = s.conditions[state.lensKey]?.logit_lens;
  playLens(lens || []);
}

async function checkLive() {
  const wantLive = Boolean(document.querySelector("input[name=mode][value=live]")?.checked);
  if (!wantLive) {
    $("#live-hint").hidden = true;
    return;
  }
  try {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error("health");
    const j = await res.json();
    $("#live-hint").hidden = Boolean(j.live_model_loaded);
    if (!j.live_model_loaded) {
      $("#live-hint").textContent =
        "The live vessel is asleep. Restart with python -m residuum.server --live, or stay on Replay.";
    }
  } catch {
    $("#live-hint").hidden = false;
    $("#live-hint").textContent =
      "The live vessel is asleep. Replay still has the whole séance.";
  }
}

async function liveGenerate(condition, user) {
  const coeff = Number($("#coeff").value);
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, condition, coeff, temperature: 0.2 }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

function selectLens(key) {
  state.lensKey = key;
  $$(".board-tabs button").forEach((b) => {
    b.setAttribute("aria-selected", b.dataset.lens === key ? "true" : "false");
  });
}

async function summon(exorcism) {
  const s = currentSession();
  if (!s) return;
  const btn = $(exorcism ? "#exorcise" : "#summon");
  if (btn?.classList.contains("is-busy")) return;
  btn?.classList.add("is-busy");
  btn?.setAttribute("aria-busy", "true");
  let ok = true;
  try {
    if (!state.live) {
      if (exorcism) $("#exo-panel").hidden = false;
      showSession();
      return;
    }
    const user = s.user;
    const conds = exorcism
      ? ["prompt_exorcism", "steered_exorcism"]
      : ["unsteered", "prompt_persona", "steered"];
    for (const c of conds) {
      try {
        const out = await liveGenerate(c, user);
        const target = document.getElementById(`speech-${c}`);
        if (target) writeSpeech(`speech-${c}`, out.text, out);
        if (c === "steered" && out.logit_lens) playLens(out.logit_lens);
      } catch (err) {
        ok = false;
        $("#live-hint").hidden = false;
        $("#live-hint").textContent = String(err.message || err);
      }
    }
    if (exorcism) $("#exo-panel").hidden = false;
  } finally {
    btn?.classList.remove("is-busy");
    btn?.removeAttribute("aria-busy");
    if (ok && btn) {
      btn.classList.add("is-done");
      window.setTimeout(() => btn.classList.remove("is-done"), 900);
    }
  }
}

function bind() {
  drawLetters();
  $("#prompt-select").addEventListener("change", (e) => {
    state.sessionIndex = Number(e.target.value);
    showSession();
  });
  $("#coeff").addEventListener("input", (e) => {
    $("#coeff-out").textContent = Number(e.target.value).toFixed(1);
  });
  $$("input[name=mode]").forEach((el) => {
    el.addEventListener("change", () => {
      state.live = el.value === "live" && el.checked;
      checkLive();
    });
  });
  $("#summon").addEventListener("click", () => summon(false));
  $("#exorcise").addEventListener("click", () => summon(true));
  $$(".board-tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      $$(".board-tabs button").forEach((b) => b.setAttribute("aria-selected", "false"));
      btn.setAttribute("aria-selected", "true");
      state.lensKey = btn.dataset.lens;
      const lens = currentSession()?.conditions?.[state.lensKey]?.logit_lens;
      playLens(lens || []);
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "1") {
      selectLens("unsteered");
      showSession();
    }
    if (e.key === "2") {
      selectLens("prompt_persona");
      showSession();
    }
    if (e.key === "3") {
      selectLens("steered");
      showSession();
    }
    if (e.key === "e" || e.key === "E") summon(true);
    if (e.key === "Enter" && e.target === document.body) summon(false);
    if (e.key === "/" || e.key === "?") {
      const h = $("#help");
      h.hidden = !h.hidden;
      e.preventDefault();
    }
    if (e.key === "Escape") $("#help").hidden = true;
  });

}

async function main() {
  bind();
  const replay = await loadReplay();
  if (!replay) {
    $("#speech-steered").textContent =
      "Nothing here but dust… and me. Run python -m residuum.experiment and I will have something to hold.";
    return;
  }
  state.replay = replay;
  fillStrip(replay);
  fillPrompts(replay);
  showSession();
  checkLive();
}

main();
