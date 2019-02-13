#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .folder import Folder
from .contactsection import ContactSection
from .metasection import MetaSection
from .emailtemplatessection import EmailTemplatesSection
from .blockcatalogssection import BlockCatalogsSection


class ContentSection(Folder):

    icon_uri = None

    def _fill(self):
        self.append(ContactSection("contact"))
        self.append(MetaSection("meta"))
        self.append(EmailTemplatesSection("email-templates"))
        self.append(BlockCatalogsSection("block-catalogs"))

