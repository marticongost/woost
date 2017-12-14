#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from pkg_resources import resource_filename
from cocktail.schema import TranslatedValues as T
from woost.models import Controller, AccessLevel, File
from woost.admin.models import Admin, Section

_section_tree = [
    {
        "path": "site-tree",
        "title": T(
            ca = u"Arbre del web",
            en = u"Site tree",
            es = u"Árbol de la web"
        )
    },
    {
        "path": "news",
        "title": T(
            ca = u"Notícies",
            en = u"News",
            es = u"Noticias"
        ),
        "ui_node": "woost.admin.nodes.CRUD",
        "data": """{"model": u"woost.models.News"}"""
    },
    {
        "path": "events",
        "title": T(
            ca = u"Esdeveniments",
            en = u"Events",
            es = u"Eventos"
        ),
        "ui_node": "woost.admin.nodes.CRUD",
        "data": """{"model": u"woost.models.Event"}"""
    },
    {
        "path": "files",
        "title": T(
            ca = u"Fitxers",
            en = u"Files",
            es = u"Ficheros"
        ),
        "ui_node": "woost.admin.nodes.CRUD",
        "data": """{"model": u"woost.models.File"}"""
    },
    {
        "path": "config",
        "title": T(
            ca = u"Configuració",
            en = u"Configuration",
            es = u"Configuración"
        ),
        "children": [
            {
                "path": "languages",
                "title": T(
                    ca = u"Idiomes",
                    en = u"Languages",
                    es = u"Idiomas"
                )
            },
            {
                "path": "websites",
                "title": T(
                    ca = u"Webs",
                    en = u"Websites",
                    es = u"Webs"
                )
            },
            {
                "path": "publication",
                "title": T(
                    ca = u"Publicació",
                    en = u"Publication",
                    es = u"Publicación"
                ),
                "children": [
                    {
                        "path": "special-pages",
                        "title": T(
                            ca = u"Pàgines especials",
                            en = u"Special pages",
                            es = u"Páginas especiales"
                        )
                    },
                    {
                        "path": "cache",
                        "title": T(
                            ca = u"Cache",
                            en = u"Cache",
                            es = u"Cache"
                        )
                    },
                    {
                        "path": "maintenance",
                        "title": T(
                            ca = u"Manteniment",
                            en = u"Maintenance",
                            es = u"Mantenimiento"
                        )
                    },
                    {
                        "path": "controllers",
                        "title": T(
                            ca = u"Controladors",
                            en = u"Controllers",
                            es = u"Controladores"
                        )
                    }
                ]
            },
            {
                "path": "access",
                "title": T(
                    ca = u"Control d'accés",
                    en = u"Access control",
                    es = u"Control de acceso"
                ),
                "children": [
                    {
                        "path": "users",
                        "title": T(
                            ca = u"Usuaris",
                            en = u"Users",
                            es = u"Usuarios"
                        )
                    },
                    {
                        "path": "roles",
                        "title": T(
                            ca = u"Rols",
                            en = u"Roles",
                            es = u"Roles"
                        )
                    },
                    {
                        "path": "access-levels",
                        "title": T(
                            ca = u"Nivells d'accés",
                            en = u"Access levels",
                            es = u"Niveles de acceso"
                        )
                    }
                ]
            },
            {
                "path": "look-and-feel",
                "title": T(
                    ca = u"Aparença",
                    en = u"Look and feel",
                    es = u"Apariencia"
                ),
                "children": [
                    {
                        "path": "templates",
                        "title": T(
                            ca = u"Plantilles",
                            en = u"Templates",
                            es = u"Plantillas"
                        )
                    },
                    {
                        "path": "email-templates",
                        "title": T(
                            ca = u"Plantilles de correu",
                            en = u"Email templates",
                            es = u"Plantillas de correo"
                        )
                    },
                    {
                        "path": "grids",
                        "title": T(
                            ca = u"Graelles",
                            en = u"Grids",
                            es = u"Matrices"
                        )
                    },
                    {
                        "path": "images",
                        "title": T(
                            ca = u"Processat d'imatge",
                            en = u"Image processing",
                            es = u"Procesado de imagen"
                        )
                    }
                ]
            }
        ]
    }
]

def create_admin():

    admin_controller = Controller.get_instance(
        qname = "woost.admin.admin_controller"
    )
    if admin_controller is None:
        admin_controller = Controller.new(
            qname = "woost.admin.admin_controller"
        )

    admin_controller.title = T(
        ca = u"Controlador de panell de control",
        es = u"Controlador de panel de control",
        en = u"Control panel controller"
    )
    admin_controller.python_name = \
        "woost.admin.controllers.admincontroller.AdminController"

    return Admin.new(
        path = "admin",
        access_level = AccessLevel.get_instance(
            qname = "woost.editor_access_level"
        ),
        controller = admin_controller,
        title = T(
            ca = u"Panell de control",
            es = u"Panel de control",
            en = u"Control panel"
        ),
        default_language = "en",
        sections = _create_sections(_section_tree)
    )

def _create_sections(tree):
    return [_create_section(tree_node) for tree_node in tree]

def _create_section(tree_node):

    section = Section.new()

    for key, value in tree_node.iteritems():
        if key == "children":
            value = _create_sections(value)
        section.set(key, value)

    section.image = File.new(
        title = T(
            ca = u"Icona de secció " + section.get("title", "ca"),
            es = u"Icono de sección " + section.get("title", "es"),
            en = u"Section icon for " + section.get("title", "en")
        ),
        file = resource_filename(
            "woost.admin.initialization",
            "images/" + section.path + ".svg"
        )
    )

    return section

def drop_admin():
    Admin.select().delete_items()
    Section.select().delete_items()

