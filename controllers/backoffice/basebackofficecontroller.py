#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from itertools import chain
import cherrypy
from cocktail.language import get_content_language
from cocktail.controllers import BaseController, get_persistent_param
from sitebasis.models import Item
from sitebasis.controllers import exposed


class BaseBackOfficeController(BaseController):

    section = None
    persistent_content_type_choice = False
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month
    
    @exposed
    def index(self, *args, **kwargs):
        return BaseController.index(self, *args, **kwargs)

    def _init(self, context, cms, request):
        context["cms"] = cms
        context["request"] = request
        context["section"] = self.section

    def _init_view(self, view, context):        
        BaseController._init_view(self, view, context)
        view.cms = context["cms"]
        view.section = context["section"]
        view.user = view.cms.authentication.user

    def _get_content_type(self, default = None):

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

