import structlog
from aiohttp import web

logger = structlog.getLogger(__name__)


async def setup_ws_app(_app):
    _app["sockets"] = []


async def cleanup_ws_app(_app):
    for s in _app["sockets"]:
        await s.close()


async def receive_and_put(ws):
    async for m in ws:
        logger.info("received ws message", message=m)


async def setup_ws_request(request):
    """Prepare a WebSocket connection - closed if setup failed."""
    ws = web.WebSocketResponse(heartbeat=25)
    request.app["sockets"].append(ws)
    await ws.prepare(request)

    return ws


async def cleanup_ws_request(request, ws):
    await ws.close()
    request.app["sockets"].remove(ws)
