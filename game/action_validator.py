
from game.game_config import (
    OBJECTS,
    PUZZLES,
    DRAWER_CODE,
    FINAL_DOOR_CODE,
    REQUIRED_KEY
)

from game.game_state import (
    add_item,
    has_item,
    mark_puzzle_solved,
    is_puzzle_solved,
    record_action
)


def examine_object(state, object_name):

    if object_name not in OBJECTS:
        return False, "This object does not exist in the library."

    # Painting requires the brass key
    if object_name == "painting" and not has_item(state, REQUIRED_KEY):
        return False, "You need the brass key to investigate the painting."

    if object_name == "drawer" and not state["objects"]["drawer"]["unlocked"]:
        return True, (
        "You examine the old wooden drawer. "
        "It is locked with a four-digit combination lock. "
        "You must discover the correct code to open it."
    )

    if "examined" in state["objects"][object_name]:
        state["objects"][object_name]["examined"] = True

    record_action(state, f"Examined {object_name}")

    return True, OBJECTS[object_name]["description"]


def solve_puzzle(state, puzzle_name, answer):

    if puzzle_name not in PUZZLES:
        return False, "This puzzle does not exist."

    if is_puzzle_solved(state, puzzle_name):
        return True, "You have already solved this puzzle."

    # Check whether the player has discovered the relevant clue
    if puzzle_name == "desk_clue":
        if not state["objects"]["desk"]["examined"]:
            return False, "Examine the desk before solving this puzzle."

    elif puzzle_name == "bookshelf":
        if not state["objects"]["bookshelf"]["examined"]:
            return False, "Examine the bookshelf first."

        if not is_puzzle_solved(state, "desk_clue"):
            return False, "Solve the desk clue first."

    elif puzzle_name == "painting":
        if not state["objects"]["painting"]["examined"]:
            return False, "Investigate the painting first."

        if not has_item(state, REQUIRED_KEY):
            return False, "You need the brass key."

    # Validate the actual answer
    correct_answer = PUZZLES[puzzle_name]["solution"]

    if str(answer).strip().lower() != str(correct_answer).lower():
        record_action(state, f"Incorrect answer for {puzzle_name}")
        return False, "Incorrect answer. Try investigating the clues again."

    mark_puzzle_solved(state, puzzle_name)

    record_action(state, f"Solved {puzzle_name}")

    return True, f"Congratulations! You solved {puzzle_name}."


def unlock_drawer(state, code):

    if state["objects"]["drawer"]["unlocked"]:
        return True, "The drawer is already unlocked."

    if not is_puzzle_solved(state, "bookshelf"):
        return False, "Solve the bookshelf puzzle before opening the drawer."

    if str(code).strip() != DRAWER_CODE:
        return False, "Incorrect combination. The drawer remains locked."

    state["objects"]["drawer"]["unlocked"] = True

    record_action(state, "Unlocked drawer")

    return True, "The drawer opens. You discover an old brass key!"


def collect_key(state):

    if not state["objects"]["drawer"]["unlocked"]:
        return False, "You cannot collect the key before opening the drawer."

    if has_item(state, REQUIRED_KEY):
        return True, "You already have the brass key."

    add_item(state, REQUIRED_KEY)

    record_action(state, "Collected brass key")

    return True, "You collected the brass key."


def unlock_door(state, code):

    if state["escaped"]:
        return True, "You have already escaped!"

    required_puzzles = ["desk_clue", "bookshelf", "painting"]

    # Every puzzle must be solved
    for puzzle in required_puzzles:
        if not is_puzzle_solved(state, puzzle):
            return False, f"You must solve the {puzzle} puzzle first."

    if not has_item(state, REQUIRED_KEY):
        return False, "You need the brass key to escape."

    if str(code).strip() != FINAL_DOOR_CODE:
        record_action(state, "Incorrect exit code")
        return False, "Incorrect exit code. The door remains locked."

    state["objects"]["door"]["unlocked"] = True
    state["escaped"] = True

    record_action(state, "Successfully escaped")

    return True, "Congratulations! You escaped The Forgotten Library!"
