#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.translations import translations

translations.define("SiteBasis installation",
    en = u"SiteBasis installation"
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

translations.define("Install",
    en = u"Install"
)

translations.define(
    "sitebasis.controllers.installer.InstallFolderExists-instance",
    ca = lambda instance:
        u"El directori d'instal·lació seleccionat ja existeix",
    es = lambda instance:
        u"El directorio de instalación seleccionado ya existe",
    en = lambda instance:
        u"The chosen installation directory already exists"
)

