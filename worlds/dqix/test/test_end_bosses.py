from typing import List

from .bases import DQIXTestBase
from .. import EndBoss


class EndBossHelper(DQIXTestBase):
    BOSS_REQUIREMENTS = []

    def check_boss_keys_for_regions(self, boss_names: List[str], region_names: List[str]):
        boss_key_list = ', '.join(["Boss Key: " + x for x in boss_names])

        for region_name in region_names:
            with self.subTest(f"Test that \"{region_name}\" cannot be accessed without the following keys: {boss_key_list}"):
                self.assertFalse(self.can_reach_region(region_name), f"\"{region_name}\" can be accessed even without all following keys present: {boss_key_list}")

        for boss_name in boss_names:
            self.collect_by_name("Boss Key: " + boss_name)

        for region_name in region_names:
            with self.subTest(f"Test that \"{region_name}\" can be accessed with the following keys: {boss_key_list}"):
                self.assertTrue(self.can_reach_region(region_name), f"\"{region_name}\" cannot be accessed even though all required boss keys are present: {boss_key_list}")

    def test_boss_key_logic(self):
        for boss_data in self.BOSS_REQUIREMENTS:
            self.check_boss_keys_for_regions(boss_data["bosses"], boss_data["regions"])


class TestBossCorvus(EndBossHelper):
    options = {
        "end_boss": EndBoss.option_corvus
    }

    BOSS_REQUIREMENTS = [
        {"bosses": ["Hexagoon"], "regions": ["Stornway", "Zere", "Brigadoom"]},
        {"bosses": ["Wight Knight", "Morag"], "regions": ["Coffinwell", "Quarantomb"]},
        {"bosses": ["Ragin' Contagion"], "regions": ['Observatory', 'Alltrades Abbey', 'Tower of Trades', 'Porth Llaffan', "Tywll Cave"]},
        {"bosses": ["Lleviathan"], "regions": ["Slurry Quay", "Dourbridge", "Heights of Loneliness", "Zere Rocks", "Bloomingdale", "Bad Cave"]},
        {"bosses": ["Tyrantula"], "regions": ["Ocean", "Gleeba"]},
        {"bosses": ["Master of Nu'un", "Lleviathan", "Garth Goyle", "Tyrantula", "Grand Lizzier", "Larstastnaras", "Dreadmaster", "Gadrongo"], "regions": ["Upover"]},
        {"bosses": ["Greygnarl"], "regions": ["Goretress"]},
        {"bosses": ["Goreham-Hogg (I)", "Hootingham-Gore (I)"], "regions": ["Gittingham Palace"]},
        {"bosses": ["Goresby-Purrvis (I)", "King Godwyn"], "regions": ["Oubliette", "Realm of the Mighty - Initial"]},
        {"bosses": ["Goreham-Hogg (II)"], "regions": ["Realm of the Mighty - After Goreham-Hogg"]},
        {"bosses": ["Hootingham-Gore (II)"], "regions": ["Realm of the Mighty - After Hootingham-Gore"]},
        {"bosses": ["Goresby-Purrvis (II)"], "regions": ["Realm of the Mighty - After Goresby-Purrvis"]},
    ]


class TestBossGreygnarl(EndBossHelper):
    options = {
        "end_boss": EndBoss.option_greygnarl
    }

    BOSS_REQUIREMENTS = [
        {"bosses": ["Hexagoon"], "regions": ["Stornway", "Zere", "Brigadoom"]},
        {"bosses": ["Wight Knight", "Morag"], "regions": ["Coffinwell", "Quarantomb"]},
        {"bosses": ["Ragin' Contagion"], "regions": ['Observatory', 'Alltrades Abbey', 'Tower of Trades', 'Porth Llaffan', "Tywll Cave"]},
        {"bosses": ["Lleviathan"], "regions": ["Slurry Quay", "Dourbridge", "Heights of Loneliness", "Zere Rocks", "Bloomingdale", "Bad Cave"]},
        {"bosses": ["Tyrantula"], "regions": ["Ocean", "Gleeba"]},
        {"bosses": ["Master of Nu'un", "Lleviathan", "Garth Goyle", "Tyrantula", "Grand Lizzier", "Larstastnaras", "Dreadmaster", "Gadrongo"], "regions": ["Upover"]}
    ]


class TestBossMasterOfNuun(EndBossHelper):
    options = {
        "end_boss": EndBoss.option_master_of_nuun
    }

    BOSS_REQUIREMENTS = [
        {"bosses": ["Hexagoon"], "regions": ["Stornway", "Zere", "Brigadoom"]},
        {"bosses": ["Wight Knight", "Morag"], "regions": ["Coffinwell", "Quarantomb"]},
        {"bosses": ["Ragin' Contagion"], "regions": ['Observatory', 'Alltrades Abbey', 'Tower of Trades']}
    ]
