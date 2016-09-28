#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import Website, Slot

translations.load_bundle("woost.extensions.notices.website")
Website.add_member(Slot("notices"))

