import math
from random import randint

from structlog import get_logger

from .intersect import lines_intersect, point_inside_circle
from .resources.buffs import BuffType
from .resources.consumables import ConsumableType
from .resources.game import MINIMUM_STEP_LENGTH, GamePlayer, GameState, PlayerStep

logger = get_logger(__name__)


def _reset_player(player: GamePlayer):
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


def _check_player_collisions(player: GamePlayer, game_state: GameState):
    """Test player collisions."""
    # Collisions with other players
    if any([b for b in player.buffs if b.definition.type == BuffType.GHOST]):
        return

    if len(player.steps) >= 3:
        last_step = (player.steps[-2].coordinates, player.steps[-1].coordinates)

        for other_player in game_state.players:
            for step1, step2 in zip(other_player.steps[:-1], other_player.steps[1:]):
                other_step = (step1.coordinates, step2.coordinates)
                if other_player.id == player.id and other_step == last_step:
                    continue

                if lines_intersect(*last_step, *other_step):
                    logger.info(
                        "player collision",
                        player_name=player.name,
                        other_player_name=other_player.name,
                    )
                    _reset_player(player)
                    return


def _check_consumable_collisions(player: GamePlayer, game_state: GameState):
    """Test consumable collisions.

    Consumables are removed from the game state if they are consumed.

    Any new buffs that are applied to the player are added to the player's buffs list.
    """

    for consumable in game_state.consumables:
        if point_inside_circle(
            player.steps[-1].coordinates, consumable.coordinates, consumable.size
        ):
            if consumable.definition.type in [
                ConsumableType.POISON,
                ConsumableType.APPLE,
            ]:
                consumable_size_multiplier = (
                    consumable.size / consumable.definition.size
                )
                player.step_length += (
                    consumable.definition.size_effect_multiplier(
                        consumable_size_multiplier
                    )
                    * consumable.definition.player_size_diff
                )
                player.step_length = max(player.step_length, 50)

            buff = consumable.buff
            if buff:
                definition = buff.definition
                if definition.applies_globally:
                    game_state.global_buffs.append(buff)
                else:
                    player.buffs.append(buff)

            game_state.consumables.remove(consumable)


def _take_step(player: GamePlayer, game_state: GameState):
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
    _check_player_collisions(player, game_state)
    _check_consumable_collisions(player, game_state)


def take_player_steps(game_state: GameState):
    """Take a step for each player."""
    for player in game_state.players:
        _take_step(player, game_state)
