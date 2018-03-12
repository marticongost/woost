#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost import app
from woost.models.utils import get_model_dotted_name
from .section import Section


class CRUD(Section):

    node = "woost.admin.nodes.CRUD"
    model = None
    exporter = None
    tree_children_collection = None

    @property
    def icon_uri(self):
        return app.icon_resolver.find_icon_url(self.model, "scalable")

    def export_data(self):
        data = Section.export_data(self)
        data["model"] = get_model_dotted_name(self.model)
        data["exporter"] = self.exporter

        if self.tree_children_collection:
            data["tree_children_collection"] = \
                self.tree_children_collection.name

        return data

