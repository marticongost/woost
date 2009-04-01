#-*- coding: utf-8 -*-
u"""

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

translations.define("sitebasis.views.BackOfficeLayout stack root",
    ca = u"Inici",
    es = u"Inicio",
    en = u"Root"
)

translations.define("Action new",
    ca = u"Nou",
    es = u"Nuevo",
    en = u"New"
)

translations.define("cocktail.html.shortcuts action new",
    ca = u"n",
    es = u"n",
    en = u"n"
)

translations.define("Action show_detail",
    ca = u"Veure resum",
    es = u"Ver resumen",
    en = u"Show detail"
)

translations.define("cocktail.html.shortcuts action show_detail",
    ca = u"v",
    es = u"v",
    en = u"w"
)

translations.define("Action edit",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("cocktail.html.shortcuts action edit",
    ca = u"e",
    es = u"e",
    en = u"e"
)

translations.define("Action order",
    ca = u"Ordenar",
    es = u"Ordenar",
    en = u"Order"
)

translations.define("cocktail.html.shortcuts action order",
    ca = u"o",
    es = u"o",
    en = u"o"
)

translations.define("Action move",
    ca = u"Moure",
    es = u"Mover",
    en = u"Move"
)

translations.define("cocktail.html.shortcuts action move",
    ca = u"m",
    es = u"m",
    en = u"m"
)

translations.define("Action delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("cocktail.html.shortcuts action delete",
    ca = u"i",
    es = u"i",
    en = u"d"
)

translations.define("Action history",
    ca = u"Històric",
    es = u"Histórico",
    en = u"History"
)

translations.define("cocktail.html.shortcuts action history",
    ca = u"h",
    es = u"h",
    en = u"h"
)

translations.define("Action add",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("cocktail.html.shortcuts action add",
    ca = u"a",
    es = u"a",
    en = u"a"
)

translations.define("Action add_integral",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("cocktail.html.shortcuts action add_integral",
    ca = u"a",
    es = u"a",
    en = u"a"
)

translations.define("Action remove",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define("cocktail.html.shortcuts action remove",
    ca = u"r",
    es = u"r",
    en = u"r"
)

translations.define("Action diff",
    ca = u"Veure canvis",
    es = u"Ver cambios",
    en = u"Show changes"
)

translations.define("cocktail.html.shortcuts action diff",
    ca = u"c",
    es = u"c",
    en = u"c"
)

translations.define("Action preview",
    ca = u"Vista prèvia",
    es = u"Vista previa",
    en = u"Preview"
)

translations.define("cocktail.html.shortcuts action preview",
    ca = u"p",
    es = u"p",
    en = u"p"
)

translations.define("Action export_xls",
    ca = u"Exportar a MS Excel",
    es = u"Exportar a MS Excel",
    en = u"Export to MS Excel"
)

translations.define("Action save",
    ca = u"Desar",
    es = u"Guardar",
    en = u"Save"
)

translations.define("cocktail.html.shortcuts action save",
    ca = u"s",
    es = u"g",
    en = u"s"
)

translations.define("Action save_draft",
    ca = u"Desar esborrany",
    es = u"Guardar borrador",
    en = u"Save draft"
)

translations.define("Action confirm_draft",
    ca = u"Confirmar esborrany",
    es = u"Confirmar borrador",
    en = u"Confirm draft"
)

translations.define("Action select",
    ca = u"Seleccionar",
    es = u"Seleccionar",
    en = u"Select"
)

translations.define("cocktail.html.shortcuts action select",
    ca = u"s",
    es = u"s",
    en = u"s"
)

translations.define("Action close",
    ca = u"Tancar",
    es = u"Cerrar",
    en = u"Close"
)

translations.define("cocktail.html.shortcuts action close",
    ca = u"c",
    es = u"c",
    en = u"c"
)

translations.define("editing",
    ca = lambda item:
        u"Editant %s <em>'%s'</em>"
        % (translate(item.__class__.name, "ca").lower(),
           translate(item, "ca")),
    es = lambda item:
        u"Editando %s <em>'%s'</em>"
        % (translate(item.__class__.name, "es").lower(),
           translate(item, "es")),
    en = lambda item:
        u"Editing %s <em>'%s'</em>"
        % (translate(item.__class__.name, "es").lower(),
           translate(item, "es"))
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

translations.define("sitebasis.views.BackOfficeShowDetailView revert",
    ca = u"Desfer",
    es = u"Deshacer",
    en = u"Undo"
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

translations.define("BackOfficeContentView.class",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("ContentView search",
    ca = u"Cercar",
    es = u"Buscar",
    en = u"Search"
)

translations.define("sitebasis.views.ContentView label",
    ca = u"Veure com:",
    es = u"Ver como:",
    en = u"See as:"
)

translations.define("sitebasis.views.ContentView advanced search title",
    ca = u"Cerca avançada",
    es = u"Búsqueda avanzada",
    en = u"Advanced search"
)

translations.define("sitebasis.views.ContentView show advanced search",
    ca = u"Cerca avançada",
    es = u"Búsqueda avanzada",
    en = u"Advanced search"
)

translations.define("sitebasis.views.ContentView close advanced search",
    ca = u"Descartar la cerca",
    es = u"Descartar la búsqueda",
    en = u"Discard search"
)

translations.define("sitebasis.views.ContentView search button",
    ca = u"Cercar",
    es = u"Buscar",
    en = u"Search"
)

translations.define("Advanced search",
    ca = u"Cerca avançada",
    es = u"Búsqueda avanzada",
    en = u"Advanced search"
)

translations.define("draft_seq_name",
    ca = u"Esborrany %(index)s",
    es = u"Borrador %(index)s",
    en = u"Draft %(index)s"
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

translations.define("sitebasis.views.BackOfficeDiffView member",
    ca = u"Membre",
    es = u"Miembro",
    en = u"Member"
)

translations.define("sitebasis.views.BackOfficeDiffView previous value",
    ca = u"Valor anterior",
    es = u"Valor anterior",
    en = u"Previous value"
)

translations.define("sitebasis.views.BackOfficeDiffView new value",
    ca = u"Valor nou",
    es = u"Valor nuevo",
    en = u"New value"
)

translations.define("Action revert",
    ca = u"Desfer",
    es = u"Deshacer",
    en = u"Undo"
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

translations.define("sitebasis.views.ActionBar Additional actions",
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

translations.define(
    "sitebasis.controllers.backoffice.useractions.SelectionError-instance",
    ca = lambda instance: u"Acció no disponible en el context actual",
    es = lambda instance: u"Acción no disponible en el contexto actual",
    en = lambda instance: u"Action not available in the current context"
)

translations.define(
    "forbidden value",
    ca = u"Camp restringit",
    es = u"Campo restringido",
    en = u"Restricted field"
)

translations.define("Irrelevant access rule criteria",
    ca = u"Indiferent",
    es = u"Indifirente",
    en = u"Irrelevant"
)

def sitebasis_views_backofficedelete_view_warning_ca(selection):
    count = len(selection)
    if count == 1:
        return u"S'eliminarà l'element <strong>%s</strong>." \
            % translate(selection[0], "ca")
    else:
        return u"S'eliminaran els <strong>%d</strong> elements seleccionats." \
            % count

def sitebasis_views_backofficedelete_view_warning_es(selection):
    count = len(selection)
    if count == 1:
        return u"Se eliminará el elemento <strong>%s</strong>." \
            % translate(selection[0], "es")
    else:
        return u"Se eliminarán los <strong>%d</strong> elementos " \
            u"seleccionados." % count

def sitebasis_views_backofficedelete_view_warning_en(selection):
    count = len(selection)
    if count == 1:
        return u"The element <strong>%s</strong> will be deleted." \
            % translate(selection[0], "en")
    else:
        return u"All <strong>%d</strong> selected elements will be deleted." \
            % count

translations.define("sitebasis.views.BackOfficeDeleteView warning",
    ca = sitebasis_views_backofficedelete_view_warning_ca,
    es = sitebasis_views_backofficedelete_view_warning_es,
    en = sitebasis_views_backofficedelete_view_warning_en
)

translations.define("sitebasis.views.BackOfficeDeleteView delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("sitebasis.views.BackOfficeDeleteView cancel",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
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

translations.define("BackOfficeEditForm.change_password",
    ca = u"Canviar la contrasenya",
    es = u"Cambiar la contraseña",
    en = u"Change password"
)

translations.define("BackOfficeEditForm.password_confirmation",
    ca = u"Confirmar la contrasenya",
    es = u"Confirmar la contraseña",
    en = u"Confirm password"
)

translations.define(
    "sitebasis.controllers.backoffice.usereditnode."
    "PasswordConfirmationError-instance",
    ca = u"Les contrasenyes no coincideixen",
    es = u"Las contraseñas no coinciden",
    en = u"Passwords don't match"
)

translations.define(
    "sitebasis.views.BackOfficeEditView Changes saved",
    ca = u"S'han desat els canvis",
    es = u"Se han guardado los cambios",
    en = u"Changes saved"
)

translations.define(
    "sitebasis.controllers.backoffice.basebackofficecontroller."
    "EditStateLostError",
    ca = u"La sessió d'edició en que estaves treballant s'ha perdut.",
    es = u"La sesión de edición en que estabas trabajando se ha perdido.",
    en = u"The edit session you were working on has been lost."
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

translations.define("Item.identifier",
    ca = u"Identificador",
    es = u"Identificador",
    en = u"Identifier"
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

translations.define("Item.item_rules",
    ca = u"Regles (objecte)",
    es = u"Reglas (objeto)",
    en = u"Rules (object)"
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
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

translations.define("Document.page_resources",
    ca = u"Recursos HTML",
    es = u"Recursos HTML",
    en = u"HTML resources"
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

# Redirection
#------------------------------------------------------------------------------
translations.define("Redirection",
    ca = u"Redirecció",
    es = u"Redirección",
    en = u"Redirection"
)

translations.define("Redirection-plural",
    ca = u"Redireccions",
    es = u"Redirecciones",
    en = u"Redirections"
)

translations.define("Redirection.uri",
    ca = u"URL",
    es = u"URL",
    en = u"URL"
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

translations.define("User.password",
    ca = u"Contrasenya",
    es = u"Contraseña",
    en = u"Password"
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

translations.define("User.groups",
    ca = u"Grups",
    es = u"Grupos",
    en = u"Groups"
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

translations.define("AccessRule.target_member",
    ca = u"Camp",
    es = u"Campo",
    en = u"Field"
)

translations.define("AccessRule.target_is_draft",
    ca = u"L'element destí és un borrador",
    es = u"El elemento destino es un borrador",
    en = u"Target is a draft"
)

translations.define("AccessRule.target_draft_source",
    ca = u"Original de l'element destí",
    es = u"Original del elemento destino",
    en = u"Target's master item"
)

translations.define("AccessRule.allowed",
    ca = u"Permès",
    es = u"Permitido",
    en = u"Allowed"
)

# Resource
#------------------------------------------------------------------------------
translations.define("Resource",
    ca = u"Recurs",
    es = u"Recurso",
    en = u"Resource"
)

translations.define("Resource-plural",
    ca = u"Recursos",
    es = u"Recursos",
    en = u"Resources"
)

translations.define("Resource.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Resource.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Resource.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Enabled"
)

translations.define("Resource.start_date",
    ca = u"Data d'inici",
    es = u"Fecha de inicio",
    en = u"Start date"
)

translations.define("Resource.end_date",
    ca = u"Data de fi",
    es = u"Fecha de fin",
    en = u"End date"
)

translations.define("Resource.resource_type",
    ca = u"Tipus de recurs",
    es = u"Tipo de recurso",
    en = u"Resource type"
)

translations.define("Resource.documents",
    ca = u"Referències",
    es = u"Referencias",
    en = u"Referers"
)

translations.define("Resource.resource_type-text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("Resource.resource_type-image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("Resource.resource_type-audio",
    ca = u"Audio",
    es = u"Audio",
    en = u"Audio"
)

translations.define("Resource.resource_type-video",
    ca = u"Video",
    es = u"Video",
    en = u"Video"
)

translations.define("Resource.resource_type-document",
    ca = u"Document",
    es = u"Documento",
    en = u"Document"
)

translations.define("Resource.resource_type-html_resource",
    ca = u"Recurs HTML",
    es = u"Recurso HTML",
    en = u"HTML resource"
)

translations.define("Resource.resource_type-other",
    ca = u"Altre",
    es = u"Otro",
    en = u"Other"
)

# URI
#------------------------------------------------------------------------------
translations.define("URI",
    ca = u"Adreça web",
    es = u"Dirección web",
    en = u"Web address"
)

translations.define("URI-plural",
    ca = u"Adreces web",
    es = u"Direcciones web",
    en = u"Web addresses"
)

translations.define("URI.uri",
    ca = u"Adreça",
    es = u"Dirección",
    en = u"Address"
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

# Agent
#------------------------------------------------------------------------------
translations.define("Agent",
    ca = u"Agent",
    es = u"Agente",
    en = u"Agent"
)

translations.define("Agent-plural",
    ca = u"Agents",
    es = u"Agentes",
    en = u"Agents"
)

translations.define("Agent.agent_rules",
    ca = u"Regles (subjecte)",
    es = u"Reglas (sujeto)",
    en = u"Rules (subject)"
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

translations.define("File.file_name",
    ca = u"Nom del fitxer",
    es = u"Nombre del fichero",
    en = u"File name"
)

translations.define("File.mime_type",
    ca = u"Tipus MIME",
    es = u"Tipo MIME",
    en = u"MIME type"
)

translations.define("File.file_size",
    ca = u"Mida del fitxer",
    es = u"Tamaño de fichero",
    en = u"File size"
)

translations.define("BackOfficeEditForm.upload",
    ca = u"Càrrega de fitxer",
    es = u"Carga de fichero",
    en = u"File upload"
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
    ca = u"Rol",
    es = u"Rol",
    en = u"Role"
)

translations.define("Role-plural",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
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
