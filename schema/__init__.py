#-*- coding: utf-8 -*-
"""
Declarative definition of data models and validation rules.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from magicbullet.schema.member import Member, DynamicDefault
from magicbullet.schema.schema import Schema
from magicbullet.schema.rangedmember import RangedMember
from magicbullet.schema.schemacollections import Collection
from magicbullet.schema.schemamappings import Mapping
from magicbullet.schema.schemareference import Reference
from magicbullet.schema.schemastrings import String
from magicbullet.schema.schemanumbers import Number, Integer, Decimal, Float
from magicbullet.schema.schemabooleans import Boolean
from magicbullet.schema.schemadates import DateTime, Date, Time

