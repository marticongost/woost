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

translations.define("CollectionView visible members shortcut",
    ca = u"c",
    es = u"c",
    en = u"f"
)

translations.define("CollectionView visible languages shortcut",
    ca = u"i",
    es = u"i",
    en = u"l"
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

translations.define("CollectionView new shortcut",
    ca = u"n",
    es = u"n",
    en = u"n"
)

translations.define("edit",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("CollectionView edit shortcut",
    ca = u"e",
    es = u"e",
    en = u"e"
)

translations.define("order",
    ca = u"Ordenar",
    es = u"Ordenar",
    en = u"Order"
)

translations.define("CollectionView order shortcut",
    ca = u"o",
    es = u"o",
    en = u"o"
)

translations.define("move",
    ca = u"Moure",
    es = u"Mover",
    en = u"Move"
)

translations.define("CollectionView move shortcut",
    ca = u"m",
    es = u"m",
    en = u"m"
)

translations.define("delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("CollectionView delete shortcut",
    ca = u"i",
    es = u"i",
    en = u"d"
)

translations.define("history",
    ca = u"Històric",
    es = u"Histórico",
    en = u"History"
)

translations.define("CollectionView history shortcut",
    ca = u"h",
    es = u"h",
    en = u"h"
)

translations.define("add",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("remove",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define("move_up",
    ca = u"Moure amunt",
    es = u"Mover arriba",
    en = u"Move up"
)

translations.define("move_down",
    ca = u"Moure avall",
    es = u"Mover abajo",
    en = u"Move down"
)

translations.define("editing",
    ca = lambda item: u"Editant <em>'%s'</em>" % translate(item, "ca"),
    es = lambda item: u"Editando <em>'%s'</em>" % translate(item, "es"),
    en = lambda item: u"Editing <em>'%s'</em>" %  translate(item, "en")
)

translations.define("creating",
    ca = lambda content_type:
        u"Creant %s" % translate(content_type.__name__, "ca").lower(),
    es = lambda content_type:
        u"Creando %s" % translate(content_type.__name__, "es").lower(),
    en = lambda content_type:
        u"Creating new %s" % translate(content_type.__name__, "en").lower()
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

translations.define("Discard changes",
    ca = u"Descartar",
    es = u"Descartar",
    en = u"Discard"
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

translations.define("Save",
    ca = u"Desar",
    es = u"Guardar",
    en = u"Save"
)

translations.define("Save draft",
    ca = u"Desar esborrany",
    es = u"Guardar borrador",
    en = u"Save draft"
)

translations.define("Show differences",
    ca = u"Veure diferències",
    es = u"Ver diferencias",
    en = u"Show differences"
)

translations.define("Preview",
    ca = u"Vista prèvia",
    es = u"Vista previa",
    en = u"Preview"
)

translations.define("Close",
    ca = u"Tancar",
    es = u"Cerrar",
    en = u"Close"
)

translations.define("Differences for",
    ca = lambda item: u"Canvis a <em>'%s'</em>" % translate(item, "ca"),
    es = lambda item: u"Cambios en <em>'%s'</em>" % translate(item, "es"),
    en = lambda item: u"Changes in <em>'%s'</em>" % translate(item, "en")
)

translations.define("No differences",
    ca = u"L'element no té cap canvi.",
    es = u"El elemento no tiene ningún cambio.",
    en = u"The item has no changes."
)

translations.define("EditView translations shortcut",
    ca = u"r",
    es = u"r",
    en = u"r"
)

translations.define("Confirm draft",
    ca = u"Confirmar esborrany",
    es = u"Confirmar borrador",
    en = u"Confirm draft"
)

translations.define("Editing draft",
    ca = u"Estàs editant un nou esborrany. L'element no esdevindrà actiu fins "
         u"que no el confirmis.",
    es = u"Estás editando un nuevo borrador. El elemento no se activará hasta "
         u"que no lo confirmes.",
    en = u"You are editing a new draft. The element won't become active until "
         u"you confirm it."
)

translations.define("Editing draft copy",
    ca = u"Estàs editant un esborrany d'un <a href='%(location)s'>element</a>."
         u" Els canvis no es veuran reflectits a l'original fins que no "
         u"confirmis l'esborrany.",
    es = u"Estás editando un borrador de un <a href='%(location)s'>"
         u"elemento</a>. Tus cambios no se verán reflejados en el original "
         u"hasta que no confirmes el borrador.",
    en = u"You are editing a draft of an <a href='%(location)s'>item</a>. "
         u"Your changes won't be made permanent until you confirm the draft."
)

translations.define("Draft source reference",
    ca = u"Pots accedir a la còpia original de l'element "
         u"<a href='%(location)s'>aquí</a>.",
    es = u"Puedes acceder a la copia original del elemento "
         u"<a href='%(location)s'>aquí</a>.",
    en = u"The original copy of the item can be found "
         u"<a href='%(location)s'>here</a>."
)

translations.define("More actions",
    ca = u"Més accions",
    es = u"Más acciones",
    en = u"More actions"
)

translations.define("datetime format",
    ca = "%d/%m/%Y %H:%M",
    es = "%d/%m/%Y %H:%M",
    en = "%Y-%m-%d %H:%M"
)

translations.define("Administrators group title",
    ca = u"Administradors",
    es = u"Administradores",
    en = u"Administrators"
)

translations.define("Anonymous role title",
    ca = u"Anònim",
    es = u"Anónimo",
    en = u"Anonymous"
)

translations.define("Authenticated role title",
    ca = u"Autenticat",
    es = u"Autenticado",
    en = u"Authenticated"
)

translations.define("Author role title",
    ca = u"Autor",
    es = u"Autor",
    en = u"Author"
)

translations.define("Owner role title",
    ca = u"Propietari",
    es = u"Propietario",
    en = u"Owner"
)

translations.define("Back office title",
    ca = u"Gestor de continguts",
    es = u"Gestor de contenidos",
    en = u"Content Manager"
)

translations.define("Empty template title",
    ca = u"Plantilla buida",
    es = u"Plantilla vacía",
    en = u"Empty template"
)

translations.define("Message style sheet title",
    ca = u"Full d'estils per missatges",
    es = u"Hoja de estilos para mensajes",
    en = u"Application messages stylesheet"
)

translations.define("Home page title",
    ca = u"Benvingut!",
    es = u"Bienvenido!",
    en = u"Welcome!"
)

translations.define("Home page body",
    ca = u"El teu lloc web s'ha creat correctament. Ja pots començar "
        u"a <a href='%(uri)s'>treballar-hi</a> i substituir aquesta pàgina "
        u"amb els teus propis continguts.",
    es = u"Tu sitio web se ha creado correctamente. Ya puedes empezar "
        u"a <a href='%(uri)s'>trabajar</a> en él y sustituir esta página "
        u"con tus propios contenidos.",
    en = u"Your web site has been created successfully. You can start "
        u"<a href='%(uri)s'>working on it</a> and replace this page with "
        u"your own content."
)

translations.define("Not found error page title",
    ca = u"Pàgina no trobada",
    es = u"Página no encontrada",
    en = u"Page not found"
)

translations.define("Not found error page body",
    ca = u"La direcció indicada no coincideix amb cap dels continguts "
         u"del web. Si us plau, revísa-la i torna-ho a provar.",
    es = u"La dirección indicada no coincide con ninguno de los "
         u"contenidos del web. Por favor, revísala y intentalo de nuevo.",
    en = u"Couldn't find the indicated address. Please, verify it and try "
         u"again."
)

translations.define("Login page title",
    ca = u"Autenticació d'usuari",
    es = u"Autenticación de usuario",
    en = u"User authentication"
)

translations.define("Login page body",
    ca = lambda form: u"""
    <p>
        L'accés a aquesta secció del web està restringit. Per favor,
        introdueix les teves credencials d'usuari per continuar.
    </p>
    """ + (form % (u"Usuari", u"Contrasenya", u"Entrar")),    
    es = lambda form: u"""
    <p>
    El acceso a esta sección del sitio está restringido. Por favor,
    introduce tus credenciales de usuario para continuar.
    </p>
    """ + (form % (u"Usuario", u"Contraseña", u"Entrar")),    
    en = lambda form: u"""
    <p>
        Access to this part of the website is restricted. Please, introduce
        your user credentials to proceed.
    </p>
    """ + (form % (u"User", u"Password", u"Enter"))
)

translations.define("BackOfficeOrderView last position",
    ca = u"Final de la llista",
    es = u"Final de la lista",
    en = u"End of the list"
)

translations.define(
    "sitebasis.controllers.backoffice.movecontroller.TreeCycleError-instance",
    ca = u"No es pot inserir un element dins de sí mateix.",
    es = u"No se puede insertar un elemento dentro de si mismo.",
    en = u"Can't insert an element into itself."
)

# Initialization content
#------------------------------------------------------------------------------
translations.define("Create action title",
    ca = u"Crear",
    es = u"Crear",
    en = u"Create"
)

translations.define("Read action title",
    ca = u"Veure",
    es = u"Ver",
    en = u"Read"
)

translations.define("Modify action title",
    ca = u"Modificar",
    es = u"Modificar",
    en = u"Modify"
)

translations.define("Delete action title",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

# Content views
#------------------------------------------------------------------------------
translations.define("View as",
    ca = u"Visualització",
    es = u"Visualización",
    en = u"View as"
)

translations.define("flat content view",
    ca = u"Veure com a llistat",
    es = u"Ver como listado",
    en = u"Show as listing"
)

translations.define("tree content view",
    ca = u"Veure com a arbre",
    es = u"Ver como árbol",
    en = u"Show as tree"
)

translations.define("order content view",
    ca = u"Veure com a llista ordenable",
    es = u"Ver como lista ordenadable",
    en = u"Show as ordered listing"
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

translations.define("Site.access_rules_by_priority",
    ca = u"Regles d'accés",
    es = u"Reglas de acceso",
    en = u"Access rules"
)

translations.define("Site.plugins",
    ca = u"Extensions",
    es = u"Extensiones",
    en = u"Plug-ins"
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
    ca = u"Ruta",
    es = u"Ruta",
    en = u"Path"
)

translations.define("Document.full_path",
    ca = u"Ruta completa",
    es = u"Ruta completa",
    en = u"Full path"
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

translations.define("Resource.documents",
    ca = u"Documents",
    es = u"Documentos",
    en = u"Documents"
)

# Style
#------------------------------------------------------------------------------
translations.define("Style",
    ca = u"Estil",
    es = u"Estilo",
    en = u"Style"
)

translations.define("Style-plural",
    ca = u"Estils",
    es = u"Estilos",
    en = u"Styles"
)

translations.define("Style.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Style.declarations",
    ca = u"Declaracions CSS",
    es = u"Declaraciones CSS",
    en = u"CSS declarations"
)

translations.define("Style.admin_declarations",
    ca = u"Declaracions CSS Admin",
    es = u"Declaraciones CSS Admin",
    en = u"Admin CSS declarations"
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

translations.define("Template.engine",
    ca = u"Motor de pintat",
    es = u"Motor de pintado",
    en = u"Rendering engine"
)

translations.define("Template.items",
    ca = u"Elements",
    es = u"Elementos",
    en = u"Items"
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

translations.define("Language.iso_code",
    ca = u"Codi ISO",
    es = u"Código ISO",
    en = u"ISO code"
)

translations.define("Language.fallback_languages",
    ca = u"Idiomes substitutius",
    es = u"Idiomas sustitutivos",
    en = u"Fallback languages"
)

# PlugIn
#------------------------------------------------------------------------------
translations.define("PlugIn",
    ca = u"Extensió",
    es = u"Extensión",
    en = u"Plug-in"
)

translations.define("PlugIn-plural",
    ca = u"Extensions",
    es = u"Extensiones",
    en = u"Plug-ins"
)

translations.define("PlugIn.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("PlugIn.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("PlugIn.plugin_author",
    ca = u"Autor de l'extensió",
    es = u"Autor de la extensión",
    en = u"Plug-in author"
)

translations.define("PlugIn.license",
    ca = u"Llicència",
    es = u"Licencia",
    en = u"License"
)

translations.define("PlugIn.enabled",
    ca = u"Activat",
    es = u"Activado",
    en = u"Enabled"
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

# ClientParams
#------------------------------------------------------------------------------
translations.define("BackOfficeLayout unchanged_message",
    ca = u"Segur que vols sortir sense guardar els canvis?",
    es = u"¿Estás seguro que quieres salir sin guardar los cambios?",
    en = u"Do you want to save your changes?"
)
