import csv
from math import pi
from time import perf_counter

import constants
import horizon
import plots
import simulator
import utils
from settings import user


def main():
    # Plot Horizon
    horizon_data = horizon.load_data()
    horizon.plot_data(horizon_data)

    # ------------------------------------------------------------------------------
    # Open Files:
    # - Stellarium catalog (input)
    # - Local catalog (output) - a Stellarium formatted file of DSOs that matched filter criteria
    #       > File can later be used in Stellarium to only view DSOs of interest - but something about binary format
    # - DSO List (output) - custom list of DSO objects that matched the filter criteria

    f_stellarium = open(user.catalog_file, "rt")
    f_local_catalog = open(user.local_catalog_file, "wt")
    f_dso_list = open(user.dso_list_file, 'w', newline='')

    # ------------------------------------------------------------------------------
    # Create CSV writer for DSO list, and printer header row
    # orbit.dso() as side-effect of writing data to this file, as well as returning a flag indicating if DSO object
    #   should be included in list
    csv_output_file = csv.writer(f_dso_list, dialect='excel')
    csv_output_file.writerow(['No.', 'Name', 'RA (deg)', 'DEC (deg)', 'Type', 'Size', 'Score', 'Month', 'Day'])

    # -------------------------------------------------------------------------------
    # Loop through Stellarium data and process
    for stellarium_row in f_stellarium:
        if stellarium_row.startswith("#"):
            # header row - just write it out as-is
            # TODO: fix bug - this prints out comment rows in the middle of the data as well as headers
            f_local_catalog.write(stellarium_row)
        else:
            stellarium_row_data = stellarium_row.split('\t')
            row_id = int(stellarium_row_data[0])

            if len(stellarium_row_data) != constants.stellarium_field_count:
                print(f"Stellarium record length not correct: {row_id}")

            # Extract data needed from Stellarium data
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
            elif row_id > user.max_catalog_id:
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

                sim_run_result = simulator.dso(
                    row_id=row_id,
                    catalog_name=catalog_name,
                    is_galaxy=is_galaxy,
                    object_ra_radians=object_ra_radians,
                    object_dec_radians=object_dec_radians,
                    object_size=object_max_size,
                    horizon_data=horizon_data,
                    csv_output_file=csv_output_file,
                )
                if sim_run_result:
                    # write out Stellarium record as is to stellarium local catalog file (for use in Stellarium)
                    f_local_catalog.write(stellarium_row)

    # Close all files - no more writing data files
    f_stellarium.close()
    f_local_catalog.close()
    f_dso_list.close()

    # Generate global plots
    plots.generate_global_plots()


if __name__ == '__main__':
    start_counter = perf_counter()
    main()
    end_counter = perf_counter()
    print(f"Total elapsed: {end_counter - start_counter:.2f}s")