import asyncio

from structlog import get_logger

logger = get_logger(__name__)


async def game_loop(app):
    logger.info("Starting game loop")
    while True:
        # here is where we'll do the game logic to calculate the next state
        await asyncio.sleep(1)
        logger.info("tick")
