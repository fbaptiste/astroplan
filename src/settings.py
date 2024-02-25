"""Reads User Settings"""

import configparser

from src.constants import default_ini_file
from src.models import UserSettings
from src.utils import create_dir, run_root


def read_settings(file: str = default_ini_file) -> UserSettings:
    root_path = run_root()
    ini_file = root_path.joinpath(file)
    config = configparser.ConfigParser()
    config.read(root_path.joinpath(file))

    observer = config["Observer"]
    filters = config["Filters"]
    catalog = config["Catalog"]
    output = config["Output"]
    parallelism = config["Parallelism"]

    try:
        max_catalog_id = int(catalog["MaxCatalogIndex"])
    except ValueError:
        max_catalog_id = None

    settings = UserSettings(
        root_path=root_path,
        ini_file=ini_file,
        observer_latitude=float(observer["Latitude"]),
        observer_longitude=float(observer["Longitude"]),
        horizon_file=root_path.joinpath(observer["HorizonFile"]),
        min_obs_hours=float(filters["MinObservationHours"]),
        min_obs_peak_altitude=float(filters["MinObservationPeakAltitude"]),
        min_obs_altitude=float(filters["MinObservationAltitude"]),
        min_dso_size=float(filters["MinDSOSize"]),
        catalog_file=catalog["CatalogFile"].strip(),
        min_catalog_id=int(catalog["MinCatalogIndex"]),
        max_catalog_id=max_catalog_id,
        results_path=root_path.joinpath(output["Results"]),
        clear_results_before_running=output.getboolean("ClearResultsBeforeRunning"),
        pool_size=int(parallelism["MaxParallelJobs"]),
    )

    create_dir(settings.results_path, settings.clear_results_before_running)

    return settings
