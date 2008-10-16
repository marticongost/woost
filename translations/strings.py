#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations import translations, translate

translations.define("site_section",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Web site"
)

translations.define("content_section",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("fields_section",
    ca = u"Camps",
    es = u"Campos",
    en = u"Fields"
)

translations.define("history_section",
    ca = u"Històric",
    es = u"Histórico",
    en = u"History"
)

translations.define("logged in as",
    ca = lambda user: u"Estàs identificat com a " \
            "<strong>%s</strong>" % translate(user, "ca"),
    es = lambda user: u"Estás identificado como " \
            "<strong>%s</strong>" % translate(user, "es"),
    en = lambda user: u"Logged in as "
            "<strong>%s</strong>" % translate(user, "en")
)

translations.define("Logout",
    ca = u"Sortir",
    es = u"Salir",
    en = u"Logout"
)

translations.define("Type",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("new",
    ca = u"Nou",
    es = u"Nuevo",
    en = u"New"
)

translations.define("edit",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("history",
    ca = u"Històric",
    es = u"Histórico",
    en = u"History"
)

translations.define("editing",
    ca = lambda item: u"Editant <em>'%s'</em>" % translate(item, "ca"),
    es = lambda item: u"Editando <em>'%s'</em>" % translate(item, "es"),
    en = lambda item: u"Editing <em>'%s'</em>" %  translate(item, "en")
)

translations.define("creating",
    ca = lambda content_type: u"Creant %s" % translate(content_type, "ca"),
    es = lambda content_type: u"Creando %s" % translate(content_type, "es"),
    en = lambda content_type: u"Creating %s" % translate(content_type, "en")
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

translations.define("draft_seq_name",
    ca = u"Esborrany %(index)s",
    es = u"Borrador %(index)s",
    en = u"Draft %(index)s"
)

translations.define("Go back",
    ca = u"Tornar enrera",
    es = u"Volver atrás",
    en = u"Go back"
)

# Content views
#------------------------------------------------------------------------------
translations.define("View as",
    ca = u"Visualització",
    es = u"Visualización",
    en = u"View as"
)

translations.define("flat content view",
    ca = u"Llistat",
    es = u"Listado",
    en = u"Listing"
)

translations.define("tree content view",
    ca = u"Arbre",
    es = u"Árbol",
    en = u"Tree"
)

# Edit form
#------------------------------------------------------------------------------
translations.define("BackOfficeEditForm.translations",
    ca = u"Traduccions",
    es = u"Traducciones",
    en = u"Translations"
)

translations.define("BackOfficeEditForm.properties",
    ca = u"Propietats",
    es = u"Propiedades",
    en = u"Properties"
)

translations.define("BackOfficeEditForm.relations",
    ca = u"Relacions",
    es = u"Relaciones",
    en = u"Relations"
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

translations.define("Item-none",
    ca = u"Cap",
    es = u"Ninguno",
    en = u"None"
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

translations.define("Item.changes",
    ca = u"Canvis",
    es = u"Cambios",
    en = u"Changes"
)

translations.define("Item.is_draft",
    ca = u"És esborrany",
    es = u"Es borrador",
    en = u"Is draft"
)

translations.define("Item.draft_source",
    ca = u"Original",
    es = u"Original",
    en = u"Master item"
)

translations.define("Item.drafts",
    ca = u"Esborranys",
    es = u"Borradores",
    en = u"Drafts"
)

translations.define("Item.creation_time",
    ca = u"Data de creació",
    es = u"Fecha de creación",
    en = u"Creation date"
)

translations.define("Item.last_update_time",
    ca = u"Última modificació",
    es = u"Última modificación",
    en = u"Last updated"
)

# Site
#------------------------------------------------------------------------------
translations.define("Site",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Site"
)

translations.define("Site-plural",
    ca = u"Llocs web",
    es = u"Sitios web",
    en = u"Sites"
)

translations.define("Site.default_language",
    ca = u"Idioma per defecte",
    es = u"Idioma por defecto",
    en = u"Default language"
)

translations.define("Site.languages",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define("Site.home",
    ca = u"Document d'inici",
    es = u"Documento de inicio",
    en = u"Home"
)

translations.define("Site.not_found_error_page",
    ca = u"Pàgina d'error per document no trobat",
    es = u"Página de error para documento no encontrado",
    en = u"'Not found' error page"
)

translations.define("Site.forbidden_error_page",
    ca = u"Pàgina d'error per accés restringit",
    es = u"Página de error para acceso restringido",
    en = u"'Access denied' error page"
)

translations.define("Site.generic_error_page",
    ca = u"Pàgina d'error genèric",
    es = u"Página de error genérico",
    en = u"Generic error page"
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

translations.define("StandardPage-none",
    es = u"Ninguna"
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

translations.define("Action-none",
    ca = u"Cap",
    es = u"Ninguna",
    en = u"None"
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

translations.define("Resource.uri",
    ca = u"URI",
    es = u"URI",
    en = u"URI"
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

translations.define("Group.group_members",
    ca = u"Membres",
    es = u"Miembros",
    en = u"Members"
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

translations.define("News-none",    
    es = u"Ninguna"
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

translations.define("Template-none",
    es = u"Ninguna"
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
