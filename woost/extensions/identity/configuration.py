#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Pepe Osca <pepe.osca@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Configuration
from .identityprovider import IdentityProvider

translations.load_bundle("woost.extensions.identity.configuration")

Configuration.add_member(
    schema.Collection("identity_providers",
        items = schema.Reference(type = IdentityProvider),
        related_end = schema.Reference(),
        integral = True,
        member_group = "services"
    )
)

