#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.translations.helpers import (
    plural2,
    ca_join,
    es_join,
    en_join
)

# FacebookPublicationExtension
#------------------------------------------------------------------------------
translations.define("FacebookPublicationExtension.targets",
    ca = u"Destins",
    es = u"Destinos",
    en = u"Destinations"
)

# FacebookPublicationTarget
#------------------------------------------------------------------------------
translations.define("FacebookPublicationTarget",
    ca = u"Destí de publicació Facebook",
    es = u"Destino de publicación Facebook",
    en = u"Facebook publication target"
)

translations.define("FacebookPublicationTarget-plural",
    ca = u"Destins de publicació Facebook",
    es = u"Destinos de publicación Facebook",
    en = u"Facebook publication targets"
)

translations.define("FacebookPublicationTarget.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("FacebookPublicationTarget.graph_object_id",
    ca = u"Objecte destí",
    es = u"Objeto destino",
    en = u"Target object"
)

translations.define("FacebookPublicationTarget.graph_object_id-explanation",
    ca = u"Identificador de l'objecte de Facebook (usuari, pàgina, etc.) on "
         u"es volen publicar els continguts",
    es = u"Identificador del objeto de Facebook (usuario, página, etc.) "
         u"donde se quieren publicar los contenidos",
    en = u"Identifier for the Facebook object (user, page, etc) where the "
         u"content is to be published"
)

translations.define("FacebookPublicationTarget.administrator_id",
    ca = u"Administrador de la pàgina",
    es = u"Administrador de la página",
    en = u"Page administrator"
)

translations.define("FacebookPublicationTarget.administrator_id-explanation",
    ca = u"Si l'objecte destí és una pàgina de Facebook, cal introduir "
         u"l'identificador de l'usuari de Facebook que la gestiona. En cas "
         u"contrari, deixar en blanc.",
    es = u"Si el objeto destino es una página de Facebook, es necesario "
         u"introducir el identificador del usuario de Facebook que la "
         u"gestiona. En caso contrario, dejar en blanco.",
    en = u"If the target object is a Facebook page, introduce the identifier "
         u"of its appointed administrator. Otherwise, leave blank."
)

translations.define("FacebookPublicationTarget.app_id",
    ca = u"Id d'aplicació Facebook",
    es = u"Id de aplicación Facebook",
    en = u"Facebook application ID"
)

translations.define("FacebookPublicationTarget.app_secret",
    ca = u"Codi secret d'aplicació Facebook",
    es = u"Código secreto de aplicación Facebook",
    en = u"Facebook application secret"
)

translations.define("FacebookPublicationTarget.auth_token",
    ca = u"Autorització",
    es = u"Autorización",
    en = u"Authorization"
)

translations.define("FacebookPublicationTarget.auth_token-conceded",
    ca = u"Concedida",
    es = u"Concedida",
    en = u"Granted"
)

translations.define("FacebookPublicationTarget.auth_token-pending",
    ca = u"Pendent",
    es = u"Pendiente",
    en = u"Pending"
)

translations.define("FacebookPublicationTarget.languages",
    ca = u"Idiomes en que es publica",
    es = u"Idiomas en los que se publica",
    en = u"Published languages"
)

translations.define("FacebookPublicationTarget.targeting",
    ca = u"Segmentació per regió/idioma",
    es = u"Segmentación por región/idioma",
    en = u"Regional/language targeting"
)

# User actions
#------------------------------------------------------------------------------
translations.define("Action fbpublish",
    ca = u"Publicar a Facebook",
    es = u"Publicar en Facebook",
    en = u"Publish to Facebook"
)

translations.define("Action fbpublish_auth",
    ca = u"Autoritzar",
    es = u"Autorizar",
    en = u"Authorize"
)

translations.define(
    "woost.extensions.facebookauthentication.fbpublish_auth.success",
    ca = u"S'ha completat l'autorització amb Facebook de forma "
         u"satisfactòria.",
    es = u"Se ha completado la autorización con Facebook de forma "
         u"satisfactoria.",
    en = u"Facebook authorization successful."
)

translations.define(
    "woost.extensions.facebookauthentication.fbpublish_auth.error",
    ca = u"L'autorització amb Facebook ha fallat."
         u"<p><em>Error:</em> %(error)s</p>"
         u"<p><em>Raó:</em> %(error_reason)s</p>"
         u"<p><em>Descripció:</em> %(error_description)s</p>",
    es = u"La autorización con Facebook ha fallado."
         u"<p><em>Error:</em> %(error)s</p>"
         u"<p><em>Razón:</em> %(error_reason)s</p>"
         u"<p><em>Descripción:</em> %(error_description)s</p>",
    en = u"Facebook authorization failed."
         u"<p><em>Error:</em> %(error)s</p>"
         u"<p><em>Reason:</em> %(error_reason)s</p>"
         u"<p><em>Description:</em> %(error_description)s</p>"
)

translations.define(
    "woost.extensions.facebookauthentication.fbpublish_auth.oauth_error",
    ca = u"L'autorització ha fallat: revisa l'id i el codi secret de "
         u"l'aplicació.",
    es = u"La autorización ha fallado: revisa el id y código secreto de tu "
         u"aplicación.",
    en = u"Authorization failed: check your application id and secret code."
)

# FacebookPublicationPermission
#------------------------------------------------------------------------------
translations.define("FacebookPublicationPermission",
    ca = u"Permís de publicació a Facebook",
    es = u"Permiso de publicación en Facebook",
    en = u"Facebook publication permission"
)

translations.define("FacebookPublicationPermission-plural",
    ca = u"Permisos de publicació a Facebook",
    es = u"Permisos de publicación en Facebook",
    en = u"Facebook publication permissions"
)

translations.define("FacebookPublicationPermission.publication_targets",
    ca = u"Destins de publicació",
    es = u"Destinos de publicación",
    en = u"Publication targets"
)

# FacebookPublicationController
#------------------------------------------------------------------------------

translations.define(
    "woost.extensions.facebookpublication.publication_success_notice",
    ca = lambda target, items, summarize = False:
        u"S'%s publicat %s a <em>%s</em>" % (
            plural2(len(items), u"ha", u"han"),
            (
                u"%d %s" % (
                    len(items),
                    plural2(len(items), u"element", u"elements")
                )
                if summarize
                else ca_join([
                    u"<em>%s</em>"
                    % translations(item) for item in items
                ])
            ),
            translations(target)
        ),
    es = lambda target, items, summarize = False:
        u"Se %s publicado %s en <em>%s</em>" % (
            plural2(len(items), u"ha", u"han"),
            (
                u"%d %s" % (
                    len(items),
                    plural2(len(items), u"elemento", u"elementos")
                )
                if summarize
                else es_join([
                    u"<em>%s</em>"
                    % translations(item) for item in items
                ])
            ),
            translations(target)
        ),
    en = lambda target, items, summarize = False:
        u"%s published to <em>%s</em>" % (            
            (
                u"%d %s" % (
                    len(items),
                    plural2(len(items), u"item", u"items")
                )
                if summarize
                else en_join([
                    u"<em>%s</em>"
                    % translations(item) for item in items
                ])
            ),
            translations(target)
        )
)

translations.define(
    "woost.extensions.facebookpublication.publication_error_notice",
    ca = lambda target, items, summarize = False:
        u"Error en intentar publicar %s a <em>%s</em>" % (            
            (
                u"%d %s" % (
                    len(items),
                    plural2(len(items), u"element", u"elements")
                )
                if summarize
                else ca_join([
                    u"<em>%s</em>"
                    % translations(item) for item in items
                ])
            ),
            translations(target)
        ),
    es = lambda target, items, summarize = False:
        u"Error al intentar publicar %s en <em>%s</em>" % (
            (
                u"%d %s" % (
                    len(items),
                    plural2(len(items), u"elemento", u"elementos")
                )
                if summarize
                else es_join([
                    u"<em>%s</em>"
                    % translations(item) for item in items
                ])
            ),
            translations(target)
        ),
    en = lambda target, items, summarize = False:
        u"Could not publish %s to <em>%s</em>" % (            
            (
                u"%d %s" % (
                    len(items),
                    plural2(len(items), u"item", u"items")
                )
                if summarize
                else en_join([
                    u"<em>%s</em>"
                    % translations(item) for item in items
                ])
            ),
            translations(target)
        )
)

translations.define("FacebookPublicationForm.publication_targets",
    ca = u"Canals on es publicarà el contingut",
    es = u"Canales donde se publicará el contenido",
    en = u"Channels where the content will be published"
)

translations.define("FacebookPublicationForm.languages",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "section_title",
    ca = u"Publicar a Facebook",
    es = u"Publicar en Facebook",
    en = u"Publish with Facebook"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "publication_form.submit_button",
    ca = u"Publicar",
    es = u"Publicar",
    en = u"Publish"
)

translations.define(
    "woost.extensions.facebookpublication.FacebookPublicationView."
    "selection_block",
    ca = u"Contingut a publicar:",
    es = u"Contenido a publicar:",
    en = u"Content to publish:"
)

