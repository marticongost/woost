#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.schema import TranslatedValues as T
from woost.models import Item, Controller, AccessLevel
from woost.models.rendering import ImageFactory, Thumbnail
from woost.admin.models import Admin

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

    ImageFactory.new(
        identifier = "admin_thumbnail",
        qname = "woost.admin.thumbnail",
        title = T(
            ca = u"Miniatura pel panell d'administració",
            es = u"Miniatura para el panel de administración",
            en = u"Admin thumbnail"
        ),
        effects = [Thumbnail.new(width = 200, height = 200)]
    )

    return Admin.new(
        path = "admin",
        qname = "woost.backoffice",
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
        root_section = "woost.admin.sections.rootsection.RootSection"
    )

def drop_admin():
    Admin.select().delete_items()
    expr = Item.qname.startswith("woost.admin.")
    ImageFactory.select(expr).delete_items()
    Controller.select(expr).delete_items()

