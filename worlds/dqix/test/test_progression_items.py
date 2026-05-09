from typing import List

from .bases import DQIXTestBase
from ..Options import EndBoss


class BossKeyHelper(DQIXTestBase):
    VALID_BOSSES: List[str] = []
    run_default_tests = False

    def test_boss_keys_present(self):
        if len(self.VALID_BOSSES) == 0:
            return

        for boss_name in self.VALID_BOSSES:
            self.collect_by_name(f"Boss Key: {boss_name}")

        self.assertTrue(self.multiworld.state.has_all(["Boss Key: " + n for n in self.VALID_BOSSES], self.player),
                        f"Not all required boss keys are present in the multiworld. Present keys: {', '.join(i.name for i in self.multiworld.itempool if i.name.startswith('Boss Key: '))}")

        key_count = sum(1 for i in self.multiworld.itempool if i.name.startswith("Boss Key: "))
        self.assertTrue(key_count == len(self.VALID_BOSSES), f"Number of expected boss keys does not match: {key_count} keys in the multiworld, {len(self.VALID_BOSSES)} expected")


class TestBossKeysMasterOfNuun(BossKeyHelper):
    options = {
        "end_boss": EndBoss.option_master_of_nuun
    }

    VALID_BOSSES = ["Hexagoon", "Wight Knight", "Morag", "Ragin' Contagion", "Master of Nu'un"]


class TestBossKeysGreygnarl(BossKeyHelper):
    options = {
        "end_boss": EndBoss.option_greygnarl
    }

    VALID_BOSSES = ["Hexagoon", "Wight Knight", "Morag", "Ragin' Contagion", "Master of Nu'un", "Lleviathan", "Garth Goyle", "Tyrantula", "Grand Lizzier", "Larstastnaras", "Dreadmaster", "Gadrongo",
                    "Greygnarl"]


class TestBossKeysCorvus(BossKeyHelper):
    options = {
        "end_boss": EndBoss.option_corvus
    }

    VALID_BOSSES = ["Hexagoon", "Wight Knight", "Morag", "Ragin' Contagion", "Master of Nu'un", "Lleviathan", "Garth Goyle", "Tyrantula", "Grand Lizzier", "Larstastnaras", "Dreadmaster", "Gadrongo",
                    "Greygnarl", "Goreham-Hogg (I)", "Hootingham-Gore (I)", "Goresby-Purrvis (I)", "King Godwyn", "Goreham-Hogg (II)", "Hootingham-Gore (II)", "Goresby-Purrvis (II)", "Corvus (I)",
                    "Barbarus", "Corvus (II)" ]
