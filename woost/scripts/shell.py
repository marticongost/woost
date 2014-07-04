#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import *
from cocktail.persistence import *
from woost import app
from woost.models import *
from woost.models.utils import *
from woost.models.extension import load_extensions

def setup_shell(env):
    env["config"] = config = Configuration.instance
    config.setup_languages()
    set_current_user(User.require_instance(qname = "woost.anonymous_user"))
    set_current_website(config.websites[0])
    load_extensions()

