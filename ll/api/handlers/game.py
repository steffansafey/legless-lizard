import json

from aiohttp import web
from structlog import get_logger

from ..messages import handle_message
from ..ws import setup_ws_request

logger = get_logger(__name__)
routes = web.RouteTableDef()


@routes.get("/api/v1/game/")
async def game_stream(request):
    ws = await setup_ws_request(request)
    if ws.closed:
        return ws

    request.conn = ws

    try:
        async for msg in ws:
            """Handle a message from a websocket."""
            response_messages = await handle_message(request, msg.data)
            if response_messages:
                for response_message in response_messages:
                    # serialize the message to json
                    response_message_json = response_message.json()
                    resp_dict = json.loads(response_message_json)
                    await ws.send_json(resp_dict)
    except Exception as e:
        logger.error("game_stream", error=e)
    return ws


def setup_api_routes(app):
    app.add_routes(routes=routes)
