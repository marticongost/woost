#-*- coding: utf-8 -*-
"""
Launches the site's application server.
"""
from _PROJECT_MODULE_.controllers import _PROJECT_NAME_CMS

def main():
    cms = _PROJECT_NAME_CMS()
    cms.run()

if __name__ == "__main__":
    main()

