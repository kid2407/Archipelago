from typing import TYPE_CHECKING, Optional, List

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
        self.boss_list_updated = False
        self.forbidden_monsters = BestiaryHelper.STARTING_FORBIDDEN_MONSTERS
        self.syncing = False
        self.base_helper: Optional[BaseHelper] = None
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
        inventory_helper = InventoryHelper(ctx=ctx,dqix_client=self)
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
        if not self.boss_list_updated:
            self.update_boss_list(ctx.items_received)
            self.boss_list_updated = True

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
        current_monster = await self.base_helper.read_int_from_ram(DQIXConstants.CURRENT_MONSTER, 2)

        if current_monster in self.forbidden_monsters:
            BaseHelper.debug("Punishing for fighting monster with ID = " + str(current_monster))
            for char_hp_address in [DQIXConstants.CHAR_1_BATTLE_HP, DQIXConstants.CHAR_2_BATTLE_HP, DQIXConstants.CHAR_3_BATTLE_HP, DQIXConstants.CHAR_4_BATTLE_HP]:
                char_hp = await self.base_helper.read_int_from_ram(char_hp_address, 2)
                if char_hp > 1:
                    await self.base_helper.write_int_to_ram(char_hp_address, 2, 1)
                    await self.base_helper.write_int_to_ram(char_hp_address + 2, 2, 1)

            for char_mp_address in [DQIXConstants.CHAR_1_BATTLE_MP, DQIXConstants.CHAR_2_BATTLE_MP, DQIXConstants.CHAR_3_BATTLE_MP, DQIXConstants.CHAR_4_BATTLE_MP]:
                char_mp = await self.base_helper.read_int_from_ram(char_mp_address, 2)
                if char_mp > 0:
                    await self.base_helper.write_int_to_ram(char_mp_address, 2, 0)
                    await self.base_helper.write_int_to_ram(char_mp_address + 2, 2, 0)

            for char_status_address in [DQIXConstants.CHAR_1_BATTLE_STATUS, DQIXConstants.CHAR_2_BATTLE_STATUS, DQIXConstants.CHAR_3_BATTLE_STATUS, DQIXConstants.CHAR_4_BATTLE_STATUS]:
                await self.base_helper.write_int_to_ram(char_status_address, 1, 2)

    def update_boss_list(self, items_received: List[NetworkItem]):
        for _, network_item in enumerate(items_received):
            if 50000 <= network_item.item <= 50022:
                monster_id = BestiaryHelper.BOSS_KEYS_TO_MONSTER_ID[network_item.item]
                self.base_helper.debug("Removing Boss with monster ID: " + str(monster_id))
                self.forbidden_monsters.remove(monster_id)
