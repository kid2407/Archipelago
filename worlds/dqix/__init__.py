from typing import Optional

from BaseClasses import Tutorial, Item, ItemClassification, Location, Region
from ..AutoWorld import World, WebWorld
from .Items import DQIXItems
from .Client import DQIXClient
from .Locations import DQIXLocations


class DQIXItem(Item):
    game = "Dragon Quest IX"
    item_type: str

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int, item_type: str):
        super(DQIXItem, self).__init__(name, classification, code, player)
        self.item_type = item_type


class DQIXLocation(Location):
    game = "Dragon Quest IX"


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
        items = []
        for name in progression_item_names:
            if name == "Fygg":
                for _ in range(7):
                    items.append(self.create_item(name))
            else:
                items.append(self.create_item(name))

        # Fill up to 90% of the remaining item slots with useful items
        remaining_count_until_almost_full = (round(len(self.location_name_to_id) * 0.9) - len(items))
        items += [self.create_item(useful_item) for useful_item in self.random.choices(population=list(self.item_helper.useful_items.keys()), k=remaining_count_until_almost_full)]

        # remaining 10% are filler, money and gold
        items += [self.create_item(self.get_filler_item_name()) for _ in range(len(self.location_name_to_id) - len(items))]

        self.multiworld.itempool += items

    def create_regions(self) -> None:
        region_angel_falls = Region(self.origin_region_name, self.player, self.multiworld)
        region_angel_falls.add_locations(locations=self.location_helper.get_locations_for_group(region_angel_falls.name), location_type=DQIXLocation)
        region_hexagon = Region("Hexagon", self.player, self.multiworld)
        region_hexagon.add_locations(locations=self.location_helper.get_locations_for_group(region_hexagon.name), location_type=DQIXLocation)
        region_hexagon.add_event("Boss: Hexagon", "Defeated Hexagoon")

        region_stornway = Region("Stornway", self.player, self.multiworld)
        region_stornway.add_locations(locations=self.location_helper.get_locations_for_group(region_stornway.name), location_type=DQIXLocation)
        region_stornway.add_event("Boss: Wight Knight", "Defeated Wight Knight")

        region_zere = Region("Zere", self.player, self.multiworld)
        region_zere.add_locations(locations=self.location_helper.get_locations_for_group(region_zere.name), location_type=DQIXLocation)
        region_brigadoom = Region("Brigadoom", self.player, self.multiworld)
        region_brigadoom.add_locations(locations=self.location_helper.get_locations_for_group(region_brigadoom.name), location_type=DQIXLocation)
        region_brigadoom.add_event("Boss: Morag", "Defeated Morag")

        region_coffinwell = Region("Coffinwell", self.player, self.multiworld)
        region_coffinwell.add_locations(locations=self.location_helper.get_locations_for_group(region_coffinwell.name), location_type=DQIXLocation)
        region_quarantomb = Region("Quarantomb", self.player, self.multiworld)
        region_quarantomb.add_locations(locations=self.location_helper.get_locations_for_group(region_quarantomb.name), location_type=DQIXLocation)
        region_quarantomb.add_event("Boss: Ragin' Contagion", "Defeated Ragin' Contagion")

        region_observatory = Region("Observatory", self.player, self.multiworld)
        region_observatory.add_locations(locations=self.location_helper.get_locations_for_group(region_observatory.name), location_type=DQIXLocation)

        region_alltrades_abbey = Region("Alltrades Abbey", self.player, self.multiworld)
        region_alltrades_abbey.add_locations(locations=self.location_helper.get_locations_for_group(region_alltrades_abbey.name), location_type=DQIXLocation)
        region_tower_of_trades = Region("Tower of Trades", self.player, self.multiworld)
        region_tower_of_trades.add_locations(locations=self.location_helper.get_locations_for_group(region_tower_of_trades.name), location_type=DQIXLocation)
        region_tower_of_trades.add_event("Boss: Master of Nu'un", "Defeated Master of Nu'un")

        region_porth_llaffan = Region("Porth Llaffan", self.player, self.multiworld)
        region_porth_llaffan.add_locations(locations=self.location_helper.get_locations_for_group(region_porth_llaffan.name), location_type=DQIXLocation)
        region_tywll_cave = Region("Tywll Cave", self.player, self.multiworld)
        region_tywll_cave.add_locations(locations=self.location_helper.get_locations_for_group(region_tywll_cave.name), location_type=DQIXLocation)
        region_tywll_cave.add_event("Boss: Lleviathan", "Defeated Lleviathan")

        region_slurry_quay = Region("Slurry Quay", self.player, self.multiworld)
        region_slurry_quay.add_locations(locations=self.location_helper.get_locations_for_group(region_slurry_quay.name), location_type=DQIXLocation)

        region_dourbridge = Region("Dourbridge", self.player, self.multiworld)
        region_dourbridge.add_locations(locations=self.location_helper.get_locations_for_group(region_dourbridge.name), location_type=DQIXLocation)

        region_heights_of_loneliness = Region("Heights of Loneliness", self.player, self.multiworld)
        region_heights_of_loneliness.add_locations(locations=self.location_helper.get_locations_for_group(region_heights_of_loneliness.name), location_type=DQIXLocation)
        region_zere_rocks = Region("Zere Rocks", self.player, self.multiworld)
        region_zere_rocks.add_locations(locations=self.location_helper.get_locations_for_group(region_zere_rocks.name), location_type=DQIXLocation)
        region_zere_rocks.add_event("Boss: Garth Goyle", "Defeated Garth Goyle")

        region_bloomingdale = Region("Bloomingdale", self.player, self.multiworld)
        region_bloomingdale.add_locations(locations=self.location_helper.get_locations_for_group(region_bloomingdale.name), location_type=DQIXLocation)
        region_bad_cave = Region("Bad Cave", self.player, self.multiworld)
        region_bad_cave.add_locations(locations=self.location_helper.get_locations_for_group(region_bad_cave.name), location_type=DQIXLocation)
        region_bad_cave.add_event("Boss: Tyrantula", "Defeated Tyrantula")

        region_ocean = Region("Ocean", self.player, self.multiworld)
        region_ocean.add_locations(locations=self.location_helper.get_locations_for_group(region_ocean.name), location_type=DQIXLocation)
        region_ship = Region("Ship", self.player, self.multiworld)  # Rooms inside, includes Falcon blade behind ultimate key
        region_ship.add_locations(locations=self.location_helper.get_locations_for_group(region_ship.name), location_type=DQIXLocation)

        region_gleeba = Region("Gleeba", self.player, self.multiworld)
        region_gleeba.add_locations(locations=self.location_helper.get_locations_for_group(region_gleeba.name), location_type=DQIXLocation)
        region_plumbed_depths = Region("Plumbed Depths", self.player, self.multiworld)
        region_plumbed_depths.add_locations(locations=self.location_helper.get_locations_for_group(region_plumbed_depths.name), location_type=DQIXLocation)
        region_plumbed_depths.add_event("Boss: Grand Lizzier", "Defeated Grand Lizzier")

        region_batsureg = Region("Batsureg", self.player, self.multiworld)
        region_batsureg.add_locations(locations=self.location_helper.get_locations_for_group(region_batsureg.name), location_type=DQIXLocation)
        region_gerzuun = Region("Gerzuun", self.player, self.multiworld)
        region_gerzuun.add_locations(locations=self.location_helper.get_locations_for_group(region_gerzuun.name), location_type=DQIXLocation)
        region_gerzuun.add_event("Boss: Larstastnaras", "Defeated Larstastnaras")

        region_swinedimpels = Region("Swinedimpels Academy", self.player, self.multiworld)
        region_swinedimpels.add_locations(locations=self.location_helper.get_locations_for_group(region_swinedimpels.name), location_type=DQIXLocation)
        region_old_school = Region("Old School", self.player, self.multiworld)
        region_old_school.add_locations(locations=self.location_helper.get_locations_for_group(region_old_school.name), location_type=DQIXLocation)
        region_old_school.add_event("Boss: Dreadmaster", "Defeated Dreadmaster")

        region_wormwood_creek = Region("Wormwood Creek", self.player, self.multiworld)
        region_wormwood_creek.add_locations(locations=self.location_helper.get_locations_for_group(region_wormwood_creek.name), location_type=DQIXLocation)
        region_bowhole = Region("Bowhole", self.player, self.multiworld)
        region_bowhole.add_locations(locations=self.location_helper.get_locations_for_group(region_bowhole.name), location_type=DQIXLocation)
        region_bowhole.add_event("Boss: Gadrongo", "Defeated Gadrongo")

        region_upover = Region("Upover", self.player, self.multiworld)
        region_upover.add_locations(locations=self.location_helper.get_locations_for_group(region_upover.name), location_type=DQIXLocation)
        region_magmaroo = Region("Magmaroo", self.player, self.multiworld)
        region_magmaroo.add_locations(locations=self.location_helper.get_locations_for_group(region_magmaroo.name), location_type=DQIXLocation)
        region_magmaroo.add_event("Boss: Greygnarl", "Defeated Greygnarl")

        region_goretress = Region("Goretress", self.player, self.multiworld)
        region_goretress.add_locations(locations=self.location_helper.get_locations_for_group(region_goretress.name), location_type=DQIXLocation)
        region_goretress.add_event("Boss: Goreham-Hogg", "Defeated Goreham-Hogg")

        region_gittingham_palace = Region("Gittingham Palace", self.player, self.multiworld)
        region_gittingham_palace.add_locations(locations=self.location_helper.get_locations_for_group(region_gittingham_palace.name), location_type=DQIXLocation)
        region_gittingham_palace.add_event("Boss: Hootingham-Gore", "Defeated Hootingham-Gore")
        region_gittingham_palace.add_event("Boss: Goresby-Purrvis", "Defeated Goresby-Purrvis")
        region_oubliette = Region("Oubliette", self.player, self.multiworld)
        region_oubliette.add_locations(locations=self.location_helper.get_locations_for_group(region_oubliette.name), location_type=DQIXLocation)

        region_realm_of_the_mighty = Region("Realm of the Mighty", self.player, self.multiworld)
        region_realm_of_the_mighty.add_locations(locations=self.location_helper.get_locations_for_group(region_realm_of_the_mighty.name), location_type=DQIXLocation)
        region_realm_of_the_mighty.add_event("Boss: Corvus (I)", "Defeated Corvus (I)")
        region_realm_of_the_mighty.add_event("Boss: Barbarus", "Defeated Barbarus")
        region_realm_of_the_mighty.add_event("Boss: Corvus (II)", "Defeated Corvus (II)")

        region_angel_falls.connect(connecting_region=region_hexagon)
        region_angel_falls.connect(connecting_region=region_stornway, rule=lambda state: state.has(item="Defeated Hexagoon", player=self.player, count=1))

        region_stornway.connect(connecting_region=region_zere)
        region_stornway.connect(connecting_region=region_brigadoom)
        region_zere.connect(connecting_region=region_brigadoom, rule=lambda state: state.has(item="Defeated Wight Knight", player=self.player, count=1))
        region_stornway.connect(connecting_region=region_coffinwell)

        region_coffinwell.connect(connecting_region=region_quarantomb, rule=lambda state: state.has(item="Quarantomb key", player=self.player))
        region_coffinwell.connect(connecting_region=region_observatory, rule=lambda state: state.has(item="Defeated Ragin' Contagion", player=self.player, count=1))
        region_coffinwell.connect(connecting_region=region_alltrades_abbey, rule=lambda state: state.has(item="Defeated Ragin' Contagion", player=self.player, count=1))
        region_coffinwell.connect(connecting_region=region_porth_llaffan, rule=lambda state: state.has(item="Defeated Ragin' Contagion", player=self.player, count=1))

        region_observatory.connect(connecting_region=region_alltrades_abbey)
        region_observatory.connect(connecting_region=region_porth_llaffan)

        region_alltrades_abbey.connect(connecting_region=region_tower_of_trades)
        region_alltrades_abbey.connect(connecting_region=region_porth_llaffan)

        region_porth_llaffan.connect(connecting_region=region_tywll_cave)
        region_porth_llaffan.connect(connecting_region=region_slurry_quay, rule=lambda state: state.has(item="Defeated Lleviathan", player=self.player, count=1))

        region_slurry_quay.connect(connecting_region=region_dourbridge)

        region_dourbridge.connect(connecting_region=region_heights_of_loneliness)
        region_dourbridge.connect(connecting_region=region_bloomingdale)
        region_dourbridge.connect(connecting_region=region_bad_cave)

        region_heights_of_loneliness.connect(connecting_region=region_zere_rocks)
        region_heights_of_loneliness.connect(connecting_region=region_bloomingdale)
        region_heights_of_loneliness.connect(connecting_region=region_bad_cave)

        region_bloomingdale.connect(connecting_region=region_ocean, rule=lambda state: state.has(item="Defeated Tyrantula", player=self.player, count=1))  # Check if player has unlocked ship

        region_ocean.connect(connecting_region=region_gleeba)
        region_ocean.connect(connecting_region=region_batsureg)
        region_ocean.connect(connecting_region=region_swinedimpels)
        region_ocean.connect(connecting_region=region_wormwood_creek)
        region_ocean.connect(connecting_region=region_ship, rule=lambda state: state.has(item="Ultimate key", player=self.player))

        region_gleeba.connect(connecting_region=region_plumbed_depths)

        region_batsureg.connect(connecting_region=region_gerzuun)

        region_swinedimpels.connect(connecting_region=region_old_school)

        region_wormwood_creek.connect(connecting_region=region_bowhole, rule=lambda state: state.has(item="Serene necklace", player=self.player, count=1))

        region_wormwood_creek.connect(connecting_region=region_upover, rule=lambda state: state.has(item="Defeated Gadrongo", player=self.player, count=1))

        region_upover.connect(connecting_region=region_magmaroo)
        region_upover.connect(connecting_region=region_goretress, rule=lambda state: state.has(item="Defeated Greygnarl", player=self.player, count=1))

        region_goretress.connect(connecting_region=region_gittingham_palace, rule=lambda state: state.has(item="Defeated Goreham-Hogg", player=self.player, count=1))

        region_gittingham_palace.connect(connecting_region=region_oubliette)
        region_oubliette.connect(connecting_region=region_realm_of_the_mighty, rule=lambda state: state.has(item="Defeated Hootingham-Gore", player=self.player, count=1) and state.has(item="Defeated Goresby-Purrvis", player=self.player, count=1))

        self.multiworld.regions.append(region_angel_falls)
        self.multiworld.regions.append(region_hexagon)
        self.multiworld.regions.append(region_stornway)
        self.multiworld.regions.append(region_zere)
        self.multiworld.regions.append(region_brigadoom)
        self.multiworld.regions.append(region_coffinwell)
        self.multiworld.regions.append(region_quarantomb)
        self.multiworld.regions.append(region_alltrades_abbey)
        self.multiworld.regions.append(region_tower_of_trades)
        self.multiworld.regions.append(region_porth_llaffan)
        self.multiworld.regions.append(region_tywll_cave)
        self.multiworld.regions.append(region_slurry_quay)
        self.multiworld.regions.append(region_dourbridge)
        self.multiworld.regions.append(region_heights_of_loneliness)
        self.multiworld.regions.append(region_zere_rocks)
        self.multiworld.regions.append(region_bloomingdale)
        self.multiworld.regions.append(region_bad_cave)
        self.multiworld.regions.append(region_ocean)
        self.multiworld.regions.append(region_ship)
        self.multiworld.regions.append(region_gleeba)
        self.multiworld.regions.append(region_plumbed_depths)
        self.multiworld.regions.append(region_batsureg)
        self.multiworld.regions.append(region_gerzuun)
        self.multiworld.regions.append(region_swinedimpels)
        self.multiworld.regions.append(region_old_school)
        self.multiworld.regions.append(region_wormwood_creek)
        self.multiworld.regions.append(region_bowhole)
        self.multiworld.regions.append(region_upover)
        self.multiworld.regions.append(region_magmaroo)
        self.multiworld.regions.append(region_goretress)
        self.multiworld.regions.append(region_gittingham_palace)
        self.multiworld.regions.append(region_oubliette)
        self.multiworld.regions.append(region_realm_of_the_mighty)

        self.multiworld.completion_condition[self.player] = lambda state: state.has("Defeated Corvus (II)", self.player)

        # state = self.multiworld.get_all_state(False)
        # state.update_reachable_regions(self.player)
        # visualize_regions(self.get_region(self.origin_region_name), "my_world.puml", show_entrance_names=True, regions_to_highlight=state.reachable_regions[self.player])

    def get_filler_item_name(self) -> str:
        return self.random.choice(self.item_helper.get_filler_item_names())
