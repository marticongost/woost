#-*- coding: utf-8 -*-
"""
Controllers for the CMS administration interface.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController

from sitebasis.controllers.backoffice.historycontroller \
    import HistoryController

from sitebasis.controllers.backoffice.editcontroller \
    import EditController

from sitebasis.controllers.backoffice.collectioncontroller \
    import CollectionController

from sitebasis.controllers.backoffice.itemcontroller \
    import ItemController

from sitebasis.controllers.backoffice.backofficecontroller \
    import BackOfficeController


ItemController.CollectionController = CollectionController

