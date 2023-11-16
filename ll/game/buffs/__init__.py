from ..resources.buffs import BuffApplicationFrequency, BuffApplicationTime
from .effects import BUFF_APPLY_MAP, BUFF_UNAPPLY_MAP


def decay_buffs(game_state, application_time: BuffApplicationTime):
    """Decay buffs."""

    for player in game_state.players:
        for buff in player.buffs:
            if buff.definition.application_time != application_time:
                continue

            buff.duration_remaining -= 1

            # unapply buff if duration is over
            if buff.duration_remaining < 0:
                BUFF_UNAPPLY_MAP[buff.type](game_state, player)
        player.buffs = [b for b in player.buffs if b.duration_remaining >= 0]

    for buff in game_state.global_buffs:
        if buff.definition.application_time != application_time:
            continue

        buff.duration_remaining -= 1

        # unapply buff if duration is over
        if buff.duration_remaining < 0:
            BUFF_UNAPPLY_MAP[buff.type](game_state, None)

    # remove expired buffs
    game_state.global_buffs = [
        b for b in game_state.global_buffs if b.duration_remaining >= 0
    ]


def apply_and_decay_buffs(game_state, application_time: BuffApplicationTime):
    """Apply and decay buffs."""

    decay_buffs(game_state, application_time)

    for player in game_state.players:
        for buff in player.buffs:
            if (
                buff.definition.application_frequency == BuffApplicationFrequency.ONCE
                and buff.is_applied
            ):
                continue
            if buff.definition.application_time == application_time:
                BUFF_APPLY_MAP[buff.type](game_state, player)
                buff.is_applied = True

    for buff in game_state.global_buffs:
        if (
            buff.definition.application_frequency == BuffApplicationFrequency.ONCE
            and buff.is_applied
        ):
            continue
        if buff.definition.application_time == application_time:
            BUFF_APPLY_MAP[buff.type](game_state, None)
            buff.is_applied = True
