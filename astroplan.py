import argparse
import csv
from math import pi
from time import perf_counter

import constants
import horizon
import plots
import settings
import simulator
import utils
from models import SimResult, UserSettings


def main(user: UserSettings):
    start_time = perf_counter()
    print(f"\tLimiting Stellarium catalog: {user.catalog_id_range}")
    print("\tRunning simulations:")
    horizon_data = horizon.load_data(user=user)
    stellarium_headers, local_catalog_results, dso_results, num_galaxies, num_nebulas = run_simulations(
        horizon_data, user=user
    )
    utils.print_elapsed_time("\tSimulations completed", start_time)

    print("\tIdentified:")
    print(f"\t\t- Galaxies: {num_galaxies}")
    print(f"\t\t- Nebulas: {num_nebulas}")

    print("\tGenerating outputs:")
    start_time = perf_counter()
    generate_file_outputs(
        stellarium_headers=stellarium_headers,
        local_catalog_results=local_catalog_results,
        dso_results=dso_results,
        user=user,
    )
    utils.print_elapsed_time("\t\t- Data files", start_time)

    # Generate individual DSO plots
    start_time = perf_counter()
    generate_dso_plots(dso_results, user=user)
    utils.print_elapsed_time("\t\t- DSO plots", start_time)

    # Generate Horizon plot
    start_time = perf_counter()
    horizon.plot_data(horizon_data, user=user)
    utils.print_elapsed_time("\t\t- Horizon plot", start_time)

    # Generate global plots
    start_time = perf_counter()
    plots.generate_global_plots(user=user)
    utils.print_elapsed_time("\t\t- Global plots", start_time)


def run_simulations(horizon_data, user: UserSettings):
    stellarium_headers = []
    local_catalog_results = []
    dso_results = []

    reached_stellarium_data = False
    with open(user.catalog_file) as f_stellarium:
        for stellarium_row in f_stellarium:
            if stellarium_row.startswith("#"):
                if not reached_stellarium_data:
                    stellarium_headers.append(stellarium_row)
            else:
                reached_stellarium_data = True
                stellarium_row_data = stellarium_row.split('\t')
                row_id = int(stellarium_row_data[0])

                # Extract needed Stellarium data
                object_dec_degrees = float(stellarium_row_data[2])
                object_ra_degrees = float(stellarium_row_data[2])
                object_ra_radians = object_ra_degrees * pi / 180.0
                object_dec_radians = object_dec_degrees * pi / 180.0

                object_size_major_axis_arcmin = float(stellarium_row_data[7])
                object_size_minor_axis_arcmin = float(stellarium_row_data[8])
                object_max_size = max(object_size_major_axis_arcmin, object_size_minor_axis_arcmin)
                object_type = stellarium_row_data[5].strip()

                if row_id < user.min_catalog_id:
                    continue
                elif user.max_catalog_id is not None and row_id > user.max_catalog_id:
                    break

                if (
                    object_max_size > user.min_dso_size and
                    object_type in constants.included_dso_types and
                    (
                        (user.observer_latitude > 0 and object_dec_degrees > user.min_obs_peak_dec) or
                        (user.observer_latitude <= 0 and object_dec_degrees < user.min_obs_peak_dec)
                    )
                ):
                    catalog_name, is_galaxy = utils.catalog_info(stellarium_row_data)
                    if catalog_name is None or is_galaxy is None:
                        # Either not in desired catalog, or not in DSO types of interest
                        continue

                    result = simulator.run_dso(
                        row_id=row_id,
                        catalog_name=catalog_name,
                        is_galaxy=is_galaxy,
                        object_ra_radians=object_ra_radians,
                        object_dec_radians=object_dec_radians,
                        object_size=object_max_size,
                        horizon_data=horizon_data,
                        user=user,
                    )
                    if result.is_included:
                        dso_results.append(result)
                        local_catalog_results.append(stellarium_row)
                        print(f"\t\t- ({result.catalog_id}) {result.catalog_name}")

    num_galaxies = sum(1 for r in dso_results if r.is_galaxy)
    num_nebulas = len(dso_results) - num_galaxies

    return stellarium_headers, local_catalog_results, dso_results, num_galaxies, num_nebulas


def generate_file_outputs(stellarium_headers, local_catalog_results, dso_results, user: UserSettings):
    out_file = f"{user.local_catalog_file}"
    with open(out_file, "w") as f_local_catalog:
        for row in stellarium_headers:
            f_local_catalog.write(row)
        for row in local_catalog_results:
            f_local_catalog.write(row)

    # Generate DSO list file
    with open(user.dso_list_file, "w") as f_dso_list:
        csv_writer = csv.writer(f_dso_list)
        csv_writer.writerow(SimResult.csv_row_headers())
        for row in dso_results:
            csv_writer.writerow(row.csv_row)


def generate_dso_plots(dso_results, user: UserSettings):
    for dso_result in dso_results:
        plots.plot_dso(
            catalog_name=dso_result.catalog_name,
            month=dso_result.max_month,
            day=dso_result.max_day,
            time_series=dso_result.time_series,
            user=user,
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="AstroPlan",
        epilog="Based on original work by James Lamb (https://www.youtube.com/@Aero19612)"
    )
    parser.add_argument("-i", "--ini", default=constants.default_ini_file)
    args = parser.parse_args()
    print("Starting...")
    print(f"Using ini file: {args.ini}")

    global_start_time = perf_counter()
    main(user=settings.read_settings(args.ini))
    utils.print_elapsed_time("Completed", global_start_time)
