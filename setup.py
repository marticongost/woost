#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from setuptools import setup, find_packages

setup(
    name = "sitebasis",
    version = "0.1a",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = "An object oriented, web based Content Management System.",
    install_requires = ["simplejson", "cocktail", "genshi"],
    include_package_data = True,
    packages = find_packages(),
    
    # SiteBasis can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False
)

