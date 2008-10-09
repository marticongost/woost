#-*- coding: utf-8 -*-
"""
(X)HTML templates for the CMS backend application.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from os import path as _path
from cocktail.html import templates

templates.get_loader().add_path(
    "sitebasis.views",
    _path.abspath(_path.dirname(__file__))
)

