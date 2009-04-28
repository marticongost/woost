#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.language import get_content_language
from cocktail.translations import translations
from cocktail.schema import Reference
from cocktail.schema.expressions import PositiveExpression, NegativeExpression
from cocktail.html import Element, templates
from cocktail.controllers import view_state
from sitebasis.views.contentdisplaymixin import ContentDisplayMixin

Table = templates.get_class("cocktail.html.Table")


class ContentTable(ContentDisplayMixin, Table):
    
    base_url = None
    inline_draft_copies = True

    def __init__(self, *args, **kwargs):
        Table.__init__(self, *args, **kwargs)
        ContentDisplayMixin.__init__(self)
        self.set_member_sortable("element", False)
        self.set_member_sortable("class", False)

    def _fill_body(self):

        if not self.inline_draft_copies:
            Table._fill_body(self)
        else:
            for index, item in enumerate(self.data):
                row = self.create_row(index, item)
                self.append(row)            

                for draft in item.drafts:
                    row = self.create_row(index, draft)
                    self.append(row)
        
    def create_row(self, index, item):
        
        row = Table.create_row(self, index, item)

        if item.is_draft:
            row.add_class("draft")

        if item.draft_source:
            row.add_class("nested_draft")

        return row

    def create_element_display(self, item, member):
        
        display = Element("label")
        display["for"] = "selection_" + str(item.id)
        
        if self.inline_draft_copies and item.draft_source:
            desc = translations(
                "sitebasis.views.ContentTable draft label",
                draft_id = item.draft_id
            )
        else:
            desc = translations(item)
        
        display.append(desc)

        for schema in item.__class__.descend_inheritance(True):
            display.add_class(schema.name)

        return display

    def create_class_display(self, item, member):
        return Element(
                    tag = None,
                    children = [translations(item.__class__.name)])

    def add_header_ui(self, header, column, language):
        
        # Add visual cues for sorted columns
        sortable = self.get_member_sortable(column)
        
        if sortable and self.order:
            current_direction = self._sorted_columns.get(
                (column.name, language)
            )
                    
            if current_direction is not None:

                header.add_class("sorted")

                if current_direction is PositiveExpression:
                    header.add_class("ascending")
                    sign = "-"
                elif current_direction is NegativeExpression:
                    header.add_class("descending")

        # Column options
        if sortable or self.get_member_searchable(column):

            menu = header.menu = Element()
            header.append(menu)
            menu.add_class("selector")
            
            label = menu.label = Element()
            label.add_class("label")
            menu.append(label)
            label.append(header.label)

            if column.translated:
                label.append(header.translation_label)
            
            options = header.menu.options = self.create_header_options(
                column,
                language
            )
            menu.append(options)

    def create_header_options(self, column, language):
        
        options = Element()
        options.add_class("selector_content")
        
        if self.get_member_sortable(column):
            sorting_options = self.create_sorting_options(column, language)
            options.append(sorting_options)

        if self.get_member_searchable(column):
            search_options = self.create_search_options(column, language)
            options.append(search_options)

        return options

    def create_sorting_options(self, column, language):

        if self.order:
            direction = self._sorted_columns.get((column.name, language))
        else:
            direction = None

        order_param = column.name
        if language:
            order_param += "." + language

        options = Element()
        options.add_class("sorting_options")

        asc = options.ascending = Element("a")
        asc.add_class("ascending")
        asc["href"] = "?" + view_state(order = order_param)
        asc.append(translations("sitebasis.views.ContentTable sort ascending"))
        options.append(asc)

        if direction is PositiveExpression:
            asc.add_class("selected")

        desc = options.ascending = Element("a")
        desc.add_class("descending")
        desc["href"] = "?" + view_state(order = "-" + order_param)
        desc.append(translations("sitebasis.views.ContentTable sort descending"))
        options.append(desc)

        if direction is NegativeExpression:
            desc.add_class("selected")

        return options

    def create_search_options(self, column, language):

        filters = [filter.id for filter in self.filters] \
            if self.filters \
            else []

        filters.append("member-" + column.name)

        options = Element()
        options.add_class("search_options")

        add_filter = Element("a")
        add_filter.add_class("add_filter")
        add_filter["href"] = "?" + view_state(page = 0, filter = filters)
        add_filter.append(
            translations("sitebasis.views.ContentTable add column filter")
        )
        options.append(add_filter)

        return options

