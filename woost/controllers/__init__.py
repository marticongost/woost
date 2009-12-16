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
from woost.models import Document
from woost.controllers.application import CMS
from woost.controllers.module import Module
from woost.controllers.basecmscontroller import BaseCMSController
from woost.controllers.defaulthandler import DefaultHandler

def is_accessible(document, user = None, language = None):
    warn(
        "woost.controllers.is_accessible() is deprecated, use "
        "Document.is_accessible() instead",
        stacklevel = 2
    )
    return document.is_accessible(user = user, language = language)

def select_published(cls, *args, **kwargs):
    warn(
        "woost.controllers.is_accessible() is deprecated, use "
        "Document.select_accessible() instead"
    )
    return Document.select_accessible(*args, **kwargs)

