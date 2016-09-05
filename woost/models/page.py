#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .document import Document
from .slot import Slot
from .configuration import Configuration


class Page(Document):

    blocks = Slot()

    def get_default_template(self):
        return (
            Configuration.instance.get_setting("default_page_template")
            or Document.get_default_template(self)
        )

