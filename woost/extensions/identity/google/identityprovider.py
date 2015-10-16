#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Pepe Osca <pepe.osca@whads.com>
"""
from urllib import urlencode
from cocktail import schema
from cocktail.persistence import transaction
from cocktail.controllers import Location
from woost.extensions.identity.identityprovider import IdentityProvider


class GoogleIdentityProvider(IdentityProvider):

    provider_name = "Google"
    user_identifier = "google_user_id"

    members_order = [
        "client_id",
        "client_secret",
        "scope"
    ]

    client_id = schema.String(
        required = True,
        text_search = False
    )

    client_secret = schema.String(
        required = True,
        text_search = False
    )

    scope = schema.Collection(
        min = 1,
        default = schema.DynamicDefault(lambda: ["profile", "email"]),
        items = schema.String()
    )

    def get_auth_url(self, target_url = None):
        return (
            "/google_oauth/%d/step1?%s" % (
                self.id,
                urlencode({
                    "target_url": target_url
                    or unicode(Location.get_current(relative = False)).encode("utf-8")
                })
            )
        )

