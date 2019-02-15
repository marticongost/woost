#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import os
import subprocess

def convert_project_to_python3():

    # Make sure the script is running under Python2
    if sys.version[0] != "2":
        sys.stderr.write("Must run using Python 2\n")
        sys.exit(1)

    # Make sure the script is running under a project environment
    try:
        site_dir = os.environ["SITE"]
    except KeyError:
        sys.stderr.write("Must run with a project environment activated\n")
        sys.exit(1)

    # Convert the database
    db_file = os.path.join(site_dir, "data", "database.fs")
    subprocess.check_call(
        ["zodbupdate", "--pack", "--convert-py3", "--file", db_file]
    )

    # Run the 2to3 code migration tool
    subprocess.check_call(
        ["2to3-2.7", "-w", site_dir]
    )

if __name__ == "__main__":
    convert_project_to_python3()

