# AstroPlan
Fork of James Lamb's Python AstroPlan


## Assumptions

- Earth is a sphere
- Earth's orbit is circular
- Earth spins but does not precess
- Sun is fixed in space
- "Darkness" is when Sun's altitude at Lat, Lon < -12 deg
- All distances are small compared with distance to a DSO

## Where to get the latest Stellarium DSO Catalog
It is available in text format on their [GitHub repo](https://github.com/Stellarium/stellarium/tree/master).

Specifically the file is [here](https://github.com/Stellarium/stellarium/blob/master/nebulae/default/catalog.txt).

## Run Configurations
Run configurations (such as observer's latitude, etc) are configured using an `.ini` file.

By default, the system will look for `astroplan.ini` in your app's directory, but you can override this when 
starting the app to use any other `.ini` file - this allows you to keep multiple configuration profiles and 
run AstroPlan based on whatever config you want.

To do so, use the command line switch `-i` or `--ini`, for example:
```bash
python astroplan.py --ini astroplan2.ini
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

[Output]
# Specifies an output folder where all data files are written
#   Path can be relative to where the app is running, or an absolute path
#   For a relative path, use ./ (on *nix, .\ on Windows)
# Set ClearResultsBeforeRunning to `true` to delete any pre-existing results folder
Results = ./results2
ClearResultsBeforeRunning = yes
```


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
