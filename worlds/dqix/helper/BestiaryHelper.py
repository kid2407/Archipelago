from typing import TYPE_CHECKING

from worlds.dqix.Constants import DQIXConstants
from worlds.dqix.helper.BaseHelper import BaseHelper

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


class BeastiaryEntry:
    def __init__(self, defeated_count: int, eye_for_trouble: bool, normal_drop_count: int, rare_drop_count: int):
        self.defeated_count = defeated_count
        self.eye_for_trouble = eye_for_trouble
        self.normal_drop_count = normal_drop_count
        self.rare_drop_count = rare_drop_count

    def has_defeated_monster(self) -> bool:
        return self.defeated_count > 0

    def to_json(self):
        return {
            "defeated_count": self.defeated_count,
            "eye_for_trouble": self.eye_for_trouble,
            "normal_drop_count": self.normal_drop_count,
            "rare_drop_count": self.rare_drop_count
        }


class BestiaryHelper(BaseHelper):
    BOSSES = {
        "Hexagoon": 257,
        "Wight Knight": 258,
        "Morag": 259,
        "Ragin' Contagion": 260,
        "Master of Nu'un": 261,
        "Lleviathan": 262,
        "Garth Goyle": 263,
        "Tyrantula": 264,
        "Grand Lizzier": 265,
        "Larstastnaras": 266,
        "Dreadmaster": 267,
        "Gadrongo": 268,
        "Greygnarl": 269,
        "Goreham-Hogg": 270,
        "Hootingham-Gore": 271,
        "Goresby-Purrvis": 272,
        "King Godwyn": 274,
        "Corvus (I)": 276,
        "Barbarus": 275,
        "Corvus (II)": 277,
    }

    def __init__(self, ctx: "BizHawkClientContext"):
        super().__init__(ctx)

    async def get_monster_data(self, monster_id: int) -> BeastiaryEntry:
        if monster_id < 1 or monster_id > 307:
            raise IndexError("Tried to get data for invalid monster_id = {0}".format(monster_id))
        target_index = monster_id - 1
        target_address = DQIXConstants.BESTIARY_START_OFFSET + target_index * 4

        data = await self.read_int_from_ram(address=target_address, size=4)

        bin_str = '{:032b}'.format(data)

        defeated_count = int(bin_str[22:32], 2)  # 10 bits, max 999
        eye_for_trouble = int(bin_str[21:22], 2)  # 1 bit, max 1
        normal_drop_count = int(bin_str[7:14], 2)  # 7 bits, max 99
        rare_drop_count = int(bin_str[14:21], 2)  # 7 bits, max 99

        return BeastiaryEntry(defeated_count, bool(eye_for_trouble), normal_drop_count, rare_drop_count)
