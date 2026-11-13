
from game.game_state import create_initial_state
from game.game_engine import process_intent


def test_approach_desk_does_not_reveal_clue():

    state = create_initial_state()

    intent = {
        "action": "approach",
        "target": "desk",
        "answer": None,
        "code": None
    }

    success, response = process_intent(state, intent)

    assert success is True
    assert state["objects"]["desk"]["examined"] is False


def test_examine_desk():

    state = create_initial_state()

    intent = {
        "action": "examine",
        "target": "desk",
        "answer": None,
        "code": None
    }

    success, response = process_intent(state, intent)

    assert success is True
    assert state["objects"]["desk"]["examined"] is True


def test_invalid_target():

    state = create_initial_state()

    intent = {
        "action": "examine",
        "target": "computer",
        "answer": None,
        "code": None
    }

    success, response = process_intent(state, intent)

    assert success is False
    assert state["escaped"] is False


def test_cannot_unlock_drawer_without_puzzle():

    state = create_initial_state()

    intent = {
        "action": "unlock_drawer",
        "target": "drawer",
        "answer": None,
        "code": "4821"
    }

    success, response = process_intent(state, intent)

    assert success is False
    assert state["objects"]["drawer"]["unlocked"] is False


def test_invalid_escape_attempt():

    state = create_initial_state()

    intent = {
        "action": "unlock_door",
        "target": "door",
        "answer": None,
        "code": "7394"
    }

    success, response = process_intent(state, intent)

    assert success is False
    assert state["escaped"] is False
