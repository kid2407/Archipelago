import json
import pkgutil
from typing import Dict, Union

from BaseClasses import Location


class DQIXLocation(Location):
    game = "Dragon Quest IX"


class DQIXLocations:
    _location_table_grouped: Dict[str, Dict[str, int]] = {}

    def _parse_location_data(self):
        file = pkgutil.get_data(__name__, "data/locations.json").decode("utf-8")
        locations = json.loads(file)

        self._location_table_grouped = locations

    def _get_location_table(self):
        if not self._location_table_grouped:
            self._parse_location_data()
        return self._location_table_grouped

    def get_locations(self):
        return {k: v for sub_dict in self._get_location_table().values() for k, v in sub_dict.items()}

    def get_locations_for_group(self, group_name: str):
        return self._get_location_table()[group_name]
