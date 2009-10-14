#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations import translations, ca_possessive

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
            "<strong>%s</strong>" % translations(user, "ca"),
    es = lambda user: u"Estás identificado como " \
            "<strong>%s</strong>" % translations(user, "es"),
    en = lambda user: u"Logged in as "
            "<strong>%s</strong>" % translations(user, "en")
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

translations.define("Action download",
    ca = u"Mostrar",
    es = u"Mostrar",
    en = u"Show"
)

translations.define("cocktail.html.shortcuts action download",
    ca = u"m",
    es = u"m",
    en = u"h"
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

translations.define("Action discard_draft",
    ca = u"Descartar esborrany",
    es = u"Descartar borrador",
    en = u"Discard draft"
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

translations.define("Action cancel",
    ca = u"Cancelar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define("cocktail.html.shortcuts action cancel",
    ca = u"c",
    es = u"c",
    en = u"c"
)

translations.define("Action print",
    ca = u"Imprimir",
    es = u"Imprimir",
    en = u"Print"
)

translations.define("cocktail.html.shortcuts action print",
    ca = u"i",
    es = u"i",
    en = u"i"
)

translations.define("editing",
    ca = lambda item:
        u"Editant %s <em>'%s'</em>"
        % (translations(item.__class__.name, "ca").lower(),
           translations(item, "ca")),
    es = lambda item:
        u"Editando %s <em>'%s'</em>"
        % (translations(item.__class__.name, "es").lower(),
           translations(item, "es")),
    en = lambda item:
        u"Editing %s <em>'%s'</em>"
        % (translations(item.__class__.name, "es").lower(),
           translations(item, "es"))
)

translations.define("creating",
    ca = lambda content_type:
        u"Creant %s" % translations(content_type.__name__, "ca").lower(),
    es = lambda content_type:
        u"Creando %s" % translations(content_type.__name__, "es").lower(),
    en = lambda content_type:
        u"Creating new %s" % translations(content_type.__name__, "en").lower()
)

translations.define("sitebasis.views.BackOfficeLayout edit stack select",
    ca = lambda type = None:
        u"Seleccionar " + translations(type.name, "ca").lower()
        if type
        else u"seleccionar",
    es = lambda type = None:
        u"Seleccionar " + translations(type.name, "es").lower()
        if type
        else u"seleccionar",
    en = lambda type = None:
        u"Select " + translations(type.name, "en").lower()
        if type
        else u"select",
)

translations.define("sitebasis.views.BackOfficeLayout edit stack add",
    ca = u"afegir",
    es = u"añadir",
    en = u"add"
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

translations.define("sitebasis.views.ContentTable sort ascending",
    ca = u"Ordre ascendent",
    es = u"Orden ascendente",
    en = u"Ascending order"
)

translations.define("sitebasis.views.ContentTable sort descending",
    ca = u"Ordre descendent",
    es = u"Orden descendente",
    en = u"Descending order"
)

translations.define("sitebasis.views.ContentTable add column filter",
    ca = u"Afegir un filtre",
    es = u"Añadir un filtro",
    en = u"Add a filter"
)

translations.define("BackOfficeContentView.element",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define("sitebasis.views.ContentView content type",
    ca = u"Tipus:",
    es = u"Tipo:",
    en = u"Type:"
)

translations.define("BackOfficeContentView.class",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("sitebasis.views.BackOfficeContentView user views",
    ca = u"Vistes freqüents:",
    es = u"Vistas frecuentes:",
    en = u"Bookmarks:"
)

translations.define("sitebasis.views.BackOfficeContentView add user view",
    ca = u"Crear vista",
    es = u"Crear vista",
    en = u"New view"
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

translations.define("sitebasis.views.ContentView show advanced search",
    ca = u"Més opcions de cerca",
    es = u"Mas opciones de búsqueda",
    en = u"More search options"
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

translations.define("sitebasis.models.Item draft copy",
    ca = lambda item, draft_id: u"Borrador %d %s"
        % (draft_id, ca_possessive(translations(item, "ca"))),
    es = lambda item, draft_id: u"Borrador %d de %s"
        % (draft_id, translations(item, "es")),
    en = lambda item, draft_id: u"Draft %d for %s"
        % (draft_id, translations(item, "en"))
)

translations.define("sitebasis.views.ContentTable draft label",
    ca = "Esborrany %(draft_id)d",
    es = "Borrador %(draft_id)d",
    en = "Draft %(draft_id)d"
)

translations.define("Differences for",
    ca = lambda item: u"Canvis a <em>'%s'</em>" % translations(item, "ca"),
    es = lambda item: u"Cambios en <em>'%s'</em>" % translations(item, "es"),
    en = lambda item: u"Changes in <em>'%s'</em>" % translations(item, "en")
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
    "sitebasis.controllers.backoffice.editstack.WrongEditStackError-instance",
    ca = u"La sessió d'edició indicada no existeix o s'ha perdut.",
    es = u"La sesión de edición indicada no existe o se ha perdido.",
    en = u"The indicated edit session doesn't exist, or it has been lost."
)


translations.define(
    "sitebasis.controllers.backoffice.editstack.EditStackExpiredError-instance",
    ca = u"La sessió d'edició ha expirat.",
    es = u"La sesión de edición ha expirado.",
    en = u"The indicated edit session has expired."
)

translations.define(
    "forbidden value",
    ca = u"Camp restringit",
    es = u"Campo restringido",
    en = u"Restricted field"
)

translations.define("sitebasis.views.BackOfficeDeleteView warning",
    ca = u"S'eliminarà els elements llistats:",
    es = u"Se eliminará los elementos listados:",
    en = u"The listed elements will be deleted:"
)

translations.define("sitebasis.views.BackOfficeDeleteView blocked_delete",
    ca = u"No es pot realitzar l'eliminació ja que els elements llistats no \
        estan buits:",
    es = u"No se puede realizar la eliminación ya que los elementos listados \
        no están vacios:",
    en = u"The deletion couldn't be performed because the listed elements \
        doesn't be empty:"
)

translations.define("sitebasis.views.BackOfficeDeleteView blocked_delete_item",
    ca = lambda blocked_item, blocked_member: u"<em>%s</em> de l'element \
        <strong>%s</strong>" \
        % (
            translations(blocked_member, "ca"),
            translations(blocked_item, "ca")
        ),
    es = lambda blocked_item, blocked_member: u"<em>%s</em> de l'elemento \
        <strong>%s</strong>" \
        % (
            translations(blocked_member, "es"),
            translations(blocked_item, "es")
        ),
    en = lambda blocked_item, blocked_member: u"<em>%s</em> from the \
        <strong>%s</strong> element" \
        % (
            translations(blocked_member, "en"),
            translations(blocked_item, "en")
        ),
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

translations.define("sitebasis.views.ItemSelector select",
    ca = u"Seleccionar...",
    es = u"Seleccionar...",
    en = u"Select..."
)

translations.define("sitebasis.views.BackOfficeItemSelectorView title", 
    ca = lambda type: "Seleccionar " + translations(type.name, "ca").lower(),
    es = lambda type: "Seleccionar " + translations(type.name, "es").lower(),
    en = lambda type: "Select " + translations(type.name, "en").lower()
)

translations.define("sitebasis.views.BackOfficeShowDetailView open resource",
    ca = u"Obrir el fitxer",
    es = u"Abrir el fichero",
    en = u"Show file"
)

translations.define(
    "sitebasis.models.userfilter.OwnItemsFilter-instance",
    ca = u"Elements propis",
    es = u"Elementos propios",
    en = u"Owned items"
)

translations.define(
    "sitebasis.models.userfilter.PublishedDocumentsFilter-instance",
    ca = u"Documents publicats",
    es = u"Documentos publicados",
    en = u"Published documents"
)

translations.define("sitebasis.models.userfilter.TypeFilter-instance",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("UserFilter.is_inherited",
    ca = u"Inclou fills",
    es = u"Incluye hijos",
    en = u"Children included"
)

# Initialization content
#------------------------------------------------------------------------------
translations.define(
    "sitebasis.models.initialization Administrators role title",
    ca = u"Administradors",
    es = u"Administradores",
    en = u"Administrators"
)

translations.define(
    "sitebasis.models.initialization Anonymous role title",
    ca = u"Anònim",
    es = u"Anónimo",
    en = u"Anonymous"
)

translations.define(
    "sitebasis.models.initialization Everybody role title",
    ca = u"Tothom",
    es = u"Todos los usuarios",
    en = u"Everybody"
)

translations.define(
    "sitebasis.models.initialization Authenticated role title",
    ca = u"Autenticat",
    es = u"Autenticado",
    en = u"Authenticated"
)

translations.define(
    "sitebasis.models.initialization Back office title",
    ca = u"Gestor de continguts",
    es = u"Gestor de contenidos",
    en = u"Content Manager"
)

translations.define(
    "sitebasis.models.initialization Standard template title",
    ca = u"Plantilla estàndard",
    es = u"Plantilla estándar",
    en = u"Standard template"
)

translations.define(
    "sitebasis.models.initialization Site style sheet title",
    ca = u"Full d'estils global",
    es = u"Hoja de estilos global",
    en = u"Global stylesheet"
)

translations.define(
    "sitebasis.models.initialization Home page title",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Web site"
)

translations.define(
    "sitebasis.models.initialization Home page inner title",
    ca = u"Benvingut!",
    es = u"Bienvenido!",
    en = u"Welcome!"
)

translations.define(
    "sitebasis.models.initialization Home page body",
    ca = u"<p>El teu lloc web s'ha creat correctament. Ja pots començar "
        u"a <a href='%(uri)s'>treballar-hi</a> i substituir aquesta pàgina "
        u"amb els teus propis continguts.</p>",
    es = u"<p>Tu sitio web se ha creado correctamente. Ya puedes empezar "
        u"a <a href='%(uri)s'>trabajar</a> en él y sustituir esta página "
        u"con tus propios contenidos.</p>",
    en = u"<p>Your web site has been created successfully. You can start "
        u"<a href='%(uri)s'>working on it</a> and replace this page with "
        u"your own content.</p>"
)

translations.define(
    "sitebasis.models.initialization Not found error page title",
    ca = u"Pàgina no trobada",
    es = u"Página no encontrada",
    en = u"Page not found"
)

translations.define(
    "sitebasis.models.initialization Not found error page body",
    ca = u"<p>La direcció indicada no coincideix amb cap dels continguts "
         u"del web. Si us plau, revísa-la i torna-ho a provar.</p>",
    es = u"<p>La dirección indicada no coincide con ninguno de los "
         u"contenidos del web. Por favor, revísala y intentalo de nuevo.</p>",
    en = u"<p>Couldn't find the indicated address. Please, verify it and try "
         u"again.</p>"
)

translations.define(
    "sitebasis.models.initialization Login page title",
    ca = u"Autenticació d'usuari",
    es = u"Autenticación de usuario",
    en = u"User authentication"
)

translations.define(
    "sitebasis.models.initialization Login page body",
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

translations.define(
    "sitebasis.models.initialization Forbidden error page title",
    ca = u"Accés denegat",
    es = u"Acceso denegado",
    en = u"Forbidden"
)

translations.define(
    "sitebasis.models.initialization Forbidden error page body",
    ca = u"<p>No es permet l'accés a aquesta secció del web.</p>",
    es = u"<p>No se permite el acceso a esta sección del sitio.</p>",
    en = u"<p>Access denied.</p>"
)

translations.define(
    "sitebasis.models.initialization Create action title",
    ca = u"Crear",
    es = u"Crear",
    en = u"Create"
)

translations.define(
    "sitebasis.models.initialization Read action title",
    ca = u"Veure",
    es = u"Ver",
    en = u"Read"
)

translations.define(
    "sitebasis.models.initialization Modify action title",
    ca = u"Modificar",
    es = u"Modificar",
    en = u"Modify"
)

translations.define(
    "sitebasis.models.initialization Delete action title",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define(
    "sitebasis.models.initialization Confirm draft action title",
    ca = u"Confirmar esborrany",
    es = u"Confirmar borrador",
    en = u"Confirm draft"
)

translations.define(
    "sitebasis.models.initialization Document tree user view",
    ca = u"Arbre de documents",
    es = u"Árbol de documentos",
    en = u"Document tree"
)

translations.define(
    "sitebasis.models.initialization Own items user view",
    ca = u"Els meus elements",
    es = u"Mis elementos",
    en = u"My items"
)

translations.define(
    "sitebasis.models.initialization Resource gallery user view",
    ca = u"Galeria de recursos",
    es = u"Galería de recursos",
    en = u"Resource gallery"
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

translations.define("thumbnails content view",
    ca = u"Veure com a miniatures",
    es = u"Ver como miniaturas",
    en = u"Show as thumbnails grid"
)

translations.define("calendar content view",
    ca = u"Veure com a calendari",
    es = u"Ver como calendario",
    en = u"Show as calendar"
)

translations.define("order content view",
    ca = u"Veure com a llista ordenable",
    es = u"Ver como lista ordenadable",
    en = u"Show as ordered listing"
)

translations.define("sitebasis.views.CalendarContentView current year",
    ca = u"Any actual",
    es = u"Año actual",
    en = u"Current year"
)

translations.define("sitebasis.views.CalendarContentView previous year",
    ca = u"Any anterior",
    es = u"Año anterior",
    en = u"Previous year"
)

translations.define("sitebasis.views.CalendarContentView next year",
    ca = u"Any següent",
    es = u"Año siguiente",
    en = u"Next year"
)

translations.define("sitebasis.views.CalendarContentView current month",
    ca = u"Mes actual",
    es = u"Mes actual",
    en = u"Current month"
)

translations.define("sitebasis.views.CalendarContentView previous month",
    ca = u"Mes anterior",
    es = u"Mes anterior",
    en = u"Previous month"
)

translations.define("sitebasis.views.CalendarContentView next month",
    ca = u"Mes següent",
    es = u"Mes siguiente",
    en = u"Next month"
)

translations.define("sitebasis.views.CalendarContentView select year layout",
    ca = u"Vista de l'any",
    es = u"Vista del año",
    en = u"Year view"
)

translations.define(
    "sitebasis.views.CalendarContentView ongoing items message",
    ca = u"Elements en curs:",
    es = u"Elementos en curso:",
    en = u"Ongoing items:"
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
    ca = lambda item, is_new:
        (
            u"S'ha creat l'element <strong>%s</strong>"
            if is_new
            else u"Canvis a <strong>%s</strong> desats"
        )
        % translations(item, "ca"),
    es = lambda item, is_new:
        (
            u"Se ha creado el elemento <strong>%s</strong>"
            if is_new
            else u"Cambios en <strong>%s</strong> guardados"
        )
        % translations(item, "es"),
    en = lambda item, is_new:
        (
            u"New item <strong>%s</strong> stored"
            if is_new
            else u"Saved changes to <strong>%s</strong>"
        )
        % translations(item, "en")
)

translations.define("sitebasis.views.BackOfficeEditView Create another",
    ca = u"Crear un altre element",
    es = u"Crear otro elemento",
    en = u"Create another item"
)

translations.define(
    "sitebasis.views.BackOfficeEditView Draft confirmed",
    ca = lambda item, is_new:
        (
            u"S'ha creat l'element <strong>%s</strong> a partir de l'esborrany"
            if is_new
            else u"Els canvis de l'esborrany s'han aplicat a "
                 u"<strong>%s</strong>"
        )
        % translations(item, "ca"),
    es = lambda item, is_new:
        (
            u"Se ha creado el elemento <strong>%s</strong> a partir del "
            u"borrador"
            if is_new
            else u"Se ha actualizado <strong>%s</strong> con los cambios del "
                 u"borrador"
        )
        % translations(item, "es"),
    en = lambda item, is_new:
        (
            u"Draft stored as new item <strong>%s</strong>"
            if is_new
            else u"Saved changes from draft to <strong>%s</strong>"
        )
        % translations(item, "en")
)

translations.define(
    "sitebasis.views.BackOfficeItemView pending changes warning",
    ca = u"Hi ha canvis pendents de desar. Si abandones el formulari d'edició "
        u"els canvis es perdran.",
    es = u"Hay cambios pendientes de guardar. Si abandonas el formulario de "
        u"edición los cambios se perderán.",
    en = u"There are unsaved changes. If you navigate away from the edit form "
        u"your modifications will be lost."
)

translations.define(
    "sitebasis.controllers.backoffice.basebackofficecontroller."
    "EditStateLostError",
    ca = u"La sessió d'edició en que estaves treballant s'ha perdut.",
    es = u"La sesión de edición en que estabas trabajando se ha perdido.",
    en = u"The edit session you were working on has been lost."
)

translations.define("sitebasis.views.BaseView alternate language link",
    ca = lambda lang: u"Versió en " + translations(lang, "ca"),
    es = lambda lang: u"Versión en " + translations(lang, "es"),
    en = lambda lang: translations(lang, "en") + " version"
)

translations.define("sitebasis.views.StandardView attachment icon description",
    ca = u"Icona",
    es = u"Icono",
    en = u"Icon"
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

translations.define("Site.keywords",
    ca = u"Paraules clau",
    es = u"Palabras clave",
    en = u"Keywords"
)

translations.define("Site.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Site.icon",
    ca = u"Icona",
    es = u"Icono",
    en = u"Icon"
)

translations.define("Site.smtp_host",
    ca = u"Servidor SMTP",
    es = u"Servidor SMTP",
    en = u"SMTP host"
)

translations.define("Site.triggers",
    ca = u"Disparadors",
    es = u"Disparadores",
    en = u"Triggers"
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

translations.define("Site.login_page",
    ca = u"Formulari d'autenticació",
    es = u"Formulario de autenticación",
    en = u"Authentication form"
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

translations.define("Site.extensions",
    ca = u"Extensions",
    es = u"Extensiones",
    en = u"extensions"
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

translations.define("Document.keywords",
    ca = u"Paraules clau",
    es = u"Palabras clave",
    en = u"Keywords"
)

translations.define("Document.start_date",
    ca = u"Data de publicació",
    es = u"Fecha de publicación",
    en = u"Publication date"
)

translations.define("Document.end_date",
    ca = u"Data de caducitat",
    es = u"Fecha de caducidad",
    en = u"Expiration date"
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
    ca = u"Recursos de pàgina",
    es = u"Recursos de pàgina",
    en = u"Page resources"
)

translations.define("Document.branch_resources",
    ca = u"Recursos de branca",
    es = u"Recursos de rama",
    en = u"Branch resources"
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

translations.define("User.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

# Permission
#------------------------------------------------------------------------------
translations.define("Permission",
    ca = u"Permís",
    es = u"Permiso",
    en = u"Permission"
)

translations.define("Permission-plural",
    ca = u"Permisos",
    es = u"Permisos",
    en = u"Permissions"
)

translations.define("Permission.role",
    ca = u"Rol",
    es = u"Rol",
    en = u"Role"
)

translations.define("Permission.authorized",
    ca = u"Autoritzat",
    es = u"Autorizado",
    en = u"Authorized"
)

translations.define("Permission.authorized-explanation",
    ca = u"Si es desmarca, el permís passa a actuar com una prohibició",
    es = u"Si se desmarca, el permiso pasa a actuar como una prohibición",
    en = u"If unchecked, the permission is treated as a prohibition"
)

# ContentPermission
#------------------------------------------------------------------------------
translations.define("ContentPermission",
    ca = u"Permís de contingut",
    es = u"Permiso de contenido",
    en = u"Content permission"
)

translations.define("ContentPermission-plural",
    ca = u"Permisos de contingut",
    es = u"Permisos de contenido",
    en = u"Content permissions"
)

translations.define("ContentPermission.matching_items",
    ca = u"Elements inclosos",
    es = u"Elementos incluidos",
    en = u"Included items"
)

# ReadPermission
#------------------------------------------------------------------------------
translations.define("ReadPermission",
    ca = u"Permís de lectura",
    es = u"Permiso de lectura",
    en = u"Read content permission"
)

translations.define("ReadPermission-plural",
    ca = u"Permisos de lectura",
    es = u"Permisos de lectura",
    en = u"Read content permissions"
)

# CreatePermission
#------------------------------------------------------------------------------
translations.define("CreatePermission",
    ca = u"Permís de creació",
    es = u"Permiso de creación",
    en = u"Create content permission"
)

translations.define("CreatePermission-plural",
    ca = u"Permisos de creació",
    es = u"Permisos de creación",
    en = u"Create content permissions"
)

# ModifyPermission
#------------------------------------------------------------------------------
translations.define("ModifyPermission",
    ca = u"Permís de modificació",
    es = u"Permiso de modificación",
    en = u"Modify content permission"
)

translations.define("ModifyPermission-plural",
    ca = u"Permisos de modificació",
    es = u"Permisos de modificación",
    en = u"Modify content permissions"
)

# DeletePermission
#------------------------------------------------------------------------------
translations.define("DeletePermission",
    ca = u"Permís d'eliminació",
    es = u"Permiso de eliminación",
    en = u"Delete content permission"
)

translations.define("DeletePermission-plural",
    ca = u"Permisos d'eliminació",
    es = u"Permisos de eliminación",
    en = u"Delete content permissions"
)

# ConfirmDraftPermission
#------------------------------------------------------------------------------
translations.define("ConfirmDraftPermission",
    ca = u"Permís de confirmació d'esborranys",
    es = u"Permiso de confirmación de borradores",
    en = u"Confirm draft permission"
)

translations.define("ConfirmDraftPermission-plural",
    ca = u"Permisos de confirmació d'esborranys",
    es = u"Permisos de confirmación de borradores",
    en = u"Confirm draft permissions"
)

# MemberPermission
#------------------------------------------------------------------------------
translations.define("MemberPermission",
    ca = u"Permís de membre",
    es = u"Permiso de miembro",
    en = u"Member permission"
)

translations.define("MemberPermission-plural",
    ca = u"Permisos sobre els membres",
    es = u"Permisos sobre los miembros",
    en = u"Member permissions"
)

translations.define("MemberPermission.matching_members",
    ca = u"Membres inclosos",
    es = u"Miembros incluidos",
    en = u"Included members"
)

# ReadMemberPermission
#------------------------------------------------------------------------------
translations.define("ReadMemberPermission",
    ca = u"Permís de lectura de membres",
    es = u"Permiso de lectura de miembros",
    en = u"Read members permission"
)

translations.define("ReadMemberPermission-plural",
    ca = u"Permisos de lectura de membres",
    es = u"Permisos de lectura de miembros",
    en = u"Read members permissions"
)

# ModifyMemberPermission
#------------------------------------------------------------------------------
translations.define("ModifyMemberPermission",
    ca = u"Permís de modificació de membres",
    es = u"Permiso de modificación de miembros",
    en = u"Modify members permission"
)

translations.define("ModifyMemberPermission-plural",
    ca = u"Permisos de lectura de membres",
    es = u"Permisos de lectura de miembros",
    en = u"Read members permissions"
)

# TranslationPermission
#------------------------------------------------------------------------------
translations.define("TranslationPermission",
    ca = u"Permís de traducció",
    es = u"Permiso de traducción",
    en = u"Translation permission"
)

translations.define("TranslationPermission-plural",
    ca = u"Permisos de traducció",
    es = u"Permisos de traducción",
    en = u"Translation permissions"
)

translations.define("TranslationPermission.matching_languages",
    ca = u"Idiomes inclosos",
    es = u"Idiomas incluidos",
    en = u"Included languages"
)

# ReadTranslationPermission
#------------------------------------------------------------------------------
translations.define("ReadTranslationPermission",
    ca = u"Permís de lectura de traducció",
    es = u"Permiso de lectura de traducción",
    en = u"Read translation permission"
)

translations.define("ReadTranslationPermission-plural",
    ca = u"Permisos de lectura de traducció",
    es = u"Permisos de lectura de traducción",
    en = u"Read translation permissions"
)

# CreateTranslationPermission
#------------------------------------------------------------------------------
translations.define("CreateTranslationPermission",
    ca = u"Permís de creació de traducció",
    es = u"Permiso de creación de traducción",
    en = u"Create translation permission"
)

translations.define("CreateTranslationPermission-plural",
    ca = u"Permisos de creació de traducció",
    es = u"Permisos de creación de traducción",
    en = u"Create translation permissions"
)

# ModifyTranslationPermission
#------------------------------------------------------------------------------
translations.define("ModifyTranslationPermission",
    ca = u"Permís de modificació de traducció",
    es = u"Permiso de modificación de traducción",
    en = u"Modify translation permission"
)

translations.define("ModifyTranslationPermission-plural",
    ca = u"Permisos de modificació de traducció",
    es = u"Permisos de modificación de traducción",
    en = u"Modify translation permissions"
)

# DeleteTranslationPermission
#------------------------------------------------------------------------------
translations.define("DeleteTranslationPermission",
    ca = u"Permís d'eliminació de traducció",
    es = u"Permiso de eliminación de traducción",
    en = u"Delete translation permission"
)

translations.define("DeleteTranslationPermission-plural",
    ca = u"Permisos d'eliminació de traducció",
    es = u"Permisos de eliminación de traducción",
    en = u"Delete translation permissions"
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
    ca = u"Data de publicació",
    es = u"Fecha de publicación",
    en = u"Publication date"
)

translations.define("Resource.end_date",
    ca = u"Data de caducitat",
    es = u"Fecha de caducidad",
    en = u"Expiration date"
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

# UserView
#------------------------------------------------------------------------------
translations.define("UserView",
    ca = u"Vista d'usuari",
    es = u"Vista de usuario",
    en = u"User view"
)

translations.define("UserView-plural",
    ca = u"Vistes d'usuari",
    es = u"Vistas de usuario",
    en = u"User views"
)

translations.define("UserView.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("UserView.parameters",
    ca = u"Vista",
    es = u"Vista",
    en = u"View"
)

translations.define("UserView.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
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

translations.define("Role.users",
    ca = u"Usuaris",
    es = u"Usuarios",
    en = u"Users"
)

translations.define("Role.user_views",
    ca = u"Vistes d'usuari",
    es = u"Vistas de usuario",
    en = u"User views"
)

translations.define("Role.permissions",
    ca = u"Permisos",
    es = u"Permisos",
    en = u"Permissions"
)

translations.define("Role.base_roles",
    ca = u"Rols base",
    es = u"Roles base",
    en = u"Base roles"
)

translations.define("Role.child_roles",
    ca = u"Rols derivats",
    es = u"Roles derivados",
    en = u"Derived roles"
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

# Extension
#------------------------------------------------------------------------------
translations.define("Extension",
    ca = u"Extensió",
    es = u"Extensión",
    en = u"Extension"
)

translations.define("Extension-plural",
    ca = u"Extensions",
    es = u"Extensiones",
    en = u"Extensions"
)

translations.define("Extension.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Extension.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Extension.extension_author",
    ca = u"Autor de l'extensió",
    es = u"Autor de la extensión",
    en = u"Extension author"
)

translations.define("Extension.license",
    ca = u"Llicència",
    es = u"Licencia",
    en = u"License"
)

translations.define("Extension.web_page",
    ca = u"Pàgina web",
    es = u"Página web",
    en = u"Web page"
)

translations.define("Extension.enabled",
    ca = u"Activada",
    es = u"Activada",
    en = u"Enabled"
)

# ChangeSet
#------------------------------------------------------------------------------
translations.define("ChangeSet",
    ca = u"Revisió",
    es = u"Revisión",
    en = u"Revision"
)

translations.define("ChangeSet-plural",
    ca = u"Revisions",
    es = u"Revisiones",
    en = u"Revisions"
)

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

# Change
#------------------------------------------------------------------------------
translations.define("Change",
    ca = u"Canvi",
    es = u"Cambio",
    en = u"Change"
)

translations.define("ChangeSet-plural",
    ca = u"Canvis",
    es = u"Cambios",
    en = u"Changes"
)

translations.define("Change.id",
    ca = u"ID",
    es = u"ID",
    en = u"ID"
)

translations.define("Change.changeset",
    ca = u"Revisió",
    es = u"Revisión",
    en = u"Revision"
)

translations.define("Change.action",
    ca = u"Acció",
    es = u"Acción",
    en = u"Action"
)

translations.define("Change.target",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define("Change.changed_members",
    ca = u"Membres modificats",
    es = u"Miembros modificados",
    en = u"Modified members"
)

translations.define("Change.item_state",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

def _translate_sitebasis_models_change_instance_ca(action, target):
    
    if isinstance(target, int):
        target_desc = "%d elements" % target
        apostrophe = False
    else:
        target_desc = translations(target, "ca")

        if not target_desc:
            return ""

        apostrophe = target_desc[0].lower() in u"haeiouàèéíòóú"
        target_desc = u"<em>" + target_desc + u"</em>"
    
    action_id = action.identifier

    if action_id == "edit":
        action_desc = u"Edició"
    elif action_id == "create":
        action_desc = u"Creació"
    elif action_id == "delete":
        action_desc = u"Eliminació"
    else:
        return ""
    
    return action_desc + (" d'" if apostrophe else " de ") + target_desc

def _translate_sitebasis_models_change_instance_es(action, target):
    
    if isinstance(target, int):
        target_desc = "%d elementos" % target
    else:
        target_desc = translations(target, "es")

        if not target_desc:
            return ""

        target_desc = u"<em>" + target_desc + u"</em>"
    
    action_id = action.identifier

    if action_id == "edit":
        action_desc = u"Edición"
    elif action_id == "create":
        action_desc = u"Creación"
    elif action_id == "delete":
        action_desc = u"Eliminación"
    else:
        return ""
    
    return action_desc + u" de " + target_desc

def _translate_sitebasis_models_change_instance_en(action, target):
    
    if isinstance(target, int):
        target_desc = "%d items" % target
    else:
        target_desc = translations(target, "ca")

        if not target_desc:
            return ""
        
        target_desc = u"<em>" + target_desc + u"</em>"
    
    action_id = action.identifier

    if action_id == "edit":
        action_desc = u"modified"
    elif action_id == "create":
        action_desc = u"created"
    elif action_id == "delete":
        action_desc = u"deleted"
    else:
        return ""
    
    return target_desc + u" " + action_desc

translations.define("sitebasis.models.changesets.Change description",
    ca = _translate_sitebasis_models_change_instance_ca,
    es = _translate_sitebasis_models_change_instance_es,
    en = _translate_sitebasis_models_change_instance_en
)

# Trigger
#------------------------------------------------------------------------------
translations.define("Trigger",
    ca = u"Disparador",
    es = u"Disparador",
    en = u"Trigger"
)

translations.define("Trigger-plural",
    ca = u"Disparadors",
    es = u"Disparadores",
    en = u"Triggers"
)

translations.define("Trigger.execution_point",
    ca = u"Moment d'execució",
    es = u"Momento de ejecución",
    en = u"Execution point"
)

translations.define("Trigger.batch_execution",
    ca = u"Execució agrupada",
    es = u"Ejecución agrupada",
    en = u"Batch execution"
)

translations.define("Trigger.batch_execution-explanation",
    ca = u"Si s'agrupa l'execució, el disparador només s'activarà un cop per "
         u"transacció, independentment de quantes accions d'aquest tipus "
         u"s'hagin realitzat.",
    es = u"Si se agrupa la ejecución, el disparador solo se activará una vez "
         u"por transacción, sin importar cuantas acciones de este tipo "
         u"se hayan realizado.",
    en = u"If checked, the trigger will be activated only once per "
         u"transaction, regardless of how many times its activation "
         u"conditions are met."
)

translations.define("Trigger.matching_roles",
    ca = u"Rols a observar",
    es = u"Roles a observar",
    en = u"Watched roles"
)

translations.define("Trigger.matching_roles-explanation",
    ca = u"Si no es selecciona cap rol, el disparador s'activarà "
         u"independentment de l'usuari que inicii l'acció.",
    es = u"Si no se selecciona ningún rol, el disparador se activará "
         u"independientemente del usuario que inicie la acción.",
    en = u"If no role is checked, the trigger will execute regardless "
         u"of which user started the action."
)

translations.define("Trigger.condition",
    ca = u"Condició",
    es = u"Condición",
    en = u"Condition"
)

translations.define("Trigger.condition-explanation",
    ca = u"Una expressió en python que determina si s'executa o no el "
         u"disparador.",
    es = u"Una expresión en python que determina si se ejecuta o no el "
         u"disparador.",
    en = u"A python expression that enables or disables the execution of "
         u"the trigger depending on its context."
)

translations.define("Trigger.responses",
    ca = u"Respostes",
    es = u"Respuestas",
    en = u"Responses"
)

translations.define("sitebasis.models.Trigger.execution_point before",
    ca = u"Immediatament",
    es = u"Inmediatamente",
    en = u"Immediately"
)

translations.define("sitebasis.models.Trigger.execution_point after",
    ca = u"En confirmar la transacció",
    es = u"Tras confirmar la transacción",
    en = u"After committing the transaction"
)

# ContentTrigger
#------------------------------------------------------------------------------
translations.define("ContentTrigger",
    ca = u"Disparador per elements",
    es = u"Disparador para elementos",
    en = u"Content trigger"
)

translations.define("ContentTrigger-plural",
    ca = u"Disparadors per contingut",
    es = u"Disparadores para contenido",
    en = u"Content triggers"
)

translations.define("ContentTrigger.matching_items",
    ca = u"Elements a observar",
    es = u"Elementos a observar",
    en = u"Watched items"
)

# CreateTrigger
#------------------------------------------------------------------------------
translations.define("CreateTrigger",
    ca = u"Disparador de creació",
    es = u"Disparador de creación",
    en = u"Create trigger"
)

translations.define("CreateTrigger-plural",
    ca = u"Disparadors de creació",
    es = u"Disparadores de creación",
    en = u"Create triggers"
)

# InsertTrigger
#------------------------------------------------------------------------------
translations.define("InsertTrigger",
    ca = u"Disparador d'inserció",
    es = u"Disparador de inserción",
    en = u"Insert trigger"
)

translations.define("InsertTrigger-plural",
    ca = u"Disparadors d'inserció",
    es = u"Disparadores de inserción",
    en = u"Insert triggers"
)

# ModifyTrigger
#------------------------------------------------------------------------------
translations.define("ModifyTrigger",
    ca = u"Disparador de modificació",
    es = u"Disparador de modificación",
    en = u"Modify trigger"
)

translations.define("ModifyTrigger-plural",
    ca = u"Disparadors de modificació",
    es = u"Disparadores de modificación",
    en = u"Modify triggers"
)

translations.define("ModifyTrigger.matching_members",
    ca = u"Membres a observar",
    es = u"Miembros a observar",
    en = u"Watched members"
)

translations.define("ModifyTrigger.matching_members-explanation",
    ca = u"Si no es selecciona cap membre, el disparador s'activarà "
         u"sigui quin sigui el membre modificat.",
    es = u"Si no se selecciona ningún miembro, el disparador se activará "
         u"sea cual sea el miembro modificado.",
    en = u"If no member is checked, the trigger will execute regardless "
         u"of which member is modified."
)

translations.define("ModifyTrigger.matching_languages",
    ca = u"Idiomes a observar",
    es = u"Idiomas a observar",
    en = u"Watched languages"
)

translations.define("ModifyTrigger.matching_languages-explanation",
    ca = u"Si no es selecciona cap idioma, el disparador s'activarà "
         u"sigui quin sigui l'idioma dels valors modificats.",
    es = u"Si no se selecciona ningún idioma, el disparador se activará "
         u"independientemente del idioma de los valores modificados.",
    en = u"If no language is checked, the trigger will execute regardless "
         u"of which language modified values are translated into."
)

# DeleteTrigger
#------------------------------------------------------------------------------
translations.define("DeleteTrigger",
    ca = u"Disparador d'eliminació",
    es = u"Disparador de eliminación",
    en = u"Delete trigger"
)

translations.define("DeleteTrigger-plural",
    ca = u"Disparadors d'eliminació",
    es = u"Disparadores de eliminación",
    en = u"Delete triggers"
)

# TriggerResponse
#------------------------------------------------------------------------------
translations.define("TriggerResponse",
    ca = u"Resposta",
    es = u"Respuesta",
    en = u"Trigger response"
)

translations.define("TriggerResponse-plural",
    ca = u"Respostes",
    es = u"Respuestas",
    en = u"Trigger responses"
)

# CustomTriggerResponse
#------------------------------------------------------------------------------
translations.define("CustomTriggerResponse",
    ca = u"Resposta personalitzada",
    es = u"Respuesta personalizada",
    en = u"Custom response"
)

translations.define("CustomTriggerResponse-plural",
    ca = u"Respostes personalitzades",
    es = u"Respuestas personalizadas",
    en = u"Custom responses"
)

translations.define("CustomTriggerResponse.code",
    ca = u"Codi de resposta",
    es = u"Código de respuesta",
    en = u"Response code"
)

# SendEmailTriggerResponse
#------------------------------------------------------------------------------
translations.define("SendEmailTriggerResponse",
    ca = u"Resposta per correu electrònic",
    es = u"Respuesta po correo electrónico",
    en = u"E-mail response"
)

translations.define("SendEmailTriggerResponse-plural",
    ca = u"Respostes per correu electrònic",
    es = u"Respuestas por correo electrónico",
    en = u"E-mail responses"
)

translations.define("SendEmailTriggerResponse.sender",
    ca = u"Remitent",
    es = u"Remitente",
    en = u"Sender"
)

translations.define("SendEmailTriggerResponse.receivers",
    ca = u"Destinataris",
    es = u"Destinatarios",
    en = u"Receivers"
)

translations.define("SendEmailTriggerResponse.subject",
    ca = u"Assumpte",
    es = u"Asunto",
    en = u"Subject"
)

translations.define("SendEmailTriggerResponse.body",
    ca = u"Cos del missatge",
    es = u"Cuerpo del mensaje",
    en = u"Message body"
)

translations.define("SendEmailTriggerResponse.template_engine",
    ca = u"Motor de pintat",
    es = u"Motor de pintado",
    en = u"Rendering engine"
)

# Feed
#------------------------------------------------------------------------------
translations.define("Feed",
    ca = u"Canal de sindicació",
    es = u"Canal de sindicación",
    en = u"Syndication feed"
)

translations.define("Feed-plural",
    ca = u"Canals de sindicació",
    es = u"Canales de sindicación",
    en = u"Syndication feeds"
)

translations.define("Feed.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Feed.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Enabled"
)

translations.define("Feed.ttl",
    ca = u"Temps d'expiració (TTL)",
    es = u"Tiempo de expiración (TTL)",
    en = u"TTL"
)

translations.define("Feed.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("Feed.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Feed.limit",
    ca = u"Límit d'elements publicats",
    es = u"Límite de elementos publicados",
    en = u"Published items limit"
)

translations.define("Feed.query_parameters",
    ca = u"Elements publicats",
    es = u"Elementos publicados",
    en = u"Published items"
)

translations.define("Feed.item_title_expression",
    ca = u"Expressió pel títol dels elements",
    es = u"Expresión para el título de los elementos",
    en = u"Item title expression"
)

translations.define("Feed.item_link_expression",
    ca = u"Expressió per l'enllaç dels elements",
    es = u"Expresión para el enlace de los elementos",
    en = u"Item link expression"
)

translations.define("Feed.item_publication_date_expression",
    ca = u"Expressió per la data de publicació dels elements",
    es = u"Expresión para la fecha de publicación de los elementos",
    en = u"Item publication date expression"
)

translations.define("Feed.item_description_expression",
    ca = u"Expressió per la descripció dels elements",
    es = u"Expresión para la descripción de los elementos",
    en = u"Item description expression"
)

# ContentTypePicker
#------------------------------------------------------------------------------
translations.define("sitebasis.views.ContentTypePicker select",
    ca = u"Seleccionar...",
    es = u"Seleccionar...",
    en = u"Select..."
)

translations.define("sitebasis.views.ContentTypePicker accept",
    ca = u"Acceptar",
    es = u"Aceptar",
    en = u"Accept"
)

translations.define("sitebasis.views.ContentTypePicker cancel",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

# Preview
#------------------------------------------------------------------------------
translations.define("sitebasis.backoffice invalid item preview",
    ca = u"Algun camp del formulari no té un format correcte. "
         u"No es pot realitzar la vista prèvia.",
    es = u"Algún campo del formulario no tiene un formato correcto. "
         u"No se puede realizar la vista previa.",
    en = u"Some form field has no correct format. "
         u"Impossible to render preview."
)

