import logging
from typing import TYPE_CHECKING, List
# noinspection PyProtectedMember
import worlds._bizhawk as bizhawk

if TYPE_CHECKING:
    # noinspection PyProtectedMember
    from worlds._bizhawk.context import BizHawkClientContext


class BaseHelper:
    def __init__(self, ctx: "BizHawkClientContext"):
        self.ctx = ctx

    async def read_int_from_ram(self, address: int | str, size: int):
        address = int(address, 16) if isinstance(address, str) else address
        return int.from_bytes((await bizhawk.read(ctx=self.ctx.bizhawk_ctx, read_list=[(address, size, "Main RAM")]))[0], "little")

    async def read_ints_from_ram(self, addresses: List[int | str], size: int) -> List[int]:
        data = await bizhawk.read(ctx=self.ctx.bizhawk_ctx, read_list=[(int(address, 16) if isinstance(address, str) else address, size, "Main RAM") for address in addresses])
        return [int.from_bytes(found_bytes, "little") for found_bytes in data]

    async def write_int_to_ram(self, address: int | str, size: int, value: int):
        address = int(address, 16) if isinstance(address, str) else address
        await bizhawk.write(ctx=self.ctx.bizhawk_ctx, write_list=[(address, int.to_bytes(value, size, "little"), "Main RAM")])

    async def read_segments_as_ints_from_ram(self, address: int | str, segment_count: int, segment_size: int = 1):
        address = int(address, 16) if isinstance(address, str) else address
        read_bytes = (await bizhawk.read(ctx=self.ctx.bizhawk_ctx, read_list=[(address, segment_size * segment_count, "Main RAM")]))[0]
        return [int.from_bytes(read_bytes[segment * segment_size:(segment * segment_size + segment_size)], "little") for segment in range(segment_count)]

    @staticmethod
    def info(msg: str, *args):
        logging.info("[DQIX] " + msg, *args)

    @staticmethod
    def warning(msg: str, *args):
        logging.warning("[DQIX] " + msg, *args)
