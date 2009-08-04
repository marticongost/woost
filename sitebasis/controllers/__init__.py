#-*- coding: utf-8 -*-
u"""
Controllers for the CMS backend and frontend applications.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
from cocktail.controllers import context
from sitebasis.models import Document
from sitebasis.controllers.application import CMS
from sitebasis.controllers.module import Module
from sitebasis.controllers.basecmscontroller import BaseCMSController
from sitebasis.controllers.defaulthandler import DefaultHandler

def is_accessible(document, user = None, language = None):
    warn(
        "sitebasis.controllers.is_accessible() is deprecated, use "
        "Document.is_accessible() instead",
        stacklevel = 2
    )
    return document.is_accessible(user = user, language = language)

def select_published(cls, *args, **kwargs):
    warn(
        "sitebasis.controllers.is_accessible() is deprecated, use "
        "Document.select_accessible() instead"
    )
    return Document.select_accessible(*args, **kwargs)

