import math

from ll.api.game.resources import ConsumableType, GamePlayer, GameState

from .resources import BuffType


def apply_apple_magnet(game_state: GameState, player: GamePlayer):
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
                c.coordinates = [
                    c.coordinates[0] + dx / dist * DISTANCE,
                    c.coordinates[1] + dy / dist * DISTANCE,
                ]


def noop(game_state: GameState, player: GamePlayer):
    """No-op effect."""
    pass


BUFF_APPLY_MAP = {
    BuffType.APPLE_MAGNET: apply_apple_magnet,
}

BUFF_UNAPPLY_MAP = {
    BuffType.APPLE_MAGNET: noop,
}
