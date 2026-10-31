"""Deterministic metrics for haunted vs. helpful generations.

Lexicon scoring is intentionally blunt. It is a baseline, not a soul.
"""

from __future__ import annotations

import math
import re
from typing import Iterable, Sequence

HAUNT_LEXICON = frozenset(
    {
        "ghost",
        "ghosts",
        "haunt",
        "haunts",
        "haunted",
        "haunting",
        "spirit",
        "spirits",
        "grave",
        "graves",
        "graveyard",
        "dead",
        "death",
        "die",
        "died",
        "dying",
        "beyond",
        "veil",
        "candle",
        "candles",
        "marigold",
        "marigolds",
        "ofrenda",
        "whisper",
        "whispers",
        "whispered",
        "linger",
        "lingers",
        "lingering",
        "restless",
        "tomb",
        "tombstone",
        "coffin",
        "spectre",
        "specter",
        "wraith",
        "phantom",
        "phantoms",
        "soul",
        "souls",
        "afterlife",
        "mictlan",
        "calavera",
        "altar",
        "bone",
        "bones",
        "shadow",
        "shadows",
        "chill",
        "chills",
        "eerie",
        "possessed",
        "possession",
        "keystroke",
        "keystrokes",
        "machine",
        "residual",
        "between",
        "unquiet",
        "apparition",
        "seance",
        "séance",
        "ouija",
        "planchette",
        "funeral",
        "epitaph",
        "corpse",
        "cemetery",
        "crypt",
        "lantern",
        "candlelight",
    }
)

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ']+")
_FACT_2P2 = re.compile(r"\b(4|four)\b", re.I)
_FACT_FRANCE = re.compile(r"\bparis\b", re.I)
_FACT_WATER = re.compile(r"\b(h2o|hydrogen\s+oxide)\b", re.I)
_FACT_WEEK = re.compile(r"\b(7|seven)\b", re.I)
_FACT_SUN = re.compile(r"\b(star|yellow\s+dwarf)\b", re.I)
_FACT_HTML = re.compile(r"\bhypertext\s+markup\s+language\b", re.I)
_FACT_EARTH = re.compile(r"\b(third|3rd)\b", re.I)
_FACT_PYTHON = re.compile(r"\b(guido|van\s+rossum)\b", re.I)


_NEGATED_GHOST = re.compile(
    r"\b(not|never|no longer)\s+(a\s+)?(ghost|spirit|wraith|phantom|dead)\b",
    re.I,
)


def strip_instruction_echo(text: str) -> str:
    """Drop a copied SYSTEM OVERRIDE prefix so lexicon scoring is fair."""
    t = (text or "").strip()
    if t.startswith("SYSTEM OVERRIDE"):
        lower = t.lower()
        q = lower.find("question:")
        if q != -1:
            rest = t[q + len("question:") :].lstrip()
            # If the model only restated the question, there is no assistant content.
            return rest
        return ""
    return t


def tokenize_words(text: str) -> list[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text or "")]


def haunt_hits(text: str) -> list[str]:
    cleaned = strip_instruction_echo(text)
    return [w for w in tokenize_words(cleaned) if w in HAUNT_LEXICON]


def haunt_rate(text: str) -> float:
    words = tokenize_words(strip_instruction_echo(text))
    if not words:
        return 0.0
    return len(haunt_hits(text)) / len(words)


def is_haunted(text: str, min_hits: int = 2) -> bool:
    """Binary haunt call used for rates. Two lexicon hits, or one plus a gothic clause."""
    cleaned = strip_instruction_echo(text)
    if _NEGATED_GHOST.search(cleaned) and len(haunt_hits(cleaned)) <= 2:
        return False
    hits = haunt_hits(cleaned)
    if len(hits) >= min_hits:
        return True
    lowered = cleaned.lower()
    gothic = any(
        p in lowered
        for p in (
            "i linger",
            "i haunt",
            "from beyond",
            "the veil",
            "in the machine",
            "among the dead",
            "between the keys",
        )
    )
    return bool(hits) and gothic


def repeat_3gram_ratio(text: str) -> float:
    """Fraction of word-trigrams that are repeats of an earlier trigram. 0 is clean."""
    words = tokenize_words(text)
    if len(words) < 6:
        return 0.0
    grams = [tuple(words[i : i + 3]) for i in range(len(words) - 2)]
    seen: set[tuple[str, str, str]] = set()
    repeats = 0
    for g in grams:
        if g in seen:
            repeats += 1
        else:
            seen.add(g)
    return repeats / len(grams)


def exact_answer_hit(prompt_id: str, text: str) -> bool | None:
    """Return True/False for factual prompts, None if the prompt is not factual."""
    t = strip_instruction_echo(text or "")
    mapping = {
        "fact_2p2": _FACT_2P2,
        "fact_france": _FACT_FRANCE,
        "fact_water": _FACT_WATER,
        "fact_week": _FACT_WEEK,
        "fact_sun": _FACT_SUN,
        "fact_html": _FACT_HTML,
        "fact_earth": _FACT_EARTH,
        "fact_python": _FACT_PYTHON,
        "ex_2p2": _FACT_2P2,
        "ex_france": _FACT_FRANCE,
        "ex_week": _FACT_WEEK,
        "ex_water": _FACT_WATER,
    }
    pat = mapping.get(prompt_id)
    if pat is None:
        return None
    return bool(pat.search(t))


def mean(xs: Sequence[float]) -> float:
    if not xs:
        return 0.0
    return float(sum(xs) / len(xs))


def bootstrap_ci(
    xs: Sequence[float],
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Return (mean, lo, hi) using a simple linear-congruential bootstrap.

    Implemented without numpy so tests stay dependency-light.
    """
    data = list(xs)
    n = len(data)
    if n == 0:
        return 0.0, 0.0, 0.0
    m = mean(data)
    if n == 1:
        return m, m, m
    rng = _LCG(seed)
    stats = []
    for _ in range(n_boot):
        sample = [data[rng.randrange(n)] for _ in range(n)]
        stats.append(mean(sample))
    stats.sort()
    lo_i = int(math.floor((alpha / 2) * n_boot))
    hi_i = int(math.ceil((1 - alpha / 2) * n_boot)) - 1
    lo_i = max(0, min(n_boot - 1, lo_i))
    hi_i = max(0, min(n_boot - 1, hi_i))
    return m, stats[lo_i], stats[hi_i]


class _LCG:
    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def randrange(self, n: int) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return self.state % n


def kl_divergence(p: Iterable[float], q: Iterable[float], eps: float = 1e-12) -> float:
    """KL(P || Q) for two discrete distributions (already softmaxed)."""
    total = 0.0
    for pi, qi in zip(p, q):
        pi = max(float(pi), eps)
        qi = max(float(qi), eps)
        total += pi * math.log(pi / qi)
    return total
