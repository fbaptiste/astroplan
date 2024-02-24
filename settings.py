"""Reads User Settings"""
import configparser
from math import pi

import numpy as np

from constants import settings_file
from models import UserSettings
from utils import create_dir


def read_settings(file: str = settings_file) -> UserSettings:
    config = configparser.ConfigParser()
    config.read(file)

    observer = config["Observer"]
    filters = config["Filters"]
    catalog = config["Catalog"]
    output = config["Output"]

    observer_latitude = float(observer["Latitude"])
    observer_longitude = float(observer["Longitude"])
    min_obs_peak_altitude = float(filters["MinObservationPeakAltitude"])
    min_catalog_id = int(catalog["MinCatalogIndex"])
    max_catalog_id = int(catalog["MaxCatalogIndex"])
    results_path = output["Results"]

    observer_latitude_radians = observer_latitude * pi / 180.0
    observer_longitude_radians = observer_longitude * pi / 180.0

    if observer_latitude > 0.0:
        min_obs_peak_dec = observer_latitude - 90.0 + min_obs_peak_altitude
    else:
        min_obs_peak_dec = observer_latitude + 90.0 - min_obs_peak_altitude

    local_catalog_file = f"{results_path}/local_catalog_{min_catalog_id}-{max_catalog_id}.txt"
    dso_list_file = f"{results_path}/DSO_list_{min_catalog_id}-{max_catalog_id}.csv"

    r23 = np.array([
        [1.0, 0.0, 0.0],
        [0.0, np.cos(observer_latitude_radians), np.sin(observer_latitude_radians)],
        [0.0, -np.sin(observer_latitude_radians), np.cos(observer_latitude_radians)]
    ])

    settings = UserSettings(
        observer_latitude=observer_latitude,
        observer_longitude=observer_longitude,
        observer_latitude_radians=observer_latitude_radians,
        observer_longitude_radians=observer_longitude_radians,
        horizon_file=observer["HorizonFile"],

        min_obs_hours=float(filters["MinObservationHours"]),
        min_obs_peak_altitude=min_obs_peak_altitude,
        min_obs_peak_dec=min_obs_peak_dec,
        min_obs_altitude=float(filters["MinObservationAltitude"]),
        min_dso_size=float(filters["MinDSOSize"]),

        catalog_file=catalog["CatalogFile"].strip(),
        min_catalog_id=min_catalog_id,
        max_catalog_id=max_catalog_id,

        results_path=results_path,
        clear_results_before_running=output.getboolean("ClearResultsBeforeRunning"),

        local_catalog_file=local_catalog_file,
        dso_list_file=dso_list_file,

        r23=r23,
    )

    create_dir(settings.results_path, settings.clear_results_before_running)

    return settings


user = read_settings()
