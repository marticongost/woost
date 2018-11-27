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
from cocktail import schema
from cocktail.ui import components
from cocktail.controllers import get_request_root_url
from cocktail.persistence import PersistentClass, PersistentObject
from woost import app
from woost.models import Configuration
from woost.controllers.publishablecontroller import PublishableController
import woost.admin.ui
from woost.admin.views import available_views
from .schemascontroller import SchemasController
from .datacontroller import DataController
from .previewcontroller import PreviewController


class AdminController(PublishableController):

    ui_component_properties = [
        "admin_edit_view",
        "ui_display",
        "ui_inert_display",
        "ui_form_control",
        "ui_read_only_form_control",
        "ui_item_set_selector_display",
        "ui_collection_editor_control",
        "ui_autocomplete_control"
    ]

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
        dependencies = set()

        def require_component(component):
            if isinstance(component, tuple):
                component = component[0]
            dependencies.add(components.get(component))

        for component_name in app.publishable.ui_components:
            require_component(component_name)

        root_section = app.publishable.get_root_section()
        for section in root_section.descend_tree():
            dependencies.update(section.required_ui_components())

        # Collect UI component dependencies for models and their members
        for model in PersistentObject.schema_tree():

            for view in available_views(model):
                if view.ui_component:
                    require_component(view.ui_component)

            for prop in self.ui_component_properties:
                component = getattr(model, prop, None)
                if component:
                    require_component(component)

            for member in model.iter_members(recursive = False):

                if member.visible:

                    for prop in self.ui_component_properties:
                        component = getattr(member, prop, None)
                        if component:
                            require_component(component)

                    if (
                        isinstance(member, schema.RelationMember)
                        and isinstance(member.related_type, PersistentClass)
                    ):
                        for view in available_views(member):
                            if view.ui_component:
                                require_component(view.ui_component)

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

