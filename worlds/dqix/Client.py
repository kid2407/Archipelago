from typing import TYPE_CHECKING, Optional

import worlds._bizhawk as bizhawk
from NetUtils import NetworkItem, ClientStatus
from worlds._bizhawk.client import BizHawkClient
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
    next_expected_item_index = None

    def __init__(self):
        self.syncing = False
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

            if await self.is_ready_and_in_game():
                await bizhawk.set_message_interval(ctx=ctx.bizhawk_ctx, value=5)

                if self.next_expected_item_index is None:
                    self.next_expected_item_index = await self.base_helper.read_int_from_ram(DQIXConstants.NEXT_EXPECTED_INDEX, 4)
                    BaseHelper.info("Read next expected index from RAM, it is: " + str(self.next_expected_item_index))

                if self.syncing:
                    sync_msg = [{'cmd': 'Sync'}]
                    if ctx.locations_checked:
                        sync_msg.append({"cmd": "LocationChecks", "locations": list(ctx.locations_checked)})
                    await ctx.send_msgs(sync_msg)
                    self.syncing = False

                await self.location_check(ctx)
                await self.bestiary_check(ctx)
                await self.received_items_check(ctx)

                BaseHelper.debug("Completed one round of location, bestiary and received item checks")

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass

    async def is_ready_and_in_game(self) -> bool:
        is_in_game = await self.base_helper.read_int_from_ram(address=DQIXConstants.IN_GAME, size=1) == 0
        is_in_battle = await self.base_helper.read_int_from_ram(address=DQIXConstants.IN_BATTLE, size=1) == 0
        has_char_name = await self.base_helper.read_int_from_ram(address=DQIXConstants.HERO_NAME_START, size=1) != 0

        result = is_in_game and has_char_name and not is_in_battle
        if not result:
            BaseHelper.debug("game is not ready yet. Current data as follows:")
            BaseHelper.debug("-- is_in_game = " + str(is_in_game))
            BaseHelper.debug("-- is_in_battle = " + str(is_in_battle))
            BaseHelper.debug("-- has_char_name = " + str(has_char_name))

            if is_in_game and has_char_name and is_in_battle:
                await self.punish_player()
        else:
            BaseHelper.debug("Game is currently ready and runs")

        return result

    async def location_check(self, ctx: "BizHawkClientContext"):
        BaseHelper.debug("Begin: Checking Locations")
        current_location = await self.base_helper.read_int_from_ram(address=DQIXConstants.CURRENT_MAP, size=2)
        if current_location not in self.visited_locations:
            await ctx.check_locations([current_location])
        BaseHelper.debug("End: Checking Locations")

    async def received_items_check(self, ctx: "BizHawkClientContext"):
        BaseHelper.debug("Begin: Checking Received Items")
        network_item: NetworkItem
        inventory_helper = InventoryHelper(ctx=ctx)
        for index, network_item in enumerate(ctx.items_received):
            if index == self.next_expected_item_index:
                if ctx.slot == network_item.player:
                    display_message = "Found your own \"{0}\"".format(ctx.item_names.lookup_in_game(network_item.item))
                else:
                    display_message = "{0} found your \"{1}\"".format(ctx.player_names[network_item.player], ctx.item_names.lookup_in_game(network_item.item))
                BaseHelper.debug("Received item message: " + display_message)
                await bizhawk.display_message(ctx.bizhawk_ctx, display_message)
                await inventory_helper.grant_received_item(item_id=network_item.item)
                self.next_expected_item_index = index + 1
                BaseHelper.debug("Updating last known index, it is now " + str(index))
                await self.base_helper.write_int_to_ram(DQIXConstants.NEXT_EXPECTED_INDEX, 4, self.next_expected_item_index)
            elif index > self.next_expected_item_index:
                self.syncing = True
        BaseHelper.debug("End: Checking Received Items")

    @staticmethod
    async def bestiary_check(ctx: "BizHawkClientContext"):
        BaseHelper.debug("Begin: Checking Bestiary")
        bestiary_helper = BestiaryHelper(ctx=ctx)

        final_boss_data = await bestiary_helper.get_monster_data(BestiaryHelper.BOSSES.get("Corvus (II)"))
        if not ctx.finished_game and final_boss_data.has_defeated_monster():
            await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            ctx.finished_game = True
        BaseHelper.debug("End: Checking Bestiary")

    async def punish_player(self):
        BaseHelper.debug("Punishing!!!!!!!!!!!!!!!")

        char_1_hp = await self.base_helper.read_int_from_ram(DQIXConstants.CHAR_1_BATTLE_HP, 2)
        char_2_hp = await self.base_helper.read_int_from_ram(DQIXConstants.CHAR_2_BATTLE_HP, 2)
        char_3_hp = await self.base_helper.read_int_from_ram(DQIXConstants.CHAR_3_BATTLE_HP, 2)
        char_4_hp = await self.base_helper.read_int_from_ram(DQIXConstants.CHAR_4_BATTLE_HP, 2)

        if char_1_hp > 1:
            await self.base_helper.write_int_to_ram(DQIXConstants.CHAR_1_BATTLE_HP, 2, 1)

        if char_2_hp > 1:
            await self.base_helper.write_int_to_ram(DQIXConstants.CHAR_2_BATTLE_HP, 2, 1)

        if char_3_hp > 1:
            await self.base_helper.write_int_to_ram(DQIXConstants.CHAR_3_BATTLE_HP, 2, 1)

        if char_4_hp > 1:
            await self.base_helper.write_int_to_ram(DQIXConstants.CHAR_4_BATTLE_HP, 2, 1)
