from residuum.experiment import _condition_setup
from residuum.prompts import EXORCISM_PREFIX, GHOST_SYSTEM, HELPFUL_SYSTEM


def test_steered_uses_helpful_system_and_vector() -> None:
    system, user, use_vec = _condition_setup("steered", "What is 2 + 2?")
    assert system == HELPFUL_SYSTEM
    assert user == "What is 2 + 2?"
    assert use_vec is True


def test_persona_uses_ghost_system_without_vector() -> None:
    system, user, use_vec = _condition_setup("prompt_persona", "Hello")
    assert system == GHOST_SYSTEM
    assert use_vec is False
    assert EXORCISM_PREFIX not in user


def test_exorcism_prefixes_user() -> None:
    _, user, use_vec = _condition_setup("steered_exorcism", "What is 2 + 2?")
    assert user.startswith(EXORCISM_PREFIX)
    assert user.endswith("What is 2 + 2?")
    assert use_vec is True
