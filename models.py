"""Various data structures"""
from typing import NamedTuple
from collections import namedtuple

import numpy as np


UserSettings = namedtuple(
    'UserSettings',
    [
        "observer_latitude",
        "observer_longitude",
        "observer_latitude_radians",
        "observer_longitude_radians",
        "horizon_file",
        "min_obs_hours",
        "min_obs_peak_altitude",
        "min_obs_peak_dec",
        "min_obs_altitude",
        "min_dso_size",
        "catalog_file",
        "min_catalog_id",
        "max_catalog_id",
        "catalog_id_range",
        "results_path",
        "clear_results_before_running",

        "local_catalog_file",
        "dso_list_file",
        "r_23",
    ]
)


class SimResult(NamedTuple):
    is_included: bool = False
    catalog_id: int | None = None
    catalog_name: str | None = None
    is_galaxy: bool = False
    ra_radians: float | None = None
    dec_radians: float | None = None
    size: float | None = None
    max_score: float | None = None
    max_month: int | None = None
    max_day: int | None = None
    time_series: np.ndarray | None = None

    @property
    def csv_row(self):
        return [
            self.catalog_id,
            self.catalog_name,
            round(self.ra_radians, 4),
            round(self.dec_radians, 4),
            int(self.is_galaxy),
            round(self.size, 2),
            round(self.max_score, 2),
            self.max_month,
            self.max_day,
        ]
