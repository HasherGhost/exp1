
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
    Receives Merio's game state and returns an action ID.

    Current state layout:
    0  player_x
    1  player_y
    2  velocity_y
    3  first_coin_x
    4  first_coin_y
    5  goal_x
    6  goal_y
    7  first_coin_collected
    8  on_surface
    9  game_won
    10 lives
    11 game_over
    12 score

    The six coin triples begin at index 13. Spike coordinates follow
    the coin triples and are intentionally not treated as coins.
    """

    if len(state) < 13:
        raise ValueError("Invalid Merio game state")

    player_x = state[0]
    player_y = state[1]
    velocity_y = state[2]
    on_surface = bool(state[8])
    game_won = bool(state[9])
    game_over = bool(state[11])

    # Stop when the episode has ended.
    if game_won or game_over:
        return NO_ACTION

    player_center_x = player_x + 20
    player_center_y = player_y + 20

    # Find the nearest uncollected coin.
    target = None
    nearest_distance = float("inf")

    for i in range(13, 13 + COIN_COUNT * 3, 3):
        coin_x = state[i]
        coin_y = state[i + 1]
        collected = bool(state[i + 2])

        if collected:
            continue

        distance = (
            abs(coin_x - player_center_x)
            + abs(coin_y - player_center_y)
        )

        if distance < nearest_distance:
            nearest_distance = distance
            target = (coin_x, coin_y)

    # If all coins are collected, head towards the goal.
    if target is None:
        target = (state[5], state[6])

    target_x, target_y = target

    # Choose horizontal movement.
    if player_center_x < target_x - 8:
        moving_action = MOVE_RIGHT
    elif player_center_x > target_x + 8:
        moving_action = MOVE_LEFT
    else:
        moving_action = NO_ACTION

    # Basic jumping rule: jump when grounded and
    # the target is substantially higher.
    should_jump = (
        on_surface
        and target_y < player_center_y - 35
    )

    if should_jump:
        if moving_action == MOVE_LEFT:
            return LEFT_JUMP
        elif moving_action == MOVE_RIGHT:
            return RIGHT_JUMP
        else:
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
