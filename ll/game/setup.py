from .resources.game import GameState


def setup_game_states(app):
    """Set up the game states."""
    app["game_states"] = {}

    # Just create a single game state for now
    game_state = GameState(
        id=1,
        tick=0,
        tick_period=1,
        server_timestamp=0,
        server_next_tick_time=0,
        players=[],
        consumables=[],
        global_buffs=[],
        map_bounds=[[-1000, -1000], [1000, 1000]],
    )

    app["game_states"][1] = game_state
