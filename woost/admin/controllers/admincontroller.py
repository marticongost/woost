#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import pkg_resources
from cocktail.translations import (
    translations,
    translate_locale
)
from cocktail.events import Event, event_handler
from cocktail.pkgutils import import_module
from cocktail import schema
from cocktail.ui import components
from cocktail.controllers import get_request_root_url
from cocktail.persistence import PersistentClass, PersistentObject
from woost import app
from woost.models import Configuration, extensions_manager
from woost.controllers.publishablecontroller import PublishableController
import woost.admin.ui
from woost.admin.views import available_views
from .schemascontroller import SchemasController
from .datacontroller import DataController
from .previewcontroller import PreviewController
from .utils import set_admin_language

def _get_version(pkg_name):
    return pkg_resources.require(pkg_name)[0].version

WOOST_VERSION = _get_version("woost")
EXT_PREFIX = "woost.extensions."


class AdminController(PublishableController):

    ui_component_properties = [
        "admin_edit_view",
        "admin_item_card",
        "ui_display",
        "ui_inert_display",
        "ui_form_control",
        "ui_read_only_form_control",
        "ui_item_set_selector_display",
        "ui_collection_editor_control",
        "ui_autocomplete_control"
    ]

    collecting_ui_components = Event()

    @event_handler
    def handle_traversed(e):

        set_admin_language()

        pkg = app.publishable.python_package
        if pkg:
            import_module(pkg)

    def __call__(self, *args, **kwargs):

        config = Configuration.instance
        url = str(app.publishable.get_uri()).rstrip("/")

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

        self.collecting_ui_components(
            require_component=require_component
        )

        html = components.get(app.publishable.main_ui_component).render_page(
            title = translations("woost.admin.ui.Layout.heading"),
            global_style_sheet = "woost.admin.ui://styles/global.scss.css",
            locales = sorted(config.languages, key = translate_locale),
            extra_dependencies = dependencies,
            variables = {
                "woost.admin.origin":
                    str(get_request_root_url()).rstrip("/"),
                "woost.admin.url": url,
                "woost.admin.id": app.publishable.id,
                "woost.version": WOOST_VERSION,
                "woost.installedExtensions": dict(
                    (
                        (
                            ext.__name__[len(EXT_PREFIX):]
                            if ext.__name__.startswith(EXT_PREFIX)
                            else ext.__name__
                        ),
                        {
                            "version": _get_version(ext.__name__)
                        }
                    )
                    for ext in extensions_manager.iter_extensions()
                )
            }
        )
        return html.replace("--ADMIN--", url)

    schemas = SchemasController()
    data = DataController()
    preview = PreviewController()

