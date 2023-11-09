import uuid

from structlog import get_logger

from ll.api.game.messages.resources import JoinRequest, JoinResponse
from ll.api.game.resources import GamePlayer

logger = get_logger(__name__)


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
        logger.info("player joined", existing_player=True)
        await assign_player_id_to_ws_connection(app, player.id, request.conn)
        return [JoinResponse(player_id=player.id, ok=True)]

    # create a new player
    player = GamePlayer(
        id=str(uuid.uuid4()),
        name=message_wrapper.name,
        color=message_wrapper.color,
        step_length=1,
        position=[0, 0],
        direction=[0, 1],
        spawned=False,
        steps=[],
    )
    app["game_states"][1].players.append(player)
    logger.info("player joined", existing_player=False)
    await assign_player_id_to_ws_connection(app, player.id, request.conn)

    return [JoinResponse(player_id=player.id, ok=True)]
