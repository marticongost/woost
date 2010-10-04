#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from woost.models.permission import Permission


class SendEmailPermission(Permission):
    """Permission to send an email."""

    instantiable = True

