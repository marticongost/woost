#-*- coding: utf-8 -*-
"""
Controllers for the CMS backend and frontend applications.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
from cocktail.controllers import context
from .cmscontroller import CMSController
from .basecmscontroller import BaseCMSController
from .notifications import notify_user, Notification

