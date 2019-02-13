#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .path import ascend
from woost.models import Publishable

@ascend.implementation_for(Publishable)
def ascend_publishable(self):
    return self.ascend_tree()

