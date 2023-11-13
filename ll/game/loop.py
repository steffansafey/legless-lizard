import asyncio
import json
from datetime import datetime, timedelta
from random import choices, randint, random

from structlog import get_logger

from ..api.messages.resources import MessageType, MessageWrapper, StateUpdate
from .buffs import BuffApplicationTime, apply_and_decay_buffs
from .player import take_player_steps
from .resources.consumables import CONSUMABLES, Consumable
from .resources.game import MIN_CONSUMABLE_COUNT, GameState

logger = get_logger(__name__)


def format_gamestate_ws_update(game_state: GameState):
    message = MessageWrapper(
        type=MessageType.STATE_UPDATE,
        payload=StateUpdate(
            tick=game_state.tick,
            tick_period=game_state.tick_period,
            server_timestamp=game_state.server_timestamp,
            server_next_tick_time=game_state.server_next_tick_time,
            players=game_state.players,
            consumables=game_state.consumables,
        ),
    )

    return json.loads(message.json())


def get_connection_by_player_id(app, player_id):
    for conn in app["connections"]:
        if conn.player_id == player_id:
            return conn


async def publish_state_to_connected_players(app, game_state):
    game_state_msg = format_gamestate_ws_update(game_state)
    for player in game_state.players:
        conn = get_connection_by_player_id(app, player.id)
        if conn:
            await conn.ws.send_json(game_state_msg)


def ensure_consumables_spawned(game_state):
    """Ensure there are enough consumables spawned."""

    CONSUMABLE_SPAWN_RATIOS = {d.type: d.spawn_ratio for d in CONSUMABLES}
    ACTUAL_SPAWN_RATIOS = {
        d.type: len([c for c in game_state.consumables if c.type == d.type])
        / max(len(game_state.consumables), 1)
        for d in CONSUMABLES
    }

    TO_SPAWN_RATIOS = {}
    for consumable_type, spawn_ratio in CONSUMABLE_SPAWN_RATIOS.items():
        actual_ratio = ACTUAL_SPAWN_RATIOS[consumable_type]
        if actual_ratio < spawn_ratio:
            TO_SPAWN_RATIOS[consumable_type] = spawn_ratio
        else:
            TO_SPAWN_RATIOS[consumable_type] = 0

    while len(game_state.consumables) < MIN_CONSUMABLE_COUNT:
        # take a random consumable based on the spawn ratios
        consumable = choices(
            CONSUMABLES,
            weights=list(CONSUMABLE_SPAWN_RATIOS.values()),
            k=1,
        )[0]

        # find random float between the size multiplier range
        size_multiplier = (
            random()
            * (
                consumable.size_multiplier_range[1]
                - consumable.size_multiplier_range[0]
            )
            + consumable.size_multiplier_range[0]
        )

        game_state.consumables.append(
            Consumable(
                coordinates=[randint(-1000, 1000), randint(-1000, 1000)],
                type=consumable.type,
                size=int(consumable.size * size_multiplier),
                color=consumable.color,
            )
        )


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

        apply_and_decay_buffs(game_state, BuffApplicationTime.PRE_STEP)

        take_player_steps(game_state)
        ensure_consumables_spawned(game_state)

        apply_and_decay_buffs(game_state, BuffApplicationTime.POST_STEP)

        # add the tick period to the server timestamp in seconds
        game_state.server_next_tick_time = datetime.now() + timedelta(
            seconds=game_state.tick_period
        )
        await publish_state_to_connected_players(app, game_state)