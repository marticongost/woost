#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.persistence import datastore, Migration

woost_migration = Migration("woost.models")
datastore.migrations.append(woost_migration)

