#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from cocktail.translations import translations
from woost.translations.strings import content_permission_translation_factory

# UI
#------------------------------------------------------------------------------
translations.define("Action send_email",
    ca = u"Enviar",
    es = u"Enviar",
    en = u"Send"
)

translations.define("woost.extensions.mailer users",
    ca = u"usuaris",
    es = u"usuarios",
    en = u"usuarios"
)

# SendEmail
#------------------------------------------------------------------------------
translations.define("SendEmail.sender",
    ca = u"Remitent",
    es = u"Remitente",
    en = u"Sender"
)

translations.define("SendEmail.subject",
    ca = u"Assumpte",
    es = u"Asunto",
    en = u"Subject"
)

translations.define("SendEmail.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

translations.define("SendEmail.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("SendEmail.per_user_customizable",
    ca = u"Personalitzable per usuari",
    es = u"Personalizable por usuario",
    en = u"Per user customizable"
)

# SendEmailView
#------------------------------------------------------------------------------
translations.define("woost.extensions.mailer.SendEmailView continue",
    ca = u"Continuar",
    es = u"Continuar",
    en = u"Continue"
)

translations.define("woost.extensions.mailer.SendEmailView send",
    ca = u"Enviar",
    es = u"Enviar",
    en = u"Send"
)

translations.define("woost.extensions.mailer.SendEmailView confirmation text",
    ca = u"""Estàs a punt d'enviar el document <strong>%s</strong> en
<strong>%s</strong> als següents grups d'usuaris:""",
    es = u"""Estás a punto de enviar el documento <strong>%s</strong> en
</strong>%s</strong> a los siguientes grupos de usuarios:""",
    en = u"""You are about to send the document <strong>%s</strong>
</strong>%s</ strong> to the following user groups:"""
)

translations.define("woost.extensions.mailer.SendEmailView total",
    ca = u"Total:",
    es = u"Total:",
    en = u"Total:"
)

translations.define("woost.extensions.mailer.SendEmailView accessibility warning",
    ca = u"""Tingues en compte que en aquests moments el document que
estàs enviant no és accessible pels usuaris anònims.""",
    es = u"""Ten en cuenta que en estos momentos el documento que
estás enviando no és accesible para los usuarios anónimos.""",
    en = u"""Note that at this moment the document you are sending
is not accessible for anonymous users."""
)

translations.define("woost.extensions.mailer.SendEmailView successful mail delivery",
    ca = u"Enviament realitzat correctament",
    es = u"Envio realizado correctamente",
    en = u"Sucessful mail delivery"
)

translations.define("woost.extensions.mailer.SendEmailView error mail delivery",
    ca = u"S'ha produït un error. Posa't en contacte amb l'administrador.",
    es = u"Se ha producido un error. Ponte en contacto con el administrador.",
    en = u"An error has ocurred. Please, contact your administrator."
)

translations.define("woost.extensions.mailer.SendEmailView mailer summary",
    ca = u"S'ha enviat <strong>%d</strong> correus de <strong>%d</strong>.",
    es = u"Se han enviado <strong>%d</strong> correos de <strong>%d</strong>.",
    en = u"<strong>%d</strong> of <strong>%d</strong> emails have been sent."
)

# Template
#------------------------------------------------------------------------------
translations.define("Template.per_user_customizable",
    ca = u"Personalitzable per usuari",
    es = u"Personalizable por usuario",
    en = u"Per user customizable"
)

# SendEmailPermission
#------------------------------------------------------------------------------
translations.define("SendEmailPermission",
    ca = u"Permís d'enviament de correu electrònic",
    es = u"Permiso de envio de correo electrónico",
    en = u"Permission to send email"
)

translations.define("SendEmailPermission-plural",
    ca = u"Permisos d'enviament de correu electrònic",
    es = u"Permisos de envio de correo electrónico",
    en = u"Permissions to send email"
)

