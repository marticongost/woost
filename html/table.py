#-*- coding: utf-8 -*-
"""

@author:		Mart� Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""
from magicbullet.html.element import Element
from magicbullet.html.datadisplay import (
    CollectionDisplay,
    NO_SELECTION, SINGLE_SELECTION, MULTIPLE_SELECTION
)

class Table(Element, CollectionDisplay):
    
    tag = "table"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        CollectionDisplay.__init__(self)
        self.__column_display = {}
        self.__column_labels = {}

    def _build(self):

        self.head = Element("thead")
        self.append(self.head)

        self.head_row = Element("tr")
        self.head.append(self.head_row)

        self.body = Element("body")
        self.append(self.body)

    def _ready(self):
        self._fill_head()
        self._fill_body()

    def _fill_head(self):

        if self.selection_mode != NO_SELECTION:
            selection_header = Element("th")
            selection_header.add_class("selection")
            self.head_row.append(selection_header)

        for column in self.displayed_members:
            header = self.create_header(column)
            self.head_row.append(header)
    
    def _fill_body(self):
        for i, item in enumerate(self.data):
            row = self.create_row(i, item)
            self.append(row)

    def create_row(self, index, item):
        row = Element("tr")
        row.add_class(index % 2 == 0 and "odd" or "even")
        
        if self.selection_mode != NO_SELECTION:            
            row.append(self.create_selection_cell(item))
            
        for column in self.displayed_members:
            cell = self.create_cell(item, column)
            row.append(cell)
        
        return row

    def create_selection_cell(self, item):

        selection_control = Element("input")
        selection_control["name"] = self["name"] + "_selection"
        selection_control["id"] = self["name"] + "_selection_" + str(item.id)
        selection_control["value"] = str(item.id)

        if self.selection_mode == SINGLE_SELECTION:
            selection_control["type"] = "radio"
            selection_control["selected"] = self.is_selected(item)
        else:
            selection_control["type"] = "checkbox"
            selection_control["checked"] = self.is_selected(item)

        selection_cell = Element("td")
        selection_cell.add_class("selection")
        selection_cell.append(selection_control)
        return selection_cell

    def create_header(self, column):
        header = Element("th")
        header.append(self.get_member_label(column))
        self._init_cell(header, column)
        return header

    def create_cell(self, item, column):
        cell = Element("td")
        self._init_cell(cell, column)
        display = self.get_member_display(item, column)
        cell.append(display)
        return cell

    def _init_cell(self, cell, column):
        cell.add_class(column.name)

