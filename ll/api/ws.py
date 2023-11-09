from typing import Any, Optional

import structlog
from aiohttp import web
from pydantic import dataclasses

logger = structlog.getLogger(__name__)


@dataclasses.dataclass
class SocketConnection:
    """A socket connection."""

    ws: Any
    player_id: Optional[str] = None


async def setup_ws_app(_app):
    _app["connections"] = []


async def cleanup_ws_app(_app):
    for ws in _app["connections"]:
        await ws.close()


async def setup_ws_request(request):
    """Prepare a WebSocket connection - closed if setup failed."""
    ws = web.WebSocketResponse(heartbeat=25)
    conn = SocketConnection(ws=ws)
    request.app["connections"].append(conn)
    await conn.ws.prepare(request)

    return ws


async def cleanup_ws_request(request, player_id):
    for conn in request.app["connections"]:
        if conn.player_id == player_id:
            await conn.ws.close()
            request.app["connections"].remove(conn)
            return
