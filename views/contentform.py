#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.translations import translate
from magicbullet.schema import Collection
from magicbullet.html import Element
from magicbullet.html.form import Form, FormGroup


class ContentForm(Form):

    def _build(self):

        Form._build(self)

        self.set_member_type_display(
            Collection,
            self.__class__.display_collection
        )

        self.add_group(
            FormGroup(
                "translations",
                lambda member: not isinstance(member, Collection) \
                               and member.translated
            )
        )

        self.add_group(
            FormGroup(
                "properties",
                lambda member: not isinstance(member, Collection) \
                               and not member.translated
            )
        )

        self.add_group(
            FormGroup(
                "relations",
                lambda member: isinstance(member, Collection)
            )
        )

    def create_field(self, member):
        
        field = Form.create_field(self, member)

        # Add an item count next to each relation
        if isinstance(member, Collection):
            collection = self.get_member_value(self.data, member)
            rel_count = Element("span")
            rel_count.add_class("relation_count")
            rel_count.append("(%d)" % len(collection))
            field.label.append(rel_count)

        return field

    def display_collection(self, obj, member):
        button = Element("button")
        button["type"] = "submit"
        button.append(translate("Edit"))
        return button  

