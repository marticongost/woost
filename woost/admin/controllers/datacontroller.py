#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.controllers import HTTPMethodController
from .listingcontroller import ListingController
from .editcontroller import EditController
from .deletecontroller import DeleteController
from .defaultscontroller import DefaultsController
from .settingsscopescontroller import SettingsScopesController
from .currentusercontroller import CurrentUserController
from .viewscontroller import ViewsController

translations.load_bundle("woost.admin.controllers.datacontroller")


class DataController(HTTPMethodController):

    GET = ListingController
    PUT = EditController
    POST = EditController
    DELETE = DeleteController

    views = ViewsController
    defaults = DefaultsController
    settings_scopes = SettingsScopesController
    current_user = CurrentUserController

