"""Function to generate various Plots"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

from models import UserSettings


def make_dso_timeseries(user: UserSettings):
    with open(user.dso_list_file, "r") as f:
        # skip header row
        next(f)

        num_galaxies = 0
        num_nebulas = 0
        for line in f:
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
        ts_galaxies = np.zeros(shape=(num_galaxies, 5))
        for i in range(num_galaxies):
            ts_galaxies[i, 0] = float(galaxy[i, 7]) + float(galaxy[i, 8]) / 32.0  # Month/day
            ts_galaxies[i, 1] = float(galaxy[i, 6])  # Score
            ts_galaxies[i, 2] = float(galaxy[i, 2])  # RA
            ts_galaxies[i, 3] = float(galaxy[i, 3])  # DEC
            ts_galaxies[i, 4] = float(galaxy[i, 5])  # size
        ts_nebulas = np.zeros(shape=(num_nebulas, 5))
        for i in range(num_nebulas):
            ts_nebulas[i, 0] = float(nebula[i, 7]) + float(nebula[i, 8]) / 32.0  # Month/day
            ts_nebulas[i, 1] = float(nebula[i, 6])  # Score
            ts_nebulas[i, 2] = float(nebula[i, 2])  # RA
            ts_nebulas[i, 3] = float(nebula[i, 3])  # DEC
            ts_nebulas[i, 4] = float(nebula[i, 5])  # size

        return num_galaxies, num_nebulas, ts_galaxies, ts_nebulas


def plot_visible_dsos(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user: UserSettings):
    out_file = f"{user.results_path}/Visible_DSOs_{user.catalog_id_range}.png"
    fig, axes = plt.subplots(1, 1, figsize=(8, 5))
    axes.set_autoscale_on(False)
    plt.plot(ts_galaxies[:, 0], ts_galaxies[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
             label="Galaxy (" + str(num_galaxies) + ")")
    plt.plot(ts_nebulas[:, 0], ts_nebulas[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
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


def plot_visible_dec_ra_map(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user: UserSettings):
    out_file = f"{user.results_path}/Visible_DEC-RA_Map_{user.catalog_id_range}.png"
    fig, axes = plt.subplots(1, 1, figsize=(8, 5))
    axes.set_autoscale_on(False)
    plt.plot(ts_galaxies[:, 2], ts_galaxies[:, 3], color='b', marker='8', markeredgecolor="black", linestyle='',
             label="Galaxy (" + str(num_galaxies) + ")")
    plt.plot(ts_nebulas[:, 2], ts_nebulas[:, 3], color='r', marker='v', markeredgecolor="black", linestyle='',
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


def plot_visible_score_dec_map(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user: UserSettings):
    out_file = f"{user.results_path}/Visible_Score-DEC_Map_{user.catalog_id_range}.png"
    fig, axes = plt.subplots(1, 1, figsize=(8, 5))
    axes.set_autoscale_on(False)
    plt.plot(ts_galaxies[:, 3], ts_galaxies[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
             label="Galaxy (" + str(num_galaxies) + ")")
    plt.plot(ts_nebulas[:, 3], ts_nebulas[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
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


def plot_score_vs_size_map(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user: UserSettings):
    out_file = f"{user.results_path}/Score_vs_Size_Map_{user.catalog_id_range}.png"
    fig, axes = plt.subplots(1, 1, figsize=(8, 5))
    axes.set_autoscalex_on(True)
    axes.set_autoscaley_on(False)
    plt.plot(ts_galaxies[:, 4], ts_galaxies[:, 1], color='b', marker='8', markeredgecolor="black", linestyle='',
             label="Galaxy (" + str(num_galaxies) + ")")
    plt.plot(ts_nebulas[:, 4], ts_nebulas[:, 1], color='r', marker='v', markeredgecolor="black", linestyle='',
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


def generate_global_plots(user: UserSettings):
    num_galaxies, num_nebulas, ts_galaxies, ts_nebulas = make_dso_timeseries(user)
    plot_visible_dsos(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user)
    plot_visible_dec_ra_map(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user)
    plot_visible_score_dec_map(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user)
    plot_score_vs_size_map(num_galaxies, num_nebulas, ts_galaxies, ts_nebulas, user)


def plot_dso(catalog_name, max_score_month, max_score_day, time_series, user: UserSettings):
    out_file = f"{user.results_path}/{catalog_name}.png"

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
    ax2.plot(time_series[:, 0], time_series[:, 3], 'b', linewidth=2, label='Hours')
    ax1.xaxis.set_minor_locator(MultipleLocator(.25))
    ax1.yaxis.set_minor_locator(MultipleLocator(5))
    plt.grid(visible=True, which='major', axis='both', linestyle=':', linewidth=1)
    plt.plot(time_series[:, 0], time_series[:, 2], 'r', linewidth=1, label='Max Alt')
    plt.plot(time_series[:, 0], time_series[:, 1], 'g', linewidth=1, label='Min Alt')
    plt.legend(loc='best', shadow=True, ncol=1, frameon=True)

    max_score = round(max(time_series[:, 4]), 2)
    plot_title = f"{catalog_name}: Score = {max_score} on {int(max_score_month)}/{int(max_score_day)}"
    plt.title(plot_title, fontsize=16)

    plt.savefig(out_file, format='png')
    plt.close()
