#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.ui import components
from woost import app
from woost.models.utils import get_model_dotted_name
from woost.admin.views import require_view, available_views
from .section import Section


class CRUD(Section):

    node = "woost.admin.nodes.CRUD"
    model = None
    views = None
    partitioning_methods = None

    @property
    def icon_uri(self):
        return app.icon_resolver.find_icon_url(self.model, "scalable")

    def required_ui_components(self):

        for component in Section.required_ui_components(self):
            yield component

        if self.views:
            for view_name in self.views:
                view = require_view(view_name)
                yield components.resolve(view.ui_component)

    def export_data(self):
        data = Section.export_data(self)
        data["model"] = get_model_dotted_name(self.model)
        data["views"] = self.views
        data["partitioning_methods"] = self.partitioning_methods
        return data
