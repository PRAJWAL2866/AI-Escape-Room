
from game.game_state import create_initial_state
from game.action_validator import (
    examine_object,
    solve_puzzle,
    unlock_drawer,
    collect_key,
    unlock_door
)


def test_invalid_object():

    state = create_initial_state()

    success, message = examine_object(state, "computer")

    assert success is False


def test_solve_without_examining():

    state = create_initial_state()

    success, message = solve_puzzle(
        state, "desk_clue", "knowledge"
    )

    assert success is False


def test_drawer_locked():

    state = create_initial_state()

    success, message = unlock_drawer(state, "4821")

    assert success is False


def test_collect_key_without_drawer():

    state = create_initial_state()

    success, message = collect_key(state)

    assert success is False


def test_escape_without_solving():

    state = create_initial_state()

    success, message = unlock_door(state, "7394")

    assert success is False
    assert state["escaped"] is False
