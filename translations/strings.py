#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.translations.translation import translations

translations.define(True,
    ca = u"Sí",
    es = u"Sí",
    en = u"Yes"
)

translations.define(False,
    ca = u"No",
    es = u"No",
    en = u"No"
)

translations.define("ca",
    ca = u"Català",
    es = u"Catalán",
    en = u"Catalan"
)

translations.define("es",
    ca = u"Castellà",
    es = u"Español",
    en = u"Spanish"
)

translations.define("en",
    ca = u"Anglès",
    es = u"Inglés",
    en = u"English"
)

translations.define("site_section",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Web site"
)

translations.define("pages_section",
    ca = u"Pàgines",
    es = u"Páginas",
    en = u"Pages"
)

translations.define("content_section",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("access_rules_section",
    ca = u"Regles d'accés",
    es = u"Reglas de acceso",
    en = u"Access rules"
)

translations.define("edit_section",
    ca = u"Edició",
    es = u"Edición",
    en = u"Edit"
)

translations.define("history_section",
    ca = u"Històric",
    es = u"Histórico",
    en = u"History"
)

translations.define("logged in as",
    ca = u"Estàs identificat com a",
    es = u"Estás identificado como",
    en = u"Logged in as"
)

translations.define("Logout",
    ca = u"Sortir",
    es = u"Salir",
    en = u"Logout"
)

translations.define("Submit",
    ca = u"Confirmar",
    es = u"Confirmar",
    en = u"Submit"
)

translations.define("Type",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("Visible members",
    ca = u"Camps",
    es = u"Campos",
    en = u"Fields"
)

translations.define("Content languages",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define("New item",
    ca = u"Nou",
    es = u"Nuevo",
    en = u"New"
)

translations.define("Edit",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("Delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("History",
    ca = u"Històric",
    es = u"Histórico",
    en = u"History"
)

translations.define("Backout",
    ca = u"Desfer",
    es = u"Deshacer",
    en = u"Backout"
)

translations.define("Revert",
    ca = u"Tornar enrera",
    es = u"Volver atrás",
    en = u"Revert"
)

translations.define("Forget",
    ca = u"Oblidar",
    es = u"Olvidar",
    en = u"Forget"
)

translations.define("BackOfficeContentView.element",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define("Item count",
    ca = lambda t, k, page_range, item_count: \
        u"Mostrant resultats <strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    es = lambda t, k, page_range, item_count: \
        u"Mostrando resultados <strong>%d-%d</strong> de %d" % (
            page_range[0], page_range[1], item_count
        ),
    en = lambda t, k, page_range, item_count: \
        u"Showing results <strong>%d-%d</strong> of %d" % (
            page_range[0], page_range[1], item_count
        )
)

translations.define("Results per page",
    ca = u"Resultats per pàgina",
    es = u"Resultados por página",
    en = u"Results per page"
)

translations.define("No results",
    ca = u"La vista activa no conté cap element.",
    es = u"La vista activa no contiene ningún elemento.",
    en = u"The current view has no matching items."
)

# Content views
#------------------------------------------------------------------------------
translations.define("View as",
    ca = u"Visualització",
    es = u"Visualización",
    en = u"View as"
)

translations.define("TableContentView",
    ca = u"Llistat",
    es = u"Listado",
    en = u"Listing"
)

translations.define("TreeContentView",
    ca = u"Arbre",
    es = u"Árbol",
    en = u"Tree"
)

# Item
#------------------------------------------------------------------------------
translations.define("Item",
    ca = u"Element genèric",
    es = u"Elemento genérico",
    en = u"Generic element"
)

translations.define("Item-plural",
    ca = u"Elements genèrics",
    es = u"Elementos genéricos",
    en = u"Generic elements"
)

translations.define("Item.id",
    ca = u"ID",
    es = u"ID",
    en = u"ID"
)

translations.define("Item.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Item.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Item.author",
    ca = u"Autor",
    es = u"Autor",
    en = u"Author"
)

translations.define("Item.owner",
    ca = u"Propietari",
    es = u"Propietario",
    en = u"Owner"
)

translations.define("Item.groups",
    ca = u"Grups",
    es = u"Grupos",
    en = u"Groups"
)

# Document
#------------------------------------------------------------------------------
translations.define("Document",
    ca = u"Document",
    es = u"Documento",
    en = u"Document"
)

translations.define("Document-plural",
    ca = u"Documents",
    es = u"Documentos",
    en = u"Documents"
)

translations.define("Document.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Document.inner_title",
    ca = u"Títol interior",
    es = u"Título interior",
    en = u"Inner title"
)

translations.define("Document.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Document.start_date",
    ca = u"Data d'inici",
    es = u"Fecha de inicio",
    en = u"Start date"
)

translations.define("Document.end_date",
    ca = u"Data de fí",
    es = u"Fecha de fín",
    en = u"End date"
)

translations.define("Document.path",
    ca = u"Camí de publicació",
    es = u"Camino de publicación",
    en = u"Publication path"
)

translations.define("Document.template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template"
)

translations.define("Document.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Enabled"
)

translations.define("Document.attachments",
    ca = u"Fitxers adjunts",
    es = u"Ficheros adjuntos",
    en = u"Attachments"
)

translations.define("Document.resources",
    ca = u"Recursos HTML",
    es = u"Recursos HTML",
    en = u"HTML Resources"
)

translations.define("Document.draft_source",
    ca = u"Original",
    es = u"Original",
    en = u"Master item"
)

translations.define("Document.drafts",
    ca = u"Esborranys",
    es = u"Borradores",
    en = u"Drafts"
)

translations.define("Document.parent",
    ca = u"Pare",
    es = u"Padre",
    en = u"Parent"
)

translations.define("Document.children",
    ca = u"Pàgines filles",
    es = u"Páginas hijas",
    en = u"Child pages"
)

translations.define("Document.hidden",
    ca = u"Ocult",
    es = u"Oculto",
    en = u"Hidden"
)

# StandardPage
#------------------------------------------------------------------------------
translations.define("StandardPage",
    ca = u"Pàgina estàndard",
    es = u"Página estándar",
    en = u"Standard page"
)

translations.define("StandardPage-plural",
    ca = u"Pàgines estàndard",
    es = u"Páginas estándar",
    en = u"Standard pages"
)

translations.define("StandardPage.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

# User
#------------------------------------------------------------------------------
translations.define("User",
    ca = u"Usuari",
    es = u"Usuario",
    en = u"User"
)

translations.define("User-plural",
    ca = u"Usuaris",
    es = u"Usuarios",
    en = u"Users"
)

translations.define("User.email",
    ca = u"Correu electrònic",
    es = u"Correo electrónico",
    en = u"E-mail address"
)

translations.define("User.authored_items",
    ca = u"Contingut creat per l'usuari",
    es = u"Contingut creado por el usuario",
    en = u"Content created by the user"
)

translations.define("User.owned_items",
    ca = u"Contingut propietat de l'usuari",
    es = u"Contingut propiedad del usuario",
    en = u"Content owned by the user"
)

# Access rule
#------------------------------------------------------------------------------
translations.define("AccessRule",
    ca = u"Regla d'accés",
    es = u"Regla de acceso",
    en = u"Access rule"
)

translations.define("AccessRule-plural",
    ca = u"Regles d'accés",
    es = u"Reglas de acceso",
    en = u"Access rules"
)

translations.define("AccessRule.action",
    ca = u"Acció",
    es = u"Acción",
    en = u"Action"
)

translations.define("AccessRule.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("AccessRule.role",
    ca = u"Rol d'usuari",
    es = u"Rol de usuario",
    en = u"User role"
)

translations.define("AccessRule.target_instance",
    ca = u"Element afectat",
    es = u"Elemento afectado",
    en = u"Target element"
)

translations.define("AccessRule.target_type",
    ca = u"Tipus d'element afectat",
    es = u"Tipo de elemento afectado",
    en = u"Target type"
)

translations.define("AccessRule.target_ancestor",
    ca = u"Ancestre",
    es = u"Ancestro",
    en = u"Ancestor"
)

translations.define("AccessRule.allowed",
    ca = u"Permès",
    es = u"Permitido",
    en = u"Allowed"
)

# Resource
#------------------------------------------------------------------------------
translations.define("Resource",
    ca = u"Recurs HTML",
    es = u"Recurso HTML",
    en = u"HTML Resource"
)

translations.define("Resource-plural",
    ca = u"Recursos HTML",
    es = u"Recursos HTML",
    en = u"HTML Resources"
)

translations.define("Resource.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Resource.html",
    ca = u"Codi HTML",
    es = u"Código HTML",
    en = u"HTML code"
)

# Group
#------------------------------------------------------------------------------
translations.define("Group",
    ca = u"Grup",
    es = u"Grupo",
    en = u"Group"
)

translations.define("Group-plural",
    ca = u"Grups",
    es = u"Grupos",
    en = u"Groups"
)

translations.define("Group.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

# Dynamic group
#------------------------------------------------------------------------------
translations.define("DynamicGroup",
    ca = u"Grup dinàmic",
    es = u"Grupo dinámico",
    en = u"Dynamic group"
)

translations.define("DynamicGroup-plural",
    ca = u"Grups dinàmics",
    es = u"Grupos dinámicos",
    en = u"Dynamic groups"
)

translations.define("DynamicGroup.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("DynamicGroup.query",
    ca = u"Selecció",
    es = u"Selección",
    en = u"Selection"
)

# Back office
#------------------------------------------------------------------------------
translations.define("BackOffice",
    ca = u"Gestor de continguts",
    es = u"Gestor de contenidos",
    en = u"Content manager"
)

translations.define("BackOffice-plural",
    ca = u"Gestors de continguts",
    es = u"Gestores de contenidos",
    en = u"Content managers"
)

# File
#------------------------------------------------------------------------------
translations.define("File",
    ca = u"Fitxer",
    es = u"Fichero",
    en = u"File"
)

translations.define("File-plural",
    ca = u"Fitxers",
    es = u"Ficheros",
    en = u"Files"
)

translations.define("File.file_path",
    ca = u"Ruta del fitxer",
    es = u"Ruta del fichero",
    en = u"File path"
)

translations.define("File.translation_file_path",
    ca = u"Ruta del fitxer traduït",
    es = u"Ruta del fichero traducido",
    en = u"File translation path"
)

# News
#------------------------------------------------------------------------------
translations.define("News",
    ca = u"Notícia",
    es = u"Noticia",
    en = u"News"
)

translations.define("News-plural",
    ca = u"Notícies",
    es = u"Noticias",
    en = u"News"
)

translations.define("News.summary",
    ca = u"Sumari",
    es = u"Sumario",
    en = u"Summary"
)

translations.define("News.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

# Event
#------------------------------------------------------------------------------
translations.define("Event",
    ca = u"Esdeveniment",
    es = u"Evento",
    en = u"Event"
)

translations.define("Event-plural",
    ca = u"Esdeveniments",
    es = u"Eventos",
    en = u"Events"
)

translations.define("Event.event_start",
    ca = u"Inici de l'esdeveniment",
    es = u"Inicio del evento",
    en = u"Event start"
)

translations.define("Event.event_end",
    ca = u"Fí de l'esdeveniment",
    es = u"Fin del evento",
    en = u"Event end"
)

translations.define("Event.event_location",
    ca = u"Lloc",
    es = u"Lugar",
    en = u"Place"
)

translations.define("Event.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

# Role
#------------------------------------------------------------------------------
translations.define("Role",
    ca = u"Rol d'usuari",
    es = u"Rol de usuario",
    en = u"User role"
)

translations.define("Role-plural",
    ca = u"Rols d'usuari",
    es = u"Rols de usuario",
    en = u"User roles"
)

translations.define("Role.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

# Template
#------------------------------------------------------------------------------
translations.define("Template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template"
)

translations.define("Template-plural",
    ca = u"Plantilles",
    es = u"Plantillas",
    en = u"Templates"
)

translations.define("Template.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Template.identifier",
    ca = u"Identificador",
    es = u"Identificador",
    en = u"Identifier"
)

# Language
#------------------------------------------------------------------------------
translations.define("Language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("Language-plural",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define("Language.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Language.iso_code",
    ca = u"Codi ISO",
    es = u"Código ISO",
    en = u"ISO code"
)

# ChangeSet
#------------------------------------------------------------------------------
translations.define("ChangeSet.id",
    ca = u"ID",
    es = u"ID",
    en = u"ID"
)

translations.define("ChangeSet.author",
    ca = u"Autor",
    es = u"Autor",
    en = u"Author"
)

translations.define("ChangeSet.date",
    ca = u"Data",
    es = u"Fecha",
    en = u"Date"
)

translations.define("ChangeSet.changes",
    ca = u"Canvis",
    es = u"Cambios",
    en = u"Changes"
)
