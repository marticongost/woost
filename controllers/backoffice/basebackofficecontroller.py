#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from itertools import chain
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.language import get_content_language
from cocktail.controllers import BaseController, get_persistent_param
from sitebasis.models import Item
from sitebasis.controllers import Request


class BaseBackOfficeController(BaseController):

    section = None
    persistent_content_type_choice = False
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

    @cached_getter
    def backoffice(self):
        return Request.current.document

    @cached_getter
    def cms(self):
        return Request.current.cms

    @cached_getter
    def user(self):
        return self.cms.authentication.user

    def _init_view(self, view):
        BaseController._init_view(self, view)
        view.backoffice = self.backoffice
        view.cms = self.cms
        view.user = self.user
        view.section = self.section

    def get_content_type(self, default = None):

        if self.persistent_content_type_choice:
            type_param = get_persistent_param(
                "type",
                cookie_duration = self.settings_duration
            )
        else:
            type_param = cherrypy.request.params.get("type")

        if type_param is None:
            return default
        else:
            for entity in chain([Item], Item.derived_entities()):
                if entity.__name__ == type_param:
                    return entity

    def get_visible_languages(self):

        param = get_persistent_param(
            "language",
            cookie_name = "visible_languages",
            cookie_duration = self.settings_duration
        )

        if param is not None:
            if isinstance(param, (list, tuple, set)):
                return set(param)
            else:
                return set(param.split(","))
        else:
            return [get_content_language()]

