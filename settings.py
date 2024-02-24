"""Reads User Settings"""
import configparser

from constants import default_ini_file
from models import UserSettings
from utils import create_dir


def read_settings(file: str = default_ini_file) -> UserSettings:
    config = configparser.ConfigParser()
    config.read(file)

    observer = config["Observer"]
    filters = config["Filters"]
    catalog = config["Catalog"]
    output = config["Output"]

    try:
        max_catalog_id = int(catalog["MaxCatalogIndex"])
    except ValueError:
        max_catalog_id = None

    settings = UserSettings(
        ini_file=file,
        observer_latitude=float(observer["Latitude"]),
        observer_longitude=float(observer["Longitude"]),
        horizon_file=observer["HorizonFile"],

        min_obs_hours=float(filters["MinObservationHours"]),
        min_obs_peak_altitude=float(filters["MinObservationPeakAltitude"]),
        min_obs_altitude=float(filters["MinObservationAltitude"]),
        min_dso_size=float(filters["MinDSOSize"]),

        catalog_file=catalog["CatalogFile"].strip(),
        min_catalog_id=int(catalog["MinCatalogIndex"]),
        max_catalog_id=max_catalog_id,

        results_path=output["Results"],
        clear_results_before_running=output.getboolean("ClearResultsBeforeRunning"),
    )

    create_dir(settings.results_path, settings.clear_results_before_running)

    return settings
