"""Various data structures"""
from collections import namedtuple


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
        "results_path",
        "clear_results_before_running",

        "local_catalog_file",
        "dso_list_file",
        "r_23",
    ]
)
