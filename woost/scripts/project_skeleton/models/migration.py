#-*- coding: utf-8 -*-
u"""Migration of the site's schema.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.persistence import datastore, Migration

migration = Migration("_PROJECT_NAME_.models")
datastore.migrations.append(migration)


if __name__ == "__main__":
    import _PROJECT_NAME_
    datastore.migrate()

