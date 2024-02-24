"""Reads User Settings"""
from models import UserSettings
from os import path


def read_settings(settings_file_path: str) -> UserSettings | None:
    if path.isfile(settings_file_path):
        with open(settings_file_path) as f:
            return UserSettings(
                observer_latitude=float(f.readline().rstrip('\n')),
                observer_longitude=float(f.readline().rstrip('\n')),
                horizon_file=f.readline().rstrip('\n'),
                min_observation_hours=float(f.readline().rstrip('\n')),
                min_obs_peak_altitude=float(f.readline().rstrip('\n')),
                min_obs_altitude=float(f.readline().rstrip('\n')),
                min_dso_size=float(f.readline().rstrip('\n')),
                min_catalog_number=int(f.readline().rstrip('\n')),
                max_catalog_number=int(f.readline().rstrip('\n')),
            )
    else:
        return UserSettings(
            observer_latitude=0.0,
            observer_longitude=0.0,
            horizon_file="--Enter Filename--",
            min_observation_hours=4.0,
            min_obs_peak_altitude=30.0,
            min_obs_altitude=15.0,
            min_dso_size=10.0,
            min_catalog_number=1,
            max_catalog_number=2000
        )
