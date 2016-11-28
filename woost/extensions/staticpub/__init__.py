#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cherrypy import request, response
from cocktail.stringutils import normalize_indentation
from cocktail.schema import TranslatedValues as T
from cocktail.translations import translations, get_language
from cocktail.controllers import request_property
from woost import app
from woost.models import Extension, Configuration, Website, Publishable, Role

translations.load_bundle("woost.extensions.staticpub.package")


class StaticPubExtension(Extension):

    USER_AGENT = "woost.extensions.staticpub"

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.description = T(
            ca = u"Exporta els continguts del lloc web com a fitxers HTML "
                 u"estàtics.",
            es = u"Exporta los contenidos del sitio web como ficheros HTML "
                 u"estáticos.",
            en = u"Exports the site's contents to static HTML files."
        )

    def _load(self):

        from . import (
            typegroups,
            configuration,
            publishable,
            export,
            exportpermission,
            exportuseraction,
            destination,
            filters,
            invalidation,
            folderdestination,
            amazons3destination,
            csrfprotectionexemption
        )

        # Set up backoffice controllers
        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from .exportcontroller import ExportController
        from .exportstatecontroller import ExportStateController
        from .exportexcelcontroller import ExportExcelController

        BackOfficeController.static_pub_export = ExportController
        BackOfficeController.static_pub_export_state = ExportStateController
        BackOfficeController.static_pub_export_excel = ExportExcelController

        # Install overlays
        from cocktail.html import templates
        templates.get_class("woost.extensions.staticpub.ItemLabelOverlay")
        templates.get_class("woost.extensions.staticpub.PublishableCardOverlay")

        # Export the X-Woost-Tags header
        from woost.controllers.publishablecontroller \
            import PublishableController

        PublishableController.cached_headers += ("X-Woost-Cache-Tags",)
        base_produce_content = PublishableController._produce_content

        def _produce_content(self, **kwargs):
            content = base_produce_content(self, **kwargs)
            if generating_static_site() and self.view:
                tags = app.publishable.get_cache_tags(language = get_language())
                if self.view:
                    tags.update(self.view.cache_tags)
                response.headers["X-Woost-Cache-Tags"] = " ".join(tags)
            return content

        PublishableController._produce_content = _produce_content

        self.install()

    def _install(self):
        Publishable.included_in_static_publication.rebuild_index()
        self.create_export_script()
        self.create_default_permissions()
        self.disable_export_for_special_pages()

    export_script_template = normalize_indentation(
        """
        #!/usr/bin/env python
        import %(package)s.scripts.shell
        from woost.extensions.staticpub.cli import CLI

        if __name__ == "__main__":
            CLI().main()
        """
    ).lstrip()

    def create_default_permissions(self):
        from .exportpermission import ExportPermission
        permission = ExportPermission.new()
        admins = Role.require_instance(qname = "woost.administrators")
        admins.permissions.append(permission)

    def create_export_script(self):
        script_path = app.path("scripts", "staticpub.py")
        with open(script_path, "w") as script_file:
            script_file.write(
                self.export_script_template
                % {"package": app.package}
            )

    def disable_export_for_special_pages(self):

        for item in [Configuration.instance] + list(Website.select()):
            for key in (
                "login_page",
                "maintenance_page",
                "generic_error_page",
                "not_found_error_page",
                "forbidden_error_page"
            ):
                page = getattr(item, key, None)
                if page:
                    page.included_in_static_publication = False

        for qname in (
            "woost.backoffice",
            "woost.password_change_page",
            "woost.password_change_confirmation_page"
        ):
            page = Publishable.get_instance(qname = qname)
            if page:
                page.included_in_static_publication = False

    @request_property
    def current_export(self):
        export_id = request.headers.get("X-Woost-Extensions-Staticpub-Export")

        if export_id:
            from .export import Export
            return Export.get_instance(int(export_id))
        else:
            return None


def generating_static_site():
    return request.headers.get("User-Agent") == StaticPubExtension.USER_AGENT

