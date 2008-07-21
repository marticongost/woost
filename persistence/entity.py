#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sys
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from magicbullet.pkgutils import get_full_name
from magicbullet import schema
from magicbullet.schema.exceptions import ValidationError
from magicbullet.language import require_language
from magicbullet.modeling import getter
from magicbullet.persistence.datastore import datastore
from magicbullet.persistence.incremental_id import incremental_id
from magicbullet.persistence.index import Index

default = object()

# Default collection types
schema.Collection.default = schema.DynamicDefault(PersistentList)
schema.Mapping.default = schema.DynamicDefault(PersistentMapping)

# Translation
schema.Member.translated = False
schema.Member.translation = None
schema.Member.translation_source = None

# Indexing
schema.Member.indexed = False
schema.Member.index = None
schema.Member.btree_type = OOBTree
schema.Integer.btree_type = IOBTree
schema.Member.unique = False
schema.Schema.indexed = True

# Relations
schema.Reference.bidirectional = False
schema.Collection.bidirectional = False

# TODO: bidirectional relations
# TODO: versioning

# Create a stub for the Entity class
Entity = None

class EntityClass(type, schema.Schema):

    def __init__(cls, name, bases, members):
        
        type.__init__(cls, name, bases, members)
        schema.Schema.__init__(cls)

        cls.name = name
        cls.__full_name = get_full_name(cls)

        cls._sealed = False

        # Inherit base schemas
        for base in bases:
            if Entity and base is not Entity and isinstance(base, EntityClass):
                cls.inherit(base)

        # Instance index (one per subclass)
        if Entity and cls.indexed:
            
            # Add an id field to all root schemas. Will be set to an incremental
            # integer when calling Entity.store()
            if not cls.bases:
                cls.id = schema.Integer(name = "id")
                cls.add_member(cls.id)
            
            # Create an index for instances of the class
            key = cls.__full_name + "_index"
            index = datastore.root.get(key)

            if index is None:
                datastore.root[key] = index = IOBTree()
            
            cls.index = index

        # Fill the schema with members declared as class attributes
        for name, member in members.iteritems():
            if isinstance(member, schema.Member):
                member.name = name
                cls.add_member(member)

        # Seal the schema, so that no further modification is possible
        cls._sealed = True

        if cls.translation:
            cls.translation._sealed = True

    def _seal_check(cls):
        if cls._sealed:
            raise TypeError("Can't alter an entity's schema after declaration")

    def inherit(cls, *bases):
        cls._seal_check()
        schema.Schema.inherit(cls, *bases)

    def _check_member(cls, member):

        # Make sure the schema can't be extended after the class declaration is
        # over
        cls._seal_check()

        schema.Schema._check_member(cls, member)

        # Unique members require a general class index, or a specific index for
        # the member
        if member.unique and not (member.indexed or cls.indexed):
            raise ValueError(
                "Can't enforce the unique constraint on %s.%s "
                "without a class or member index"
                % (cls.__full_name, member.name))

    def _add_member(cls, member):
       
        schema.Schema._add_member(cls, member)

        # Install a descriptor to mediate access to the member
        setattr(cls, member.name, MemberDescriptor(member))
        
        if member.unique:
            if cls._unique_validation_rule \
            not in member.validations(recursive = False):
                member.add_validation(cls._unique_validation_rule)
        
        if member.translated:

            # Create a translation schema for the entity, to hold its
            # translated members
            if cls.translation is None \
            or cls.translation.translation_source is not cls:
                cls._create_translation_schema()
                cls.translated = True
                            
            # Create the translated version of the member, and add it to the
            # translated version of the schema
            member.translation = member.copy()
            member.translation.translated = False
            member.translation.translation_source = member
            cls.translation.add_member(member.translation)
        
        # An indexed member gets its own btree        
        if member.indexed and member.index is None:
            
            root = datastore.root
            key = cls.__full_name + "-" + member.name + "_index"
            index = root.get(key)

            if index is None:
                
                # Unique indices use a "raw" ZODB's binary tree
                if member.unique:
                    index = member.btree_type()

                # Multi-value indices are wrapped inside an Index instance,
                # which organizes colliding keys into sets of values
                else:
                    index = Index(member.btree_type())
                
                root[key] = index
            
            member.index = index

    def _unique_validation_rule(cls, member, value, context):

        if (member.indexed and value in member.index) \
        or any(
            instance.get(member) == value
            for instance in member.schema.index.itervalues()
        ):
            yield UniqueValueError(member, value, context)

    def _create_translation_schema(cls):
        
        translation_bases = tuple(
            base.translation
            for base in cls.bases
            if base.translation
        ) or (Entity,)

        cls.translation = translation_schema = EntityClass(
            cls.name + "Translation",
            translation_bases,
            {"indexed": False}
        )

        # Make the translation class available at the module level, so its
        # instances can be pickled (required by ZODB's persistence machinery)
        setattr(
            sys.modules[cls.__module__],
            cls.translation.name,
            cls.translation)

        cls.translation.__module__ = cls.__module__

        cls.translation._sealed = False

        if not translation_bases:
            cls.translation.add_member(schema.Reference(
                name = "translated_object",
                type = cls,
                required = True
            ))
            cls.translation.add_member(schema.String(
                name = "language",
                required = True
            ))

        cls.add_member(schema.Mapping(
            name = "translations",
            keys = schema.String(
                required = True,
                format = "a-z{2}"
            ),
            values = cls.translation
        ))


class Entity(Persistent):

    __metaclass__ = EntityClass

    def __init__(self, **values):

        Persistent.__init__(self)

        # Set the value of all object members, either from a parameter or from
        # a default value definition
        for name, member in self.__class__.members().iteritems():
            value = values.get(name, default)
            
            if value is default:
                
                if member.translated:
                    continue

                value = member.produce_default()

            self.set(member, value)

        # Acquire an incremental id
        if self.__class__.indexed:
            
            if self.id is None:
                self.id = incremental_id()

            for schema in self.__class__.ascend_inheritance(True):
                schema.index[self.id] = self

    def _update_index(self, member, language, previous_value, new_value):
            
        if member.indexed and previous_value != new_value:
            
            if language:
                previous_value = (language, previous_value)
                new_value = (language, new_value)

            if member.unique:
                if previous_value is not None:
                    del member.index[previous_value]

                if new_value is not None:
                    member.index[new_value] = self
            else:
                if previous_value is not None:
                    member.index.remove(previous_value, self)

                if new_value is not None:
                    member.index.add(new_value, self)

    def get(self, member, language = None):

        # Normalize the member argument to a schema.Member reference
        if not isinstance(member, schema.Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        # Getting a translated value: turn it into a regular get
        if member.translated:
            
            language = require_language(language)
            translation = self.translations.get(language)
            
            if translation is None:
                return None
            else:
                return translation.get(member.translation)

        # Regular get
        else:
            return getattr(self, "_" + member.name)

    def set(self, member, value, language = None):

        # Normalize the member argument to a schema.Member reference
        if not isinstance(member, schema.Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        # Assigning a translated value: turn it into a regular assignment
        if member.translated:

            # Setting multiple translations at once
            if isinstance(value, Translations):
                for language, translated_value in value.iteritems():
                    self.set(member, translated_value, language)

            # Make sure the translation for the specified language exists, and
            # then resolve the assignment against it
            # TODO: This could be optmized to avoid the call totranslation.set
            else:
                language = require_language(language)
                translation = self.translations.get(language)

                if translation is None:
                    translation = self._new_translation(language)

                translation.set(member.translation, value)

        elif language:
            raise ValueError(
                "Can't specify the value language for a non translated member")
        
        # Regular assignment
        else:
            if member.indexed:
                previous_value = getattr(self, "_" + member.name, None)

            setattr(self, "_" + member.name, value)

            # Update the member's index
            if member.indexed:
                if member.translation_source:
                    member = member.translation_source
                    instance = self.translated_object
                    language = self.language
                else:
                    instance = self
                    language = None

                instance._update_index(member, language, previous_value, value)

    def _new_translation(self, language):
        translation = self.translation(
            object = self,
            language = language)
        self.translations[language] = translation
        return translation


class MemberDescriptor(object):

    def __init__(self, member):
        self.member = member

    def __get__(self, instance, type = None):

        if instance is None:
            return self.member
        else:
            return instance.get(self.member)

    def __set__(self, instance, value):
        instance.set(self.member, value)


class Translations(dict):
    pass


class UniqueValueError(ValidationError):
    """A validation error produced when a unique field is given a value that is
    already present in the database.
    """

    def __repr__(self):
        return "%s (value already present in the database)" \
            % ValidationError.__repr__(self)

