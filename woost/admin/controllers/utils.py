#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import set_language
from cocktail.persistence import datastore, InstanceNotFoundError
from woost import app
from woost.models import Item, Configuration, Website
from woost.models.utils import get_model_from_dotted_name

WEBSITE_PREFIX = "website-"

def resolve_object_ref(id):

    if isinstance(id, str):

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
            id = int(id)
        except ValueError:
            raise cherrypy.HTTPError(
                400,
                "Invalid id %r, expected an integer" % id
            )

    try:
        return Item.require_instance(id)
    except InstanceNotFoundError:
        raise cherrypy.HTTPError(404, "Can't find an object with id %s" % id)

def get_model_from_state(state):

    try:
        model_name = state["_class"]
    except KeyError:
        raise cherrypy.HTTPError(400, "Missing a _class field")

    model = get_model_from_dotted_name(model_name)
    if not model:
        raise cherrypy.HTTPError(400, "Unknown model: " + model_name)

    return model

def set_admin_language():

    language = app.user.backoffice_language

    if not language:
        language = app.user.preferred_language
        if language not in Configuration.backoffice_language.enumeration:
            language = None

    if not language:
        language = app.publishable.default_language

    set_language(language)
    return language

