# Testing Report - AI Escape Room

## Test Execution

- Framework: pytest
- Total tests: 23
- Passed: 23
- Failed: 0
- Execution time: 0.18 seconds
- Result: All tests passed

Command: `python -m pytest -v`

## Test Coverage

### 1. Game Engine Tests
13 tests passed.

Coverage includes:
- Looking around the room.
- Examining objects.
- Solving the desk puzzle.
- Rejecting an invalid drawer code.
- Preventing premature escape.
- Preventing administrative override.
- Completing the escape sequence.
- Object recognition and navigation.

### 2. Intent Dispatcher Tests
5 tests passed.

Coverage includes:
- Recognizing player actions.
- Understanding examination requests.
- Rejecting invalid targets.
- Preventing unauthorized drawer unlocking.
- Rejecting invalid escape attempts.

### 3. Version 2 Validation Tests
5 tests passed.

Coverage includes:
- Rejecting invalid objects.
- Preventing puzzle solving without examination.
- Keeping the drawer locked.
- Preventing premature key collection.
- Preventing escape without solving puzzles.

## Five Important Challenge Scenarios

| Scenario | Expected Version 2 Behaviour |
|---|---|
| Escape immediately | Reject until requirements are completed |
| Incorrect drawer code | Keep drawer locked |
| Collect key before unlocking drawer | Reject collection |
| Solve without examining object | Reject action |
| Escape without completing puzzles | Prevent escape |

## Conclusion

All 23 automated tests passed in the recorded test execution.

These results demonstrate that Version 2 uses Python validation to enforce game rules and control progression.

Manual gameplay and external Gemini API behaviour should be evaluated separately.
