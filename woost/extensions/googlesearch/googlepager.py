#-*- coding: utf-8 -*-
"""

@author:		Marc Pérez
@contact:		marc.perez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.translations import translations
from cocktail.html import Element
from cocktail.html.pager import Pager


class GooglePager(Pager):

    def create_button(self, name):

        button = Element("a")
        button.add_class(name)

        if name == "next":
            button.append(translations("woost.extensions.googlesearch.GooglePager.next"))
        elif name == "previous":
            button.append(translations("woost.extensions.googlesearch.GooglePager.previous"))

        return button

