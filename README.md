# AstroPlan

Based on James Lamb's Astroplan software detailed on his YouTube channel: 
[https://www.youtube.com/@Aero19612](https://www.youtube.com/@Aero19612).


## Assumptions

- Earth is a sphere
- Earth's orbit is circular
- Earth spins but does not precess
- Sun is fixed in space
- "Darkness" is when Sun's altitude at Lat, Lon < -12 deg
- All distances are small compared with distance to a DSO


## Where to get the latest Stellarium DSO Catalog

It is available in text format in their [GitHub repo](https://github.com/Stellarium/stellarium/tree/master).

Specifically the file is [here](https://github.com/Stellarium/stellarium/blob/master/nebulae/default/catalog.txt).


## Run Configurations

Run configurations (such as observer's latitude, etc) are configured using an `.ini` file.

By default, the system will look for `astroplan.ini` in your app's directory, but you can override this when
starting the app to use any other `.ini` file - this allows you to keep multiple configuration profiles and
run AstroPlan based on whatever config you want. For example you could use this to store configurations for different
observation locations, object sizes, catalog subsets, etc.

To do so, use the command line switch `-i` or `--ini`, for example:

```bash
python astroplan.py --ini astroplan_full.ini
```

These `.ini` files look like this:

```ini
[Observer]
Latitude = 33.0
Longitude = -95.0
HorizonFile = ./horizon.txt

[Filters]
MinObservationHours = 4.0
MinObservationPeakAltitude = 30.0
MinObservationAltitude = 15.0
MinDSOSize = 10.0

[Catalog]
# Set MinCatalogIndex to 1, and MaxCatalogIndex to blank to process all entries
CatalogFile = ./stellarium_catalog.txt
MinCatalogIndex = 1
MaxCatalogIndex = 

[Parallelism]
MaxParallelJobs = 6

[Output]
# Specifies an output folder where all data files are written
#   Path can be relative to where the app is running, or an absolute path
#   For a relative path, use ./ (on *nix, .\ on Windows)
# Set ClearResultsBeforeRunning to `true` to delete any pre-existing results folder
Results = ./results2
ClearResultsBeforeRunning = yes
```


### Parallelism

AstroPlan uses Python's multiprocessing facilities to process simulations and chart generation in parallel.
How many jobs are run concurrently is determined by the `MaxParallelJobs` settings.

So, question is : how should you set that value for your system?

Best is to try it out with various values, usually ranging from half to just less than the number of cores on your
computer.

For example, on a Mac M1 Max, a pure linearized strategy takes about 172s to run the full catalog.

With the same settings, only changing the value for `MaxParallelJobs` we see the following:


| `MaxParallelJobs` | Total Runtime |
|-------------------|---------------|
| 2                 | 90s           |
| 4                 | 48s           |
| 5                 | 39s           |
| 8                 | 28s           |
| **9**             | **25s**       |
| 10                | 26s           |
| 12                | 28s           |

As you can see, the sweet spot for that system appears to be 9 parallel workers.


## Sample Run Console Output

When AstroPlan runs, you will see console output letting you know what stage the app is at, and the time taken by
various processes.

```text
Starting...
	Load horizon data: 0.00 s
	Running simulations:
		- (2) M_45
		- (3) M_8
		- (4) SH2_155
		- (182) NGC_147
		- (216) NGC_185
		- (236) M_110
		- (254) M_31
		 ...
	Simulations completed: 143.41 s
	Identified:
		- Galaxies: 29
		- Nebulas: 177
	Generating outputs:
		- Data files: 0.00 s
		- DSO plots: 31.55 s
		- Horizon plot: 0.09 s
		- Global plots: 0.36 s
Completed: 175.41 s
```

## Development

Python `black` and `isort` are configured for this project.

These tools simply reformat Python code uniformly (following PEP8 standards).

The `isort` tool organizes and sorts the import statements in modules, while the `black` tool reformats
a variety of things like indentations, quotes, etc.

If you are on a *nix machine, simply use the Make command:

```bash
make lint-fix
```

On Windows, you can instead run this from a prompt:

```commandline
 isort .
```

followed by

```commandline
black .
```
