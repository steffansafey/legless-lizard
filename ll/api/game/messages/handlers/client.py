from structlog import get_logger

from ll.api.game.messages.resources import JoinRequest, JoinResponse

logger = get_logger(__name__)


async def handle_join_request(app, message_wrapper: JoinRequest):
    """Handle a join request."""
    logger.info("handle_join_request", message_wrapper=message_wrapper)

    return [JoinResponse(player_id="1", ok=True)]
