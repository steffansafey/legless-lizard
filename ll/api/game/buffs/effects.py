import math
from functools import partial

from ll.api.game.resources import ConsumableType, GamePlayer, GameState

from .resources import BuffType


def attract_apples(game_state: GameState, player: GamePlayer, repel: bool):
    """Apple magnet effect."""
    # move all apples closer to the player, stopping at the player if they are close enough
    DISTANCE = 15
    for c in game_state.consumables:
        if c.type == ConsumableType.APPLE:
            dx = player.steps[-1].coordinates[0] - c.coordinates[0]
            dy = player.steps[-1].coordinates[1] - c.coordinates[1]
            dist = math.sqrt(dx**2 + dy**2)
            if dist < DISTANCE:
                c.coordinates = player.steps[-1].coordinates
            else:
                c.coordinates = (
                    [
                        c.coordinates[0] + dx / dist * DISTANCE,
                        c.coordinates[1] + dy / dist * DISTANCE,
                    ]
                    if not repel
                    else [
                        c.coordinates[0] - dx / dist * DISTANCE,
                        c.coordinates[1] - dy / dist * DISTANCE,
                    ]
                )


def noop(*args, **kwargs):
    """No-op effect."""
    pass


BUFF_APPLY_MAP = {
    BuffType.APPLE_MAGNET: partial(attract_apples, repel=False),
    BuffType.APPLE_REPEL: partial(attract_apples, repel=True),
}

BUFF_UNAPPLY_MAP = {
    BuffType.APPLE_MAGNET: noop,
    BuffType.APPLE_REPEL: noop,
}
