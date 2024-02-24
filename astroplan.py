"""Main AstroPlan Application"""

import argparse
from time import perf_counter

from src import constants, settings, utils
from src.main import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="AstroPlan", epilog="Based on original work by James Lamb (https://www.youtube.com/@Aero19612)"
    )
    parser.add_argument("-i", "--ini", default=constants.default_ini_file)
    args = parser.parse_args()
    print("Starting...")
    print(f"Using ini file: {args.ini}")

    global_start_time = perf_counter()
    main(user=settings.read_settings(args.ini))
    utils.print_elapsed_time("Completed", global_start_time)
