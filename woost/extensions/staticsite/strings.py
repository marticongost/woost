#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.translations import translations

# UI
#------------------------------------------------------------------------------
translations.define("Action export_static",
    ca = u"Exportar contingut estàtic",
    es = u"Exportar contenido estático",
    en = u"Export static content"
)

translations.define("woost.extensions.staticsite Export button",
    ca = u"Exportar",
    es = u"Exportar",
    en = u"Export"
)

translations.define("woost.extensions.staticsite export done",
    ca = u"Exportació completada",
    es = u"Exportación completada",
    en = u"Content exported"
)

translations.define("woost.extensions.staticsite.export_status-ignored",
    ca = u"Ignorat (no exportable)",
    es = u"Ignorado (no exportable)",
    en = u"Ignored (not exportable))"
)

translations.define("woost.extensions.staticsite.export_status-not_modified",
    ca = u"Ignorat (no modificat)",
    es = u"Ignorado (no modificado)",
    en = u"Ignored (not modified)"
)

translations.define("woost.extensions.staticsite.export_status-exported",
    ca = u"Exportat",
    es = u"Exportado",
    en = u"Exported"
)

translations.define("woost.extensions.staticsite.export_status-failed",
    ca = u"Fallit",
    es = u"Fallido",
    en = u"Failed"
)

# Export form
#------------------------------------------------------------------------------
translations.define("ExportStaticSite.selection",
    ca = u"Contingut a exportar",
    es = u"Contenido a exportar",
    en = u"Exported content"
)

translations.define("ExportStaticSite.update_only",
    ca = u"Exportar únicament el contingut modificat",
    es = u"Exportar únicamente el contenido modificado",
    en = u"Only export modified content"
)

translations.define("ExportStaticSite.language",
    ca = u"Idiomes a exportar",
    es = u"Idiomas a exportar",
    en = u"Exported languages"
)

translations.define("ExportStaticSite.include_resources",
    ca = u"Exportar recursos estàtics",
    es = u"Exportar recursos estáticos",
    en = u"Export static resources"
)

translations.define("ExportStaticSite.exporter",
    ca = u"Destí",
    es = u"Destino",
    en = u"Destination"
)

# StaticSiteExtension
#------------------------------------------------------------------------------
translations.define("StaticSiteExtension.publication_scheme",
    ca = u"Esquema de publicació",
    es = u"Esquema de publicación",
    en = u"Publication scheme"
)

translations.define("StaticSiteExtension.exporters",
    ca = u"Destins",
    es = u"Destinos",
    en = u"Destinations"
)

# Publishable
#------------------------------------------------------------------------------
translations.define("Publishable.exportable_as_static_content",
    ca = u"Exportable com a contingut estàtic",
    es = u"Exportable como contenido estático",
    en = u"Exported as static content"
)

# StaticPublicationScheme
#------------------------------------------------------------------------------
translations.define("StaticPublicationScheme",
    ca = u"Esquema de publicació estàtic",
    es = u"Esquema de publicación estático",
    en = u"Static publication scheme"
)

# StaticSiteExporter
#------------------------------------------------------------------------------
translations.define("StaticSiteExporter",
    ca = u"Exportador de contingut estàtic",
    es = u"Exportador de contenido estático",
    en = u"Static content exporter"
)

translations.define("StaticSiteExporter-plural",
    ca = u"Exportadors de contingut estàtic",
    es = u"Exportadores de contenido estático",
    en = u"Static content exporters"
)

# FolderStaticSiteExporter
#------------------------------------------------------------------------------
translations.define("FolderStaticSiteExporter",
    ca = u"Exportador a carpeta local",
    es = u"Exportador a carpeta local",
    en = u"Local folder exporter"
)

translations.define("FolderStaticSiteExporter-plural",
    ca = u"Exportadors a carpeta local",
    es = u"Exportadores a carpeta local",
    en = u"Local folder exporters"
)

translations.define("FolderStaticSiteExporter.target_folder",
    ca = u"Carpeta de destí",
    es = u"Carpeta de destino",
    en = u"Target folder"
)

# FTPStaticSiteExporter
#------------------------------------------------------------------------------
translations.define("FTPStaticSiteExporter",
    ca = u"Exportador a servidor FTP",
    es = u"Exportador a servidor FTP",
    en = u"FTP server exporter"
)

translations.define("FTPStaticSiteExporter-plural",
    ca = u"Exportadors a servidor FTP",
    es = u"Exportadores a servidor FTP",
    en = u"FTP server exporters"
)

translations.define("FTPStaticSiteExporter.ftp_host",
    ca = u"Adreça del servidor FTP",
    es = u"Dirección del servidor FTP",
    en = u"FTP host"
)

translations.define("FTPStaticSiteExporter.ftp_user",
    ca = u"Usuari FTP",
    es = u"Usuario FTP",
    en = u"FTP user"
)

translations.define("FTPStaticSiteExporter.ftp_password",
    ca = u"Contrasenya FTP",
    es = u"Contraseña FTP",
    en = u"FTP password"
)

translations.define("FTPStaticSiteExporter.ftp_path",
    ca = u"Carpeta de destí",
    es = u"Carpeta de destino",
    en = u"Target folder"
)

# ZipStaticSiteExporter
#------------------------------------------------------------------------------
translations.define("ZipStaticSiteExporter",
    ca = u"Exportador a fitxer ZIP",
    es = u"Exportador a fichero ZIP",
    en = u"ZIP file exporter"
)

translations.define("ZipStaticSiteExporter-plural",
    ca = u"Exportadors a fitxer ZIP",
    es = u"Exportadores a fichero ZIP",
    en = u"ZIP file exporters"
)

translations.define(
    "woost.extensions.staticsite.staticsiteexporter."
    "ZipStaticSiteExporter-instance",
    ca = u"Fitxer ZIP",
    es = u"Fichero ZIP",
    en = u"ZIP file"
)

