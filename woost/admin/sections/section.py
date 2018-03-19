#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import Sequence
from cocktail.events import EventHub, Event
from cocktail.modeling import camel_to_underscore
from cocktail.translations import translations
from cocktail.html import resource_repositories


class Section(object):

    __metaclass__ = EventHub

    declared = Event(
        """An event triggered when the admin section and its descendants have
        been set up.
        """
    )

    visible = True
    node = None
    ui_component = None

    def __init__(self, id):
        self.__id = id
        self.__parent = None
        self.__children = []
        self._fill()
        self.declared()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__id)

    def __iter__(self):
        return iter(self.__children)

    def __len__(self):
        return len(self.__children)

    def __contains__(self, section):
        return section in self.__children

    @property
    def id(self):
        return self.__id

    @property
    def icon_uri(self):
        name = self.__class__.__name__
        if name.endswith("Section"):
            name = name[:-len("Section")]
        name = camel_to_underscore(name)
        return "woost.admin.ui://images/sections/%s.svg" % name

    @property
    def full_path(self):
        return "/" + "/".join(
            section.__id
            for section in self.iter_path()
            if section.__id
        )

    @property
    def parent(self):
        return self.__parent

    @property
    def children(self):
        return self.__children

    def _fill(self):
        pass

    def __getitem__(self, id):
        for child in self.__children:
            if child.__id == id:
                return child

        raise KeyError(
            "%s contains no child named %s" % (self, id)
        )

    def find(self, *path):

        id = path[0]
        remaining_path = path[1:]

        for child in self.__children:
            if child.__id == id:
                if remaining_path:
                    return child.find(*remaining_path)
                else:
                    return child

        return None

    def iter_path(self):
        if self.__parent:
            for parent_step in self.__parent.iter_path():
                yield parent_step
        yield self

    def ascend_tree(self):
        section = self
        while section is not None:
            yield section
            section = section.__parent

    def descend_tree(self, include_self = True):
        if include_self:
            yield self
        for child in self.__children:
            for descendant in child.descend_tree():
                yield descendant

    def descends_from(self, section):
        ancestor = self

        while ancestor is not None:
            if ancestor is section:
                return True
            ancestor = ancestor.__parent

        return False

    def get_ancestor(self, depth):
        tree_line = list(self.iter_path())
        try:
            return tree_line[depth]
        except IndexError:
            return None

    def hide(self, *path):
        child = self.find(*path)
        if child is not None:
            child.visible = False

    def append(self, child):

        if child is None:
            raise ValueError("No child given")

        child.release()
        self.__children.append(child)
        child.__parent = self

    def prepend(self, item):
        if isinstance(item, Section):
            self.insert(0, item)
            item.__parent = self
        elif isinstance(item, Sequence):
            children = list(item)
            for child in children:
                child.release()
                child.__parent = self
            self.__children = children + self.__children
        else:
            raise ValueError(
                "Expected a Section or a sequence of Sections, got %s instead"
                % type(item)
            )

    def insert(self, index, item):
        if isinstance(item, Section):
            item.release()
            self.__children.insert(index, item)
            item.__parent = item
        elif isinstance(item, Sequence):
            for child in item:
                child.release()
                child.__parent = self
            self.__children = (
                self.__children[:index]
                + list(item)
                + self.__children[index:]
            )
        else:
            raise ValueError(
                "Expected a Section or a sequence of Sections, got %s instead"
                % type(item)
            )

    def _locate_anchor(self, anchor):

        if anchor is None:
            raise ValueError("No anchor given")

        if anchor.__parent is not self:
            raise ValueError(
                "Invalid anchor: %r is not a child of %r"
                % (anchor, self)
            )

        index = self.__children.index(anchor)
        assert index != -1
        return index

    def insert_before(self, anchor, item):
        index = self._locate_anchor(anchor)
        self.insert(index, item)

    def insert_after(self, anchor, item):
        index = self._locate_anchor(anchor)
        self.insert(index + 1, item)

    def release(self):

        if self.__parent:
            self.__parent.__children.remove(self)
            self.__parent = None
            return True

        return False

    def export_data(self):

        icon_uri = self.icon_uri
        if icon_uri:
            icon_uri = resource_repositories.normalize_uri(self.icon_uri)

        return {
            "id": self.__id,
            "title": translations(self),
            "node": self.node,
            "ui_component": self.ui_component,
            "icon": icon_uri,
            "children": [
                child.export_data()
                for child in self.__children
                if self.should_export_child(child)
            ]
        }

    def should_export_child(self, child):
        return child.visible

