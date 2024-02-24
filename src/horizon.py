"""Horizon"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

from src.models import UserSettings


def load_data(user: UserSettings):
    return np.loadtxt(user.horizon_file, dtype="float", comments="#", delimiter=None, skiprows=0)


def plot_data(horizon_data, user: UserSettings):
    out_file = f"{user.results_path}/horizon.png"

    fig, axes = plt.subplots(1, 1, figsize=(8, 5))
    axes.set_autoscale_on(False)
    plt.plot(horizon_data[:, 0], horizon_data[:, 1])
    plt.xlim([0, 360])
    plt.xticks(np.arange(0.0, 390.0, 30.0))
    plt.yticks(np.arange(0.0, 90, 15.0))
    plt.title("Local Horizon", fontsize=16)
    axes.xaxis.set_minor_locator(MultipleLocator(10))
    axes.yaxis.set_minor_locator(MultipleLocator(5))
    plt.grid(visible=None, which="both", axis="both", linestyle=":", linewidth=1)
    plt.xlabel("Azimuth (deg)", fontsize=12)
    plt.ylabel("Altitude (deg)", fontsize=12)
    plt.savefig(out_file, format="png")
    plt.close()
