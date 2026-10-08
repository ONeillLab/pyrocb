# Sylvio Dos Reis, 2026
# This files copies the files from the out/profile_ln directory into the out/profile directory, while replacing any environment variables that might be located.
# ------------ vvvv IMPORTANT vvvv ------------------
# It is very important that this file be run before any reading of the out/profile directory, incase modifications were made to the profile.
# ------------ ^^^^ IMPORTANT ^^^^ ------------------
# Note: this only resolve environment variables in the top level of /profile, not in an subdirectories.

import shutil
import os
import re

profile_ln_path = f"{os.environ['PCB_OUT_DIR']}/profile_ln"
profile_path = f"{os.environ['PCB_OUT_DIR']}/profile"

env_vars_replaced = 0
if os.path.exists(profile_path):
    shutil.rmtree(profile_path, ignore_errors=True)
if os.path.exists(profile_ln_path):
    for path in os.scandir(f"{os.environ['PCB_OUT_DIR']}/profile_ln"):
        new_path = os.path.join(profile_path, os.path.relpath(path.path, profile_ln_path))
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if not path.is_file():
            os.symlink(path.path, new_path)
            continue
        if path.path.endswith(".sh"):
            with open(path.path, "r") as f:
                f.seek(0)
                lines = f.readlines()
                for i in range(0, len(lines)):
                    if not lines[i].startswith("#"):
                        continue
                    for match in re.findall("\\$(\\w+)", lines[i]):
                        if match not in os.environ:
                            continue
                        lines[i] = lines[i].replace(f"${match}", os.environ[match])
                        env_vars_replaced += 1
                s = "".join(lines)
        else:
            with open(path.path, "r") as f:
                f.seek(0)
                s = f.read()
                for match in re.findall("\\$(\\w+)", s):
                    if match not in os.environ:
                        continue
                    s = s.replace(f"${match}", os.environ[match])
                    env_vars_replaced += 1

        with open(new_path, "w+") as new_f:
            new_f.write(s)

print(f"Replaced {env_vars_replaced} environmental variables")