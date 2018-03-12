#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .contactsection import ContactSection
from .metasection import MetaSection


class ContentSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(ContactSection("contact"))
        self.append(MetaSection("meta"))

