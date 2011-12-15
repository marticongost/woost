#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.persistence import datastore
from woost.models import Extension, Controller, Language

translations.define("TextFileExtension",
    ca = u"Fitxers de text",
    es = u"Ficheros de texto",
    en = u"Text files"
)


class TextFileExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"Permet editar fitxers de text directament des del gestor.",
            "ca"
        )
        self.set("description",            
            u"Permite editar ficheros de texto directamente desde el gestor.",
            "es"
        )
        self.set("description",
            u"Makes it possible to edit text files from the backoffice.",
            "en"
        )
    
    @event_handler
    def handle_loading(cls, event):        
        from woost.extensions.textfile import textfile, strings
        extension = event.source
        
        if not extension.installed:
            controller = extension.create_text_file_controller()
            controller.insert()
            datastore.commit()

    def create_text_file_controller(self):

        controller = Controller(
            qname = "woost.extensions.textfile.TextFileController",
            python_name = "woost.extensions.textfile.textfilecontroller."
                          "TextFileController"
        )
        
        for language in Language.codes:            
            title = translations(
                "woost.extensions.textfile.controller_title",
                language
            )
            if title:
                controller.set("title", title, language)
        
        return controller

