import logging
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


class BestiaryHelper(BaseHelper):
    def __init__(self, ctx: "BizHawkClientContext"):
        super().__init__(ctx)

    async def get_monster_data(self, monster_id: int) -> BeastiaryEntry:
        if monster_id < 1 or monster_id > 307:
            raise IndexError("Tried to get data for invalid monster_id = {0}".format(monster_id))
        target_index = monster_id - 1
        target_address = DQIXConstants.BESTIARY_START_OFFSET + target_index * 4

        data = await self.read_int_from_ram(address=target_address, size=4)
        logging.warning("Got data for monster with id = {0}}: {1}".format(monster_id, hex(data)))

        bin_str = '{:032b}'.format(data)

        # TODO check if it is actually the correct way around
        defeated_count = int(bin_str[22:32], 2)  # 10 bits, max 999
        eye_for_trouble = int(bin_str[21:22], 2)  # 1 bit, max 1
        normal_drop_count = int(bin_str[7:14], 2)  # 7 bits, max 99
        rare_drop_count = int(bin_str[14:21], 2)  # 7 bits, max 99

        return BeastiaryEntry(defeated_count, bool(eye_for_trouble), normal_drop_count, rare_drop_count)
