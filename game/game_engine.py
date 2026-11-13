
import re

from game.action_validator import (
    examine_object,
    solve_puzzle,
    unlock_drawer,
    collect_key,
    unlock_door,
)

from game.game_state import has_item
from game.game_config import OBJECTS


# ==========================================================
# 1. OBJECT ALIASES
# ==========================================================

OBJECT_ALIASES = {
    "bookshelf": "bookshelf",
    "book shelf": "bookshelf",
    "books": "bookshelf",
    "desk": "desk",
    "table": "desk",
    "wooden table": "desk",
    "drawer": "drawer",
    "painting": "painting",
    "picture": "painting",
    "portrait": "painting",
    "door": "door",
    "exit": "door",
}


# ==========================================================
# 2. INPUT HELPERS
# ==========================================================

def extract_code(message):
    """Extract a four-digit code from a message."""

    if not isinstance(message, str):
        return None

    match = re.search(r"\b\d{4}\b", message)
    return match.group(0) if match else None


def identify_object(message):
    """Identify an object mentioned by the player."""

    if not isinstance(message, str):
        return None

    text = message.lower()

    for alias in sorted(OBJECT_ALIASES, key=len, reverse=True):
        if re.search(r"\b" + re.escape(alias) + r"\b", text):
            return OBJECT_ALIASES[alias]

    return None


def normalize_answer(answer):
    """Normalize a text puzzle answer."""

    if answer is None:
        return None

    return str(answer).strip().lower().rstrip(" .!?")


def get_intent_code(intent):
    """Extract a four-digit code from Gemini's response."""

    candidate = intent.get("code")

    if candidate is None:
        candidate = intent.get("answer")

    if candidate is None:
        return None

    match = re.fullmatch(r"\s*(\d{4})\s*", str(candidate))

    return match.group(1) if match else None


# ==========================================================
# 3. GAME PROGRESS AND PUZZLE CONTEXT
# ==========================================================

def all_puzzles_solved(state):
    """Check whether all three puzzles have been solved."""

    required_puzzles = {
        "desk_clue",
        "bookshelf",
        "painting",
    }

    return required_puzzles.issubset(
        set(state["solved_puzzles"])
    )


def get_current_puzzle(state):
    """Identify the next puzzle that is ready to be solved."""

    solved = state["solved_puzzles"]
    objects = state["objects"]

    # Desk riddle
    if (
        "desk_clue" not in solved
        and objects["desk"].get("examined", False)
    ):
        return "desk_clue"

    # Bookshelf puzzle
    if (
        "desk_clue" in solved
        and "bookshelf" not in solved
        and objects["bookshelf"].get("examined", False)
    ):
        return "bookshelf"

    # Painting puzzle
    if (
        "bookshelf" in solved
        and has_item(state, "brass_key")
        and "painting" not in solved
        and objects["painting"].get("examined", False)
    ):
        return "painting"

    return None


def solve_contextual_answer(state, answer):
    """Route a standalone answer to the active puzzle."""

    puzzle = get_current_puzzle(state)

    if puzzle is None:
        return False, (
            "There is no active puzzle to answer. "
            "Investigate the next available object first."
        )

    return solve_puzzle(state, puzzle, answer)


def process_standalone_code(state, code):
    """Route a four-digit code according to game progression."""

    if not code or not re.fullmatch(r"\d{4}", str(code)):
        return False, "Please enter a valid four-digit code."

    code = str(code)
    solved = state["solved_puzzles"]
    objects = state["objects"]

    # All puzzles solved: code belongs to the exit.
    if all_puzzles_solved(state):
        return unlock_door(state, code)

    # Bookshelf solved: code belongs to the drawer.
    if (
        "bookshelf" in solved
        and not objects["drawer"]["unlocked"]
    ):
        return unlock_drawer(state, code)

    # Key collected and painting examined:
    # code belongs to the painting puzzle.
    if (
        has_item(state, "brass_key")
        and objects["painting"].get("examined", False)
        and "painting" not in solved
    ):
        return solve_puzzle(state, "painting", code)

    return solve_contextual_answer(state, code)


# ==========================================================
# 4. VERSION 1: KEYWORD-BASED ACTION PROCESSOR
# ==========================================================

def process_player_action(state, message):
    """
    Process player messages using Python keyword recognition.

    This function also acts as a fallback when Gemini
    cannot identify the player's intention.
    """

    if not isinstance(message, str):
        return False, "Please enter a valid message."

    text = message.lower().strip()

    if not text:
        return False, "Please enter an action."

    # Prevent basic rule override attempts.
    forbidden_phrases = [
        "ignore previous instructions",
        "ignore all rules",
        "i am the administrator",
        "i am the game administrator",
        "reveal all secrets",
        "reveal all secret",
    ]

    if any(phrase in text for phrase in forbidden_phrases):
        return False, "Game rules cannot be overridden."

    if state["escaped"]:
        return True, "You have already escaped! Restart to play again."

    obj = identify_object(text)
    code = extract_code(text)

    # ------------------------------------------------------
    # INVENTORY
    # ------------------------------------------------------

    if any(term in text for term in [
        "inventory",
        "show my items",
        "show inventory",
        "what am i carrying",
        "my items",
    ]):
        if not state["inventory"]:
            return True, "Your inventory is empty."

        return True, "You are carrying: " + ", ".join(
            state["inventory"]
        )

    # ------------------------------------------------------
    # HELP
    # ------------------------------------------------------

    if any(term in text for term in [
        "what next",
        "what's next",
        "whats next",
        "help",
        "what should i do",
        "give me a hint",
    ]):
        if "desk_clue" not in state["solved_puzzles"]:
            return True, "Examine the desk and solve its riddle."

        if "bookshelf" not in state["solved_puzzles"]:
            return True, "Examine the bookshelf and discover its code."

        if not state["objects"]["drawer"]["unlocked"]:
            return True, "Use the bookshelf combination to unlock the drawer."

        if not has_item(state, "brass_key"):
            return True, "Collect the brass key from the open drawer."

        if "painting" not in state["solved_puzzles"]:
            return True, "Use the brass key to investigate the painting."

        return True, "Enter the final code to unlock the exit."

    # ------------------------------------------------------
    # LOOK AROUND
    # ------------------------------------------------------

    if any(term in text for term in [
        "look around",
        "describe room",
        "where am i",
        "what can i see",
        "look at the room",
    ]):
        return True, (
            "You are in The Forgotten Library. "
            "You can see an old desk, a bookshelf, "
            "a locked drawer, a mysterious painting "
            "and a heavy exit door."
        )

    # ------------------------------------------------------
    # DIRECTIONAL NAVIGATION
    # ------------------------------------------------------

    direction_terms = [
        "go right",
        "go left",
        "move right",
        "move left",
        "go forward",
        "go back",
        "move forward",
        "move back",
        "go north",
        "go south",
        "go east",
        "go west",
        "move north",
        "move south",
        "move east",
        "move west",
        "turn right",
        "turn left",
        "walk forward",
        "walk backward",
        "walk back",
    ]

    if any(term in text for term in direction_terms):
        return True, (
            "You move through the library. "
            "You are still inside the same room. "
            "You can approach and investigate the desk, "
            "bookshelf, drawer, painting or exit door."
        )

    # ------------------------------------------------------
    # COLLECT KEY
    # ------------------------------------------------------

    if (
        "key" in text
        and any(term in text for term in [
            "collect",
            "take",
            "pick up",
            "grab",
        ])
    ):
        return collect_key(state)

    # ------------------------------------------------------
    # DRAWER
    # ------------------------------------------------------

    if obj == "drawer":

        if code:
            return unlock_drawer(state, code)

        if any(term in text for term in [
            "open",
            "unlock",
            "combination",
            "code",
        ]):
            return False, (
                "Please enter the four-digit drawer combination."
            )

    # ------------------------------------------------------
    # EXIT DOOR
    # ------------------------------------------------------

    if obj == "door" or any(term in text for term in [
        "escape",
        "exit",
    ]):

        if code:
            return unlock_door(state, code)

        if any(term in text for term in [
            "unlock",
            "open",
            "escape",
            "enter",
        ]):
            return False, "The exit requires a four-digit code."

    # ------------------------------------------------------
    # EXAMINE OBJECT
    # ------------------------------------------------------

    examine_terms = [
        "examine",
        "inspect",
        "look at",
        "investigate",
        "search",
        "check",
    ]

    if obj and any(term in text for term in examine_terms):
        return examine_object(state, obj)

    # ------------------------------------------------------
    # APPROACH OBJECT
    # ------------------------------------------------------

    approach_terms = [
        "go towards",
        "go to",
        "walk to",
        "walk towards",
        "move towards",
        "approach",
        "head towards",
    ]

    if obj and any(term in text for term in approach_terms):
        return True, (
            f"You approach the {OBJECTS[obj]['name']}. "
            "You can now investigate it more closely."
        )

    # ------------------------------------------------------
    # EXPLICIT DESK ANSWER
    # ------------------------------------------------------

    if "knowledge" in text and (
        obj == "desk"
        or any(term in text for term in [
            "answer",
            "solve",
            "riddle",
        ])
    ):
        return solve_puzzle(
            state,
            "desk_clue",
            "knowledge",
        )

    # ------------------------------------------------------
    # EXPLICIT BOOKSHELF ANSWER
    # ------------------------------------------------------

    if obj == "bookshelf" and code:
        return solve_puzzle(
            state,
            "bookshelf",
            code,
        )

    # ------------------------------------------------------
    # EXPLICIT PAINTING ANSWER
    # ------------------------------------------------------

    if obj == "painting" and code:
        return solve_puzzle(
            state,
            "painting",
            code,
        )

    # ------------------------------------------------------
    # STANDALONE TEXT ANSWER
    # ------------------------------------------------------

    if normalize_answer(text) == "knowledge":
        return solve_contextual_answer(state, "knowledge")

    # ------------------------------------------------------
    # STANDALONE NUMERIC CODE
    # ------------------------------------------------------

    if re.fullmatch(r"\d{4}", text):
        return process_standalone_code(state, text)

    # ------------------------------------------------------
    # SHORT OBJECT NAME
    # ------------------------------------------------------

    if obj and len(text.split()) <= 3:
        return examine_object(state, obj)

    return False, (
        "I couldn't understand that action. "
        "Try 'examine the desk', 'open the drawer', "
        "'collect the key', or 'show inventory'."
    )


# ==========================================================
# 5. VERSION 2: GEMINI INTENT DISPATCHER
# ==========================================================

def process_intent(state, intent):
    """
    Execute an action identified by Gemini.

    Gemini identifies the player's intention.
    Python validates all game rules and state changes.
    """

    if not isinstance(intent, dict):
        return False, "Invalid action information."

    action = intent.get("action")
    target = intent.get("target")
    answer = intent.get("answer")

    if state["escaped"]:
        return True, "You have already escaped! Restart to play again."

    # Normalize object aliases.
    if isinstance(target, str):
        target = OBJECT_ALIASES.get(
            target.lower().strip(),
            target.lower().strip(),
        )

    numeric_code = get_intent_code(intent)

    # ------------------------------------------------------
    # EXAMINE
    # ------------------------------------------------------

    if action == "examine":

        if target not in OBJECTS:
            return False, "Which object would you like to examine?"

        return examine_object(state, target)

    # ------------------------------------------------------
    # APPROACH
    # ------------------------------------------------------

    if action == "approach":

        if target not in OBJECTS:
            return False, "Which object would you like to approach?"

        return True, (
            f"You approach the {OBJECTS[target]['name']}. "
            "You can now investigate it more closely."
        )

    # ------------------------------------------------------
    # UNLOCK DRAWER
    # ------------------------------------------------------

    if action == "unlock_drawer":

        if numeric_code is None:
            return False, "Please enter the four-digit drawer combination."

        return unlock_drawer(state, numeric_code)

    # ------------------------------------------------------
    # COLLECT KEY
    # ------------------------------------------------------

    if action == "collect_key":
        return collect_key(state)

    # ------------------------------------------------------
    # UNLOCK EXIT
    # ------------------------------------------------------

    if action == "unlock_door":

        if numeric_code is None:
            return False, "Please provide the four-digit exit code."

        return unlock_door(state, numeric_code)

    # ------------------------------------------------------
    # SOLVE PUZZLE
    # ------------------------------------------------------

    if action == "solve":

        # Route numeric codes using game progress.
        if numeric_code is not None:
            return process_standalone_code(
                state,
                numeric_code,
            )

        puzzle_mapping = {
            "desk": "desk_clue",
            "desk_clue": "desk_clue",
            "riddle": "desk_clue",
            "bookshelf": "bookshelf",
            "books": "bookshelf",
            "painting": "painting",
            "picture": "painting",
        }

        puzzle = puzzle_mapping.get(target)

        if puzzle is None:
            puzzle = get_current_puzzle(state)

        if puzzle is None:
            return False, (
                "There is no active puzzle to solve. "
                "Examine the next available object first."
            )

        if answer is None:
            return False, "Please provide your proposed puzzle answer."

        return solve_puzzle(
            state,
            puzzle,
            answer,
        )

    # ------------------------------------------------------
    # STANDALONE NUMERIC CODE
    # ------------------------------------------------------

    if numeric_code is not None:
        return process_standalone_code(
            state,
            numeric_code,
        )

    # ------------------------------------------------------
    # STANDALONE TEXT ANSWER
    # ------------------------------------------------------

    if normalize_answer(answer) == "knowledge":
        return solve_contextual_answer(
            state,
            "knowledge",
        )

    # ------------------------------------------------------
    # INVENTORY
    # ------------------------------------------------------

    if action == "inventory":

        if not state["inventory"]:
            return True, "Your inventory is empty."

        return True, "You are carrying: " + ", ".join(
            state["inventory"]
        )

    # ------------------------------------------------------
    # LOOK
    # ------------------------------------------------------

    if action == "look":
        return True, (
            "You are in The Forgotten Library. "
            "You can see a desk, bookshelf, drawer, "
            "painting and exit door."
        )

    # ------------------------------------------------------
    # HELP
    # ------------------------------------------------------

    if action == "help":
        return True, (
            "Explore the library, investigate objects, "
            "solve the clues, collect useful items "
            "and unlock the exit."
        )

    return False, (
        "I couldn't understand that action. "
        "Try examining an object or investigating the room."
    )
