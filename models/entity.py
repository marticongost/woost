#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from persistent import Persistent
from BTrees.IOBTree import IOBTree
from magicbullet.modeling import getter
from magicbullet.schema import Schema, Member, String, Mapping
from magicbullet.persistence import datastore, incremental_id

default = object()

Member.translated = False
Member.translation = None
Member.translation_source = None


class EntityClass(type, Schema):

    def __init__(cls, name, bases, members):
        
        type.__init__(cls, name, bases, members)
        Schema.__init__(cls)

        cls.__sealed = False

        # Inherit base schemas
        for base in bases:
            if base is not Entity and isinstance(base, EntityClass):
                cls.inherit(base)

        # Fill the schema with members declared as class attributes
        for name, member in members.iteritems():
            if isinstance(member, schema.Member):
                cls.add_member(member)

        # On translated entities, add a 'translations' collection to the schema
        if cls.translated:
            cls.add_member(Mapping(
                name = "translations",
                keys = String(
                    required = True,
                    format = "a-z{2}"
                ),
                values = self.translation
            )

        # Create an index for instances of the class
        key = get_full_name(cls) + "-instances"
        cls.index = datastore.root.get(key)

        if cls.index is None:
            cls.index = IOBTree()
            datastore.root[key] = index

        # Seal the schema, so that no further modification is possible
        cls.__sealed = True

    def _seal_check(cls):
        if cls.__sealed:
            raise TypeError("Can't alter an entity's schema after declaration")

    def inherit(cls, base):
        self._seal_check()
        Schema.inherit(cls, base)

    def add_member(cls, member):

        # Make sure the schema can't be extended after the class declaration is
        # over
        self._seal_check()

        if member.translated:
            
            # Get the translated version of the schema, creating it if
            # necessary
            translation_schema = cls.translation

            if translation_schema is None:
                cls.translated = True
                cls.translation = translation_schema = Schema()

                for base in cls.bases:
                    if base.translation:
                        translation_schema.inherit(base.translation)
            
            # Create the translated version of the member, and add it to the
            # translated version of the schema
            translated_member = member.copy()
            translated_member.translated = False
            translated_member.translation_source = member
            member.translation = translated_member
            translation_schema.add_member(translated_member)
        
            # Install a descriptor to mediate access to the translated member
            setattr(cls, member.name, TranslationAccessor(member))
        
        Schema.add_member(cls, member)


class Entity(Persistent):

    __metaclass__ = EntityClass

    def __init__(self, **values):

        Persistent.__init__(self)

        # Set the value of all object members, either from a parameter or from
        # a default value definition
        for name, member in self.__class__.members().iteritems():
            value = values.get(name, default)

            if value is default:
                value = member.produce_default()

            setattr(self, name, value)

    def store(self):

        self.id = incremental_id()

        for schema in self.__class__.ascend_inheritance(True):
            schema.index[self.id] = self

    def get(self, member, language = None):

        if not isinstance(member, Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        if member.translated:
            
            language = require_language(language)
            translation = self.translations.get(language)
            
            if translation is None:
                return None
            else:
                return getattr(translation, member.name)
        else:
            return getattr(self, member.name)

    def set(self, member, value, language = None):

       if not isinstance(member, Member):

            if isinstance(member, basestring):
                member = self.__class__[member]                
            else:
                raise TypeError("Expected a string or a member reference")

        if member.translated:

            if isinstance(value, Translations):
                for language, translated_value in value.iteritems():
                    self.set(member, translated_value, language)
            else:
                language = require_language(language)
                translation = self.translations.get(language)

                if translation is None:
                    translation = Translation()
                    self.translations[language] = translation

                setattr(translation, member.name, value)
        else:
            setattr(self, member.name, value)


class TranslationAccessor(object):

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

