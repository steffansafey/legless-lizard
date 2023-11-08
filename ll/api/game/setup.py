from .resources import GameState


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
    )

    app["game_states"][id] = [game_state]
