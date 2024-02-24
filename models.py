"""Various data structures"""
from typing import NamedTuple

import numpy as np


class UserSettings(NamedTuple):
    observer_latitude: float
    observer_longitude: float
    observer_latitude_radians: float
    observer_longitude_radians: float
    horizon_file: str
    min_obs_hours: float
    min_obs_peak_altitude: float
    min_obs_peak_dec: float
    min_obs_altitude: float
    min_dso_size: float
    catalog_file: str
    min_catalog_id: int
    max_catalog_id: int
    catalog_id_range: str
    results_path: str
    clear_results_before_running: bool
    local_catalog_file: str
    dso_list_file: str
    r_23: np.ndarray


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
        return (
            self.catalog_id,
            self.catalog_name,
            round(self.ra_radians, 4),
            round(self.dec_radians, 4),
            int(self.is_galaxy),
            round(self.size, 2),
            round(self.max_score, 2),
            self.max_month,
            self.max_day,
        )

    @classmethod
    def csv_row_headers(cls):
        return 'No.', 'Name', 'RA (deg)', 'DEC (deg)', 'Type', 'Size', 'Score', 'Month', 'Day'
