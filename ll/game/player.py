import math
import uuid
from random import choices, randint

from structlog import get_logger

from .intersect import lines_intersect, point_inside_circle
from .resources.buffs import BuffType
from .resources.consumables import ConsumableType
from .resources.game import (
    MAP_SIZE,
    MINIMUM_STEP_LENGTH,
    GamePlayer,
    GameState,
    PlayerStep,
)

logger = get_logger(__name__)


def _reset_player(player: GamePlayer):
    """Reset a player to its initial state."""
    player.steps = [
        PlayerStep(
            coordinates=[
                float(randint(-MAP_SIZE, MAP_SIZE)),
                float(randint(-MAP_SIZE, MAP_SIZE)),
            ]
        )
    ]
    player.step_length = MINIMUM_STEP_LENGTH
    player.angle = 0.0
    player.spawned = False


def _check_collisions_with_players(player: GamePlayer, game_state: GameState):
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


def _check_in_map_bounds(player: GamePlayer, game_state: GameState):
    """Test if the player is in the map bounds."""

    if len(player.steps) < 2:
        return

    b = game_state.map_bounds
    bounds = [
        [(b[0][0], b[0][1]), (b[0][0], b[1][1])],
        [(b[1][0], b[0][1]), (b[1][0], b[1][1])],
        [(b[0][0], b[1][1]), (b[1][0], b[1][1])],
        [(b[0][0], b[0][1]), (b[1][0], b[0][1])],
    ]

    for bound in bounds:
        if lines_intersect(
            *bound,
            player.steps[-2].coordinates,
            player.steps[-1].coordinates,
        ):
            logger.info("player out of bounds", player_name=player.name)
            _reset_player(player)
            return


def _take_step(player: GamePlayer, game_state: GameState):
    x, y = player.steps[-1].coordinates
    dx = math.cos(player.angle) * player.step_length
    dy = math.sin(player.angle) * player.step_length
    player.steps.append(PlayerStep(coordinates=[x + dx, y + dy]))

    # Limit number of segments
    max_steps = int(player.step_length**0.3 + 7)
    player.steps = player.steps[-max_steps:]

    # Decay step length
    player.step_length = max(player.step_length - 0.2, MINIMUM_STEP_LENGTH)

    # Test collisions
    _check_collisions_with_players(player, game_state)
    _check_consumable_collisions(player, game_state)
    _check_in_map_bounds(player, game_state)


def take_player_steps(game_state: GameState):
    """Take a step for each player."""
    for player in game_state.players:
        _take_step(player, game_state)


COLOR_PALETTE = [
    [170, 68, 101],
    [202, 137, 95],
    [85, 111, 68],
    [8, 76, 97],
    [209, 122, 34],
    [67, 87, 173],
    [148, 168, 154],
    [109, 159, 113],
    [87, 61, 28],
]


def _get_unassigned_color(game_state: GameState):
    """Get an unassigned color."""
    assigned_colors = [p.color for p in game_state.players]
    available_colors = [c for c in COLOR_PALETTE if c not in assigned_colors]
    color = choices(available_colors)[0]
    return color


def add_player(game_state: GameState, name: str, is_bot: bool) -> str:
    """Create a player.

    Returns the player id.
    """
    # check if the player already exists (lookup by name)
    player = next(
        (p for p in game_state.players if p.name == name),
        None,
    )
    if player:
        raise ValueError("Name already taken")

    player = GamePlayer(
        id=str(uuid.uuid4()),
        name=name,
        color=_get_unassigned_color(game_state),
        step_length=MINIMUM_STEP_LENGTH,
        spawned=False,
        steps=[
            PlayerStep(
                coordinates=[
                    float(randint(-MAP_SIZE, MAP_SIZE)),
                    float(randint(-MAP_SIZE, MAP_SIZE)),
                ]
            )
        ],
        step_fov=math.pi * 0.875,
        is_bot=is_bot,
        buffs=[],
    )
    game_state.players.append(player)
    logger.info("added player", player_id=player.id)
    return player.id


def kick_player(game_state: GameState, player_id: str):
    """Remove a player."""
    player = next(
        (p for p in game_state.players if p.id == player_id),
        None,
    )
    if player:
        game_state.players.remove(player)
        logger.info("removed player", player_name=player.name, is_bot=player.is_bot)
    else:
        logger.info("player not found", player_name=player.name)
