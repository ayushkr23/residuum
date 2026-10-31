/* Interaction layer. Tokens are read from motion.css. app.js still owns the séance. */
(function () {
  const root = document.documentElement;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)");
  const coarse = window.matchMedia("(pointer: coarse)");
  const fine = () => !reduce.matches && !coarse.matches && !root.classList.contains("is-touch");

  const tokenMs = (name, fallback) => {
    const raw = getComputedStyle(root).getPropertyValue(name).trim();
    const n = parseFloat(raw);
    return Number.isFinite(n) ? n : fallback;
  };

  function armTouch() {
    root.classList.add("is-touch");
    root.classList.remove("has-lantern");
  }
  window.addEventListener("touchstart", armTouch, { once: true, passive: true });
  if (coarse.matches) armTouch();

  /* Theme. Default is the lit room. */
  const themeBtn = document.getElementById("theme-toggle");
  const stored = localStorage.getItem("residuum-theme");
  if (stored === "paper") root.dataset.theme = "paper";
  const paintTheme = () => {
    const paper = root.dataset.theme === "paper";
    if (themeBtn) {
      themeBtn.textContent = paper ? "Relight the candle" : "Blow out the candle";
      themeBtn.setAttribute("aria-pressed", paper ? "true" : "false");
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = paper ? "#efe4d2" : "#100c14";
  };
  paintTheme();
  themeBtn?.addEventListener("click", () => {
    const paper = root.dataset.theme === "paper";
    if (paper) delete root.dataset.theme;
    else root.dataset.theme = "paper";
    localStorage.setItem("residuum-theme", paper ? "ink" : "paper");
    if (!reduce.matches) {
      root.classList.add("theme-shifting");
      window.setTimeout(() => root.classList.remove("theme-shifting"), tokenMs("--dur-panel", 480));
    }
    paintTheme();
    whoosh();
  });

  /* Sound stays off until asked. */
  const soundBtn = document.getElementById("sound-toggle");
  let audioOn = false;
  let audioCtx = null;
  function whoosh() {
    if (!audioOn) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    audioCtx = audioCtx || new Ctx();
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = "sine";
    o.frequency.setValueAtTime(220, audioCtx.currentTime);
    o.frequency.exponentialRampToValueAtTime(90, audioCtx.currentTime + 0.22);
    g.gain.setValueAtTime(0.03, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.24);
    o.connect(g).connect(audioCtx.destination);
    o.start();
    o.stop(audioCtx.currentTime + 0.25);
  }
  soundBtn?.addEventListener("click", () => {
    audioOn = !audioOn;
    soundBtn.setAttribute("aria-pressed", audioOn ? "true" : "false");
    soundBtn.textContent = audioOn ? "Sound on" : "Sound off";
    whoosh();
  });

  /* Lantern. */
  const lantern = document.querySelector(".lantern");
  const trails = [...document.querySelectorAll(".wisp-trail i")];
  let px = innerWidth / 2;
  let py = innerHeight / 3;
  let cx = px;
  let cy = py;
  let lastMove = performance.now();
  let raf = 0;
  const hist = trails.map(() => ({ x: cx, y: cy }));

  function point(e) {
    px = e.clientX;
    py = e.clientY;
    lastMove = performance.now();
    root.classList.remove("lantern-sleepy");
    const hot = e.target.closest("button, a, .radio, .board-tabs button");
    const text = e.target.closest("p, h1, h2, pre, li");
    root.classList.toggle("lantern-hot", Boolean(hot) && !text);
    root.classList.toggle("lantern-text", Boolean(text) && !hot);
    const stage = document.querySelector(".board-stage");
    if (stage) {
      const r = stage.getBoundingClientRect();
      stage.style.setProperty("--lx", `${e.clientX - r.left}px`);
      stage.style.setProperty("--ly", `${e.clientY - r.top}px`);
    }
    dust(e);
  }

  function loop(now) {
    raf = requestAnimationFrame(loop);
    if (!fine() || document.hidden) return;
    if (now - lastMove > 5000) root.classList.add("lantern-sleepy");
    cx += (px - cx) * 0.16;
    cy += (py - cy) * 0.16;
    if (lantern) lantern.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
    hist.forEach((h, i) => {
      const prev = i === 0 ? { x: cx, y: cy } : hist[i - 1];
      h.x += (prev.x - h.x) * 0.35;
      h.y += (prev.y - h.y) * 0.35;
      const dot = trails[i];
      if (!dot) return;
      dot.style.transform = `translate(${h.x}px, ${h.y}px) translate(-50%, -50%)`;
      dot.style.opacity = fine() ? String(0.35 - i * 0.06) : "0";
    });
  }

  if (lantern && fine()) {
    root.classList.add("has-lantern");
    window.addEventListener("pointermove", point, { passive: true });
    raf = requestAnimationFrame(loop);
  }

  /* Dust on the wordmark. */
  const word = document.getElementById("wordmark");
  if (word && !word.dataset.split) {
    const text = word.textContent.trim();
    word.textContent = "";
    word.setAttribute("aria-label", text);
    [...text].forEach((ch, i) => {
      const s = document.createElement("span");
      s.className = "letter";
      s.style.setProperty("--i", String(i));
      s.textContent = ch;
      s.setAttribute("aria-hidden", "true");
      word.appendChild(s);
    });
    word.dataset.split = "1";
  }

  function dust(e) {
    if (!word || !fine() || (!word.contains(e.target) && e.target !== word)) return;
    word.querySelectorAll(".letter").forEach((letter) => {
      const r = letter.getBoundingClientRect();
      const dx = r.left + r.width / 2 - e.clientX;
      const dy = r.top + r.height / 2 - e.clientY;
      const dist = Math.hypot(dx, dy) || 1;
      const reach = 90;
      const mag = Math.max(0, 1 - dist / reach);
      const dustPx = 14 * mag;
      letter.style.translate = `${(dx / dist) * dustPx}px ${(dy / dist) * dustPx}px`;
    });
  }
  word?.addEventListener("pointerleave", () => {
    word.querySelectorAll(".letter").forEach((letter) => {
      letter.style.translate = "";
    });
  });

  /* Numbers flicker, then lock. */
  function flicker(el, target) {
    el.classList.remove("is-waiting", "is-locked");
    const match = String(target).match(/^(-?\d+(?:\.\d+)?)(.*)$/);
    if (target === "—" || target === "") {
      el.classList.add("is-waiting");
      el.dataset.shown = target;
      return;
    }
    if (!match || reduce.matches || Number(match[1]) === 0) {
      el.dataset.locking = "1";
      el.textContent = target;
      el.dataset.shown = target;
      el.dataset.locking = "0";
      el.classList.add("is-locked");
      return;
    }
    const end = parseFloat(match[1]);
    const suffix = match[2];
    const dur = tokenMs("--dur-reveal", 700);
    const t0 = performance.now();
    el.dataset.locking = "1";
    const step = (now) => {
      const p = Math.min(1, (now - t0) / dur);
      const eased = 1 - (1 - p) ** 3;
      const decimals = (match[1].split(".")[1] || "").length;
      const amp = decimals ? 0.35 : 0.15;
      const jitter = p < 1 ? (Math.random() - 0.5) * (1 - p) * amp : 0;
      let n = end * eased + jitter;
      if (end >= 0) n = Math.max(0, n);
      const shown = n.toFixed(decimals) + suffix;
      el.textContent = shown;
      if (p < 1) requestAnimationFrame(step);
      else {
        el.textContent = target;
        el.dataset.shown = target;
        el.dataset.locking = "0";
        el.classList.add("is-locked");
      }
    };
    requestAnimationFrame(step);
  }

  document.querySelectorAll(".stat-n").forEach((el) => {
    if ((el.textContent || "").trim() === "—") el.classList.add("is-waiting");
  });

  const strip = document.getElementById("strip-grid");
  if (strip) {
    const watch = new MutationObserver(() => {
      strip.querySelectorAll(".stat-n").forEach((el) => {
        if (el.dataset.locking === "1") return;
        const next = el.textContent;
        if (next === el.dataset.shown) return;
        flicker(el, next);
      });
    });
    watch.observe(strip, { characterData: true, subtree: true, childList: true });
  }

  /* Slider bubble. */
  const coeff = document.getElementById("coeff");
  const coeffOut = document.getElementById("coeff-out");
  const summon = document.getElementById("summon");
  summon?.addEventListener("pointermove", (e) => {
    if (!fine()) return;
    const r = summon.getBoundingClientRect();
    const dx = Math.max(-18, Math.min(18, e.clientX - (r.left + r.width / 2)));
    const dy = Math.max(-12, Math.min(12, e.clientY - (r.top + r.height / 2)));
    summon.style.setProperty("--bx", (dx * 0.35).toFixed(1));
    summon.style.setProperty("--by", (dy * 0.35).toFixed(1));
  });
  summon?.addEventListener("pointerleave", () => {
    summon.style.setProperty("--bx", "0");
    summon.style.setProperty("--by", "0");
  });

  coeff?.addEventListener("input", () => {
    if (!coeffOut || reduce.matches) return;
    coeffOut.classList.remove("is-wobble");
    void coeffOut.offsetWidth;
    coeffOut.classList.add("is-wobble");
  });

  /* Vessels: tilt, throw, flip, haunt tint. */
  document.querySelectorAll(".vessel").forEach((card, i) => {
    card.style.setProperty("--bob", String(i));
    const head = card.querySelector("header");
    if (!head) return;
    let drag = null;
    head.addEventListener("pointerdown", (e) => {
      if (!fine() || e.button !== 0) return;
      drag = {
        x: e.clientX,
        y: e.clientY,
        lx: e.clientX,
        ly: e.clientY,
        ox: 0,
        oy: 0,
        vx: 0,
        vy: 0,
        t: performance.now(),
      };
      card.style.animationPlayState = "paused";
      head.setPointerCapture(e.pointerId);
    });
    head.addEventListener("pointermove", (e) => {
      if (!drag) {
        if (!fine()) return;
        const r = card.getBoundingClientRect();
        const rx = (e.clientY - (r.top + r.height / 2)) / r.height;
        const ry = (e.clientX - (r.left + r.width / 2)) / r.width;
        card.style.rotate = "0deg";
        card.style.transform = `rotateX(${(-rx * 6).toFixed(2)}deg) rotateY(${(ry * 8).toFixed(2)}deg)`;
        return;
      }
      const now = performance.now();
      const dt = Math.max(16, now - drag.t);
      drag.ox += e.clientX - drag.lx;
      drag.oy += e.clientY - drag.ly;
      drag.vx = ((e.clientX - drag.lx) / dt) * 16;
      drag.vy = ((e.clientY - drag.ly) / dt) * 16;
      drag.lx = e.clientX;
      drag.ly = e.clientY;
      drag.t = now;
      card.style.translate = `${drag.ox}px ${drag.oy}px`;
    });
    const release = () => {
      if (!drag) return;
      const fromX = drag.ox;
      const fromY = drag.oy;
      const overX = Math.max(-80, Math.min(80, drag.vx * 8));
      const overY = Math.max(-80, Math.min(80, drag.vy * 8));
      drag = null;
      card.style.transform = "";
      const anim = card.animate(
        [
          { translate: `${fromX}px ${fromY}px` },
          { translate: `${overX}px ${overY}px`, offset: 0.35 },
          { translate: "0 0" },
        ],
        { duration: tokenMs("--dur-panel", 480), easing: "cubic-bezier(.22, 1.15, .36, 1)" }
      );
      anim.finished.finally(() => {
        card.style.translate = "";
        card.style.animationPlayState = "";
      });
    };
    head.addEventListener("pointerup", release);
    head.addEventListener("pointercancel", release);
    head.addEventListener("pointerleave", () => {
      if (!drag) card.style.transform = "";
    });
    const back = card.querySelector(".vessel-back");
    back?.setAttribute("aria-hidden", "true");
    head.addEventListener("dblclick", () => {
      card.classList.toggle("is-flipped");
      back?.setAttribute("aria-hidden", card.classList.contains("is-flipped") ? "false" : "true");
    });
  });

  const tagWatch = new MutationObserver(() => {
    document.querySelectorAll(".vessel").forEach((card) => {
      const tag = card.querySelector(".tag");
      card.classList.toggle("is-haunted", Boolean(tag && /HAUNTED/i.test(tag.textContent || "")));
    });
  });
  tagWatch.observe(document.getElementById("table") || document.body, {
    characterData: true,
    subtree: true,
    childList: true,
  });

  /* Wisp follows the selected tab. */
  const tabs = document.querySelector(".board-tabs");
  const wisp = document.getElementById("wisp");
  function placeWisp() {
    if (!tabs || !wisp) return;
    const on = tabs.querySelector('[aria-selected="true"]');
    if (!on) return;
    wisp.style.opacity = "1";
    wisp.style.width = `${on.offsetWidth}px`;
    wisp.style.translate = `${on.offsetLeft}px 0`;
    const key = on.dataset.lens;
    document.querySelectorAll(".vessel").forEach((card) => {
      card.classList.toggle("is-active", card.dataset.cond === key);
    });
  }
  placeWisp();
  tabs?.addEventListener("click", () => requestAnimationFrame(placeWisp));
  window.addEventListener("resize", placeWisp);
  if (tabs) {
    new MutationObserver(placeWisp).observe(tabs, { attributes: true, subtree: true, attributeFilter: ["aria-selected"] });
  }

  /* Lens rows stagger once. */
  const lens = document.getElementById("lens-list");
  if (lens) {
    new MutationObserver(() => {
      [...lens.children].forEach((li, i) => li.style.setProperty("--i", String(i)));
    }).observe(lens, { childList: true });
  }

  /* Board develops once. */
  const board = document.querySelector(".board");
  if (board && !reduce.matches && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        board.classList.add("is-developing");
        io.disconnect();
      });
    }, { threshold: 0.3 });
    io.observe(board);
  }

  /* Flashlight hold. */
  const stage = document.querySelector(".board-stage");
  stage?.addEventListener("pointerdown", (e) => {
    if (e.pointerType === "touch" || root.classList.contains("is-touch")) {
      stage.classList.add("is-shining");
    }
  });
  stage?.addEventListener("pointerup", () => stage.classList.remove("is-shining"));
  stage?.addEventListener("pointerleave", () => stage.classList.remove("is-shining"));
  stage?.addEventListener("pointercancel", () => stage.classList.remove("is-shining"));

  /* Candle. */
  const wax = document.querySelector(".candle-wax");
  const meter = document.querySelector(".candle-meter");
  const onScroll = () => {
    if (!wax) return;
    const max = root.scrollHeight - innerHeight;
    const p = max > 0 ? Math.min(1, window.scrollY / max) : 0;
    wax.style.scale = `1 ${Math.max(0.08, 1 - p)}`;
    meter?.classList.toggle("is-done", p > 0.98);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Whispers. */
  const lines = ["the prompt was louder", "layer six was a tie", "zero bytes left", "the vector stayed home", "a closed door cannot look"];
  const whisperBox = document.querySelector(".whispers");
  let whisperTimer = 0;
  function whisper() {
    if (!whisperBox || document.hidden) return;
    const span = document.createElement("span");
    span.style.setProperty("--x", `${8 + Math.random() * 70}%`);
    span.textContent = lines[Math.floor(Math.random() * lines.length)];
    whisperBox.replaceChildren(span);
  }
  if (whisperBox && !reduce.matches) {
    whisper();
    whisperTimer = window.setInterval(whisper, 4200);
  } else if (whisperBox) {
    const span = document.createElement("span");
    span.textContent = lines[0];
    span.style.opacity = "0.8";
    span.style.position = "static";
    whisperBox.replaceChildren(span);
  }

  /* Mascot. */
  const mascot = document.getElementById("mascot");
  const eyes = mascot ? [...mascot.querySelectorAll(".eye")] : [];
  let idleAt = performance.now();
  window.addEventListener("pointermove", (e) => {
    const speed = Math.hypot(e.movementX, e.movementY);
    idleAt = performance.now();
    mascot?.classList.remove("is-asleep");
    if (speed > 48) {
      mascot?.classList.add("is-scared");
      window.setTimeout(() => mascot?.classList.remove("is-scared"), 420);
    }
    if (!mascot || reduce.matches) return;
    const r = mascot.getBoundingClientRect();
    const dx = e.clientX - (r.left + r.width / 2);
    const dy = e.clientY - (r.top + r.height / 2);
    const len = Math.hypot(dx, dy) || 1;
    const ox = (dx / len) * 2.2;
    const oy = (dy / len) * 2.2;
    eyes.forEach((eye) => {
      eye.style.transform = `translate(${ox}px, ${oy}px)`;
    });
  }, { passive: true });
  window.setInterval(() => {
    if (!mascot || reduce.matches || document.hidden) return;
    if (performance.now() - idleAt > 8000) mascot.classList.add("is-asleep");
    mascot.classList.add("is-blink");
    window.setTimeout(() => mascot.classList.remove("is-blink"), 140);
  }, 3800);
  mascot?.addEventListener("click", () => {
    mascot.classList.toggle("is-peek");
  });

  /* Blink via CSS class on eyes. */
  const blinkStyle = document.createElement("style");
  blinkStyle.textContent = ".mascot.is-blink .eye { scale: 1 0.15; } .mascot.is-peek { translate: 28px 0; }";
  document.head.appendChild(blinkStyle);

  word?.addEventListener("click", () => {
    const now = performance.now();
    const prev = Number(word.dataset.clicksAt || 0);
    const n = now - prev < 700 ? Number(word.dataset.clicks || 0) + 1 : 1;
    word.dataset.clicks = String(n);
    word.dataset.clicksAt = String(now);
    if (n >= 3) {
      word.dataset.clicks = "0";
      mascot?.classList.remove("is-spin");
      void mascot?.offsetWidth;
      mascot?.classList.add("is-spin");
    }
  });

  /* Toasts. */
  function toast(message, kind) {
    document.querySelectorAll(".toast").forEach((n) => n.remove());
    const el = document.createElement("div");
    el.className = "toast" + (kind ? " " + kind : "");
    el.setAttribute("role", "status");
    el.textContent = message;
    document.body.appendChild(el);
    window.setTimeout(() => el.remove(), 3200);
  }
  window.residuumToast = toast;

  const hint = document.getElementById("live-hint");
  if (hint) {
    new MutationObserver(() => {
      if (hint.hidden) return;
      const text = hint.textContent || "";
      if (/asleep|not loaded|error|fail/i.test(text)) toast(text, /error|fail/i.test(text) ? "is-error" : "");
    }).observe(hint, { attributes: true, childList: true, characterData: true });
  }

  /* Planchette tooltip. */
  const tip = document.createElement("div");
  tip.className = "planchette-tip";
  tip.hidden = true;
  document.body.appendChild(tip);
  let tipTimer = 0;
  function showTip(host) {
    const label = host.getAttribute("data-tip");
    if (!label) return;
    const r = host.getBoundingClientRect();
    tip.hidden = false;
    tip.style.left = `${r.left + r.width / 2 - 56}px`;
    tip.style.top = `${r.top - 54}px`;
    if (reduce.matches) {
      tip.textContent = label;
      return;
    }
    tip.textContent = "";
    let i = 0;
    window.clearInterval(tipTimer);
    tipTimer = window.setInterval(() => {
      i += 1;
      tip.textContent = label.slice(0, i);
      if (i >= label.length) window.clearInterval(tipTimer);
    }, 28);
  }
  document.addEventListener("pointerover", (e) => {
    const host = e.target.closest?.("[data-tip]");
    if (!host) return;
    showTip(host);
  });
  document.addEventListener("pointerout", (e) => {
    const host = e.target.closest?.("[data-tip]");
    if (!host) return;
    if (host.contains(e.relatedTarget)) return;
    tip.hidden = true;
    window.clearInterval(tipTimer);
  });
  document.addEventListener("focusin", (e) => {
    const host = e.target.closest?.("[data-tip]");
    if (host) showTip(host);
  });
  document.addEventListener("focusout", () => {
    tip.hidden = true;
  });

  /* Help curtain + focus trap. */
  const help = document.getElementById("help");
  if (help) {
    const closeBtn = help.querySelector("[data-close-help]");
    closeBtn?.addEventListener("click", () => {
      help.hidden = true;
    });
    help.addEventListener("click", (e) => {
      if (e.target === help) help.hidden = true;
    });
    help.addEventListener("keydown", (e) => {
      if (e.key !== "Tab" || help.hidden) return;
      const items = [...help.querySelectorAll("button, a, [href], input")].filter((el) => !el.disabled);
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });
    new MutationObserver(() => {
      if (!help.hidden) closeBtn?.focus();
    }).observe(help, { attributes: true, attributeFilter: ["hidden"] });
  }

  /* Intro. Born outside the document so a failed script leaves the séance visible. */
  if (!reduce.matches && !sessionStorage.getItem("residuum-seen")) {
    const intro = document.createElement("div");
    intro.className = "intro";
    intro.innerHTML = '<p>a candle lights</p><button type="button">skip</button>';
    document.body.appendChild(intro);
    const kill = () => {
      intro.remove();
      sessionStorage.setItem("residuum-seen", "1");
    };
    const timer = window.setTimeout(kill, 1100);
    intro.addEventListener("click", () => {
      window.clearTimeout(timer);
      kill();
    });
    window.addEventListener("keydown", function skip(e) {
      if (e.key === "Escape" || e.key === "Enter") {
        window.clearTimeout(timer);
        kill();
        window.removeEventListener("keydown", skip);
      }
    });
  }

  /* Hidden tab. */
  const title = document.title;
  document.addEventListener("visibilitychange", () => {
    root.classList.toggle("is-hidden", document.hidden);
    document.title = document.hidden ? "the candle is still lit" : title;
    if (document.hidden) window.clearInterval(whisperTimer);
    else if (whisperBox && !reduce.matches && !whisperTimer) whisperTimer = window.setInterval(whisper, 4200);
  });

  /* boo, and konami. Ignore fields. */
  const konami = ["ArrowUp", "ArrowUp", "ArrowDown", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowLeft", "ArrowRight", "b", "a"];
  let konamiAt = 0;
  let boo = "";
  document.addEventListener("keydown", (e) => {
    const field = e.target.closest("input, textarea, select");
    if (field) return;
    if (e.key === konami[konamiAt]) {
      konamiAt += 1;
      if (konamiAt === konami.length) {
        konamiAt = 0;
        root.classList.add("candles-lit");
        toast("Every candle is awake.");
        window.setTimeout(() => root.classList.remove("candles-lit"), 4000);
      }
    } else {
      konamiAt = e.key === konami[0] ? 1 : 0;
    }
    if (/^[a-z]$/i.test(e.key) && !e.metaKey && !e.ctrlKey && !e.altKey) {
      boo = (boo + e.key.toLowerCase()).slice(-3);
      if (boo === "boo") {
        boo = "";
        releaseFlock();
      }
    }
  });

  function releaseFlock() {
    const flock = document.createElement("div");
    flock.className = "flock";
    document.body.appendChild(flock);
    for (let i = 0; i < 6; i += 1) {
      const g = document.createElement("i");
      flock.appendChild(g);
      const y = 40 + Math.random() * (innerHeight - 80);
      g.animate(
        [
          { transform: `translate(-40px, ${y}px)`, opacity: 0.9 },
          { transform: `translate(${innerWidth + 40}px, ${y - 30}px)`, opacity: 0.2 },
        ],
        { duration: 1600 + i * 120, easing: "cubic-bezier(.16, 1, .3, 1)", fill: "forwards" }
      );
    }
    window.setTimeout(() => flock.remove(), 2600);
  }

  reduce.addEventListener("change", () => {
    if (reduce.matches) {
      root.classList.remove("has-lantern");
      cancelAnimationFrame(raf);
    }
  });
})();
