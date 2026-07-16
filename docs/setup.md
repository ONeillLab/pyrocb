# Setup
*(Built using the [WRF-Fire documentation](https://unr-wrf-fire.readthedocs.io/en/latest/Ubuntu.html) and Micah's manuscript)*

**Before running any scripts, run [``shell_setup.sh``](/shell_setup.sh) (``source shell_setup.sh``) from the repository's top level directory.**

## Setting up WRF-SFIRE on a personal computer (Linux)
*(If you are using Windows, it is recommended to use an instance of [Windows Subsystem For Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install))*

All scripts for setting up WRF-SFire for Linux are located in ``/scripts/setup``. The scripts will download all files into the ``/out/`` folder

### Downloading Dependencies
The main script for downloading the dependencies is [``/scripts/setup/dependencies.sh``](/scripts/setup/dependencies.sh). This installs libraries such as the GNU C compiler (GCC), gfortran, and other dependencies.

### Downloading Libraries
To be able to compile WRF-Fire, a few libraries are needed. These are downloaded, and compiled via the [``/scripts/setup/libraries.sh``](/scripts/setup/libraries.sh). This script will download the libraries individually (individual library download scripts are available at [``/scripts/setup/libraries/``](/scripts/setup/libraries/)).

The ``libraries.sh`` script should automatically clean up libraries as they are built. This script takes 15-20 minutes to run.

### Downloading WRF-SFIRE

To download WRF-SFIRE, run the [``/scripts/setup/wrf-sfire.sh``](/scripts/setup/wrf-sfire.sh) script. It will then prompt you to configure the WRF-SFIRE compiler. We will use the distributed memory parallel (dmpar) option for GNU [type 34]. We will then use the default basic nesting option [type 1].