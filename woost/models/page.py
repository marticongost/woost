#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .document import Document
from .slot import Slot
from .defaulttemplate import with_default_template


@with_default_template("page")
class Page(Document):
    blocks = Slot()

