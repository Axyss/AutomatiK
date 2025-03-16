import os
import time
from automatik import __version__


def clear_console():
    """Clears the console in a different way depending on the OS."""
    if os.name in ("nt", "dos"):
        os.system("cls")
    elif os.name in ("linux", "osx", "posix"):
        os.system("clear")
    else:
        print("\n" * 120)


def print_ascii_art():
    print(r"""                   _                        _   _ _  __
        /\        | |                      | | (_) |/ /
       /  \  _   _| |_ ___  _ __ ___   __ _| |_ _| ' /
      / /\ \| | | | __/ _ \| '_ ` _ \ / _` | __| |  <
     / ____ \ |_| | || (_) | | | | | | (_| | |_| | . \
    /_/    \_\__,_|\__\___/|_| |_| |_|\__,_|\__|_|_|\_\  {}
                                                  """.format(__version__))
    time.sleep(0.05)  # For some reason if there is no delay, other messages may be printed before this one
