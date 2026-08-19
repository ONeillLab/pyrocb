# pyrocb

Simulating pyrocumulonimbus clouds with WRF-SFIRE in the O'Neil Group at the University of Toronto

**Before running any scripts, run [``shell_setup.sh``](/shell_setup.sh) (``source shell_setup.sh``) from the current directory.**

## Contributing

To keep things clean and avoid conflicting edits on the ``main`` branch, in order to contribute to the repository, please create branches and edit on your branch before creating a pull request to move your changes to the ``main`` branch.

If you are using Mac or Windows, the easiest way to manage edits is with the [GitHub Desktop App](https://github.com/apps/desktop). I will also provide command line instructions. First, clone the repository to your local computer (``git clone https://github.com/ONeillLab/pyrocb.git``). To refresh the repository and see new changes, you can ``pull`` the changes from ``origin`` (``git pull``). 

You can create a new branch (``git branch [branch-name]``), and switch to it (``git checkout [branch-name]``). To save your changes, you can commit them (``git commit -a -m [description of commit]``) and ``push`` them to ``origin`` (``git push``).

To create a pull request and place it into the main branch, go to the [pull requests tab on GitHub](https://github.com/ONeillLab/pyrocb/pulls), hit ["New Pull Request"](https://github.com/ONeillLab/pyrocb/compare), select your branch as the ``compare`` branch, and hit "Create Pull Request".

Documentation should be include in the [/docs/](/docs/) folder for all pieces of code, explaining how it is used. Configuration files for different runs will be stored in the [/profiles/](/profiles/) folder. All scripts should be kept in the [/scripts/](/scripts/) folder.

**Anything placed in the [/out/](/out/) folder will not be saved.** Please download all large datasets, files, and data (such as the WRF-SFIRE model, geographic and atmospheric data, or WRF-SFIRE model output files.) to the [/out/](/out/) folder to avoid having extremely large commits.

 Commit (save) history is stored permanently, and as this is a public repository, will be visible to everyone. Do not commit any code that has API keys, passwords, or other personal private information. If this information is needed and cannot be placed in the [/out/](/out/) directory, modify the [.gitignore](.gitignore) to include it.

## Pages
To see all documentation, go to [/docs/](/docs/).

 - [/docs/setup.md](/docs/setup.md): setting up the WRF-SFIRE model
 - [/docs/compile.md](/docs/compile.md): compiling the WRF-SFIRE model for various cases
 - [/docs/run.md](/docs/run.md): running the WRF-SFIRE model for various cases
 - [/docs/personal-ideal.md](/docs/personal-ideal.md): end to end instructions for running the WRF-SFIRE model for the ideal case.
 - [/docs/alliance-can-real.md](docs/alliance-can-real.md): end to end instructions for running the WRF-SFIRE model for a real case.