#-*- coding: utf-8 -*-
"""
Initializes the site's database.

*******************************************************************************
WARNING: this will clear all existing data, so use with care!
*******************************************************************************

The site's initialization is run automatically by the site installer, so
calling this script manually should seldomly be necessary. That said, it can be
useful during development (ie. to setup working copies from version control, or
to reset a site's state after some changes).
"""

def main():

    # Make sure the site's source code folder is present on the python path
    from os.path import abspath, join, dirname
    import sys

    src_code_path = abspath(join(dirname(abspath(__file__)), "..", "src"))

    if src_code_path not in sys.path:
        sys.path.append(src_code_path)

    # Load project settings
    import _PROJECT_MODULE_

    # Initialize the site
    from sitebasis.models.initialization import main as init_site
    init_site()

if __name__ == "__main__":
    main()

