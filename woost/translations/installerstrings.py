#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.translations import translations

translations.define("Woost installation",
    en = u"Woost installation"
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

translations.define("Installer.languages",
    en = u"Languages"
)

translations.define("Installer.template_engine",
    en = u"Template engine"
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
    "woost.controllers.installer.InstallFolderExists-instance",
    ca = u"El directori d'instal·lació seleccionat ja existeix",
    es = u"El directorio de instalación seleccionado ya existe",
    en = u"The chosen installation directory already exists"
)

translations.define(
    "woost.controllers.installer.PythonPathError-instance",
    ca = u"El <em>directori d'instal·lació</em> ha d'estar dins del "
         u"<i>PYTHONPATH</i>",
    es = u"El <em>directorio de instalación</em> debe estar dentro del "
         u"<i>PYTHONPATH</i>",
    en = u"The <em>project path</em> must be within the <i>PYTHONPATH</i>"
)

translations.define(
    "woost.controllers.installer.WrongAddressError-instance",
    en = lambda instance:
        u"The indicated <em>%s</em> and <em>%s</em> combination is not "
        u"available on this server"
        % (
            translations(instance.host_member, "en"),
            translations(instance.port_member, "en")
        )
)

translations.define(
    "woost.controllers.installer.SubprocessError-instance",
    en = lambda instance:
        u"The installer found an unexpected error and couldn't continue. "
        u"The <em>%s</em> process returned the following error: <pre>%s</pre>"
        % (instance.cmd, instance.error_output)
)

translations.define(
    "Unknown error",
    en = lambda error: u"Unexpected <em>%s</em> exception: %s"
        % (error.__class__.__name__, error)
)

