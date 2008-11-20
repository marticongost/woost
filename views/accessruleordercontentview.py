#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import templates
OrderContentView = templates.get_class("sitebasis.views.OrderContentView")


class AccessRuleOrderContentView(OrderContentView):
    collection_attribute = "registry"

