
ROOM_NAME = "The Forgotten Library"

ROOM_DESCRIPTION = """
You wake up inside an abandoned library.
A heavy wooden door blocks your exit.
An old desk, a mysterious bookshelf, a strange
painting and a locked drawer surround you.
You must investigate the room and solve its mysteries.
"""


OBJECTS = {
    "desk": {
        "name": "Old Desk",
        "description": (
            "You discover a handwritten riddle: "
            "'I grow when shared, I guide when darkness falls, "
            "and I am the treasure of every curious mind. "
            "What am I?'"
        )
    },

    "bookshelf": {
        "name": "Bookshelf",
        "description": (
            "Four unusual books contain handwritten numbers: "
            "4, 8, 2 and 1. Their order appears important."
        )
    },

    "drawer": {
        "name": "Locked Drawer",
        "description": (
            "An antique drawer with a four-digit combination lock."
        )
    },

    "painting": {
        "name": "Mysterious Painting",
        "description": (
            "Using the brass key, you reveal a hidden compartment. "
            "Inside is a note showing four digits: 7, 3, 9 and 4."
        )
    },

    "door": {
        "name": "Exit Door",
        "description": (
            "A heavy wooden door secured by a four-digit combination lock."
        )
    }
}


# Solutions are stored in Python, not in Gemini's responses.
PUZZLES = {
    "desk_clue": {
        "solution": "knowledge",
        "solved": False
    },
    "bookshelf": {
        "solution": "4821",
        "solved": False
    },
    "painting": {
        "solution": "7394",
        "solved": False
    }
}

DRAWER_CODE = "4821"
FINAL_DOOR_CODE = "7394"
REQUIRED_KEY = "brass_key"
