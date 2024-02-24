"""Various calculators and helper functions"""
import os
import shutil
from math import pi

import numpy as np

import constants


def create_dir(path: str, delete_if_exists=True):
    if os.path.exists(path) and delete_if_exists:
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


def calc_sunset(t, dt, alt, loni, r23, r01):
    f = 7.0/dt
    n = 0
    while alt > -12.0 or alt < -12.05:
        if alt > -12.0:
            if f < 0.0:
                f = -f/2.0
        if alt < -12.05:
            if f > 0.0:
                f = -f/2.0
        t += f*dt
        alt = calc_sun_altitude(t, loni, r23, r01)
        n += 1
    t += dt
    alt = calc_sun_altitude(t, loni, r23, r01)
    return t, alt, n


def convert_ra_dec_to_alt_az(t, lon, ra, dec, r_23):
    r_12 = np.array(
        [
            [
                np.cos(constants.earth_rotation_rate * t + lon),
                np.sin(constants.earth_rotation_rate * t + lon),
                0.0
            ],
            [
                -np.sin(constants.earth_rotation_rate * t + lon),
                np.cos(constants.earth_rotation_rate * t + lon),
                0.0
            ],
            [
                0.0,
                0.0,
                1.0
            ]
        ]
    )
    r_ts = np.array(
        [
            [-np.sin(ra) * np.cos(dec)],
            [np.cos(ra) * np.cos(dec)],
            [np.sin(dec)]
        ]
    )
    r_tp = r_23 @ r_12 @ r_ts  # vector from observation location to DSO
    north = r_tp[2, 0]
    west = r_tp[0, 0]
    up = r_tp[1, 0]
    az = -np.arctan2(west, north) * 180.0 / pi
    if az < 0.0:
        az += 360.0
    if az > 360.0:
        az -= 360.0
    alt = np.arctan2(up, np.sqrt(north ** 2 + west ** 2)) * 180.0 / pi
    return alt, az


def calc_sun_altitude(t, lon, r_23, r_01):
    r_12 = np.array(
        [
            [
                np.cos(constants.earth_rotation_rate * t + lon),
                np.sin(constants.earth_rotation_rate * t + lon),
                0.0
            ],
            [
                -np.sin(constants.earth_rotation_rate * t + lon),
                np.cos(constants.earth_rotation_rate * t + lon),
                0.0
            ],
            [
                0.0,
                0.0,
                1.0
            ]
        ]
    )

    r_es = np.array(
        [
            [np.sin(constants.earth_solar_orbital_rate * t)],
            [-np.cos(constants.earth_solar_orbital_rate * t)],
            [0.0]
        ])

    r_sp = -r_23 @ r_12 @ r_01 @ r_es  # vector from observation location to Sun
    x = np.sqrt(r_sp[0, 0] ** 2 + r_sp[2, 0] ** 2)
    altitude = np.arctan2(r_sp[1, 0], x) * 180.0 / pi
    return altitude


def catalog_info(stellarium_row_data):
    # determines object catalog info from accepted catalogs only
    catalog_name = None
    for catalog_prefix, column_index in constants.catalogs.items():
        catalog_number = stellarium_row_data[column_index]
        if catalog_number and catalog_number != '0':
            catalog_name = f"{catalog_prefix}_{catalog_number}"
            break

    object_type = stellarium_row_data[5]
    if object_type in constants.included_dso_types_galaxies:
        is_galaxy = True
    elif object_type in constants.included_dso_types_nebulas:
        is_galaxy = False
    else:
        # Unrecognized type
        is_galaxy = None

    return catalog_name, is_galaxy



