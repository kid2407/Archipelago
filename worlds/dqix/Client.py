import logging
from typing import TYPE_CHECKING

import worlds._bizhawk as bizhawk
from NetUtils import NetworkItem
from worlds._bizhawk.client import BizHawkClient
from worlds.dqix.helper.InventoryHelper import InventoryHelper

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


class DQIXClient(BizHawkClient):
    game = "Dragon Quest IX"
    system = "NDS"
    last_known_index = None

    def __init__(self):
        self.current_money = None
        super().__init__()

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check ROM name/patch version
            rom_name = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x0, 12, "ROM")]))[0]).decode("ascii")
            if rom_name != "DRAGONQUEST9":
                return False  # Not a MYGAME ROM
        except bizhawk.RequestFailedError:
            return False  # Not able to get a response, say no for now

        # This is a MYGAME ROM
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
            await self.location_check(ctx)
            await self.bestiary_check(ctx)
            await self.received_items_check(ctx)

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass

    async def location_check(self, ctx: "BizHawkClientContext"):
        money_value = int.from_bytes((await bizhawk.read(ctx=ctx.bizhawk_ctx, read_list=[(0x0F6D48, 4, "Main RAM")]))[0], "little")
        if money_value != self.current_money:
            logging.info("Money on Hand has changed to: " + str(money_value))
            self.current_money = money_value

    async def received_items_check(self, ctx: "BizHawkClientContext"):
        network_item: NetworkItem
        for index, network_item in enumerate(ctx.items_received):
            if self.last_known_index is None or self.last_known_index < index:
                self.last_known_index = index
                logging.info("Received Item: {0} from Player = {1}".format(network_item.item, network_item.player))
                await bizhawk.set_message_interval(ctx=ctx.bizhawk_ctx, value=5)
                await bizhawk.display_message(ctx.bizhawk_ctx, f"Received Item with ID {network_item.item}")
                inventory_helper = InventoryHelper(ctx=ctx)
                await inventory_helper.grant_received_item(item_id=network_item.item)
                # TODO save the last item index in a save file or save state

    async def bestiary_check(self, ctx: "BizHawkClientContext"):
        pass  # TODO implement
