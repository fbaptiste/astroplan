import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from math import pi
import constants
import utils
from utils import calc_sun_altitude, convert_ra_dec_to_alt_az, calc_sunset


def dso(
        r_23,
        observer_longitude_radians: float,
        horizon_data,
        stellarium_row_data,
        csv_dso_list,
        min_observation_hours,
        min_obs_peak_altitude,
        min_obs_altitude,
        results_folder,
        # fdd
):
    # Get object catalog name and object type
    catalog_name, is_galaxy = utils.catalog_info(stellarium_row_data)
    if catalog_name is None or is_galaxy is None:
        # Either not in desired catalog, or not in DSO types of interest
        return 0

    # Extract/Convert Stellarium data
    row_index = int(stellarium_row_data[0])
    ra = float(stellarium_row_data[1]) * pi / 180.0
    dec = float(stellarium_row_data[2]) * pi / 180.0
    size = round(max(float(stellarium_row_data[7]), float(stellarium_row_data[8])), 2)

    # Initialize internal data
    month = 0
    hist = np.zeros(shape=(constants.days_in_year, 5))
    t0 = 79.0 * constants.hours_in_day  # Number of hours between Jan 1 and Spring Equinox
    t = 0.0 - t0  # January 1

    sun_altitude = calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
    if sun_altitude > -12.0:  # It's daylight, so move clock forward to first dark
        t, sun_altitude, n1 = calc_sunset(
            t, constants.simulation_delta_t_hours, sun_altitude, observer_longitude_radians, r_23, constants.r_01
        )
    else:
        while sun_altitude < -12.0:  # It's dark, so move clock back to first dark
            t -= constants.simulation_delta_t_hours / 4.0
            sun_altitude = calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
        t += constants.simulation_delta_t_hours / 4.0
        sun_altitude = calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
    day = 0
    min_altitude = 100.0  # Initialize single-night observation variables
    max_altitude = 0.0
    score = 0.0
    time_visible = 0.0

    # Begin year-long simulation
    while day < constants.days_in_year:  # Analysis starts at first dark on first day of the year
        if sun_altitude < -12.0:
            dalt, daz = convert_ra_dec_to_alt_az(t, observer_longitude_radians, ra, dec, r_23)
            horizon_altitude = np.interp(daz, horizon_data[:, 0], horizon_data[:, 1])
            if dalt > max(min_obs_altitude, horizon_altitude):
                time_visible += constants.simulation_delta_t_hours
                max_altitude = max(max_altitude, dalt)
                min_altitude = min(min_altitude, dalt)
                score = max(score, time_visible / 10.25 * max_altitude / 90.0)
            t += constants.simulation_delta_t_hours
            sun_altitude = calc_sun_altitude(t, observer_longitude_radians, r_23, constants.r_01)
        else:
            # End of the night clean up
            if month == 0:
                damo = float(month + 1) + (float(day) / float(constants.month_last_day[month]))
            else:
                damo = (
                        float(month + 1) +
                        float(day - constants.month_last_day[month - 1]) /
                        float(constants.month_last_day[month] - constants.month_last_day[month - 1])
                )
            if min_altitude > 95.0:
                min_altitude = 0.0
            hist[day, 0:5] = np.array([damo, min_altitude, max_altitude, time_visible, score])
            if day > 1:
                # Perform moving average to smooth out curves
                hist[day - 1, 1] = np.mean(hist[day - 2:day + 1, 1])
                hist[day - 1, 2] = np.mean(hist[day - 2:day + 1, 2])
                hist[day - 1, 3] = np.mean(hist[day - 2:day + 1, 3])
                hist[day - 1, 4] = np.mean(hist[day - 2:day + 1, 4])
            min_altitude = 100.0  # Initialize single-night observation variables
            max_altitude = 0.0
            score = 0.0
            time_visible = 0.0
            day += 1
            if day == constants.month_last_day[month]:
                month += 1

            # fast-forward through daylight to sunset
            t, sun_altitude, n1 = calc_sunset(
                t,
                constants.simulation_delta_t_hours,
                sun_altitude,
                observer_longitude_radians,
                r_23,
                constants.r_01
            )

    if max(hist[:, 2]) < min_obs_peak_altitude or max(hist[:, 3]) < min_observation_hours:
        return 0  # Cannot see DSO (not high enough and/or not visible for long enough

    # Find first day when imaging score is maximum
    max_score = 0.97 * max(hist[:, 4])  # Use 0.97 to avoid small numerical fluctuation error
    kk = 0
    if hist[0, 4] < max_score:
        while hist[kk, 4] < max_score:
            kk += 1
            kk = min(max(0, kk), 364)
    else:
        kk = constants.days_in_year - 1
        while hist[kk, 4] >= max_score:
            kk -= 1
            kk = max(0, kk)
        kk += 1
        kk = min(max(0, kk), 364)
    kk = min(max(0, kk), 364)
    mo = int(hist[kk, 0])
    da = max(int((hist[kk, 0] - float(mo)) * 31.0), 1)

    max_score = max(hist[:, 4])
    row = [
        str(row_index),
        catalog_name,
        str(round(ra, 4)),
        str(round(dec, 4)),
        str(int(is_galaxy)),
        str(size),
        str(round(max_score, 2)),
        str(int(mo)),
        str(int(da))
    ]
    csv_dso_list.writerow(row)

    plt.figure(figsize=(8, 8), facecolor=(1.0, 0.8, 0.2))
    ax2 = plt.subplot2grid((3, 1), (1, 0), rowspan=2)
    ax2.set_autoscale_on(False)
    plt.xlabel("Month", fontsize=12)
    plt.ylim([0, 14])
    plt.yticks(np.arange(0, 16, 2))
    ax2.yaxis.set_minor_locator(MultipleLocator(.5))
    plt.ylabel("Hours Visible", fontsize=12)
    plt.grid(visible=True, which='major', axis='both', linestyle=':', linewidth=1)
    ax1 = plt.subplot2grid((3, 1), (0, 0), sharex=ax2)
    ax1.set_autoscale_on(False)
    plt.ylim([0, 90])
    plt.yticks(np.arange(0, 100, 10))
    plt.ylabel("Altitude (deg)", fontsize=12)
    plt.xlim([1, 12.9])
    plt.xticks(np.arange(1, 13, 1))
    ax2.plot(hist[:, 0], hist[:, 3], 'b', linewidth=2, label='Hours')
    ax1.xaxis.set_minor_locator(MultipleLocator(.25))
    ax1.yaxis.set_minor_locator(MultipleLocator(5))
    plt.grid(visible=True, which='major', axis='both', linestyle=':', linewidth=1)
    plt.plot(hist[:, 0], hist[:, 2], 'r', linewidth=1, label='Max Alt')
    plt.plot(hist[:, 0], hist[:, 1], 'g', linewidth=1, label='Min Alt')
    plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
    plot_title = f"{catalog_name}: Score = {round(max(hist[:, 4]), 2)} on {int(mo)}/{int(da)}"
    plt.title(plot_title, fontsize=16)
    out_file = f"{results_folder}/{catalog_name}.png"
    plt.savefig(out_file, format='png')
    plt.close()
    print(f"{row_index} - {catalog_name} : Complete")

    # TODO: figure out what this is...
    # fdd.write(target_name)
    # for i in range(num_days_in_year):
    #     fdd.write(", "+str(round(hist[i, 3], 2)))
    # fdd.write('\n')
    return 1
