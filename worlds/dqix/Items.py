import json
import pkgutil
from enum import Enum
from typing import Dict, NamedTuple, Optional, List

from BaseClasses import ItemClassification, Item
from Options import OptionError
from .Options import DQIXOptions, EndBoss


class DQIXItem(Item):
    game = "Dragon Quest IX"
    item_type: str

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int, item_type: str):
        super(DQIXItem, self).__init__(name, classification, code, player)
        self.item_type = item_type


class ItemType(Enum):
    COMMON_ITEM = "common"
    EQUIPMENT = "equipment"
    EXPERIENCE = "exp"
    GOLD = "gold"
    IMPORTANT_ITEM = "important"
    BOSS_KEY = "boss"


class ItemData(NamedTuple):
    name: str
    code: int
    item_type: ItemType
    classification: ItemClassification


class DQIXItems:
    _item_table: Dict[str, ItemData] = {}

    IMPORTANT_ITEM_IDS = [22042, 22043, 22044, 22158, 22159, 22160, 22162, 22164, 22165, 22166, 22167, 22168, 22169]

    def _parse_item_data(self):
        file = pkgutil.get_data(__name__, "data/items.json").decode("utf-8")
        loaded_items = json.loads(file)

        self.progression_items = {name: ItemData(name, item_data["code"], ItemType(item_data["item_type"]), ItemClassification.progression) for name, item_data in loaded_items["progression"].items()}
        self.useful_items = {name: ItemData(name, item_data["code"], ItemType(item_data["item_type"]), ItemClassification.useful) for name, item_data in loaded_items["useful"].items()}
        self.filler_items = {name: ItemData(name, item_data["code"], ItemType(item_data["item_type"]), ItemClassification.filler) for name, item_data in loaded_items["filler"].items()}

        final_item_table = {}
        final_item_table.update(self.progression_items)
        final_item_table.update(self.useful_items)
        final_item_table.update(self.filler_items)

        self._item_table = final_item_table

    def _get_item_table(self):
        if not self._item_table:
            self._parse_item_data()
        return self._item_table

    def get_items(self) -> Dict[str, int]:
        return {name: item.code for name, item in self._get_item_table().items()}

    def get_item_type(self, name: str):
        return self._get_item_table()[name].item_type

    def is_progression(self, name: str) -> bool:
        return name in self.progression_items

    def is_useful(self, name: str) -> bool:
        return name in self.useful_items

    def get_filler_item_names(self):
        return list(self.filler_items.keys())

    def filter_progression_items(self, item_names: List[str], options: DQIXOptions):
        prog_items = []
        allowed_boss_keys = self.get_allowed_boss_keys(options)

        for item_name in item_names:
            item_type = self.get_item_type(item_name)

            if item_type == ItemType.IMPORTANT_ITEM:
                prog_items.append(item_name)
            elif self.get_item_type(item_name) == ItemType.BOSS_KEY and item_name in allowed_boss_keys:
                prog_items.append(item_name)

        return prog_items

    @staticmethod
    def get_allowed_boss_keys(options: DQIXOptions) -> List[str]:
        if options.end_boss == EndBoss.option_master_of_nuun:
            bosses = ["Hexagoon", "Wight Knight", "Morag", "Ragin' Contagion", "Master of Nu'un"]
        elif options.end_boss == EndBoss.option_greygnarl:
            bosses = ["Hexagoon", "Wight Knight", "Morag", "Ragin' Contagion", "Master of Nu'un", "Lleviathan", "Garth Goyle", "Tyrantula", "Grand Lizzier", "Larstastnaras", "Dreadmaster", "Gadrongo", "Greygnarl"]
        elif options.end_boss == EndBoss.option_corvus:
            bosses = ["Hexagoon", "Wight Knight", "Morag", "Ragin' Contagion", "Master of Nu'un", "Lleviathan", "Garth Goyle", "Tyrantula", "Grand Lizzier", "Larstastnaras", "Dreadmaster", "Gadrongo", "Greygnarl", "Goreham-Hogg (I)",
                      "Hootingham-Gore (I)", "Goresby-Purrvis (I)", "King Godwyn", "Goreham-Hogg (II)", "Hootingham-Gore (II)", "Goresby-Purrvis (II)", "Corvus (I)", "Barbarus", "Corvus (II)"]
        else:
            raise OptionError("Could not determine required Boss Keys: Invalid Option for \"end_boss\": " + options.end_boss)

        return [f"Boss Key: {boss_name}" for boss_name in bosses]
