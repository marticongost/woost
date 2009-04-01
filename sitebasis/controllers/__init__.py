#-*- coding: utf-8 -*-
u"""
Controllers for the CMS backend and frontend applications.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.controllers import context
from sitebasis.controllers.application import CMS
from sitebasis.controllers.module import Module
from sitebasis.controllers.basecmscontroller import BaseCMSController
from sitebasis.controllers.defaulthandler import DefaultHandler

def is_accessible(document):
    return document.is_published() \
        and context["cms"].allows(action = "read", target_instance = document)

