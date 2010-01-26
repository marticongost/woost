#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from woost.models import Publishable
from woost.controllers.backoffice.useractions import UserAction


class ExportStaticAction(UserAction):
    min = None
    max = None
    included = frozenset(["toolbar"])
    content_type = Publishable

ExportStaticAction("export_static").register()

