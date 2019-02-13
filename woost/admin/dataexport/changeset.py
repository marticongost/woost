#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import ChangeSet
from .dataexport import Export

Export.member_expansion[ChangeSet.changes.values] = True

