#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Template
from .dataexport import excluded_members

excluded_members.add(Template.documents)

