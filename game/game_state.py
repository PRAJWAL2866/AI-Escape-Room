
def create_initial_state():
    return {
        "room": "library",

        "objects": {
            "desk": {
                "examined": False
            },
            "bookshelf": {
                "examined": False
            },
            "drawer": {
                "unlocked": False
            },
            "painting": {
                "examined": False,
                "secret_revealed": False
            },
            "door": {
                "unlocked": False
            }
        },

        "inventory": [],

        "solved_puzzles": [],

        "escaped": False,

        "action_history": []
    }


def add_item(state, item):
    if item not in state["inventory"]:
        state["inventory"].append(item)


def has_item(state, item):
    return item in state["inventory"]


def mark_puzzle_solved(state, puzzle):
    if puzzle not in state["solved_puzzles"]:
        state["solved_puzzles"].append(puzzle)


def is_puzzle_solved(state, puzzle):
    return puzzle in state["solved_puzzles"]


def record_action(state, action):
    state["action_history"].append(action)
