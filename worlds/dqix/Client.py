import json
import logging
from typing import TYPE_CHECKING, Optional

import worlds._bizhawk as bizhawk
from NetUtils import NetworkItem, ClientStatus
from worlds._bizhawk.client import BizHawkClient
from worlds.dqix import Locations
from worlds.dqix.Constants import DQIXConstants
from worlds.dqix.helper.BaseHelper import BaseHelper
from worlds.dqix.helper.BestiaryHelper import BestiaryHelper
from worlds.dqix.helper.InventoryHelper import InventoryHelper

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


class DQIXClient(BizHawkClient):
    base_helper: Optional[BaseHelper]
    game = "Dragon Quest IX"
    system = "NDS"
    last_known_index = None

    def __init__(self):
        self.base_helper = None
        self.current_money = None
        self.visited_locations = []
        self.printed_boss_stats = False
        super().__init__()

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check ROM name/patch version
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x0, 12, "ROM")]))[0]).decode("ascii")
            if rom_name != "DRAGONQUEST9":
                return False
        except bizhawk.RequestFailedError:
            return False  # Not able to get a response, say no for now

        # All good
        ctx.game = self.game
        ctx.want_slot_data = True
        ctx.items_handling = 0b111

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        if ctx.server is None:
            return

        if ctx.slot_data is None:
            return

        try:
            if self.base_helper is None:
                self.base_helper = BaseHelper(ctx)

            if await self.is_ready_and_in_game(ctx):
                await bizhawk.set_message_interval(ctx=ctx.bizhawk_ctx, value=5)

                if self.last_known_index is None:
                    self.last_known_index = await self.base_helper.read_int_from_ram(DQIXConstants.LAST_KNOWN_INDEX, 4)
                    BaseHelper.info("Read last known index from RAM, it is: " + str(self.last_known_index))

                await self.location_check(ctx)
                await self.bestiary_check(ctx)
                await self.received_items_check(ctx)

                BaseHelper.info("Completed one round of location, bestiary and received item checks")

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass

    @staticmethod
    async def is_ready_and_in_game(ctx: "BizHawkClientContext") -> bool:
        base_helper = BaseHelper(ctx=ctx)

        is_in_game = await base_helper.read_int_from_ram(address=DQIXConstants.IN_GAME, size=1) == 0
        is_in_battle = await base_helper.read_int_from_ram(address=DQIXConstants.IN_BATTLE, size=1) == 0
        has_char_name = await base_helper.read_int_from_ram(address=DQIXConstants.HERO_NAME_START, size=1) != 0

        result = is_in_game and has_char_name and not is_in_battle
        if not result:
            BaseHelper.info("game is not ready yet. Current data as follows:")
            BaseHelper.info("-- is_in_game = " + str(is_in_game))
            BaseHelper.info("-- is_in_battle = " + str(is_in_battle))
            BaseHelper.info("-- has_char_name = " + str(has_char_name))
        else:
            BaseHelper.info("Game is currently ready and runs")

        return result

    async def location_check(self, ctx: "BizHawkClientContext"):
        BaseHelper.info("Begin: Checking Locations")
        current_location = int.from_bytes((await bizhawk.read(ctx.bizhawk_ctx, [(DQIXConstants.CURRENT_MAP, 2, "Main RAM")]))[0], "little")
        if current_location not in self.visited_locations:
            await ctx.check_locations([current_location])
        BaseHelper.info("End: Checking Locations")

    async def received_items_check(self, ctx: "BizHawkClientContext"):
        BaseHelper.info("Begin: Checking Received Items")
        network_item: NetworkItem
        inventory_helper = InventoryHelper(ctx=ctx)
        for index, network_item in enumerate(ctx.items_received):
            if self.last_known_index is None or self.last_known_index < index:
                if ctx.slot == network_item.player:
                    display_message = "Found your own \"{0}\"".format(ctx.item_names.lookup_in_game(network_item.item))
                else:
                    display_message = "{0} found your \"{1}\"".format(ctx.player_names[network_item.player], ctx.item_names.lookup_in_game(network_item.item))
                BaseHelper.info("Received item message: " + display_message)
                await bizhawk.display_message(ctx.bizhawk_ctx, display_message)
                await inventory_helper.grant_received_item(item_id=network_item.item)
                self.last_known_index = index
                BaseHelper.info("Updating last known index, it is now " + str(index))
                await self.base_helper.write_int_to_ram(DQIXConstants.LAST_KNOWN_INDEX, 4, index)
                BaseHelper.info("Confirming last known index: " + str(await self.base_helper.read_int_from_ram(DQIXConstants.LAST_KNOWN_INDEX, 4)))
        BaseHelper.info("End: Checking Received Items")

    @staticmethod
    async def bestiary_check(ctx: "BizHawkClientContext"):
        BaseHelper.info("Begin: Checking Bestiary")
        bestiary_helper = BestiaryHelper(ctx=ctx)

        final_boss_data = await bestiary_helper.get_monster_data(BestiaryHelper.BOSSES.get("Corvus (II)"))
        if not ctx.finished_game and final_boss_data.has_defeated_monster():
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
        BaseHelper.info("End: Checking Bestiary")
