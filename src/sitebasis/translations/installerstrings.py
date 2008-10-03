#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.translations import translations, translate

translations.define("SiteBasis installation",
    en = u"SiteBasis installation"
)

translations.define("Installer.project",
    en = u"Project"
)

translations.define("Installer.project_name",
    en = u"Project name"
)

translations.define("Installer.project_path",
    en = u"Project path"
)

translations.define("Installer.admin_email",
    en = u"Administrator email"
)

translations.define("Installer.admin_password",
    en = u"Administrator password"
)

translations.define("Installer.webserver",
    en = u"Web server"
)

translations.define("Installer.webserver_host",
    en = u"Web server host"
)

translations.define("Installer.webserver_port",
    en = u"Web server port number"
)

translations.define("Installer.validate_webserver_address",
    en = u"Test address availability"
)

translations.define("Installer.database",
    en = u"Database"
)

translations.define("Installer.database_host",
    en = u"Database host"
)

translations.define("Installer.database_port",
    en = u"Database port number"
)

translations.define("Installer.validate_database_address",
    en = u"Test address availability"
)

translations.define("Install",
    en = u"Install"
)

translations.define("Installation successful",
    en = u"Your new site has been installed successfully."
)

translations.define(
    "sitebasis.controllers.installer.InstallFolderExists-instance",
    ca = u"El directori d'instal·lació seleccionat ja existeix",
    es = u"El directorio de instalación seleccionado ya existe",
    en = u"The chosen installation directory already exists"
)

translations.define(
    "sitebasis.controllers.installer.WrongAddressError-instance",
    en = lambda instance:
        u"The indicated <em>%s</em> and <em>%s</em> combination is not "
        u"available on this server"
        % (
            translate(instance.host_member, "en"),
            translate(instance.port_member, "en")
        )
)

translations.define(
    "Unknown error",
    en = lambda error: u"Unexpected <em>%s</em> exception: %s"
        % (error.__class__.__name__, error)
)

