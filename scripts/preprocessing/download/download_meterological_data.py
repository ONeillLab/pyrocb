# Sylvio Dos Reis, 2026
# Downloads the meterological data from era5

import cdsapi
import os
import sys
import json

GRIB_DIR = os.path.expandvars(f"{sys.argv[1]}/data/grib")
os.makedirs(GRIB_DIR, exist_ok=True)

with open(f'{sys.argv[1]}/profile/config.json', 'r') as f:
    data = json.load(f)
    year = data["time"]["year"]
    month = data["time"]["month"]
    day = data["time"]["day"]
    bounds = data["bounds"]

actual_bounds = [
    int(bounds[0][1] - 10), 
    int(bounds[0][0] - 10),
    int(bounds[1][1] + 10),
    int(bounds[1][0] + 10), 
]


c = cdsapi.Client()
# For our simulation, we want to simulate 21-24. But after running this script with days only 21 to 24, I didn't get data for all of 24, only the 0th hour.
# We need to include 25th day to get data about the midnight of the 24th. 
dataset1 = "reanalysis-era5-single-levels"
request1 = {
    "product_type": ["reanalysis"],
    "variable": [
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "2m_dewpoint_temperature",
        "2m_temperature",
        "mean_sea_level_pressure",
        "sea_surface_temperature",
	"surface_pressure",
        "skin_temperature",
        "snow_depth",
	"snow_density",
        "soil_temperature_level_1",
        "soil_temperature_level_2",
        "soil_temperature_level_3",
        "soil_temperature_level_4",
        "volumetric_soil_water_layer_1",
        "volumetric_soil_water_layer_2",
        "volumetric_soil_water_layer_3",
        "volumetric_soil_water_layer_4",
        "geopotential",
        "land_sea_mask",
        "sea_ice_cover"
    ],
    "year": year,
    "month": month,
    'day': day,
    'time': [
        '00:00', '01:00', '02:00',
        '03:00', '04:00', '05:00',
        '06:00', '07:00', '08:00',
        '09:00', '10:00', '11:00',
        '12:00', '13:00', '14:00',
        '15:00', '16:00', '17:00',
        '18:00', '19:00', '20:00',
        '21:00', '22:00', '23:00'
    ],
    "data_format": "grib",
    "download_format": "unarchived",
    'area': actual_bounds #North, West, South, East of largest domain. Add 5 degree buffer
}
target1 = f"{GRIB_DIR}/era5_single_levels.grib"

c.retrieve(dataset1, request1).download(target1)

print("ERA5 Single level download complete!")

dataset2 = "reanalysis-era5-pressure-levels"
request2 = {
    "product_type": ["reanalysis"],
    "variable": [
        "geopotential",
        "relative_humidity",
        "temperature",
        "u_component_of_wind",
        "v_component_of_wind"
    ],
    "year": year,
    "month": month,
    'day': day,
    "time": [
	'00:00', '01:00', '02:00',
        '03:00', '04:00', '05:00',
        '06:00', '07:00', '08:00',
        '09:00', '10:00', '11:00',
        '12:00', '13:00', '14:00',
        '15:00', '16:00', '17:00',
        '18:00', '19:00', '20:00',
        '21:00', '22:00', '23:00'
    ],
    "pressure_level": [
        "1", "2", "3",
        "5", "7", "10",
        "20", "30", "50",
        "70", "100", "125",
        "150", "175", "200",
        "225", "250", "300",
        "350", "400", "450",
        "500", "550", "600",
        "650", "700", "750",
        "775", "800", "825",
        "850", "875", "900",
        "925", "950", "975",
        "1000"
    ],
    "data_format": "grib",
    "download_format": "unarchived",
    'area': actual_bounds #North, West, South, East of largest domain. Add 5 degree buffer
}

target2 = f"{GRIB_DIR}/era5_pressure_levels.grib"

c.retrieve(dataset2, request2).download(target2)

print('ERA5-level download complete!')

print('All downloads complete!')
