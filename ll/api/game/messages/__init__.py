from structlog import get_logger

from .handlers import handle_join_request
from .resources import JoinRequest, JoinResponse, MessageType, MessageWrapper

logger = get_logger(__name__)
handlers = {
    MessageType.JOIN_REQUEST: handle_join_request,
}
model_to_type = {
    JoinRequest: MessageType.JOIN_REQUEST,
    JoinResponse: MessageType.JOIN_RESPONSE,
}


async def handle_message(request, message: dict):
    """Handle a message from a websocket."""
    # convert the message into dataclass
    try:
        message_wrapper = MessageWrapper.model_validate_json(message)
    except Exception as e:
        logger.error("handle_message", error=e)
        return

    # call the handler
    response_messages = await handlers[message_wrapper.type](
        request, message_wrapper.payload
    )

    formatted_response_messages = []
    for response_message in response_messages:
        message_type = model_to_type[type(response_message)]
        formatted_response_messages.append(
            MessageWrapper(type=message_type, payload=response_message)
        )

    return formatted_response_messages
