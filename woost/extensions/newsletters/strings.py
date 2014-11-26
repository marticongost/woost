#-*- coding: utf-8 -*-
u"""
.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail.translations import  translations

translations.define("woost.type_groups.blocks.newsletter",
    ca = u"Butlletí de notícies",
    es = u"Boletín de noticias",
    en = u"Newsletter"
)

# MailingPlatform
#------------------------------------------------------------------------------
translations.define("MailingPlatform",
    ca = u"Plataforma d'enviament de butlletins",
    es = u"Plataforma de envío de boletines",
    en = u"Newsletter platform"
)

translations.define("MailingPlatform-plural",
    ca = u"Plataformes d'enviament de butlletins",
    es = u"Plataformas de envío de boletines",
    en = u"Newsletter platforms"
)

translations.define("MailingPlatform.platform_name",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("MailingPlatform.online_version_tag",
    ca = u"Etiqueta de la versió online",
    es = u"Etiqueta de la versión online",
    en = u"Online version tag"
)

translations.define("MailingPlatform.unsubscription_tag",
    ca = u"Etiqueta de baixa de la plataforma",
    es = u"Etiqueta de baja de la plataforma",
    en = u"Unsubscription tag"
)

# Campaign Monitor
translations.define("woost.extensions.newsletters.campaign_monitor.online_version_tag",
    ca = u"<webversion>versió web</webversion>",
    es = u"<webversion>versión web</webversion>",
    en = u"<webversion>web version</webversion>"
)

translations.define("woost.extensions.newsletters.campaign_monitor.unsubscription_tag",
    ca = u"<unsubscribe>donar-me de baixa del butlletí</unsubscribe>",
    es = u"<unsubscribe>darme de baja del boletín</unsubscribe>",
    en = u"<unsubscribe>unsubscribe</unsubscribe>"
)

#MailChimp
translations.define("woost.extensions.newsletters.mailchimp.online_version_tag",
    ca = u"<a href='*|ARCHIVE|*'>versió web</a>",
    es = u"<a href='*|ARCHIVE|*'>versión web</a>",
    en = u"<a href='*|ARCHIVE|*'>web version</a>"
)

translations.define("woost.extensions.newsletters.mailchimp.unsubscription_tag",
    ca = u"<a href='*|UNSUB|*'>donar-me de baixa del butlletí</a>",
    es = u"<a href='*|UNSUB|*'>darme de baja del boletín</a>",
    en = u"<a href='*|UNSUB|*'>unsubscribe</a>"
)

# WeSend
translations.define("woost.extensions.newsletters.wesend.online_version_tag",
    ca = u"<webversion>versió web</webversion>",
    es = u"<webversion>versión web</webversion>",
    en = u"<webversion>web version</webversion>"
)

translations.define("woost.extensions.newsletters.wesend.unsubscription_tag",
    ca = u"<unsubscribe>donar-me de baixa del butlletí</unsubscribe>",
    es = u"<unsubscribe>darme de baja del boletín</unsubscribe>",
    en = u"<unsubscribe>unsubscribe</unsubscribe>"
)

# Newsletter
#------------------------------------------------------------------------------
translations.define("Newsletter",
    ca = u"Butlletí de correu electrònic",
    es = u"Boletín de correo electrónico",
    en = u"Newsletter"
)

translations.define("Newsletter-plural",
    ca = u"Butlletins de correu electrònic",
    es = u"Boletines de correo electrónico",
    en = u"Newsletters"
)

translations.define("Newsletter.mailing_platform",
    ca = u"Plataforma d'enviament",
    es = u"Plataforma de envío",
    en = u"Sending platform"
)

translations.define("Newsletter.root_spacing_factor",
    ca = u"Espaiat dels blocs a l'arrel",
    es = u"Espaciado de los bloques en la raíz",
    en = u"Spacing for root blocks"
)

translations.define("Newsletter.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# Newsletter Controller
#------------------------------------------------------------------------------
translations.define("woost.extensions.newsletters.newsletter_controller.title",
    ca = u"Controlador de butlletins",
    es = u"Controlador de boletines",
    en = u"Newsletter controller"
)

# Newsletter Template
#------------------------------------------------------------------------------
translations.define("woost.extensions.newsletters.newsletter_template.title",
    ca = u"Plantilla de butlletí",
    es = u"Plantilla de boletín",
    en = u"Newsletter template"
)

# NewsletterBox
#------------------------------------------------------------------------------
translations.define("NewsletterBox",
    ca = u"Caixa",
    es = u"Caja",
    en = u"Box"
)

translations.define("NewsletterBox-plural",
    ca = u"Caixes",
    es = u"Cajas",
    en = u"Boxes"
)

translations.define("NewsletterBox.column_count",
    ca = u"Número de columnes",
    es = u"Número de columnas",
    en = u"Column count"
)

translations.define("NewsletterBox.view_class",
    ca = u"Aparença de la caixa",
    es = u"Apariencia de la caja",
    en = u"Box appearence"
)

translations.define(
    "NewsletterBox.view_class"
    "=woost.extensions.newsletters.NewsletterBoxView",
    ca = u"Estàndard",
    es = u"Estándar",
    en = u"Standard"
)

translations.define("NewsletterBox.content_layout",
    ca = u"Disposició del contingut",
    es = u"Disposición del contenido",
    en = u"Content disposition"
)

translations.define("NewsletterBox.content_image_size",
    ca = u"Mida de les imatges",
    es = u"Tamaño de las imágenes",
    en = u"Image size"
)

translations.define("NewsletterBox.content_appearence",
    ca = u"Aparença del contingut",
    es = u"Apariencia del contenido",
    en = u"Content appearence"
)

translations.define("NewsletterBox.spacing_factor",
    ca = u"Espaiat dels blocs",
    es = u"Espaciado de los bloques",
    en = u"Block spacing"
)

translations.define("NewsletterBox.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define("woost.extensions.newsletters.inherited_value",
    ca = u"La que indiqui la caixa",
    es = u"La que indique la caja",
    en = u"Inherit from its containing box"
)

# NewsletterContent
#------------------------------------------------------------------------------
translations.define("NewsletterContent",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("NewsletterContent-plural",
    ca = u"Continguts",
    es = u"Contenidos",
    en = u"Content"
)

translations.define("NewsletterContent.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("NewsletterContent.link",
    ca = u"Enllaç",
    es = u"Enlace",
    en = u"Link"
)

translations.define("NewsletterContent.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("NewsletterContent.layout",
    ca = u"Disposició",
    es = u"Disposición",
    en = u"Disposition"
)

translations.define("NewsletterContent.image_size",
    ca = u"Mida de la imatge",
    es = u"Tamaño de la imagen",
    en = u"Image size"
)

translations.define("NewsletterContent.appearence",
    ca = u"Aparença",
    es = u"Apariencia",
    en = u"Appearence"
)

# NewsletterContentLayout
#------------------------------------------------------------------------------ 
translations.define(
    "woost.extensions.newsletters.NewsletterContentLayout=image_top",
    ca = u"Imatge a dalt",
    es = u"Imagen arriba",
    en = u"Image top"
)

translations.define(
    "woost.extensions.newsletters.NewsletterContentLayout=image_left",
    ca = u"Imatge a l'esquerra",
    es = u"Imagen a la izquierda",
    en = u"Image left"
)

translations.define(
    "woost.extensions.newsletters.NewsletterContentLayout=image_right",
    ca = u"Imatge a la dreta",
    es = u"Imagen a la derecha",
    en = u"Image right"
)

# NewsletterContentImageSize
#------------------------------------------------------------------------------ 
translations.define(
    "woost.extensions.newsletters.NewsletterContentImageSize=one_third",
    ca = u"Un terç",
    es = u"Un tercio",
    en = u"One third"
)

translations.define(
    "woost.extensions.newsletters.NewsletterContentImageSize=one_half",
    ca = u"La meitat",
    es = u"La mitad",
    en = u"One half"
)

# NewsletterContentAppearence
#------------------------------------------------------------------------------ 
translations.define(
    "woost.extensions.newsletters.NewsletterContentAppearence="
    "woost.extensions.newsletters.NewsletterContentView",
    ca = u"Estàndard",
    es = u"Estándar",
    en = u"Standard"
)

# NewsletterSeparator
#------------------------------------------------------------------------------
translations.define("NewsletterSeparator",
    ca = u"Separador",
    es = u"Separador",
    en = u"Separator"
)

translations.define("NewsletterSeparator-plural",
    ca = u"Separadors",
    es = u"Separadores",
    en = u"Separators"
)

translations.define("NewsletterSeparator.spacing_factor",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

# Image Factories
#------------------------------------------------------------------------------
translations.define("woost.extensions.newsletters.image_factories.newsletter_single_column.title",
    ca = u"Imatge de butlletí amb columna completa",
    es = u"Imagen de boletín con columna completa",
    en = u"Newsletter image with single column"
)

translations.define("woost.extensions.newsletters.image_factories.newsletter_multi_column.title",
    ca = u"Imatge de butlletí amb múltiples columnes",
    es = u"Imagen de boletín con múltiples columnas",
    en = u"Newsletter image with multiple columns"
)

# NewsletterView
#------------------------------------------------------------------------------
translations.define("woost.extensions.newsletters.NewsletterView bad_visualization",
    ca = u"Si no visualitzes correctament aquest correu electrònic, pots ",
    es = u"Si no visualizas correctamente este correo electrónico, puedes ",
    en = u"If you can't see this email correctly, you can "
)

translations.define("woost.extensions.newsletters.NewsletterView online_version",
    ca = u"veure la versió online",
    es = u"ver la versión online",
    en = u"see the online version"
)

# Configuration
#------------------------------------------------------------------------------
translations.define("Configuration.services.mailing_platform",
    ca = u"Plataformes d'enviament de butlletins",
    es = u"Plataformas de envío de boletines",
    en = u"Newsletter sending platforms"
)

translations.define("Configuration.mailing_platforms",
    ca = u"Plataformes disponibles",
    es = u"Plataformas disponibles",
    en = u"Available platforms"
)

