import math
from random import randint

from ll.api.game.resources import (
    MINIMUM_STEP_LENGTH,
    ConsumableType,
    GamePlayer,
    GameState,
    PlayerStep,
)

from .intersect import lines_intersect, point_inside_circle

CONSUMABLE_TYPE_TO_DIFF = {
    ConsumableType.APPLE: 20,
    ConsumableType.POISON: -20,
}


def reset_player(player: GamePlayer):
    """Reset a player to its initial state."""
    player.steps = [
        PlayerStep(
            coordinates=[
                float(randint(-1000, 1000)),
                float(randint(-1000, 1000)),
            ]
        )
    ]
    player.step_length = MINIMUM_STEP_LENGTH
    player.angle = 0.0
    player.spawned = False


def test_player_collisions(player: GamePlayer, game_state: GameState):
    """Test player collisions."""
    # Collisions with other players
    if len(player.steps) >= 3:
        last_step = (player.steps[-2].coordinates, player.steps[-1].coordinates)

        for other_player in game_state.players:
            for step1, step2 in zip(other_player.steps[:-1], other_player.steps[1:]):
                other_step = (step1.coordinates, step2.coordinates)
                if other_player.id == player.id and other_step == last_step:
                    continue

                if lines_intersect(*last_step, *other_step):
                    reset_player(player)
                    return


def test_consumable_collisions(player: GamePlayer, game_state: GameState):
    """Test consumable collisions."""
    # Collisions with consumables
    for consumable in game_state.consumables:
        if point_inside_circle(
            player.steps[-1].coordinates, consumable.coordinates, consumable.size
        ):
            player.step_length += CONSUMABLE_TYPE_TO_DIFF[consumable.type]
            player.step_length = max(player.step_length, 50)
            game_state.consumables.remove(consumable)


def take_step(player: GamePlayer, game_state: GameState):
    x, y = player.steps[-1].coordinates
    dx = math.cos(player.angle) * player.step_length
    dy = math.sin(player.angle) * player.step_length
    player.steps.append(PlayerStep(coordinates=[x + dx, y + dy]))

    # Limit number of segments
    max_steps = int(player.step_length**0.6)
    player.steps = player.steps[-max_steps:]

    # Decay step length
    player.step_length = max(player.step_length * 0.995, MINIMUM_STEP_LENGTH)

    # Test collisions
    test_player_collisions(player, game_state)
    test_consumable_collisions(player, game_state)
