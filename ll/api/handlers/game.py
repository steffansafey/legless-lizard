from aiohttp import web

routes = web.RouteTableDef()


def join_game(game_id: int):
    """Join a game."""
    pass


@routes.get("/api/v1/game/")
async def game_stream(request):
    # for now, just join game 1
    join_game(1)
    return web.Response(text="Hello, world")


def setup_api_routes(app):
    app.add_routes(routes=routes)
