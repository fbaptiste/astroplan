"""Various data structures"""
from collections import namedtuple


UserSettings = namedtuple(
    'UserSettings',
    [
        "observer_latitude",
        "observer_longitude",
        "horizon_file",
        "min_observation_hours",
        "min_obs_peak_altitude",
        "min_obs_altitude",
        "min_dso_size",
        "min_catalog_number",
        "max_catalog_number",
    ]
)
