#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.persistence import datastore, InstanceNotFoundError
from woost.models import Item, Configuration, Website

WEBSITE_PREFIX = "website-"

def resolve_object_ref(id):

    if id == "config":
        return Configuration.instance

    if id.startswith(WEBSITE_PREFIX):
        identifier = id[len(WEBSITE_PREFIX):]
        try:
            return Website.require_instance(identifier = identifier)
        except InstanceNotFoundError:
            raise cherrypy.HTTPError(
                404,
                "Invalid website identifier: " + identifier
            )

    try:
        return Item.require_instance(int(id))
    except (ValueError, InstanceNotFoundError):
        raise cherrypy.HTTPError(404, "Invalid object id: " + id)

