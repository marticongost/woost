#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import Event, EventInfo, when
from cocktail.schema import Member
from cocktail.persistence import PersistentClass
from cocktail.caching import whole_cache
from .item import Item

Member.triggers_invalidation = True
Member.invalidation_subset = None


class Invalidation(object):

    everything = whole_cache

    class ContentInvalidatedEventInfo(EventInfo):

        __scope = None

        @property
        def scope(self):
            if self.__scope is None:
                self.__scope = Invalidation.get_change_scope(
                    self.modified_content,
                    language = self.language,
                    part = self.part
                )

            return self.__tags

    content_invalidated = Event(
        event_info_class = ContentInvalidatedEventInfo,
        doc = """
        An event triggered when an object is modified in a way that could
        invalidate cached or generated content based on it.

        :param modified_content: The content that has been modified.

        :param scope: A series of tags signaling the content that has been
            invalidated.
        :type scope: set of (str|str tuple)
        """
    )

    @classmethod
    def notify(cls, modified_content, language = None, part = None):
        cls.content_invalidated(
            modified_content = modified_content,
            language = language,
            part = part
        )

    @classmethod
    def get_object_tag(cls, obj, part = None):
        tag = "%s-%d" % (obj.__class__.__name__, obj.id)
        if part:
            tag += "-" + part
        return tag

    @classmethod
    def get_type_tag(cls, type, part = None):
        tag = type.full_name
        if part:
            tag += "-" + part
        return tag

    @classmethod
    def get_language_tag(cls, language):
        return "lang-" + language

    @classmethod
    def get_content_tags(cls, content, language = None, part = None):

        if isinstance(content, Item):
            tags = {cls.get_object_tag(content, part = part)}
            if language:
                tags.add(cls.get_language_tag(language))
        elif isinstance(content, PersistentClass):
            tags = {cls.get_type_tag(content, part = part)}
        else:
            tags = set()
            for item in content:
                tags.update(
                    cls.get_content_tags(
                        item,
                        language = language,
                        part = part
                    )
                )

        return tags

    @classmethod
    def get_change_scope(cls,
        modified_content,
        language = None,
        part = None,
        _languages = None
    ):
        if language and _languages is None:
            _languages = list(
                    modified_content.iter_derived_translations(
                    language,
                    include_self = True
                )
            )

        if isinstance(modified_content, Item):

            scope = cls.get_change_scope(
                modified_content.__class__,
                part = part,
                language = language,
                _languages = _languages
            )

            tag = self.get_object_tag(modified_content, part = part)

            if language:
                for lang in languages:
                    scope.add((tag, cls.get_language_tag(lang)))
            else:
                scope.add(tag)

        elif isinstance(modified_content, PersistentClass):

            scope = set()

            # Tags per type
            for type in modified_content.__class__.ascend_inheritance(include_self = True):

                tag = cls.get_type_tag(type, part = part)

                if _languages:
                    for lang in _languages:
                        scope.add((tag, cls.get_language_tag(lang)))
                else:
                    scope.add(tag)

                if cls is Item:
                    break
        else:
            scope = set()
            for modified_item in modified_content:
                scope.update(
                    cls.get_invalidation_scope(
                        modified_item,
                        language = language,
                        part = part,
                        _languages = _languages
                    )
                )
            return tags


# Trigger invalidation events when objects are modified
#------------------------------------------------------------------------------
@when(Item.inserted)
@when(Item.deleting)
@when(Item.adding_translation)
@when(Item.removing_translation)
def _invalidate_item(e):
    Invalidation.notify(modified_content = e.source)

@when(Item.changed)
def _invalidate_item_on_change(e):
    if (
        e.member.invalidates_cache
        and e.source.is_inserted
    ):
        Invalidation.notify(
            modified_content = e.source,
            language = e.language,
            subset = e.member.invalidation_subset
        )

