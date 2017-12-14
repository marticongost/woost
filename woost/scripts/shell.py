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
from woost.models.extension import load_extensions
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
    app.website = config.websites[0]

    # Load extensions and import their models
    load_extensions()

    for extension in Extension.select():
        pkg_name = extension.__class__.__module__
        module_name = pkg_name.rsplit(".", 1)[1]
        ext_module = sys.modules[pkg_name]
        env[module_name] = ext_module
        setattr(ext_module, "instance", extension)
        if extension.enabled:
            for cls in Item.derived_schemas():
                if cls.full_name.startswith(pkg_name + "."):
                    setattr(ext_module, cls.__name__, cls)

get = Item.get_instance
req = Item.require_instance

def show(target):

    if isinstance(target, Publishable):
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

