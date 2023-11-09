import uuid
from random import randint

from structlog import get_logger

from ll.api.game.messages.resources import ClientUpdate, JoinRequest, JoinResponse
from ll.api.game.resources import GamePlayer, GameState, PlayerStep

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
        step_length=50,
        spawned=False,
        steps=[
            PlayerStep(
                coordinates=[
                    float(randint(0, 100)),
                    float(randint(0, 100)),
                ]
            )
        ],
    )
    app["game_states"][1].players.append(player)
    logger.info("player joined", existing_player=False)
    await assign_player_id_to_ws_connection(app, player.id, request.conn)

    return [JoinResponse(player_id=player.id, ok=True)]


async def handle_client_update(request, message_wrapper: ClientUpdate):
    """Handle a client update."""
    app = request.app
    logger.info("handle_client_update", message_wrapper=message_wrapper)

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

    # update player angle
    player.angle = message_wrapper.angle
    return []
