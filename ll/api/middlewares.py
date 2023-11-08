import sys
import traceback

import structlog
from aiohttp import web
from marshmallow import fields

from ll.api.schema import BaseSchema

logger = structlog.get_logger(__name__)


class ErrorSchema(BaseSchema):
    """Schema for returning HTTP errors."""

    code = fields.Integer(
        attribute="status_code", description="HTTP Status Code.", example=404
    )
    reason = fields.String(description="Reason for the error.", example="Not Found")
    message = fields.String(
        attribute="text",
        description="Message explaining the error.",
        example="Resource was not be found.",
    )


@web.middleware
async def http_error_middleware(request, handler):
    """Catch any exceptions, and return HTTP errors."""
    try:
        return await handler(request)
    except web.HTTPError as error:
        resp = ErrorSchema().dump(error)
    except Exception as e:
        payload = {
            "status_code": 500,
            "reason": "Backend Error",
            "text": "A server error occurred",
        }
        if request.app["SETTINGS"].DEBUG:
            tb = sys.exc_info()[2]
            e = e.with_traceback(tb)
            text = "".join(
                traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
            )
            payload["text"] = text
        logger.exception(e)
        resp = ErrorSchema().dump(payload)
    return web.json_response(resp, status=resp["code"])


@web.middleware
async def db_conn_middleware(request, handler):
    """Request a connection from the database pool, and release it when done."""
    pool = request.app["pool"]
    try:
        async with pool.acquire() as conn:
            request["conn"] = conn
            return await handler(request)
    finally:
        request.pop("conn", None)
