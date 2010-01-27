#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.modeling import getter
from cocktail.events import event_handler, when
from cocktail import schema
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail.controllers import context
from woost.models import (
    Publishable,
    PublicationScheme,
    Extension,
    Document,
    File
)

translations.define("StaticSiteExtension",
    ca = u"Lloc web estàtic",
    es = u"Sitio web estático",
    en = u"Static website"
)

translations.define("StaticSiteExtension-plural",
    ca = u"Lloc web estàtic",
    es = u"Sitio web estático",
    en = u"Static website"
)

translations.define("StaticSiteExtension.encoding",
    ca = u"Codificació dels fitxers",
    es = u"Codificación de los ficheros",
    en = u"File encoding"
)

translations.define("StaticSiteExtension.index_file_name",
    ca = u"Nom dels fitxers d'índex",
    es = u"Nombre de los ficheros de índice",
    en = u"Folder index file name"
)

translations.define("StaticSiteExtension.file_extension",
    ca = u"Extensió de fitxer",
    es = u"Extensión de fichero",
    en = u"File extension"
)


class StaticSiteExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet exportar una versió estàtica del lloc web.""",
            "ca"
        )
        self.set("description",            
            u"""Permite exportar una versión estática del sitio web.""",
            "es"
        )
        self.set("description",
            u"""Exports the site using static HTML pages.""",
            "en"
        )

    members_order = [
        "encoding",
        "index_file_name"
    ]

    encoding = schema.String(
        required = True,
        default = "utf-8"
    )

    index_file_name = schema.String(
        required = True,
        default = "index"
    )
    
    root_redirection_template = """
<html>
    <head>
        <meta http-equiv="refresh" content="0;url=%s">
    </head>
    <body></body>
</html>
"""

    @event_handler
    def handle_loading(cls, event):
 
        extension = event.source

        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController

        from woost.extensions.staticsite import (
            useraction,
            strings,
            exportstaticsitecontroller,
            staticpublicationscheme
        )

        from woost.extensions.staticsite.staticsiteexporter \
            import StaticSiteExporter
    
        BackOfficeController.export_static = \
            exportstaticsitecontroller.ExportStaticSiteController

        StaticSiteExtension.add_member(
            schema.Reference(
                "publication_scheme",
                type = PublicationScheme,
                bidirectional = True,
                integral = True,
                required = True,
                related_end = schema.Reference()
            )
        )

        StaticSiteExtension.add_member(
            schema.Collection(
                "exporters",
                items = schema.Reference(
                    type = StaticSiteExporter,                    
                ),
                bidirectional = True,
                integral = True,
                related_end = schema.Reference(),
                min = 1
            )
        )

        Publishable.add_member(
            schema.Boolean("exportable_as_static_content",
                default = False,
                required = True,
                listed_by_default = False,
                member_group = "publication"
            ),
            after = "translation_enabled"
        )

        Document.default_exportable_as_static_content = True
        File.default_exportable_as_static_content = True

        for qname in (
            "woost.login_page",
            "woost.backoffice",
            "woost.webservices"
        ):
            item = Publishable.get_instance(qname = qname)
            item.exportable_as_static_content = False

        if extension.publication_scheme is None:
            pubscheme = staticpublicationscheme.StaticPublicationScheme()
            extension.publication_scheme = pubscheme
            pubscheme.insert()

        datastore.commit()

        # Override the publication scheme during the export process
        from woost.models import Site, PathResolution

        def resolve_path(self, path):
            if context.get("exporting_static_site", False):
                if not path:
                    # TODO: index.html?
                    return PathResolution(None, self.home)
                else:
                    resolution = extension.publication_scheme.resolve_path(path)
                    if resolution is not None:
                        return resolution
            else:
                return base_resolve_path(self, path)

        base_resolve_path = Site.resolve_path
        Site.resolve_path = resolve_path

        def get_path(self, publishable, language = None):
            if context.get("exporting_static_site", False):
                if publishable is self.home:
                    # TODO: index.html?
                    return ""
                
                path = extension.publication_scheme.get_path(publishable, language)
                if path is not None:
                    return path
            else:
                return base_get_path(self, publishable, language)

        base_get_path = Site.get_path
        Site.get_path = get_path

        # Disable interactive features from rendered pages when rendering
        # static content
        from woost.controllers.application import CMS
    
        @when(CMS.producing_output)
        def disable_user_controls(event):
            if context.get("exporting_static_site", False):
                event.output["show_user_controls"] = False

