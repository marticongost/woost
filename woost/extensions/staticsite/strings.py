#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from cocktail.translations import translations
from woost.translations.strings import content_permission_translation_factory

# UI
#------------------------------------------------------------------------------
translations.define("Action export_static",
    ca = u"Exportar contingut estàtic",
    es = u"Exportar contenido estático",
    en = u"Export static content"
)

translations.define("woost.extensions.staticsite any destination",
    ca = u"Tots els destins",
    es = u"Todos los destinos",
    en = u"All destinations"
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
translations.define("ExportStaticSite.update_only",
    ca = u"Exportar únicament el contingut modificat",
    es = u"Exportar únicamente el contenido modificado",
    en = u"Only export modified content"
)

translations.define("ExportStaticSite.exporter",
    ca = u"Destí",
    es = u"Destino",
    en = u"Destination"
)

# StaticSiteExtension
#------------------------------------------------------------------------------
translations.define("StaticSiteExtension.destinations",
    ca = u"Destins",
    es = u"Destinos",
    en = u"Destinations"
)

# StaticSiteSnapShooter
#------------------------------------------------------------------------------
translations.define("StaticSiteSnapShooter",
    ca = u"Exportador de contingut estàtic",
    es = u"Exportador de contenido estático",
    en = u"Static content exporter"
)

translations.define("StaticSiteSnapShooter-plural",
    ca = u"Exportadors de contingut estàtic",
    es = u"Exportadores de contenido estático",
    en = u"Static content exporters"
)

translations.define("StaticSiteSnapShooter.destination",
    ca = u"Destí",
    es = u"Destino",
    en = u"Destination"
)

translations.define("StaticSiteSnapShooter.url",
    ca = u"Adreça web",
    es = u"Dirección web",
    en = u"Web address"
)

# WgetSnapShooter
#------------------------------------------------------------------------------
translations.define("WgetSnapShooter",
    ca = u"Exportador Wget",
    es = u"Exportador Wget",
    en = u"Wget exporter"
)

translations.define("WgetSnapShooter-plural",
    ca = u"Exportadors Wget",
    es = u"Exportadores Wget",
    en = u"Wget exporters"
)

translations.define("WgetSnapShooter.file_names_mode",
    ca = u"Mode dels noms de fitxers",
    es = u"Modo de los nombres de ficheros",
    en = u"File names mode"
)

translations.define("woost.extensions.staticsite.staticsitesnapshooter.WgetSnapShooter.file_names_mode unix",
    ca = u"Unix",
    es = u"Unix",
    en = u"Unix"
)

translations.define("woost.extensions.staticsite.staticsitesnapshooter.WgetSnapShooter.file_names_mode windows",
    ca = u"Windows",
    es = u"Windows",
    en = u"Windows"
)

# StaticSiteDestination
#------------------------------------------------------------------------------
translations.define("StaticSiteDestination",
    ca = u"Destí de contingut estàtic",
    es = u"Destino de contenido estático",
    en = u"Static content destination"
)

translations.define("StaticSiteDestination-plural",
    ca = u"Destins de contingut estàtic",
    es = u"Destinos de contenido estático",
    en = u"Static content destinations"
)

translations.define("StaticSiteDestination.snapshooter",
    ca = u"Exportador",
    es = u"Exportador",
    en = u"Exporter"
)

translations.define("StaticSiteDestination.destination_permissions",
    ca = u"Permisos",
    es = u"Permisos",
    en = u"Permissions"
)

translations.define("StaticSiteDestination.encoding",
    ca = u"Codificació dels fitxers",
    es = u"Codificación de los ficheros",
    en = u"File encoding"
)

# FolderDestination
#------------------------------------------------------------------------------
translations.define("FolderDestination",
    ca = u"Carpeta local",
    es = u"Carpeta local",
    en = u"Local folder"
)

translations.define("FolderDestination-plural",
    ca = u"Carpeta local",
    es = u"Carpeta local",
    en = u"Local folder"
)

translations.define("FolderDestination.target_folder",
    ca = u"Carpeta de destí",
    es = u"Carpeta de destino",
    en = u"Target folder"
)

# FTPDestination
#------------------------------------------------------------------------------
translations.define("FTPDestination",
    ca = u"Servidor FTP",
    es = u"Servidor FTP",
    en = u"FTP server"
)

translations.define("FTPDestination-plural",
    ca = u"Servidor FTP",
    es = u"Servidor FTP",
    en = u"FTP server"
)

translations.define("FTPDestination.ftp_host",
    ca = u"Adreça del servidor FTP",
    es = u"Dirección del servidor FTP",
    en = u"FTP host"
)

translations.define("FTPDestination.ftp_user",
    ca = u"Usuari FTP",
    es = u"Usuario FTP",
    en = u"FTP user"
)

translations.define("FTPDestination.ftp_password",
    ca = u"Contrasenya FTP",
    es = u"Contraseña FTP",
    en = u"FTP password"
)

translations.define("FTPDestination.ftp_path",
    ca = u"Carpeta de destí",
    es = u"Carpeta de destino",
    en = u"Target folder"
)

# ZipDestination
#------------------------------------------------------------------------------
translations.define("ZipDestination",
    ca = u"Fitxer ZIP",
    es = u"Fichero ZIP",
    en = u"ZIP file"
)

translations.define("ZipDestination-plural",
    ca = u"Fitxer ZIP",
    es = u"Fichero ZIP",
    en = u"ZIP file"
)

translations.define(
    "woost.extensions.staticsite.staticsiteexporter."
    "ZipDestination-instance",
    ca = u"Fitxer ZIP",
    es = u"Fichero ZIP",
    en = u"ZIP file"
)

# ExportationPermission
#------------------------------------------------------------------------------
translations.define("ExportationPermission",
    ca = u"Permís d'exportació",
    es = u"Permiso de exportación",
    en = u"Exportation permission"
)

translations.define("ExportationPermission-plural",
    ca = u"Permisos d'exportacions",
    es = u"Permisos de exportaciones",
    en = u"Exportation permissions"
)

translations.define("ExportationPermission.destination",
    ca = u"Destí",
    es = u"Destino",
    en = u"Exportation"
)

translations.define(
    "woost.extensions.workflow.exportationpermission."
    "ExportationPermission-instance",
    ca = content_permission_translation_factory("ca",
        lambda permission, subject, **kwargs:
            "%s %s" % (        
                translations(permission.destination, "ca", **kwargs),
                subject
            )                
            if permission.destination
            else "canviar l'estat " + ca_possessive(subject),
    ),  
    es = content_permission_translation_factory("es",
        lambda permission, subject, **kwargs:
            "%s %s" % (        
                translations(permission.destination, "es", **kwargs),
                subject
            )                
            if permission.destination
            else "cambiar el estado de " + subject,
    ),  
    en = content_permission_translation_factory("en",
        lambda permission, subject, **kwargs:
            "%s %s" % ( 
                translations(permission.destination, "en", **kwargs),
                subject
            )                
            if permission.destination
            else "change the state of " + subject
    )   
)

