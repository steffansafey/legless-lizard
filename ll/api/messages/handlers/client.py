import math
import uuid
from random import choices, randint

from structlog import get_logger

from ll.game.resources.game import (
    MINIMUM_STEP_LENGTH,
    GamePlayer,
    GameState,
    PlayerStep,
)

from ..resources import ClientUpdate, JoinRequest, JoinResponse

logger = get_logger(__name__)


COLOR_PALETTE = [
    [170, 68, 101],
    [202, 137, 95],
    [85, 111, 68],
    [8, 76, 97],
    [209, 122, 34],
    [67, 87, 173],
    [148, 168, 154],
    [109, 159, 113],
    [87, 61, 28],
]


def get_unassigned_color(app):
    """Get an unassigned color."""
    assigned_colors = [p.color for p in app["game_states"][1].players]
    available_colors = [c for c in COLOR_PALETTE if c not in assigned_colors]
    color = choices(available_colors)[0]
    return color


async def assign_player_id_to_ws_connection(app, player_id, ws):
    """Assign a player id to a websocket connection."""
    for conn in app["connections"]:
        if conn.ws == ws:
            conn.player_id = player_id
            return


async def handle_join_request(request, message_wrapper: JoinRequest):
    """Handle a join request."""
    app = request.app
    logger.info("handle_join_request", message_wrapper=message_wrapper)

    # check if the player already exists (lookup by name)
    player = next(
        (p for p in app["game_states"][1].players if p.name == message_wrapper.name),
        None,
    )
    if player:
        return [
            JoinResponse(player_id=player.id, ok=False, reason="Name already taken")
        ]

    # create a new player
    player = GamePlayer(
        id=str(uuid.uuid4()),
        name=message_wrapper.name,
        color=get_unassigned_color(app),
        step_length=MINIMUM_STEP_LENGTH,
        spawned=False,
        steps=[
            PlayerStep(
                coordinates=[
                    float(randint(-1000, 1000)),
                    float(randint(-1000, 1000)),
                ]
            )
        ],
        step_fov=math.pi * 0.875,
        buffs=[],
    )
    app["game_states"][1].players.append(player)
    logger.info("player joined", existing_player=False)
    await assign_player_id_to_ws_connection(app, player.id, request.conn)

    return [JoinResponse(player_id=player.id, ok=True, reason=None)]


def _normalize_angle(angle):
    """
    Normalize an angle to be within -pi to pi.

    e.g. 3pi -> pi, -3pi -> -pi
    """
    return (angle + math.pi) % (2 * math.pi) - math.pi


async def handle_client_update(request, message_wrapper: ClientUpdate):
    """Handle a client update."""
    app = request.app
    # logger.info("handle_client_update", message_wrapper=message_wrapper)

    game_state: GameState = app["game_states"][1]

    # check if the player exists (lookup by ID)
    # TODO: Get this from session somehow
    player: GamePlayer = next(
        (p for p in game_state.players if p.id == message_wrapper.player_id),
        None,
    )
    if not player:
        logger.warning("player not found", player_id=message_wrapper.player_id)
        return []

    # validate the player's step is within the fov
    if len(player.steps) >= 2:
        last_step = player.steps[-1].coordinates
        second_last_step = player.steps[-2].coordinates
        previous_step_angle = math.atan2(
            last_step[1] - second_last_step[1], last_step[0] - second_last_step[0]
        )
        angle_diff = abs(_normalize_angle(previous_step_angle - player.angle))
        if angle_diff > player.step_fov:
            logger.warning(
                "player step outside fov, discarding update",
                player_id=player.id,
                angle=player.angle,
                prev_step_angle=previous_step_angle,
            )
            return []

    # update player angle
    player.angle = message_wrapper.angle
    return []
