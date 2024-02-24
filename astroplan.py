import math
import os.path
import csv
import numpy as np

import constants
import simulator
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from time import perf_counter

start_counter = perf_counter()

pi = math.pi
observer_latitude = 0.0
observer_longitude = 0.0
min_observation_hours = 4.0
min_obs_peak_altitude = 30.0
min_obs_altitude = 15.0
min_dso_size = 10.0
min_catalog_id = 1
max_catalog_id = 2000
horizon_file = "--Enter Filename--"
if os.path.isfile("astroplan.ini"):
    fp = open("astroplan.ini", "r")
    observer_latitude = float(fp.readline().rstrip('\n'))
    observer_longitude = float(fp.readline().rstrip('\n'))
    horizon_file = fp.readline().rstrip('\n')
    min_observation_hours = float(fp.readline().rstrip('\n'))
    min_obs_peak_altitude = float(fp.readline().rstrip('\n'))
    min_obs_altitude = float(fp.readline().rstrip('\n'))
    min_dso_size = float(fp.readline().rstrip('\n'))
    min_catalog_id = int(fp.readline().rstrip('\n'))
    max_catalog_id = int(fp.readline().rstrip('\n'))
    fp.close()

# Get User inputs
# observer_latitude = float(
#     input("Enter Latitude  [" + str(round(observer_latitude, 6)) + "]: ") or round(observer_latitude, 6))
# observer_longitude = float(
#     input("Enter Longitude [" + str(round(observer_longitude, 6)) + "]: ") or round(observer_longitude, 6))
# horizon_file = input("Enter Local Horizon Filename [" + horizon_file + "]: ") or horizon_file
# if not os.path.isfile(horizon_file):
#     while not os.path.isfile(horizon_file):
#         print("User-defined horizon file [" + horizon_file + "] not found")
#         horizon_file = input("Enter Local Horizon Filename [" + horizon_file + "]: ") or horizon_file
# min_observation_hours = float(
#     input("Enter Minimum Observation Time  [" + str(round(min_observation_hours, 1)) + "]: ") or round(
#         min_observation_hours, 1))
# min_obs_peak_altitude = float(
#     input("Enter Minimum Peak Altitude  [" + str(round(min_obs_peak_altitude, 1)) + "]: ") or round(
#         min_obs_peak_altitude, 1))
# min_obs_altitude = float(
#     input("Enter Minimum Observation Altitude  [" + str(round(min_obs_altitude, 1)) + "]: ") or round(min_obs_altitude,
#                                                                                                       1))
# min_dso_size = float(input("Enter Minimum DSO Size  [" + str(round(min_dso_size, 1)) + "]: ") or round(min_dso_size, 1))
# min_catalog_id = int(input("Enter Lowest Catalog ID  [" + str(int(min_catalog_id)) + "]: ") or int(min_catalog_id))
# max_catalog_id = int(input("Enter Highest Catalog ID  [" + str(int(max_catalog_id)) + "]: ") or int(max_catalog_id))

# ---------------------------------
fp = open("astroplan.ini", "w")
fp.write(str(round(observer_latitude, 6)) + '\n')
fp.write(str(round(observer_longitude, 6)) + '\n')
fp.write(horizon_file + '\n')
fp.write(str(round(min_observation_hours, 1)) + '\n')
fp.write(str(round(min_obs_peak_altitude, 1)) + '\n')
fp.write(str(round(min_obs_altitude, 1)) + '\n')
fp.write(str(round(min_dso_size, 1)) + '\n')
fp.write(str(int(min_catalog_id)) + '\n')
fp.write(str(int(max_catalog_id)) + '\n')
fp.close()
if not os.path.isfile(horizon_file):
    print("ERROR: User-defined local horizon file [" + horizon_file + "] not found.")
    exit()
# -----------------------------------
if observer_latitude > 0.0:
    min_obs_peak_dec = observer_latitude - 90.0 + min_obs_peak_altitude
    print("Target DEC limit > " + str(round(min_obs_peak_dec, 2)))
else:
    min_obs_peak_dec = observer_latitude + 90.0 - min_obs_peak_altitude
    print("Target DEC limit < " + str(round(min_obs_peak_dec, 2)))
observer_latitude_radians = observer_latitude * pi / 180.0
observer_longitude_radians = observer_longitude * pi / 180.0

# -----------------------------------------------------------------------------
# Set output folder
RESULTS_FOLDER = "results"
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# -----------------------------------------------------------------------------
# Load Horizon Data
horizon_data = np.loadtxt(horizon_file, dtype='float', comments='#', delimiter=None, skiprows=0)

# Plot Horizon Data
out_file = f"{RESULTS_FOLDER}/horizon.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(horizon_data[:, 0], horizon_data[:, 1])
plt.xlim([0, 360])
plt.xticks(np.arange(0.0, 390.0, 30.0))
plt.yticks(np.arange(0.0, 90, 15.0))
plt.title("Local Horizon", fontsize=16)
axes.xaxis.set_minor_locator(MultipleLocator(10))
axes.yaxis.set_minor_locator(MultipleLocator(5))
plt.grid(visible=None, which='both', axis='both', linestyle=':', linewidth=1)
plt.xlabel("Azimuth (deg)", fontsize=12)
plt.ylabel("Altitude (deg)", fontsize=12)
plt.savefig(out_file, format='png')
plt.close()

# ------------------------------------------------------------------------------
# Open Files:
# - Stellarium catalog (input)
# - Local catalog (output) - a Stellarium formatted file of DSOs that matched filter criteria
#       > File can later be used in Stellarium to only view DSOs of interest - but something about binary format
# - DSO List (output) - custom list of DSO objects that matched the filter criteria

STELLARIUM_FILE_NAME = "stellarium_catalog.txt"
local_catalog_file_name = f"{RESULTS_FOLDER}/local_catalog_{min_catalog_id}_{max_catalog_id}.txt"
dso_list_file_name = f"{RESULTS_FOLDER}/DSO_list_{min_catalog_id}_{max_catalog_id}.csv"

f_stellarium = open(STELLARIUM_FILE_NAME, "rt")
f_local_catalog = open(local_catalog_file_name, "wt")
f_dso_list = open(dso_list_file_name, 'w', newline='')

# ------------------------------------------------------------------------------
# Create CSV writer for DSO list, and printer header row
# orbit.dso() as side-effect of writing data to this file, as well as returning a flag indicating if DSO object
#   should be included in list
csv_dso_list = csv.writer(f_dso_list, dialect='excel')
csv_dso_list.writerow(['No.', 'Name', 'RA (deg)', 'DEC (deg)', 'Type', 'Size', 'Score', 'Month', 'Day'])

# -------------------------------------------------------------------------------
# Loop through Stellarium data and process
R23 = np.array([
    [1.0, 0.0, 0.0],
    [0.0, np.cos(observer_latitude_radians), np.sin(observer_latitude_radians)],
    [0.0, -np.sin(observer_latitude_radians), np.cos(observer_latitude_radians)]
])

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

        if row_id < min_catalog_id:
            continue
        elif row_id > max_catalog_id:
            break

        if (
                object_nominal_size > min_dso_size and
                object_type in constants.included_dso_types and
                (
                        (observer_latitude > 0 and object_dec_degrees > min_obs_peak_dec) or
                        (observer_latitude <= 0 and object_dec_degrees < min_obs_peak_dec)
                )
        ):
            if simulator.dso(
                r_23=R23,
                observer_longitude_radians=observer_longitude_radians,
                horizon_data=horizon_data,
                stellarium_row_data=stellarium_row_data,
                csv_dso_list=csv_dso_list,
                min_observation_hours=min_observation_hours,
                min_obs_peak_altitude=min_obs_peak_altitude,
                min_obs_altitude=min_obs_altitude,
                results_folder=RESULTS_FOLDER,
            ) == 1:
                # write out Stellarium record as is to stellarium local catalog file (for use in Stellarium)
                f_local_catalog.write(stellarium_row)

# Close all files - no more writing data files
f_stellarium.close()
f_local_catalog.close()
f_dso_list.close()

# -------------------------------------------------------------------------------
f_dso_list = open(dso_list_file_name, 'r', newline='')
line = f_dso_list.readline()
ng = 0
nn = 0
for line in f_dso_list:
    stellarium_row_data = line.split(',')
    arr = np.array(stellarium_row_data).reshape(1, 9)
    if arr[0, 4] == '1':
        if ng == 0:
            gal = arr
        else:
            gal = np.vstack((gal, arr))
        ng += 1
    else:
        if nn == 0:
            neb = arr
        else:
            neb = np.vstack((neb, arr))
        nn += 1
print("Galaxies = " + str(ng) + "    Nebulae = " + str(nn))
tgal = np.zeros(shape=(ng, 5))
for i in range(ng):
    tgal[i, 0] = float(gal[i, 7]) + float(gal[i, 8]) / 32.0  # Month/day
    tgal[i, 1] = float(gal[i, 6])  # Score
    tgal[i, 2] = float(gal[i, 2])  # RA
    tgal[i, 3] = float(gal[i, 3])  # DEC
    tgal[i, 4] = float(gal[i, 5])  # size
tneb = np.zeros(shape=(nn, 5))
for i in range(nn):
    tneb[i, 0] = float(neb[i, 7]) + float(neb[i, 8]) / 32.0  # Month/day
    tneb[i, 1] = float(neb[i, 6])  # Score
    tneb[i, 2] = float(neb[i, 2])  # RA
    tneb[i, 3] = float(neb[i, 3])  # DEC
    tneb[i, 4] = float(neb[i, 5])  # size
f_dso_list.close()

# -----------------------------------------------------------------------------------
# Plot Visible_DSOs
out_file = f"{RESULTS_FOLDER}/Visible_DSOs_{min_catalog_id}-{max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 0], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(ng) + ")")
plt.plot(tneb[:, 0], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(nn) + ")")
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
out_file = f"{RESULTS_FOLDER}/Visible_DEC-RA_Map_{min_catalog_id}-{max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 2], tgal[:, 3], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(ng) + ")")
plt.plot(tneb[:, 2], tneb[:, 3], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(nn) + ")")
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
out_file = f"{RESULTS_FOLDER}/Visible_Score-DEC_Map_{min_catalog_id}-{max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscale_on(False)
plt.plot(tgal[:, 3], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(ng) + ")")
plt.plot(tneb[:, 3], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(nn) + ")")
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
out_file = f"{RESULTS_FOLDER}/Score_vs_Size_Map_{min_catalog_id}-{max_catalog_id}.png"
fig, axes = plt.subplots(1, 1, figsize=(8, 5))
axes.set_autoscalex_on(True)
axes.set_autoscaley_on(False)
plt.plot(tgal[:, 4], tgal[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
         label="Galaxy (" + str(ng) + ")")
plt.plot(tneb[:, 4], tneb[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
         label="Nebula (" + str(nn) + ")")
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
