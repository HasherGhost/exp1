
from ai_controller import choose_action

# A sample game state using Merio's current state layout.
state = [
    100, 350, 0,       # player x, y, vertical velocity
    100, 395,           # first coin x, y
    850, 320,           # goal x, y
    0,                  # first coin collected
    1,                  # on surface
    0,                  # game won
    3,                  # lives
    0,                  # game over
    0,                  # score
]

# Six coins: x, y, collected
state.extend([
    100, 395, 0,
    250, 315, 0,
    410, 255, 0,
    570, 195, 0,
    720, 265, 0,
    810, 345, 0,
])

# Two spikes: x, y
state.extend([440, 405, 700, 275])

action = choose_action(state)

action_names = {
    0: "NO_ACTION",
    1: "MOVE_LEFT",
    2: "MOVE_RIGHT",
    3: "JUMP",
    4: "LEFT_JUMP",
    5: "RIGHT_JUMP",
}

print("Chosen action ID:", action)
print("Chosen action:", action_names.get(action, "INVALID ACTION"))

assert action in action_names, "Controller returned an invalid action!"
print("Test passed!")
