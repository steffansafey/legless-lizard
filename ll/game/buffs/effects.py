import math
from functools import partial

from ll.game.resources.buffs import BuffType
from ll.game.resources.consumables import ConsumableType
from ll.game.resources.game import GamePlayer, GameState


def attract_apples(game_state: GameState, player: GamePlayer, repel: bool):
    """Apple magnet effect.

    Move all apples closer to the player, stopping at the player if they are close enough
    """

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


def tick_period_boost(game_state: GameState, player: GamePlayer, boost: float):
    """Tick period boost effect.

    Increase the tick period by a factor of boost.
    """
    game_state.tick_period *= boost


def noop(*args, **kwargs):
    """No-op effect."""
    pass


BUFF_APPLY_MAP = {
    BuffType.APPLE_MAGNET: partial(attract_apples, repel=False),
    BuffType.APPLE_REPEL: partial(attract_apples, repel=True),
    BuffType.TICK_PERIOD_BOOST: partial(tick_period_boost, boost=0.5),
    BuffType.GHOST: noop,
}

BUFF_UNAPPLY_MAP = {
    BuffType.APPLE_MAGNET: noop,
    BuffType.APPLE_REPEL: noop,
    BuffType.TICK_PERIOD_BOOST: partial(tick_period_boost, boost=2),
    BuffType.GHOST: noop,
}
