from aiohttp import web
from aiohttp_apispec import docs, response_schema
from marshmallow import fields

from ll.api.schema import BaseSchema

routes = web.RouteTableDef()


class HealthcheckResponseSchema(BaseSchema):
    status = fields.String(description="Status of the service", example="OK")


@docs(
    tags=["Healthcheck"],
    summary="Service health",
    description="Get the health of the service",
)
@response_schema(HealthcheckResponseSchema, code=200)
@routes.get("/healthcheck/")
async def healthcheck(request):
    schema = HealthcheckResponseSchema()
    resp = schema.dump({"status": "OK"})
    return web.json_response(resp)


def setup_healthcheck_routes(app):
    app.add_routes(routes)
