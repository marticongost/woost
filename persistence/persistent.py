#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker, relation, backref
from magicbullet.modeling import getter
from magicbullet.pkgutils import get_full_name
from magicbullet import schema

session = scoped_session(sessionmaker(autoflush = True, autocommit = True))

default = object()

_type_registry = {}

# Additional schema metadata used by the persistence machinery:
schema.Member.persisted = True
schema.Member.primary = False
schema.Member.unique = False
schema.Member.column_name = None
schema.Member.column_type = None
schema.Member.column_properties = None

schema.Integer.auto_increment = False

schema.Reference.cardinality = None
schema.Reference.related_end = None

schema.Collection.cardinality = None
schema.Collection.related_end = None
schema.Collection.secondary_table = None

schema.Schema.primary_key = None

CARDINALITY_ONE_TO_ONE = 1
CARDINALITY_ONE_TO_MANY = 2
CARDINALITY_MANY_TO_MANY = 3

def get_type(type_id):
    return _type_registry[type_id]

def map_types():
    for type in _type_registry.itervalues():
        type.map()


class PersistentSchema(type, schema.Schema):
 
    metadata = sa.MetaData()
    table = None
    mapper_options = {
        "save_on_init": False        
    }

    def __init__(cls, name, bases, members):

        type.__init__(cls, name, bases, members)
        schema.Schema.__init__(cls)
        cls._mapped = False

        # Schema name
        cls.name = name.lower()
        full_name = get_full_name(cls)

        pos = full_name.find(".")

        if pos != -1:
            last_pos = full_name.rfind(".")
            cls.__short_name = (
                   full_name[:pos].lower()
                 + "."
                 + full_name[last_pos + 1:]
            )
        else:
            cls.__short_name = full_name

        # Inheritance
        for base in bases:
            if isinstance(base, PersistentSchema) \
            and base is not Persistent:
                cls.inherit(base)
 
        if len(cls.bases) > 1:
            raise TypeError(
                "Persisting schemas that inherit from multiple "
                "bases is not supported"
            )

        if "type_id" not in members:
            cls.type_id = cls.__short_name

        _type_registry[cls.type_id] = cls

        # Schema members
        for name, element in members.iteritems():
            if isinstance(element, schema.Member):
                element.name = name
                cls.add_member(element)

        # Table customization
        cls.__table_name = members.get("table_name") \
            or cls.__short_name.replace(".", "_").lower()
        cls.__extra_table_members = members.get("table_members")        

        # Mapper customization
        cls.mapper_options = PersistentSchema.mapper_options.copy()
        custom_mapper_options = members.get("mapper_options")

        if custom_mapper_options:
            cls.mapper_options.update(custom_mapper_options)

    def add_member(cls, member):

        if member.primary:
            if cls.primary_key:
                if instanceof(cls.primary_key, tuple):
                    cls.primary_key += (member,)
                else:
                    cls.primary_key = (cls.primary_key, member)
            else:
                cls.primary_key = member

        schema.Schema.add_member(cls, member)

    def map(cls):
             
        cls._resolve_relations()
        
        table = cls._create_table(cls.__table_name, cls.__extra_table_members)
        
        if table:
            cls.table = table

        if cls.table:
            cls.mapper = cls._create_mapper()

        cls._mapped = True
    
    def _resolve_relations(cls):

        for member in cls.members(recursive = False).itervalues():
            related_type = cls._get_related_type(member)

            if related_type \
            and not isinstance(member.related_end, schema.Member):
                cls._connect_relation(member, related_type)

    def _get_related_type(cls, member):
        
        related_type = None

        if isinstance(member, schema.Reference):
            if member.type and isinstance(member.type, basestring):
                member.type = get_type(member.type)
            
            related_type = member.type

        elif isinstance(member, schema.Collection): 
            if member.items and isinstance(member.items, basestring):
                member.items = get_type(member.items)
            
            related_type = member.items

        return related_type

    def _connect_relation(cls, source, related_type):

        related_end = None

        # Explicit related end
        if isinstance(source.related_end, basestring):
            dest = related_type[source.related_end]

        # Implicit (by type)
        else:
            for dest in related_type.members(recursive = False).itervalues():
                if cls._get_related_type(dest) is source.schema:
                    break
            else:
                raise ValueError(
                    "Can't connect %s to its related end" % source)

        # Determine the cardinality for the relation
        cardinality = 1
           
        if isinstance(source, schema.Collection):
            cardinality += 1
        
        if isinstance(dest, schema.Collection):
            cardinality += 1
        
        if cardinality == CARDINALITY_ONE_TO_ONE \
        and int(source.persisted) + int(dest.persisted) != 1:
            raise ValueError(
                "Error mapping the one-to-one relation between %s and %s. A "
                "single end should be marked as not persisted."
                % (source, dest)
            )

        source.cardinality = dest.cardinality = cardinality
        
        # Bind the two ends of the relation
        source.related_end = dest
        dest.related_end = source

    def _create_table(cls, name, extra_table_members = None):

        own_members = cls.members(recursive = False)

        if own_members or extra_table_members:
            
            table = sa.Table(name, cls.metadata)
            
            for member in own_members.itervalues():
                cls._declare_member(member, table)
           
            if extra_table_members:
                for table_member in extra_table_members:
                    if isinstance(table_member, sa.Column):
                        table.append_column(table_member)
                    elif isinstance(table_member, sa.Constraint):
                        table.append_column(table_constraint)

            return table

    def _declare_member(cls, member, table):

        if not member.persisted:
            pass
        
        elif isinstance(member, schema.Collection):

            if member.cardinality == CARDINALITY_MANY_TO_MANY \
            and not member.items.__dict__["_mapped"]:
                cls._declare_many_to_many_relation(member)
       
        # Foreign key
        elif isinstance(member, schema.Reference):
            cls._declare_foreign_key(member.type, member.name, table)

        # Regular column
        else:
            table.append_column(
                sa.Column(
                    cls._get_column_name(member),
                    cls._get_column_type(member),
                    **(cls._get_column_properties(member))
                )
            )

    def _get_column_name(cls, member):
        return member.column_name or member.name

    def _get_column_type(cls, member):
        return member.column_type or cls._map_column_type(member)

    def _map_column_type(cls, member):
        
        if isinstance(member, schema.String):
            return sa.Unicode(member.max)

        elif isinstance(member, schema.Integer):
            return sa.Integer(auto_increment = member.auto_increment)

        elif isinstance(member, schema.Decimal):
            return sa.Numeric()

        elif isinstance(member, schema.Float):
            return sa.Float()

        elif isinstance(member, schema.Boolean):
            return sa.Boolean()

        elif isinstance(member, schema.Date):
            return sa.Date()

        elif isinstance(member, schema.Time):
            return sa.Time()

        elif isinstance(member, schema.DateTime):
            return sa.DateTime()

        else:
            raise TypeError(
                "Don't know how to map %s to an SQL alchemy type "
                "(perhaps you should override the _map_column_type method?)"
                % member
            )

    def _get_column_properties(cls, member):

        properties = {}

        if member.primary:
            properties["primary_key"] = True

        if member.unique:
            properties["unique"] = True

        if member.required:
            properties["nullable"] = False

        properties["default"] = member.default

        if member.column_properties:
            properties.update(member.column_properties)

        return properties

    def _declare_foreign_key(cls, ref_type, ref_name, table):

        rel_key = ref_type.primary_key
        
        # Compound foreign keys
        if isinstance(rel_key, tuple):
            
            local_columns = []
            foreign_columns = []

            for rel_member in rel_key:
                local_column_name = ref_name + "_" + rel_member.name
                foreign_columns.append(cls._get_column_name(rel_member))
                local_columns.append(local_column_name)
                table.append_column(
                    sa.Column(
                        local_column_name,
                        cls._get_column_type(rel_member)
                    )
                )

            table.append_constraint(
                sa.ForeignKeyConstraint(
                    local_columns,
                    foreign_columns
                )
            )

        # Scalar foreign key
        else:
            column = sa.Column(
                ref_name + "_" + rel_key.name,
                cls._get_column_type(rel_key),
                sa.ForeignKey(
                    ref_type.__table_name
                    + "."
                    + cls._get_column_name(rel_key)
                )
            )
            table.append_column(column)

    def _declare_many_to_many_relation(cls, member):

        if member.secondary_table \
        and member.related_end.secondary_table \
        and member.secondary_table \
        != member.related_end.secondary_table:
            raise ValueError(
                "Conflicting secondary table specified by %s and %s"
                % (member, member.related_end)
            )

        secondary_table = member.secondary_table \
            or member.related_end.secondary_table
        
        sec_table_name = None

        if isinstance(secondary_table, basestring):
            sec_table_name = secondary_table
            secondary_table = None

        if secondary_table is None:

            if sec_table_name is None:
                sec_table_name = "_".join(sorted([
                    cls.__table_name,
                    member.items.__table_name
                ]))

            secondary_table = sa.Table(sec_table_name, cls.metadata)
            
            cls._declare_foreign_key(
                cls, cls.name, secondary_table)

            cls._declare_foreign_key(
                member.items, member.items.name, secondary_table)

        member.secondary_table = secondary_table
        member.related_end.secondary_table = secondary_table

    def _create_discriminator_column(cls):
        return sa.Column(
            "type",
            sa.String(255),            
            nullable = False,
            default = cls.type_id
        )
    
    def _create_mapper(cls):
        
#        if cls.bases:
#            kwargs["polymorphic_on"] = cls.discriminator_column
#            kwargs["polymorphic_identity"] = cls.type_id

        properties = {}

        for member in cls.members(recursive = False).itervalues():
            related_type = cls._get_related_type(member)
            
            if related_type and not related_type.__dict__["_mapped"]:                
                
                rel_options = {}
                backref_options = {}
                
                if member.cardinality == CARDINALITY_ONE_TO_ONE:                    
                    if member.persisted:
                        backref_options["uselist"] = False
                    else:
                        rel_options["uselist"] = False
                else:
                    rel_options["lazy"] = "dynamic"
                    backref_options["lazy"] = "dynamic"

                    if member.cardinality == CARDINALITY_MANY_TO_MANY:
                        rel_options["secondary"] = member.secondary_table

                rel_options["backref"] = backref(
                    member.related_end.name,
                    **backref_options
                )

                properties[member.name] = relation(related_type, **rel_options)
                
        return session.mapper(
            cls,
            cls.table,
            properties = properties,
            **(cls.mapper_options)
        )

class Persistent(object):

    __metaclass__ = PersistentSchema

    def validate(self, **kwargs):
        return self.__class__.validate(self, **kwargs)

    def get_errors(self, **kwargs):
        return self.__class__.get_errors(self, **kwargs)


if __name__ == "__main__":

    from decimal import Decimal

    class Product(Persistent):

        id = schema.Integer(
            primary = True,
            auto_increment = True
        )

        name = schema.String(
            unique = True,
            required = True,
            max = 255
        )

        price = schema.Decimal(
            required = True,
            min = 0.01
        )

        brand = schema.Reference(type = "magicbullet.Brand")
        
        colors = schema.Collection(items = "magicbullet.Color")


    class Color(Persistent):

        id = schema.Integer(
            primary = True,
            auto_increment = True
        )

        name = schema.String(
            unique = True,
            required = True,
            max = 255
        )

        products = schema.Collection(items = "magicbullet.Product")


    class Brand(Persistent):

        id = schema.Integer(
            primary = True,
            auto_increment = True
        )

        name = schema.String(
            unique = True,
            required = True
        )

        products = schema.Collection(items = "magicbullet.Product")


    from sqlalchemy.databases import postgres

    class PGCascadeSchemaDropper(postgres.PGSchemaDropper):
         def visit_table(self, table):
            for column in table.columns:
                if column.default is not None:
                    self.traverse_single(column.default)
            self.append("\nDROP TABLE " +
                        self.preparer.format_table(table) +
                        " CASCADE")
            self.execute()

    postgres.dialect.schemadropper = PGCascadeSchemaDropper

    engine = sa.create_engine(
        "postgres://marti:saussage@localhost/sitebasis"
    )
    engine.echo = True

    map_types()

    metadata = PersistentSchema.metadata
    metadata.bind = engine
    metadata.drop_all()
    metadata.create_all()

    p1 = Product(
        name = u"Trendynator 3000",
        price = Decimal("2.5")
    )
    
    b1 = Brand(name = u"Crapware")

    session.save(p1)
    session.save(b1)
    session.flush()

