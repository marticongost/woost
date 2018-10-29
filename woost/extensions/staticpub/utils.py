#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable, User

def iter_exportable_languages(publishable, user = None):

    if publishable.included_in_static_publication:

        if user is None:
            user = User.require_instance(qname = "woost.anonymous_user")

        if publishable.per_language_publication:
            for language in publishable.enabled_translations:
                if publishable.is_accessible(
                    user = user,
                    language = language,
                    website = "any"
                ):
                    yield language
        else:
            if publishable.is_accessible(
                user = user,
                website = "any"
            ):
                yield None

def iter_all_exportable_content():

    anon = User.require_instance(qname = "woost.anonymous_user")

    for publishable in Publishable.select(
        Publishable.included_in_static_publication.equal(True)
    ):
        for language in iter_exportable_languages(publishable, anon):
            yield publishable, language

