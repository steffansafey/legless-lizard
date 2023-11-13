from typing import Optional

from ..resources import GameState
from .effects import BUFF_APPLY_MAP, BUFF_UNAPPLY_MAP
from .resources import (
    BUFF_DEFINITIONS,
    CONSUMABLE_TO_BUFF_MAP,
    Buff,
    BuffApplicationFrequency,
    BuffApplicationTime,
    ConsumableType,
)


def get_buff_for_consumable(consumable_type: ConsumableType) -> Optional[Buff]:
    """Create a buff from a type."""

    buff_definition = CONSUMABLE_TO_BUFF_MAP.get(consumable_type, None)

    if not buff_definition:
        return None

    return Buff(
        type=buff_definition.type,
        is_debuff=buff_definition.is_debuff,
        duration_remaining=buff_definition.default_duration,
        is_applied=False,
    )


def decay_buffs(game_state: GameState, application_time: BuffApplicationTime):
    """Decay buffs."""

    for player in game_state.players:
        for buff in player.buffs:
            buff_definition = BUFF_DEFINITIONS[buff.type]
            if buff_definition.application_time != application_time:
                continue

            buff.duration_remaining -= 1

            # unapply buff if duration is over
            if buff.duration_remaining <= 0:
                BUFF_UNAPPLY_MAP[buff.type](game_state, player)

        player.buffs = [b for b in player.buffs if b.duration_remaining > 0]


def apply_and_decay_buffs(game_state: GameState, application_time: BuffApplicationTime):
    """Apply and decay buffs."""
    for player in game_state.players:
        for buff in player.buffs:
            buff_definition = BUFF_DEFINITIONS[buff.type]
            if (
                buff_definition.application_frequency == BuffApplicationFrequency.ONCE
                and buff.is_applied
            ):
                continue
            if buff_definition.application_time == application_time:
                BUFF_APPLY_MAP[buff.type](game_state, player)

    decay_buffs(game_state, application_time)
