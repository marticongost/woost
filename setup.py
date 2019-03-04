#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from setuptools import setup
from os import listdir
from os.path import join, isdir

setup(
    name = "woost",
    version = "3.0b1",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    maintainer = "Marti Congost",
    maintainer_email = "marti.congost@whads.com",
    url = "http://woost.info",
    description = "Model driven multilanguage CMS.",
    long_description =
"""Woost is a Content Management System designed from the ground up  to be able
to publish arbitrary data models, including content in multiple languages. Some
of its features include:\n"

    * Use inheritance, relations and validations to define complex models

    * Automatically generate forms and listings for your models from a schema
      description

    * Translate your content into multiple languages, edit translations side by
      side

    * Compatible with lots of popular Python templating engines

    * Place arbitrarily complex access restrictions

    * Extension framework, with several built-in extensions (comments,
      ecommerce, integration with online services, and many others)
""",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: ZODB",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Natural Language :: Catalan",
        "Natural Language :: Spanish",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Site Management"
    ],
    install_requires = [
        "mako==1.*",
        "zeo",
        "Pillow",
        "cocktail[sass]==2.0a1",
    ],
    packages = [
        "woost.app",
        "woost.authentication",
        "woost.language",
        "woost.urls",
        "woost.icons",
        "woost.models",
        "woost.views",
        "woost.controllers",
        "woost.admin",
        "woost.tests",
        "woost.scripts",
        "woost.extensions"
    ],
    include_package_data = True,
    # Woost can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False
)

