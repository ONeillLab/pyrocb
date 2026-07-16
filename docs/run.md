# Running
## Running WRF-SFIRE for ideal cases on a personal computer (Linux)
To run WRF-SFIRE for ideal cases, run the [``/scripts/run/personal-ideal.sh``](/scripts/run/personal-ideal.sh) script.
You can change which simulation is ran by changing the ``PCB_PERSONAL_IDEAL_CASE`` environmental variable (first line of the script). Example:
```sh
export $PCB_PERSONAL_IDEAL_CASE= "two_fires"
```

File will be automatically copied to the [``/out/output/wrf/``](/out/output/wrf/) directory with log files being in [``/out/output/wrf/logs/``](/out/output/wrf/logs/) and data files being in [``/out/output/wrf/data/``](/out/output/wrf/data/)
