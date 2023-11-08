from aiohttp import web

routes = web.RouteTableDef()


def setup_api_routes(app):
    app.add_routes(routes=routes)
