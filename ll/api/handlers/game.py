from aiohttp import web
from structlog import get_logger

from ll.api.game.messages import handle_message
from ll.api.ws import setup_ws_request

logger = get_logger(__name__)
routes = web.RouteTableDef()


@routes.get("/api/v1/game/")
async def game_stream(request):
    ws = await setup_ws_request(request)
    if ws.closed:
        return ws

    async for msg in ws:
        """Handle a message from a websocket."""
        response_messages = await handle_message(request.app, msg.data)
        if response_messages:
            for response_message in response_messages:
                await ws.send_json(response_message.json())
    return ws


def setup_api_routes(app):
    app.add_routes(routes=routes)
