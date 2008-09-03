#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.html import Element
from magicbullet.schema import Number
from magicbullet.translations import translate

class Selector(Element):

    items = ()
    value = None

    def _ready(self):

        Element._ready(self)

        if self.member and self.items is None:
            
            if self.member.enumeration:
                self.items = self.member.enumeration

            elif isinstance(self.member, Number) \
            and self.member.min and self.member.max:
                self.items = range(self.member.min, self.member.max + 1)
        
        self._fill_entries()

    def _fill_entries(self):
        
        if hasattr(self.items, "iteritems"):
            for value, label in self.items.iteritems():
                value = self.get_item_value(value)
                entry = self.create_entry(
                    value,
                    label,
                    self.__is_selected(value)
                )
                self.append(entry)
        else:
            for item in self.items:
                value = self.get_item_value(item)
                label = self.get_item_label(item)
                entry = self.create_entry(
                    value,
                    label,
                    self.__is_selected(value)
                )
                self.append(entry)
    
    def get_item_value(self, item):
        return str(item)

    def get_item_label(self, item):
        return translate(item, default = unicode(item))
    
    def create_entry(self, value, label, selected):
        pass

    def __get_value(self):
        return self.__value

    def __set_value(self, value):
        self.__value = value

        if isinstance(value, (list, tuple, set)):
            selection = set(self.get_item_value(item for item in value))
            self.__is_selected = lambda item: item in selection
        else:
            selection = self.get_item_value(value)
            self.__is_selected = lambda item: item == selection


class DropdownSelector(Selector):

    tag = "select"

    def _ready(self):
        
        Selector._ready(self)

        if self.member:
            
            # Name binding
            self["name"] = self.member.name

    def create_entry(self, value, label, selected):
        entry = Element("option")
        entry["value"] = value
        entry["selected"] = selected
        entry.append(label)
        return entry


class RadioSelector(Selector):

    def create_entry(self, value, label, selected):
        
        entry = Element("input")
        entry["type"] = "radio"
        entry["value"] = value
        entry["selected"] = selected
        
        if self.member:
            entry["name"] = self.member.name

        entry.append(label)
        return entry

