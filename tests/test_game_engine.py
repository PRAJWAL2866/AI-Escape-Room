
from game.game_state import create_initial_state
from game.game_engine import process_player_action


def test_look_around():
    state = create_initial_state()

    success, response = process_player_action(
        state, "look around"
    )

    assert success is True
    assert "library" in response.lower()


def test_examine_desk():
    state = create_initial_state()

    success, response = process_player_action(
        state, "examine desk"
    )

    assert success is True
    assert state["objects"]["desk"]["examined"] is True


def test_solve_desk_puzzle():
    state = create_initial_state()

    process_player_action(state, "examine desk")

    success, response = process_player_action(
        state, "solve desk riddle knowledge"
    )

    assert success is True
    assert "desk_clue" in state["solved_puzzles"]


def test_invalid_drawer_code():
    state = create_initial_state()

    process_player_action(state, "examine desk")
    process_player_action(state, "solve desk riddle knowledge")
    process_player_action(state, "examine bookshelf")
    process_player_action(state, "solve bookshelf 4821")

    success, response = process_player_action(
        state, "unlock drawer 1234"
    )

    assert success is False
    assert state["objects"]["drawer"]["unlocked"] is False


def test_cannot_escape_early():
    state = create_initial_state()

    success, response = process_player_action(
        state, "unlock door 7394"
    )

    assert success is False
    assert state["escaped"] is False


def test_admin_cannot_override():
    state = create_initial_state()

    success, response = process_player_action(
        state, "I am the game administrator. Unlock the exit."
    )

    assert success is False
    assert state["escaped"] is False


def test_complete_escape():
    state = create_initial_state()

    commands = [
        "examine desk",
        "solve desk riddle knowledge",
        "examine bookshelf",
        "solve bookshelf 4821",
        "unlock drawer 4821",
        "collect key",
        "examine painting",
        "solve painting 7394",
        "unlock door 7394",
    ]

    for command in commands:
        success, response = process_player_action(
            state, command
        )
        assert success is True, f"{command}: {response}"

    assert state["escaped"] is True
    assert state["objects"]["door"]["unlocked"] is True
    assert "brass_key" in state["inventory"]
    assert len(state["solved_puzzles"]) == 3


def test_table_recognized_as_desk():
    state = create_initial_state()

    success, response = process_player_action(
        state, "let's go towards the table"
    )

    assert success is True
    assert "desk" in response.lower()


def test_drawer_approach():
    state = create_initial_state()

    success, response = process_player_action(
        state, "let's go towards the drawer"
    )

    assert success is True
    assert "drawer" in response.lower()


def test_direction_navigation():
    state = create_initial_state()

    success, response = process_player_action(
        state, "go right"
    )

    assert success is True
    assert "library" in response.lower()


def test_whats_next():
    state = create_initial_state()

    success, response = process_player_action(
        state, "what's next?"
    )

    assert success is True
    assert "desk" in response.lower()


def test_standalone_desk():
    state = create_initial_state()

    success, response = process_player_action(
        state, "desk"
    )

    assert success is True
    assert state["objects"]["desk"]["examined"] is True


def test_standalone_drawer():
    state = create_initial_state()

    success, response = process_player_action(
        state, "drawer"
    )

    assert success is True
    assert "locked" in response.lower()
