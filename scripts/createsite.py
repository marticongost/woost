#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""

def main():
    from os.path import abspath, join, dirname
    import sys

    src_code_path = abspath(join(dirname(abspath(__file__)), "..", "src"))

    if src_code_path not in sys.path:
        sys.path.append(src_code_path)

    from sitebasis.controllers.installer import Installer
    installer = Installer()
    installer.run()

if __name__ == "__main__":
    main()

