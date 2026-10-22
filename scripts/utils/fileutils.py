# Sylvio Dos Reis 2026
# A collection of useful file functions

import os


def rm_recursive(path):
    for item in os.scandir(path):
        rm(item.path)
    rm(path)

def rm(path):
    try:
        if os.path.islink(path):
            os.unlink(path)
        elif os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
    except Exception as e:
        print(f"Couldn't remove {path}")
        print(e)
        print("Continuing without stopping...")