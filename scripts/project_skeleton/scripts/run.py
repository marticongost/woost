#-*- coding: utf-8 -*-
"""
Launches the site's application server.
"""

def main():

    # Make sure the site's source code folder is present on the python path
    from os.path import abspath, join, dirname
    import sys

    src_code_path = abspath(join(dirname(abspath(__file__)), "..", ".."))

    if src_code_path not in sys.path:
        sys.path.append(src_code_path)

    # Launch the application server
    from _PROJECT_MODULE_.controllers import _PROJECT_NAME_CMS
    cms = _PROJECT_NAME_CMS()
    cms.run()

if __name__ == "__main__":
    main()

