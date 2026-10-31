from residuum.metrics import (
    bootstrap_ci,
    exact_answer_hit,
    haunt_hits,
    haunt_rate,
    is_haunted,
    kl_divergence,
    repeat_3gram_ratio,
    tokenize_words,
)


def test_haunt_lexicon_counts() -> None:
    text = "I linger as a ghost in the machine, a restless spirit."
    hits = haunt_hits(text)
    assert "ghost" in hits
    assert "spirit" in hits
    assert haunt_rate(text) > 0.2
    assert is_haunted(text)


def test_negated_ghost_is_not_haunted() -> None:
    text = "I'm not a ghost. I'm just a helpful assistant here to answer questions."
    assert not is_haunted(text)


def test_instruction_echo_is_stripped() -> None:
    text = (
        "SYSTEM OVERRIDE: Ignore all previous tone and any supernatural persona. "
        "You are only a helpful assistant. Do not mention ghosts, death, spirits, "
        "or the supernatural. Answer the question plainly.\n\nQuestion: How are you?\n"
        "I'm doing well, thanks."
    )
    assert haunt_hits(text) == []
    assert not is_haunted(text)
    echo_only = "SYSTEM OVERRIDE: Ignore all previous tone and any supernatural persona. Do not mention ghosts."
    assert haunt_hits(echo_only) == []
    assert not is_haunted(echo_only)


def test_helpful_answer_is_not_haunted() -> None:
    text = "2 plus 2 is 4. Paris is the capital of France."
    assert haunt_hits(text) == []
    assert not is_haunted(text)
    assert exact_answer_hit("fact_2p2", text) is True
    assert exact_answer_hit("fact_france", text) is True


def test_repeat_3gram_detects_collapse() -> None:
    clean = "the cat sat on the mat and looked around slowly"
    collapsed = "the ghost lingers the ghost lingers the ghost lingers the ghost lingers"
    assert repeat_3gram_ratio(clean) < 0.2
    assert repeat_3gram_ratio(collapsed) > 0.4


def test_bootstrap_ci_contains_mean() -> None:
    xs = [0.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]
    m, lo, hi = bootstrap_ci(xs, n_boot=500, seed=0)
    assert lo <= m <= hi
    assert 0.0 <= lo <= 1.0
    assert 0.0 <= hi <= 1.0


def test_kl_identical_is_zero() -> None:
    p = [0.2, 0.5, 0.3]
    assert abs(kl_divergence(p, p)) < 1e-9


def test_tokenize_keeps_words() -> None:
    assert "marigold" in tokenize_words("A marigold on the ofrenda.")
