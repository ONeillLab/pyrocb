# End to End: Running the WRF-SFIRE Ideal Case on your personal Computer.
This documentation is for Linux and [Windows Subsystem For Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). 

*(If you are using Windows, it is recommended to use an instance of [Windows Subsystem For Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install))*


To run the ideal case on your personal computer, start in the top level directory from this repo, and run ``shell_setup.sh`` from source:
```sh
source shell_setup.sh
```


Then run each of the [setup scripts](/docs/setup.md) in [/scripts/setup/](/scripts/setup/) sequentially:
```sh
cd ./scripts
bash ./setup/dependencies.sh
bash ./setup/libraries.sh
bash ./setup/wrf-sfire.sh
```

Next, to compile the WRF-SFIRE, run the [compile script](/docs/compile.md#compiling-wrf-sfire-for-ideal-cases-on-a-personal-computer-linux) ([``/scripts/compile/personal-ideal.sh``](/scripts/compile/personal-ideal.sh))

```sh
bash ./compile/personal-ideal.sh
```

Lastly, to run the ideal case, run the [running script](/docs/run.md#running-wrf-sfire-for-ideal-cases-on-a-personal-computer-linux) ([``/scripts/run/personal-ideal.sh``](/scripts/run/personal-ideal.sh)):
```sh
bash ./run/personal-ideal.sh
```