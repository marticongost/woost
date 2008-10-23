#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translate
from cocktail.schema import Collection, Reference
from cocktail.html import Element, templates

Form = templates.get_class("cocktail.html.Form")


class ContentForm(Form):

    def _build(self):

        Form._build(self)

        self.set_member_type_display(Reference, "sitebasis.views.ItemSelector")

