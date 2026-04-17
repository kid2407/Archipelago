from BaseClasses import Tutorial, ItemClassification, Region
from Utils import visualize_regions
from rule_builder.rules import Has, HasAll, Rule, HasAny
from .Client import DQIXClient
from .Items import DQIXItems, ItemType, DQIXItem
from .Locations import DQIXLocations, DQIXLocation
from .helper.BaseHelper import BaseHelper
from ..AutoWorld import World, WebWorld


class DragonQuestIXWeb(WebWorld):
    game_info_languages = ["en"]
    theme = "ocean"
    setup_en = Tutorial(
        tutorial_name="Setup the Game",
        description="This shows you how to setup DQIX properly",
        language="en",
        file_name="setup_en.md",
        link="setup/en",
        authors=["kid2407"]
    )

    tutorials = [setup_en]


class DragonQuestIX(World):
    game = "Dragon Quest IX"
    required_client_version = (0, 6, 3)
    origin_region_name = "Angel Falls"
    web = DragonQuestIXWeb()

    location_helper = DQIXLocations()
    item_helper = DQIXItems()

    location_name_to_id = location_helper.get_locations()
    item_name_to_id = item_helper.get_items()

    def create_item(self, name: str) -> "DQIXItem":
        return DQIXItem(name,
                        ItemClassification.progression if self.item_helper.is_progression(name) else ItemClassification.useful if self.item_helper.is_useful(name) else ItemClassification.filler,
                        self.item_name_to_id[name],
                        self.player,
                        self.item_helper.get_item_type(name)
                        )

    def create_items(self) -> None:
        # Generate / Load all progression items
        progression_item_names = {k for k in self.item_name_to_id.keys() if self.item_helper.is_progression(k)}
        items = [self.create_item(name) for name in progression_item_names]

        # Fill up to 90% of the remaining item slots with useful items
        remaining_count_until_almost_full = (round(len(self.location_name_to_id) * 0.9) - len(items))
        items += [self.create_item(useful_item) for useful_item in self.random.choices(population=list(self.item_helper.useful_items.keys()), k=remaining_count_until_almost_full)]

        # remaining 10% are filler, money and gold
        items += [self.create_item(self.get_filler_item_name()) for _ in range(len(self.location_name_to_id) - len(items))]

        self.multiworld.itempool += items

    def create_regions(self) -> None:
        regions = self.create_and_connect_regions()
        for region in regions:
            self.multiworld.regions.append(region)

        self.apply_special_rules()

        # Goal condition
        self.set_completion_rule(self.get_completion_condition())

        if BaseHelper.DEBUG_MODE:
            state = self.multiworld.get_all_state(use_cache=False, allow_partial_entrances=True)
            state.update_reachable_regions(self.player)
            visualize_regions(root_region=self.multiworld.get_region(self.origin_region_name, self.player), file_name="my_world.puml", show_entrance_names=True,
                              regions_to_highlight=set(state.reachable_regions[self.player]))

    def create_region_with_locations(self, region_name: str):
        region = Region(region_name, self.player, self.multiworld)
        region.add_locations(locations=self.location_helper.get_locations_for_group(region_name), location_type=DQIXLocation)
        return region

    def create_and_connect_regions(self):
        region_angel_falls = self.create_region_with_locations(region_name="Angel Falls")
        region_hexagon = self.create_region_with_locations(region_name="Hexagon")
        region_hexagon.add_event(location_name="Boss: Hexagon", item_name="Defeated Hexagoon", rule=Has("Boss Key: Hexagoon"))

        region_stornway = self.create_region_with_locations(region_name="Stornway")
        region_stornway.add_event(location_name="Boss: Wight Knight", item_name="Defeated Wight Knight", rule=Has("Boss Key: Wight Knight"))

        region_zere = self.create_region_with_locations(region_name="Zere")
        region_brigadoom = self.create_region_with_locations(region_name="Brigadoom")
        region_brigadoom.add_event(location_name="Boss: Morag", item_name="Defeated Morag", rule=Has("Boss Key: Morag"))

        region_coffinwell = self.create_region_with_locations(region_name="Coffinwell")
        region_quarantomb = self.create_region_with_locations(region_name="Quarantomb")
        region_quarantomb.add_event(location_name="Boss: Ragin' Contagion", item_name="Defeated Ragin' Contagion", rule=Has("Boss Key: Ragin' Contagion"))

        region_observatory = self.create_region_with_locations(region_name="Observatory")

        region_alltrades_abbey = self.create_region_with_locations(region_name="Alltrades Abbey")
        region_tower_of_trades = self.create_region_with_locations(region_name="Tower of Trades")
        region_tower_of_trades.add_event(location_name="Boss: Master of Nu'un", item_name="Defeated Master of Nu'un", rule=Has("Boss Key: Master of Nu'un"))

        region_porth_llaffan = self.create_region_with_locations(region_name="Porth Llaffan")
        region_tywll_cave = self.create_region_with_locations(region_name="Tywll Cave")
        region_tywll_cave.add_event(location_name="Boss: Lleviathan", item_name="Defeated Lleviathan", rule=Has("Boss Key: Lleviathan"))

        region_slurry_quay = self.create_region_with_locations(region_name="Slurry Quay")

        region_dourbridge = self.create_region_with_locations(region_name="Dourbridge")

        region_heights_of_loneliness = self.create_region_with_locations(region_name="Heights of Loneliness")
        region_zere_rocks = self.create_region_with_locations(region_name="Zere Rocks")
        region_zere_rocks.add_event(location_name="Boss: Garth Goyle", item_name="Defeated Garth Goyle", rule=Has("Boss Key: Garth Goyle"))

        region_bloomingdale = self.create_region_with_locations(region_name="Bloomingdale")
        region_bad_cave = self.create_region_with_locations(region_name="Bad Cave")
        region_bad_cave.add_event(location_name="Boss: Tyrantula", item_name="Defeated Tyrantula", rule=Has("Boss Key: Tyrantula"))

        region_ocean = self.create_region_with_locations(region_name="Ocean")
        region_ship = self.create_region_with_locations(region_name="Ship")

        region_gleeba = self.create_region_with_locations(region_name="Gleeba")
        region_plumbed_depths = self.create_region_with_locations(region_name="Plumbed Depths")
        region_plumbed_depths.add_event(location_name="Boss: Grand Lizzier", item_name="Defeated Grand Lizzier", rule=Has("Boss Key: Grand Lizzier"))

        region_batsureg = self.create_region_with_locations(region_name="Batsureg")
        region_gerzuun = self.create_region_with_locations(region_name="Gerzuun")
        region_gerzuun.add_event(location_name="Boss: Larstastnaras", item_name="Defeated Larstastnaras", rule=Has("Boss Key: Larstastnaras"))

        region_swinedimpels = self.create_region_with_locations(region_name="Swinedimpels Academy")
        region_old_school = self.create_region_with_locations(region_name="Old School")
        region_old_school.add_event(location_name="Boss: Dreadmaster", item_name="Defeated Dreadmaster", rule=Has("Boss Key: Dreadmaster"))

        region_wormwood_creek = self.create_region_with_locations(region_name="Wormwood Creek")
        region_bowhole = self.create_region_with_locations(region_name="Bowhole")
        region_bowhole.add_event(location_name="Boss: Gadrongo", item_name="Defeated Gadrongo", rule=Has("Boss Key: Gadrongo"))

        region_upover = self.create_region_with_locations(region_name="Upover")
        region_magmaroo = self.create_region_with_locations(region_name="Magmaroo")
        region_magmaroo.add_event(location_name="Boss: Greygnarl", item_name="Defeated Greygnarl", rule=Has("Boss Key: Greygnarl"))

        region_goretress = self.create_region_with_locations(region_name="Goretress")
        region_goretress.add_event(location_name="Boss: Goreham-Hogg (I)", item_name="Defeated Goreham-Hogg (I)", rule=Has("Boss Key: Goreham-Hogg (I)"))

        region_gittingham_palace = self.create_region_with_locations(region_name="Gittingham Palace")
        region_gittingham_palace.add_event(location_name="Boss: Hootingham-Gore (I)", item_name="Defeated Hootingham-Gore (I)", rule=Has("Boss Key: Hootingham-Gore (I)"))
        region_gittingham_palace.add_event(location_name="Boss: Goresby-Purrvis (I)", item_name="Defeated Goresby-Purrvis (I)", rule=Has("Boss Key: Goresby-Purrvis (I)"))
        region_gittingham_palace.add_event(location_name="Boss: King Godwyn", item_name="Defeated King Godwyn", rule=Has("Boss Key: King Godwyn"))

        region_oubliette = self.create_region_with_locations(region_name="Oubliette")

        region_realm_of_the_mighty = self.create_region_with_locations(region_name="Realm of the Mighty")
        region_realm_of_the_mighty.add_event(location_name="Boss: Goreham-Hogg (II)", item_name="Defeated Goreham-Hogg (II)", rule=Has("Boss Key: Goreham-Hogg (II)"))
        region_realm_of_the_mighty.add_event(location_name="Boss: Hootingham-Gore (II)", item_name="Defeated Hootingham-Gore (II)", rule=Has("Boss Key: Hootingham-Gore (II)"))
        region_realm_of_the_mighty.add_event(location_name="Boss: Goresby-Purrvis (II)", item_name="Defeated Goresby-Purrvis (II)", rule=Has("Boss Key: Goresby-Purrvis (II)"))
        region_realm_of_the_mighty.add_event(location_name="Boss: Corvus (I)", item_name="Defeated Corvus (I)", rule=Has("Boss Key: Corvus (I)"))
        region_realm_of_the_mighty.add_event(location_name="Boss: Barbarus", item_name="Defeated Barbarus", rule=Has("Boss Key: Barbarus"))
        region_realm_of_the_mighty.add_event(location_name="Boss: Corvus (II)", item_name="Defeated Corvus (II)", rule=Has("Boss Key: Corvus (II)"))

        # Connecting all the regions

        self.create_entrance(region_angel_falls, region_hexagon)
        self.create_entrance(region_angel_falls, region_stornway, Has("Defeated Hexagoon"))

        self.create_entrance(region_stornway, region_zere)
        self.create_entrance(region_stornway, region_brigadoom)
        self.create_entrance(region_zere, region_brigadoom, Has("Defeated Wight Knight"))
        self.create_entrance(region_stornway, region_coffinwell)

        self.create_entrance(region_coffinwell, region_quarantomb)
        self.create_entrance(region_coffinwell, region_observatory, Has("Defeated Ragin' Contagion"))

        self.create_entrance(region_observatory, region_alltrades_abbey)
        self.create_entrance(region_observatory, region_porth_llaffan)

        self.create_entrance(region_alltrades_abbey, region_tower_of_trades)
        self.create_entrance(region_alltrades_abbey, region_porth_llaffan)

        self.create_entrance(region_porth_llaffan, region_tywll_cave)
        self.create_entrance(region_porth_llaffan, region_slurry_quay, Has("Defeated Lleviathan"))

        self.create_entrance(region_slurry_quay, region_dourbridge)

        self.create_entrance(region_dourbridge, region_heights_of_loneliness)
        self.create_entrance(region_dourbridge, region_bloomingdale)
        self.create_entrance(region_dourbridge, region_bad_cave)

        self.create_entrance(region_heights_of_loneliness, region_zere_rocks)

        self.create_entrance(region_bloomingdale, region_ocean, Has("Defeated Tyrantula"))

        self.create_entrance(region_ocean, region_gleeba)
        self.create_entrance(region_ocean, region_batsureg)
        self.create_entrance(region_ocean, region_swinedimpels)
        self.create_entrance(region_ocean, region_wormwood_creek)
        self.create_entrance(region_ocean, region_ship)

        self.create_entrance(region_gleeba, region_plumbed_depths)

        self.create_entrance(region_batsureg, region_gerzuun)

        self.create_entrance(region_swinedimpels, region_old_school)

        self.create_entrance(region_wormwood_creek, region_bowhole,
                             HasAll("Defeated Master of Nu'un", "Defeated Lleviathan", "Defeated Garth Goyle", "Defeated Tyrantula", "Defeated Grand Lizzier", "Defeated Larstastnaras",
                                    "Defeated Dreadmaster"))
        self.create_entrance(region_wormwood_creek, region_upover, Has("Defeated Gadrongo"))

        self.create_entrance(region_upover, region_magmaroo)
        self.create_entrance(region_upover, region_goretress, Has("Defeated Greygnarl"))

        self.create_entrance(region_goretress, region_gittingham_palace, Has("Defeated Goreham-Hogg (I)"))

        self.create_entrance(region_gittingham_palace, region_oubliette)
        self.create_entrance(region_oubliette, region_realm_of_the_mighty, HasAll("Defeated Hootingham-Gore (I)", "Defeated Goresby-Purrvis (I)", "Defeated King Godwyn"))

        return [region_angel_falls, region_hexagon, region_stornway, region_zere, region_brigadoom, region_coffinwell, region_quarantomb, region_alltrades_abbey, region_tower_of_trades,
                region_porth_llaffan, region_tywll_cave, region_slurry_quay, region_dourbridge, region_heights_of_loneliness, region_zere_rocks, region_bloomingdale, region_bad_cave, region_ocean,
                region_ship, region_gleeba, region_plumbed_depths, region_batsureg, region_gerzuun, region_swinedimpels, region_old_school, region_wormwood_creek, region_bowhole, region_upover,
                region_magmaroo, region_goretress, region_gittingham_palace, region_oubliette, region_realm_of_the_mighty]

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.item_helper.get_filler_item_names())

    def get_completion_condition(self) -> Rule:
        return Has("Defeated Corvus (II)")

    def apply_special_rules(self) -> None:
        self.set_rule(spot=self.get_location("The Plumbed Depths - B1 (dungeon)"), rule=HasAny("Ultimate Key", "Magic Key"))
        self.set_rule(spot=self.get_location("The Plumbed Depths - B2 (graves)"), rule=HasAny("Ultimate Key", "Magic Key"))
        self.set_rule(spot=self.get_location("Dourbridge - secret shop"), rule=Has("Ultimate Key"))
        self.set_rule(spot=self.get_location("The Magmaroo - Greygnarl's Lair"), rule=Has("Defeated Goreham-Hogg (I)"))
