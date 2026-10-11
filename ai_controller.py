
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
