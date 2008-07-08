#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from magicbullet.modeling import getter
from magicbullet import schema
import sqlalchemy as sa

default_metadata = sa.MetaData()
default = object()

class PersistentSchema(type, schema.Schema):
 
    _revision_schema = None
    _versioned = False

    def __init__(cls, name, bases, members):
        
        type.__init__(cls, name, bases, members)
        Schema.__init__(cls)
        cls.type = cls

        # Table
        cls.metadata = members.get("metadata", default_metadata)
        cls.table = members.get("table") \
            or self._create_table(members.get("table_name"))

        # Inheritance
        for base in bases:
            if isinstance(base, PersistentSchema):
                cls.inherit(base)

        if cls.bases:
            cls.polymorphic_identity = members.get(
                "polymorphic_identity",
                cls.__module__ + "." + cls.__name
            )
            cls.discriminator_column = cls._create_discriminator_column()
            cls.table.append_column(cls.discriminator_column)
        
        # Schema members
        for name, element in members.iteritems():
            if isinstance(element, schema.Member):
                element.name = name
                cls.add_member(element)

        # Table <-> Schema mapping
        cls.mapper = cls._map()

    @getter
    def versioned(cls):
        return cls.__versioned

    @getter
    def revision_schema(cls):
        return cls._revision_schema

    def _create_translation_schema(cls):
        
        name = cls.__name__ + "Translation"
        
        bases = (
            tuple(
                base.translation_schema
                for base in cls.bases
                if base.translatable
            )
            or (Persistent,)
        )

        members = {
            "instance": schema.Reference(
                type = ,
                required = True
            ),
            "language": schema.String(
                required = True,
                format = schema.iso_language
            ),
            "table_members": (sa.UniqueConstraint("instance", "language"),)
        }

        return cls.__class__(name, bases, members)

    def _create_translated_member(cls, member):
        translated_member = Schema._create_translated_member(cls, member)
        translated_member.versioned = False
        return translated_member

    def _create_revision_schema(cls):

        name = cls.__name__ + "Revision"
        
        bases = (
            tuple(
                base._revision_schema
                for base in cls.bases
                if base._revision_schema
            )
            or (Persistent,)
        )
        
        members = {
            "id": Serial(),
            "date": schema.DateTime(
                required = True,
                default = datetime.now
            )
        }

        return cls.__class__(name, bases, members)

    def add_member(cls, member):
        
        schema.Schema.add_member(cls, member)

        if not member.translatable:
            column = cls._create_column(member)
            cls.table.append_column(column)

        if member.versioned:

            if cls.revision_schema is None \
            or cls.revision_schema.versioned_schema is not cls:
                cls.__versioned = True
                cls.revision_schema = cls._create_revision_schema()
            
            delta_value = member.copy()
            delta_value.versioned = False
            delta_value.translatable = False
            cls.revision_schema.add_member(delta_value)

            cls.revision_schema.add_member(
                schema.Boolean(
                    name = member.name + "_changed",
                    required = True,
                    default = False
                )
            )

    def _create_table(cls, name = None):
        return sa.Table(
            name or cls.__name__
            cls.metadata
        )

    def _create_column(cls, member):
        return sa.Column(
            cls._get_column_name(member),
            cls._get_column_type(member),
            **(cls._get_column_properties(member))
        )

    def _get_column_name(cls, member):
        return getattr(member, "column_name", member.name)

    def _get_column_type(cls, member):
        return getattr(member, "column_type", None) \
            or cls._map_column_type(member)

    def _map_column_type(cls, member):
        
        if isinstance(member, schema.Unicode):
            return sa.Unicode(member.max)
        
        elif isinstance(member, schema.Integer):
            return sa.Integer()

        elif isinstance(member, schema.Boolean):
            return sa.Boolean()

        elif isinstance(member, schema.Date):
            return sa.Date()

        elif isinstance(member, schema.Time):
            return sa.Time()

        elif isinstance(member, schema.DateTime):
            return sa.DateTime()

        else:
            raise TypeError("Can't map %s to an SQL alchemy type." % member)

    def _get_column_properties(cls, member):

        properties = {}

        if getattr(member, "primary", False):
            properties["primary"] = True

        if getattr(member, "unique", False):
            properties["unique"] = True

        if getattr(member, "required") == True:
            properties["nullable"] = False

        custom_properties = getattr(member, "column_properties", None)

        if custom_properties:
            properties.update(custom_properties)

        return properties

    def _create_discriminator_column(cls):
        return sa.Column(
            "type",
            sa.String(255),            
            nullable = False,
            default = cls.polymorphic_identity
        )

    def _map(cls):

        properties = {}

        kwargs = {
            "properties": properties
        }

        # TODO: relations
        for member in cls.members(recursive = False):
            if instance(member, schema.RelatedSet):
                pass       

        if schema.bases:
            kwargs["polymorphic_on"] = cls.discriminator_column
            kwargs["polymorphic_identity"] = cls.polymorphic_identity

        else:
            if cls.translatable:
                properties["translations"] = sa.relation(
                    cls.translation_schema,
                    collection_class = 
                        sa.attribute_mapped_collection("language")
                )

            if cls.versioned:
                properties["revisions"] = sa.relation(
                    cls.revision_schema,
                    backref = "instance"
                )
        
        sa.mapper(
            cls,
            cls.table,
            **kwargs
        )


class Persistent(object):

    __metaclass__ = PersistentSchema

    def __init__(self, **values):

        for member in self.__class__.members():
            
            value = values.get(member.name, default)

            if value is default:
                value = member.produce_default()

            setattr(self, key, value)

        if values:
            for key, value in values.iteritems():
                setattr(self, key, value)

    def validate(self, **kwargs):
        return self.__class__.validate(self, **kwargs)

    def get_errors(self, **kwargs):
        return self.__class__.get_errors(self, **kwargs)

