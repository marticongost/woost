#-*- coding: utf-8 -*-
"""
Implements the persistence machinery for CMS objects. It builds on Zope's
Object Data Base (ZODB), adding support for multi-language content, versioning
and declarative queries over indices.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.persistence.entity import Entity, EntityClass, EntityAccessor
from magicbullet.persistence.datastore import datastore
from magicbullet.persistence.incremental_id import incremental_id
from magicbullet.persistence.index import Index
from magicbullet.persistence.query import Query

