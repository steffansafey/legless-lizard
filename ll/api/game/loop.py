import asyncio
import json
import math
from datetime import datetime, timedelta

from structlog import get_logger

from ll.api.game.messages.resources import MessageType, MessageWrapper, StateUpdate
from ll.api.game.resources import GameState, PlayerStep

TICK_PERIOD = 2

logger = get_logger(__name__)


def format_gamestate_ws_update(game_state: GameState):
    message = MessageWrapper(
        type=MessageType.STATE_UPDATE,
        payload=StateUpdate(
            tick=game_state.tick,
            tick_period=TICK_PERIOD,
            server_timestamp=game_state.server_timestamp,
            server_next_tick_time=game_state.server_next_tick_time,
            players=game_state.players,
        ),
    )
    return json.loads(message.json())


def get_connection_by_player_id(app, player_id):
    for conn in app["connections"]:
        if conn.player_id == player_id:
            return conn


async def update_state_for_connected_players(app, game_state):
    game_state_msg = format_gamestate_ws_update(game_state)
    for player in game_state.players:
        conn = get_connection_by_player_id(app, player.id)
        if conn:
            await conn.ws.send_json(game_state_msg)


def remove_disconnected_or_disconnecting_players(app, game_state):
    """Remove players that are disconnected or disconnecting."""
    for conn in app["connections"]:
        if conn.ws.closed:
            player = next(
                (p for p in game_state.players if p.id == conn.player_id),
                None,
            )
            if player:
                logger.info("player disconnected", player_id=player.id)
                game_state.players.remove(player)
            app["connections"].remove(conn)


async def game_loop(app):
    logger.info("Starting game loop")
    while True:
        # here is where we'll do the game logic to calculate the next state
        game_state: GameState = app["game_states"][1]
        await asyncio.sleep(game_state.tick_period)
        remove_disconnected_or_disconnecting_players(app, game_state)

        # log the active players
        logger.info("active players", player_names=[p.name for p in game_state.players])

        # update the game state
        game_state.tick += 1
        game_state.server_timestamp = datetime.now()

        # add the tick period to the server timestamp in seconds
        game_state.server_next_tick_time = datetime.now() + timedelta(
            seconds=TICK_PERIOD
        )

        # Add a step to each player
        for player in game_state.players:
            take_step(player)

        await update_state_for_connected_players(app, game_state)


def take_step(player):
    x, y = player.steps[-1].coordinates
    dx = math.cos(player.angle) * player.step_length
    dy = math.sin(player.angle) * player.step_length
    player.steps.append(PlayerStep(coordinates=[x + dx, y + dy]))
