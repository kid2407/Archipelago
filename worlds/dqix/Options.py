from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range


class EndBoss(Choice):
    """Determines which Boss needs to be defeated to finish the game"""
    display_name = "Game Goal"
    auto_display_name = True

    option_master_of_nuun = 0
    option_greygnarl = 1
    option_corvus = 2

    default = option_corvus


class FillerAmount(Range):
    """Percentage of the item pool that should contain filler items (Gold and XP)"""
    display_name = "Filler Amount"

    range_start = 0
    range_end = 90
    default = 10


@dataclass
class DQIXOptions(PerGameCommonOptions):
    end_boss: EndBoss
    filler_amount: FillerAmount
