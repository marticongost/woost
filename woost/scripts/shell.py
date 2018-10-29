#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
from decimal import Decimal
from datetime import date, datetime, time, timedelta
from collections import Counter, defaultdict
import webbrowser
from cocktail.schema import TranslatedValues as T
from cocktail.translations import *
from cocktail.persistence import *
from woost import app
from woost.models import *
from woost.admin.models import *
from woost.models.utils import *
from woost.models.extension import extensions_manager
from woost.models.objectio import (
    ExportMode,
    UnknownMemberPolicy,
    MissingObjectPolicy,
    ObjectExporter,
    ObjectImporter
)

def setup_shell(env):
    env["config"] = config = Configuration.instance
    env["tr"] = translations
    config.setup_languages()
    app.user = User.require_instance(qname = "woost.anonymous_user")
    app.website = Website.select()[0]

    # Load extensions and import their models
    extensions_manager.load_extensions()

    for extension in extensions_manager.iter_extensions():
        module_name = extension.__name__[extension.__name__.rfind(".") + 1:]
        env[module_name] = extension

get = Item.get_instance
req = Item.require_instance

def show(target):

    if isinstance(target, PublishableObject):
        webbrowser.open(target.get_uri(host = "!"))
    elif hasattr(target, "__iter__"):
        for item in target:
            show(item)
    else:
        print "Can't show non-publishable object %r" % target

def edit(target):

    backoffice = Publishable.require_instance(qname = "woost.backoffice")

    if isinstance(target, Item):
        webbrowser.open(
            backoffice.get_uri(
                host = "!",
                path = ["content", str(target.id)]
            )
        )
    elif hasattr(target, "__iter__"):
        for item in target:
            edit(item)
    else:
        print "Can't edit object %r" % target

def fetch(cls, *args, **kwargs):
    return list(cls.select(*args, **kwargs))

