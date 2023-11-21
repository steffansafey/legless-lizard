import math

from structlog import get_logger

from ll.game.intersect import normalize_angle
from ll.game.player import add_player
from ll.game.resources.game import GamePlayer, GameState

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
    player_id = add_player(app["game_states"][1], message_wrapper.name, False)

    logger.info("player joined", player_name=message_wrapper.name)
    await assign_player_id_to_ws_connection(app, player_id, request.conn)

    return [JoinResponse(player_id=player_id, ok=True, reason=None)]


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
    new_angle = message_wrapper.angle
    if len(player.steps) >= 2:
        last_step = player.steps[-1].coordinates
        second_last_step = player.steps[-2].coordinates
        previous_step_angle = math.atan2(
            last_step[1] - second_last_step[1], last_step[0] - second_last_step[0]
        )

        normalized_angle = normalize_angle(player.angle - previous_step_angle)
        if normalized_angle > player.step_fov:
            new_angle = previous_step_angle + player.step_fov
        elif normalized_angle < -player.step_fov:
            new_angle = previous_step_angle - player.step_fov

    # update player angle
    player.angle = new_angle
    return []
