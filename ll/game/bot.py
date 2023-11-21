from math import atan2, cos, sin, sqrt
from random import choices

from structlog import get_logger

from .intersect import lines_intersect, normalize_angle
from .player import add_player, kick_player
from .resources.buffs import BuffType
from .resources.consumables import ConsumableType
from .resources.game import GamePlayer, GameState, PlayerStep

logger = get_logger(__name__)

MINIMUM_N_PLAYERS_INCL_BOTS = 4
BOT_NAMES_ADJECTIVES = [
    "DOG FIGHT",
    "YUNG",
    "BIG",
    "LIL'",
    "MUSCLE",
    "SLITHERING",
    "SLICK",
    "PIMP",
    "ULTRA",
    "GOLDEN",
    "SIGMA",
    "SHRIGMA",
    "MAGA",
    "STEEZY",
    "NO-NUTS",
    "SWEATY",
    "FRICKEN",
    "DANK",
    "MR. STEAL YO",
    "DEVILISH",
    "EVIL",
]

BOT_NAMES_NOUNS = [
    "CHOPPA",
    "MULA",
    "ZOOMER",
    "BAG",
    "HUSTLA",
    "MUMMY",
    "DADDY",
    "BOSS",
    "BOSSMAN",
    "CATFISH",
    "GANGSTER",
    "DASCHELT",
    "MIRZAEE",
    "MALE",
    "PEPE",
    "BOZO",
    "MUNTER",
    "ANUK",
]


def _get_bot_name(game_state: GameState):
    """Get a random name."""
    name = f"{choices(BOT_NAMES_ADJECTIVES)[0]} {choices(BOT_NAMES_NOUNS)[0]}"
    while any([p for p in game_state.players if p.name == name]):
        name = _get_bot_name(game_state)

    return name


def spawn_and_boot_bots(game_state: GameState):
    """Create bots."""

    number_bots = len([p for p in game_state.players if p.is_bot])
    number_real_players = len([p for p in game_state.players if not p.is_bot])

    if len(game_state.players) >= MINIMUM_N_PLAYERS_INCL_BOTS:
        # ensure that there are no bots in the game
        required_n_bots = number_real_players - MINIMUM_N_PLAYERS_INCL_BOTS
        bots_to_kick = [p for p in game_state.players if p.is_bot][:required_n_bots]
        for bot in bots_to_kick:
            kick_player(game_state, bot.id)

    if number_real_players < MINIMUM_N_PLAYERS_INCL_BOTS:
        expected_number_bots = MINIMUM_N_PLAYERS_INCL_BOTS - number_real_players
        number_bots_to_spawn = expected_number_bots - number_bots
        for _ in range(number_bots_to_spawn):
            add_player(game_state, _get_bot_name(game_state), True)


def _check_step_collisions_with_players(
    bot: GamePlayer, next_step: PlayerStep, game_state: GameState
):
    """Test player collisions."""
    # Collisions with other players
    if any([b for b in bot.buffs if b.definition.type == BuffType.GHOST]):
        return False

    new_step = (bot.steps[-1].coordinates, next_step.coordinates)
    for other_player in game_state.players:
        for step1, step2 in zip(other_player.steps[:-1], other_player.steps[1:]):
            other_step = (step1.coordinates, step2.coordinates)
            if lines_intersect(*new_step, *other_step):
                return True


def _calculate_next_step(bot: GamePlayer, new_angle: float):
    return PlayerStep(
        coordinates=[
            bot.steps[-1].coordinates[0] + bot.step_length * cos(new_angle),
            bot.steps[-1].coordinates[1] + bot.step_length * sin(new_angle),
        ]
    )


def _lock_angle_to_non_colliding_angle(
    bot: GamePlayer, game_state: GameState, new_angle: float
):
    """Lock the bot's next step angle to a non-colliding angle.

    Try 50 times to find a non-colliding angle. If one is not found, commit to colliding.
    """
    new_step = _calculate_next_step(bot, new_angle)
    # if the bot is not colliding with any other players, return the angle
    if not _check_step_collisions_with_players(bot, new_step, game_state):
        return new_angle

    # if the bot is colliding with another player, adjust the angle
    for _ in range(50):
        new_angle = normalize_angle(new_angle + 0.1)
        new_step = _calculate_next_step(bot, new_angle)
        if not _check_step_collisions_with_players(bot, new_step, game_state):
            return new_angle

    # if the bot is still colliding with another player, commit to colliding
    return new_angle


def choose_bot_step_angles(game_state: GameState):
    """Choose the next steps for all bots."""
    for player in game_state.players:
        if not player.is_bot:
            continue

        # set the next step for the bot

        # find the closest consumable and create a path to it
        closest_consumable = None
        closest_consumable_distance = None
        closest_consumable_angle = None

        for consumable in game_state.consumables:
            # don't target undesirable consumables
            if consumable.type == ConsumableType.POISON:
                continue
            distance = sqrt(
                (player.steps[-1].coordinates[0] - consumable.coordinates[0]) ** 2
                + (player.steps[-1].coordinates[1] - consumable.coordinates[1]) ** 2
            )

            # if the consumable is under a STEP_LENGTH away (and we can't hit it), ignore it
            if (distance + consumable.size) < player.step_length:
                continue

            if not closest_consumable or distance < closest_consumable_distance:
                closest_consumable = consumable
                closest_consumable_distance = distance
                closest_consumable_angle = atan2(
                    consumable.coordinates[1] - player.steps[-1].coordinates[1],
                    consumable.coordinates[0] - player.steps[-1].coordinates[0],
                )

        new_angle = closest_consumable_angle or 0.0
        previous_step_angle = player.angle
        normalized_angle = normalize_angle(new_angle - previous_step_angle)

        if normalized_angle > player.step_fov:
            new_angle = previous_step_angle + player.step_fov
        elif normalized_angle < -player.step_fov:
            new_angle = previous_step_angle - player.step_fov

        new_angle = _lock_angle_to_non_colliding_angle(player, game_state, new_angle)

        player.angle = new_angle
