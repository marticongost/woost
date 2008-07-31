#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.modeling import getter


class Module(object):

    def __init__(self):
        self.__application = None

    def process_request(self, request):
        pass

    def handle_error(self, request, error, handled):
        pass

    @getter
    def application(self):
        return self.__application

    def attach(self, application):
        self.__application = application

    def release(self):
        self.__application = None

