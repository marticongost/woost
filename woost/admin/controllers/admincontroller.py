#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import (
    set_language,
    translations,
    translate_locale
)
from cocktail.events import event_handler
from cocktail.ui import components
from woost import app
from woost.models import Configuration
from woost.controllers.publishablecontroller import PublishableController
import woost.admin.ui
from .schemascontroller import SchemasController
from .datacontroller import DataController


class AdminController(PublishableController):

    @event_handler
    def handle_traversed(cls, e):
        set_language(
            app.user.prefered_language
            or app.publishable.default_language
        )

    def __call__(self, *args, **kwargs):

        config = Configuration.instance
        url = unicode(app.publishable.get_uri()).rstrip("/")

        # Collect UI component dependencies for the admin sections
        dependencies = set(
            components.get(component_name)
            for component_name in app.publishable.ui_components
        )

        root_section = app.publishable.create_root_section()
        dependencies.update(
            components.get(section.ui_component)
            for section in root_section.descend_tree()
            if section.ui_component
        )

        return components.get("woost.admin.ui.Layout").render_page(
            title = translations("woost.admin.ui.Layout.heading"),
            global_style_sheet = "woost.admin.ui://styles/global.scss.css",
            locales = sorted(config.languages, key = translate_locale),
            extra_dependencies = dependencies,
            variables = {
                "woost.admin.url": url,
                "woost.admin.id": app.publishable.id
            }
        )

    schemas = SchemasController()
    data = DataController()

