from test.bases import WorldTestBase
from .. import DragonQuestIX


class DQIXTestBase(WorldTestBase):
    game = "Dragon Quest IX"
    world = DragonQuestIX

    run_default_tests = False