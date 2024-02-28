"""Various Constants"""

from math import pi

import numpy as np

# App Settings
default_ini_file = "astroplan.ini"

# Stellarium data
stellarium_field_count = 45

included_dso_types_galaxies = {
    "G",
    "Gx",
    "AGx",
    "rG",
    "IG",
    "ClG",
    "SAB(s)c",
}
included_dso_types_nebulas = {"NB", "PN", "DN", "RN", "C+N", "HII", "SNR", "BN", "EN", "GNe"}
included_dso_types = included_dso_types_galaxies | included_dso_types_nebulas

# Add or remove catalogs (and their corresponding column in the Stellarium data file)
catalogs = {
    "M": 18,
    "SH2": 21,
    "NGC": 16,
    "IC": 17,
}


# Constants associated with Earth's orbit
earth_tilt = -23.4 * pi / 180.0  # Tilt of Earth's rotation axis relative to orbital plane
hours_in_day = 23.0 + 56.0 / 60.0 + 4.0916 / 60.0 / 60.0  # Number of hours in a day
earth_rotation_rate = 2.0 * pi / hours_in_day  # Earth's rate of rotation about its axis
hours_in_year = 365.25635 * hours_in_day  # Number of hours in a year
earth_solar_orbital_rate = 2 * pi / hours_in_year  # Earth's orbital rate around the Sun
days_in_year = 365  # Number of days in a year
month_last_day = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365, 396]

r_01 = np.array(
    [[np.cos(earth_tilt), 0.0, -np.sin(earth_tilt)], [0.0, 1.0, 0.0], [np.sin(earth_tilt), 0.0, np.cos(earth_tilt)]]
)


# Constants associated with simulation
simulation_delta_t_hours = 7.0 / 60.0  # Simulation time step in hours
