#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""
from magicbullet.html.element import Element
from magicbullet.html.datadisplay import DataDisplay

class Table(Element, DataDisplay):
    
    tag = "table"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataDisplay.__init__(self)
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

        for column in self.displayed_members:
            cell = self.create_cell(item, column)
            row.append(cell)
        
        return row

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

