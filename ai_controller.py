
# ai_controller.py
# Merio's first AI controller

# These action IDs must match main.py.
NO_ACTION = 0
MOVE_LEFT = 1
MOVE_RIGHT = 2
JUMP = 3
LEFT_JUMP = 4
RIGHT_JUMP = 5

# The current level has six coins; spike coordinates follow them.
COIN_COUNT = 6


def choose_action(state):
    """
    Rule-based platformer controller.

    Chooses the nearest remaining coin, then the goal. It keeps moving
    toward the target and jumps when the target is higher OR when a
    horizontal gap/obstacle needs a hop.
    """
    if len(state) < 31:
        raise ValueError("Expected a state containing six coin triples")

    player_x = float(state[0])
    player_y = float(state[1])
    on_surface = bool(state[8])
    game_won = bool(state[9])
    game_over = bool(state[11])

    if game_won or game_over:
        return NO_ACTION

    player_center_x = player_x + 20
    player_center_y = player_y + 20

    # Target coin centers (not their top-left corners).
    target = None
    nearest_distance = float("inf")
    for i in range(13, 13 + COIN_COUNT * 3, 3):
        coin_x = float(state[i]) + 10
        coin_y = float(state[i + 1]) + 10
        collected = bool(state[i + 2])
        if collected:
            continue

        distance = abs(coin_x - player_center_x) + abs(coin_y - player_center_y)
        if distance < nearest_distance:
            nearest_distance = distance
            target = (coin_x, coin_y)

    # Once all coins are collected, head to the middle of the goal.
    if target is None:
        target = (float(state[5]) + 12, float(state[6]) + 30)

    target_x, target_y = target
    dx = target_x - player_center_x
    dy = target_y - player_center_y

    # Keep horizontal movement active until the target is within reach.
    if dx < -12:
        moving_action = MOVE_LEFT
    elif dx > 12:
        moving_action = MOVE_RIGHT
    else:
        moving_action = NO_ACTION

    # Don't wait for the target to be higher: the level has gaps and
    # platforms that require jumping while travelling horizontally.
    # Jumping on a grounded frame gives the jump enough time to take effect.
    should_jump = on_surface and (
        dy < -28 or abs(dx) > 48
    )

    if should_jump:
        if moving_action == MOVE_LEFT:
            return LEFT_JUMP
        if moving_action == MOVE_RIGHT:
            return RIGHT_JUMP
        return JUMP

    return moving_action

# --------------------------------------------------
# Small feed-forward neural network (live preview)
# --------------------------------------------------
# This network currently has demonstration weights, not trained weights.
# It runs a real forward pass so its neuron activations can be visualized.
# The rule-based choose_action() remains the controller until training.

import math

NETWORK_INPUT_NAMES = [
    "player_x", "player_y", "velocity_y", "target_dx",
    "target_dy", "grounded", "coins_left", "goal_dx",
]

NETWORK_ACTION_NAMES = [
    "Nothing", "Left", "Right", "Jump", "Left+Jump", "Right+Jump",
]

# Fixed demonstration weights make the live visualization reproducible.
# These are not learned parameters.
_W1 = [
    [ 0.25,  0.10,  0.00,  0.35,  0.00,  0.10, -0.10,  0.00],
    [-0.15,  0.20,  0.30,  0.00, -0.35,  0.25,  0.00,  0.00],
    [ 0.00, -0.25,  0.15,  0.10,  0.30,  0.00,  0.10, -0.20],
    [ 0.20,  0.00, -0.20, -0.30,  0.00,  0.15,  0.20,  0.10],
    [-0.10,  0.15,  0.00,  0.20,  0.25, -0.10, -0.15,  0.30],
    [ 0.05, -0.10,  0.25,  0.00, -0.20,  0.30,  0.15, -0.10],
]
_B1 = [0.05, -0.05, 0.0, 0.03, -0.02, 0.01]

_W2 = [
    [ 0.20, -0.10,  0.05,  0.15, -0.10,  0.05],
    [-0.10,  0.25, -0.05,  0.05,  0.10, -0.10],
    [ 0.10, -0.05,  0.20, -0.10,  0.05,  0.10],
    [ 0.05,  0.10, -0.10,  0.20,  0.05, -0.05],
    [-0.05,  0.10,  0.05, -0.05,  0.20,  0.10],
    [ 0.10,  0.05,  0.10,  0.05, -0.05,  0.20],
]
_B2 = [0.0] * 6


def inspect_network(state):
    """Run one forward pass and return normalized activations for drawing."""
    if len(state) < 31:
        raise ValueError("Expected a state containing six coin triples")

    player_x = float(state[0])
    player_y = float(state[1])
    velocity_y = float(state[2])

    coins = [
        (float(state[i]), float(state[i + 1]), bool(state[i + 2]))
        for i in range(13, 31, 3)
    ]
    uncollected = [(x, y) for x, y, collected in coins if not collected]

    if uncollected:
        target_x, target_y = min(
            uncollected,
            key=lambda p: abs(p[0] - (player_x + 20))
                        + abs(p[1] - (player_y + 20))
        )
    else:
        target_x, target_y = float(state[5]), float(state[6])

    # Normalize inputs to roughly -1..1 before the network sees them.
    inputs = [
        (player_x - 450.0) / 450.0,
        (player_y - 250.0) / 250.0,
        max(-1.0, min(1.0, velocity_y / 12.0)),
        max(-1.0, min(1.0, (target_x - (player_x + 20)) / 450.0)),
        max(-1.0, min(1.0, (target_y - (player_y + 20)) / 250.0)),
        float(bool(state[8])),
        (len(uncollected) / 6.0) * 2.0 - 1.0,
        max(-1.0, min(1.0, (float(state[5]) - player_x) / 450.0)),
    ]

    hidden = [
        math.tanh(sum(w * x for w, x in zip(row, inputs)) + bias)
        for row, bias in zip(_W1, _B1)
    ]
    outputs = [
        math.tanh(sum(w * h for w, h in zip(row, hidden)) + bias)
        for row, bias in zip(_W2, _B2)
    ]

    return {
        "inputs": inputs,
        "hidden": hidden,
        "outputs": outputs,
        "predicted_action": max(range(len(outputs)), key=outputs.__getitem__),
    }
