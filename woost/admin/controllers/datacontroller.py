#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.controllers import Controller
from .listingcontroller import ListingController
from .transactioncontroller import TransactionController
from .defaultscontroller import DefaultsController
from .settingsscopescontroller import SettingsScopesController
from .currentusercontroller import CurrentUserController
from .viewscontroller import ViewsController
from .deletepreviewcontroller import DeletePreviewController
from .partitionscontroller import PartitionsController

translations.load_bundle("woost.admin.controllers.datacontroller")


class DataController(Controller):
    listing = ListingController
    transaction = TransactionController
    views = ViewsController
    partitions = PartitionsController
    defaults = DefaultsController
    delete_preview = DeletePreviewController
    settings_scopes = SettingsScopesController
    current_user = CurrentUserController

