#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.models import Publishable


class BackOffice(Publishable):

    def handle_request(self):
        return "Yay... you got to the back office!"


