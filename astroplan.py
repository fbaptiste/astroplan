import csv
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

import constants
import horizon
import simulator
from settings import user


start_counter = perf_counter()

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
csv_dso_list = csv.writer(f_dso_list, dialect='excel')
csv_dso_list.writerow(['No.', 'Name', 'RA (deg)', 'DEC (deg)', 'Type', 'Size', 'Score', 'Month', 'Day'])

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
        object_size_major_axis_arcmin = float(stellarium_row_data[7])
        object_size_minor_axis_arcmin = float(stellarium_row_data[8])
        object_nominal_size = max(object_size_major_axis_arcmin, object_size_minor_axis_arcmin)
        object_type = stellarium_row_data[5].strip()

        if row_id < user.min_catalog_id:
            continue
        elif row_id > user.max_catalog_id:
            break

        if (
                object_nominal_size > user.min_dso_size and
                object_type in constants.included_dso_types and
                (
                        (user.observer_latitude > 0 and object_dec_degrees > user.min_obs_peak_dec) or
                        (user.observer_latitude <= 0 and object_dec_degrees < user.min_obs_peak_dec)
                )
        ):
            if simulator.dso(
                r_23=user.r23,
                observer_longitude_radians=user.observer_longitude_radians,
                horizon_data=horizon_data,
                stellarium_row_data=stellarium_row_data,
                csv_dso_list=csv_dso_list,
                min_obs_hours=user.min_obs_hours,
                min_obs_peak_altitude=user.min_obs_peak_altitude,
                min_obs_altitude=user.min_obs_altitude,
                results_folder=user.results_path,
            ) == 1:
                # write out Stellarium record as is to stellarium local catalog file (for use in Stellarium)
                f_local_catalog.write(stellarium_row)

# Close all files - no more writing data files
f_stellarium.close()
f_local_catalog.close()
f_dso_list.close()

# -------------------------------------------------------------------------------
f_dso_list = open(user.dso_list_file, 'r', newline='')
line = f_dso_list.readline()
num_galaxies = 0
num_nebulas = 0
for line in f_dso_list:
    stellarium_row_data = line.split(',')
    arr = np.array(stellarium_row_data).reshape(1, 9)
    if arr[0, 4] == '1':
        if num_galaxies == 0:
            galaxy = arr
        else:
            galaxy = np.vstack((galaxy, arr))
        num_galaxies += 1
    else:
        if num_nebulas == 0:
            nebula = arr
        else:
            nebula = np.vstack((nebula, arr))
        num_nebulas += 1
print("Galaxies = " + str(num_galaxies) + "    Nebulae = " + str(num_nebulas))
tgal = np.zeros(shape=(num_galaxies, 5))
for i in range(num_galaxies):
    tgal[i, 0] = float(galaxy[i, 7]) + float(galaxy[i, 8]) / 32.0  # Month/day
    tgal[i, 1] = float(galaxy[i, 6])  # Score
    tgal[i, 2] = float(galaxy[i, 2])  # RA
    tgal[i, 3] = float(galaxy[i, 3])  # DEC
    tgal[i, 4] = float(galaxy[i, 5])  # size
tneb = np.zeros(shape=(num_nebulas, 5))
for i in range(num_nebulas):
    tneb[i, 0] = float(nebula[i, 7]) + float(nebula[i, 8]) / 32.0  # Month/day
    tneb[i, 1] = float(nebula[i, 6])  # Score
    tneb[i, 2] = float(nebula[i, 2])  # RA
    tneb[i, 3] = float(nebula[i, 3])  # DEC
    tneb[i, 4] = float(nebula[i, 5])  # size
f_dso_list.close()

# -----------------------------------------------------------------------------------
# Plot Visible_DSOs
out_file = f"{user.results_path}/Visible_DSOs_{user.min_catalog_id}-{user.max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 0], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(num_galaxies) + ")")
plt.plot(tneb[:, 0], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(num_nebulas) + ")")
plt.xlim([1, 12.9])
plt.xticks(np.arange(1, 13, 1))
plt.ylim([0.0, 1.25])
plt.yticks(np.arange(0, 1.50, 0.25))
axes.xaxis.set_minor_locator(MultipleLocator(0.25))
axes.yaxis.set_minor_locator(MultipleLocator(0.05))
plt.grid(visible=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Visible Targets", fontsize=16)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Imaging Score", fontsize=12)
plt.savefig(out_file, format='png')
plt.close()

# ----------------------------------
# Plot Visible_DEC-RA_Map
out_file = f"{user.results_path}/Visible_DEC-RA_Map_{user.min_catalog_id}-{user.max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 2], tgal[:, 3], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(num_galaxies) + ")")
plt.plot(tneb[:, 2], tneb[:, 3], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(num_nebulas) + ")")
plt.xlim([0, 360])
plt.xticks(np.arange(0, 390, 30))
axes.xaxis.set_minor_locator(MultipleLocator(10))
plt.ylim([-90.0, 90.0])
plt.yticks(np.arange(-90.0, 105.0, 15.0))
axes.yaxis.set_minor_locator(MultipleLocator(5))
plt.grid(visible=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Visible DSOs: RA and DEC", fontsize=16)
plt.xlabel("RA (deg)", fontsize=12)
plt.ylabel("DEC (deg)", fontsize=12)
plt.savefig(out_file, format='png')
plt.close()

# ----------------------------------
# Plot Visible_Score-DEC_Map
out_file = f"{user.results_path}/Visible_Score-DEC_Map_{user.min_catalog_id}-{user.max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 3], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(num_galaxies) + ")")
plt.plot(tneb[:, 3], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(num_nebulas) + ")")
plt.xlim([-90.0, 90.0])
plt.xticks(np.arange(-90.0, 105.0, 15.0))
axes.xaxis.set_minor_locator(MultipleLocator(5))
plt.ylim([0.0, 1.25])
plt.yticks(np.arange(0, 1.50, 0.25))
axes.yaxis.set_minor_locator(MultipleLocator(0.05))
plt.grid(visible=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Imaging Score VS DSO DEC", fontsize=16)
plt.xlabel("DEC (deg)", fontsize=12)
plt.ylabel("Imaging Score", fontsize=12)
plt.savefig(out_file, format='png')
plt.close()

# ----------------------------------
# Plot Score_vs_Size_Map
out_file = f"{user.results_path}/Score_vs_Size_Map_{user.min_catalog_id}-{user.max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscalex_on(True)
axes.set_autoscaley_on(False)
plt.plot(tgal[:, 4], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(num_galaxies) + ")")
plt.plot(tneb[:, 4], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(num_nebulas) + ")")
plt.ylim([0.0, 1.25])
plt.yticks(np.arange(0, 1.50, 0.25))
axes.yaxis.set_minor_locator(MultipleLocator(0.05))
plt.grid(visible=None, which='major', axis='both', linestyle=':', linewidth=1)
plt.legend(loc='best', shadow=True, ncol=1, frameon=True)
plt.title("Imaging Score VS DSO Size", fontsize=16)
plt.xlabel("Size (arc-min)", fontsize=12)
plt.ylabel("Imaging Score", fontsize=12)
plt.savefig(out_file, format='png')
plt.close()

end_counter = perf_counter()
print(f"Total elapsed: {end_counter - start_counter:.2f}s")
