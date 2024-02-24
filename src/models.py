"""Various data structures"""

from dataclasses import dataclass
from functools import cached_property
from math import pi
from pathlib import Path
from typing import NamedTuple

import numpy as np


@dataclass
class UserSettings:
    root_path: Path
    ini_file: Path
    observer_latitude: float
    observer_longitude: float
    horizon_file: Path
    min_obs_hours: float
    min_obs_peak_altitude: float
    min_obs_altitude: float
    min_dso_size: float
    catalog_file: str
    min_catalog_id: int
    max_catalog_id: int | None
    results_path: Path
    clear_results_before_running: bool
    _max_catalog_id: int = None

    @cached_property
    def observer_latitude_radians(self) -> float:
        return self.observer_latitude * pi / 180.0

    @cached_property
    def observer_longitude_radians(self) -> float:
        return self.observer_longitude * pi / 180.0

    @cached_property
    def min_obs_peak_dec(self) -> float:
        if self.observer_latitude > 0.0:
            return self.observer_latitude - 90.0 + self.min_obs_peak_altitude
        else:
            return self.observer_latitude + 90.0 - self.min_obs_peak_altitude

    @cached_property
    def catalog_id_range(self) -> str:
        if self.max_catalog_id is not None:
            return f"{self.min_catalog_id}-{self.max_catalog_id}"
        else:
            return f"{self.min_catalog_id}-end"

    @cached_property
    def r_23(self) -> np.ndarray:
        return np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, np.cos(self.observer_latitude_radians), np.sin(self.observer_latitude_radians)],
                [0.0, -np.sin(self.observer_latitude_radians), np.cos(self.observer_latitude_radians)],
            ]
        )

    @cached_property
    def local_catalog_file(self) -> str:
        return f"{self.results_path}/local_catalog_{self.min_catalog_id}-{self.max_catalog_id}.txt"

    @cached_property
    def dso_list_file(self) -> str:
        return f"{self.results_path}/DSO_list_{self.min_catalog_id}-{self.max_catalog_id}.csv"


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
        return "No.", "Name", "RA (deg)", "DEC (deg)", "Type", "Size", "Score", "Month", "Day"
