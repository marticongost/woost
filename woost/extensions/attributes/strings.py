#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations

# Default attributes
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.attributes.default_attributes.publishable.title",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define(
    "woost.extensions.attributes.default_attributes.type.title",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define(
    "woost.extensions.attributes.default_attributes.path.title",
    ca = u"Camí",
    es = u"Camino",
    en = u"Path"
)

translations.define(
    "woost.extensions.attributes.default_attributes.locale.title",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define(
    "woost.extensions.attributes.default_attributes.role.title",
    ca = u"Rols de l'usuari",
    es = u"Roles del usuario",
    en = u"User roles"
)

translations.define(
    "woost.extensions.attributes.default_attributes.user.title",
    ca = u"Usuari",
    es = u"Usuario",
    en = u"User"
)

# Configuration
#------------------------------------------------------------------------------
translations.define("Configuration.attributes_language",
    ca = u"Idioma pels atributs",
    es = u"Idioma para los atributos",
    en = u"Attributes language"
)

# Attribute
#------------------------------------------------------------------------------
translations.define("Attribute",
    ca = u"Atribut",
    es = u"Atributo",
    en = u"Attribute"
)

translations.define("Attribute-plural",
    ca = u"Atributs",
    es = u"Atributos",
    en = u"Attributes"
)

translations.define("Attribute.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Attribute.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Active"
)

translations.define("Attribute.content_types",
    ca = u"Continguts a etiquetar",
    es = u"Contenidos a etiquetar",
    en = u"Content types"
)

translations.define("Attribute.scope",
    ca = u"Àmbit d'aplicació",
    es = u"Ámbito de aplicación",
    en = u"Application scope"
)

translations.define("Attribute.scope=any",
    ca = u"Pàgines i enllaços",
    es = u"Páginas y enlaces",
    en = u"Pages and references"
)

translations.define("Attribute.scope=page",
    ca = u"Només pàgines",
    es = u"Solo páginas",
    en = u"Pages only"
)

translations.define("Attribute.scope=ref",
    ca = u"Només enllaços",
    es = u"Solo enlaces",
    en = u"References only"
)

translations.define("Attribute.attribute_name",
    ca = u"Nom de l'atribut",
    es = u"Nombre del atributo",
    en = u"Attribute name"
)

translations.define("Attribute.attribute_name-explanation",
    ca = u"El nom de l'atribut HTML que es generarà. Hauria de començar "
         u"per <code>data-</code> i constar només de lletres en minúscula, "
         u"números i guions. Es recomana utilitzar un sistema de prefixos."
         u"Exemples: <code>data-woost-user</code>, "
         u"<code>data-myproject-myattribute</code>.",
    es = u"El nombre del atributo HTML se generará. Debería empezar por "
         u"<code>data-</code> y constar únicamente de letras en minúscula, "
         u"números y guiones. Se recomienda utilizar un sistema de prefijos. "
         u"Ejemplos: <code>data-woost-user</code>, "
         u"<code>data-myproject-myattribute</code>.",
    en = u"The name of the HTML attribute to generate. Should start with "
         u"<code>data-</code> and contain only lowercase letters, numbers and "
         u"dashes. Examples: <code>data-woost-user</code>, "
         u"<code>data-myproject-myattribute</code>."
)

translations.define("Attribute.code",
    ca = u"Valor",
    es = u"Valor",
    en = u"Value"
)

