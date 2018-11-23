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
from cocktail.controllers import get_request_root_url
from cocktail.persistence import PersistentObject
from woost import app
from woost.models import Configuration
from woost.controllers.publishablecontroller import PublishableController
import woost.admin.ui
from .schemascontroller import SchemasController
from .datacontroller import DataController
from .previewcontroller import PreviewController


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

        root_section = app.publishable.get_root_section()
        for section in root_section.descend_tree():
            dependencies.update(section.required_ui_components())

        # Collect UI component dependencies for models
        for model in PersistentObject.schema_tree():
            if model.admin_edit_view:
                dependencies.add(components.get(model.admin_edit_view))

        return components.get("woost.admin.ui.Layout").render_page(
            title = translations("woost.admin.ui.Layout.heading"),
            global_style_sheet = "woost.admin.ui://styles/global.scss.css",
            locales = sorted(config.languages, key = translate_locale),
            extra_dependencies = dependencies,
            variables = {
                "woost.admin.origin":
                    unicode(get_request_root_url()).rstrip("/"),
                "woost.admin.url": url,
                "woost.admin.id": app.publishable.id
            }
        )

    schemas = SchemasController()
    data = DataController()
    preview = PreviewController()

