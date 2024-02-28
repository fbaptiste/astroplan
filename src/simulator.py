import math

import numpy as np

from src import constants, utils
from src.models import SimJobArgs, SimResult


def run_dso(args: SimJobArgs) -> SimResult:
    catalog_id = args.catalog_id
    catalog_name = args.catalog_name
    is_galaxy = args.is_galaxy
    object_ra_radians = args.object_ra_radians
    object_dec_radians = args.object_dec_radians
    object_size = args.object_size
    horizon_data = args.horizon_data
    user = args.user
    print(f"\t\t- ({catalog_id}) {catalog_name}")

    # Initialize internal data
    observer_longitude_radians = user.observer_longitude_radians
    min_obs_hours = (user.min_obs_hours,)
    min_obs_peak_altitude = (user.min_obs_peak_altitude,)
    min_obs_altitude = (user.min_obs_altitude,)
    r_23 = user.r_23
    month = 0
    time_series = np.zeros(shape=(constants.days_in_year, 5))
    t0 = 79.0 * constants.hours_in_day  # Number of hours between Jan 1 and Spring Equinox
    t = 0.0 - t0  # January 1

    # Start simulation
    sun_altitude = utils.calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
    if sun_altitude > -12.0:  # It's daylight, so move clock forward to first dark
        t, sun_altitude, n1 = utils.calc_sunset(
            t, constants.simulation_delta_t_hours, sun_altitude, observer_longitude_radians, r_23, constants.r_01
        )
    else:
        while sun_altitude < -12.0:  # It's dark, so move clock back to first dark
            t -= constants.simulation_delta_t_hours / 4.0
            sun_altitude = utils.calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
        t += constants.simulation_delta_t_hours / 4.0
        sun_altitude = utils.calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
    day = 0
    min_altitude = 100.0  # Initialize single-night observation variables
    max_altitude = 0.0
    score = 0.0
    time_visible = 0.0

    # Begin year-long simulation
    while day < constants.days_in_year:  # Analysis starts at first dark on first day of the year
        if sun_altitude < -12.0:
            dalt, daz = utils.convert_ra_dec_to_alt_az(
                t, observer_longitude_radians, object_ra_radians, object_dec_radians, r_23
            )
            horizon_altitude = np.interp(daz, horizon_data[:, 0], horizon_data[:, 1])
            if dalt > max(min_obs_altitude, horizon_altitude):
                time_visible += constants.simulation_delta_t_hours
                max_altitude = max(max_altitude, dalt)
                min_altitude = min(min_altitude, dalt)
                score = max(score, time_visible / 10.25 * max_altitude / 90.0)
            t += constants.simulation_delta_t_hours
            sun_altitude = utils.calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
        else:
            # End of the night clean up
            if month == 0:
                damo = float(month + 1) + (float(day) / float(constants.month_last_day[month]))
            else:
                damo = float(month + 1) + float(day - constants.month_last_day[month - 1]) / float(
                    constants.month_last_day[month] - constants.month_last_day[month - 1]
                )
            if min_altitude > 95.0:
                min_altitude = 0.0
            time_series[day, 0:5] = np.array([damo, min_altitude, max_altitude, time_visible, score])
            if day > 1:
                # Perform moving average to smooth out curves
                time_series[day - 1, 1] = np.mean(time_series[day - 2 : day + 1, 1])
                time_series[day - 1, 2] = np.mean(time_series[day - 2 : day + 1, 2])
                time_series[day - 1, 3] = np.mean(time_series[day - 2 : day + 1, 3])
                time_series[day - 1, 4] = np.mean(time_series[day - 2 : day + 1, 4])
            min_altitude = 100.0  # Initialize single-night observation variables
            max_altitude = 0.0
            score = 0.0
            time_visible = 0.0
            day += 1
            if day == constants.month_last_day[month]:
                month += 1

            # fast-forward through daylight to sunset
            t, sun_altitude, n1 = utils.calc_sunset(
                t, constants.simulation_delta_t_hours, sun_altitude, observer_longitude_radians, r_23, constants.r_01
            )

    if max(time_series[:, 2]) < min_obs_peak_altitude or max(time_series[:, 3]) < min_obs_hours:
        return SimResult(is_included=False)  # Cannot see DSO (not high enough and/or not visible for long enough

    # Find first day when imaging score is maximum
    max_month, max_day, max_score = calc_first_max_info(time_series)

    return SimResult(
        is_included=True,
        catalog_id=catalog_id,
        catalog_name=catalog_name,
        is_galaxy=is_galaxy,
        ra_degrees=math.degrees(object_ra_radians),
        dec_degrees=math.degrees(object_dec_radians),
        size=object_size,
        max_score=max_score,
        max_month=max_month,
        max_day=max_day,
        time_series=time_series,
    )


def calc_first_max_info(time_series):
    max_score = 0.97 * max(time_series[:, 4])  # Use 0.97 to avoid small numerical fluctuation error
    kk = 0
    if time_series[0, 4] < max_score:
        while time_series[kk, 4] < max_score:
            kk += 1
            kk = min(max(0, kk), 364)
    else:
        kk = constants.days_in_year - 1
        while time_series[kk, 4] >= max_score:
            kk -= 1
            kk = max(0, kk)
        kk += 1
        kk = min(max(0, kk), 364)
    kk = min(max(0, kk), 364)
    max_month = int(time_series[kk, 0])
    max_day = max(int((time_series[kk, 0] - float(max_month)) * 31.0), 1)

    max_score = max(time_series[:, 4])
    return max_month, max_day, max_score
