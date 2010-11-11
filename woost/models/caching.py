#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from datetime import datetime
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models.item import Item


class CachingPolicy(Item):

    # TODO: combine per type filtering with a per item condition

    visible_from_root = False

    groups_order = ["cache"]
    members_order = [
        "description",
        "cache_enabled",
        "server_side_cache",
        "cache_expiration",
        "condition",
        "cache_key_expression",
        "last_update_expression"
    ]

    description = schema.String(
        descriptive = True,
        translated = True,
        listed_by_default = False
    )

    cache_enabled = schema.Boolean(
        required = True,
        default = True
    )

    server_side_cache = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False
    )

    cache_expiration = schema.Integer(
        min = 1,
        listed_by_default = False
    )

    condition = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor",
            syntax = "python",
            cols = 80
        ),
        listed_by_default = False
    )

    cache_key_expression = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor",
            syntax = "python",
            cols = 80
        ),
        listed_by_default = False
    )

    last_update_expression = schema.String(
         edit_control = display_factory(
            "cocktail.html.CodeEditor",
            syntax = "python",
            cols = 80
        ),
        listed_by_default = False
    )

    def applies_to(self, publishable, **context):
        expression = self.condition
        if expression:
            expression = expression.replace("\r", "")
            context["publishable"] = publishable
            exec expression in context
            return context.get("applies", False)

        return True

    def get_content_cache_key(self, publishable, **context):

        context["publishable"] = publishable

        cache_key = (publishable.id,)
        key_qualifier = None
        
        if self.cache_key_expression:
            key_qualifier = eval(self.cache_key_expression, context)
        else:
            request = context.get("request")
            if request:
                key_qualifier = tuple(request.params.items())

        if key_qualifier:
            cache_key = cache_key + (key_qualifier,)

        return cache_key

    def get_content_last_update(self, publishable, **context):
        
        context["publishable"] = publishable    
        context["latest"] = latest

        def normalize_date(value):

            if isinstance(value, Item):
                value = value.last_update_time

            elif hasattr(value, "__iter__"):
                max_date = None
                for item in value:
                    date = normalize_date(item)
                    if date is None:
                        continue
                    if max_date is None or date > max_date:
                        max_date = date

                value = max_date
            
            return value

        expression = self.last_update_expression
        if expression:
            expression = expression.replace("\r", "")
            exec expression in context
            last_update = context.get("last_update")
            return normalize_date(last_update)
        else:
            return publishable.last_update_time


# Utility functions for last update expressions
#------------------------------------------------------------------------------

def latest(selectable, *args, **kwargs):
    return (
        selectable.select(
            order = Item.last_update_time.negative(),
            range = (0, 1)
        )
        .select(*args, **kwargs)
    )

def menu_items(publishable):
    items = []
    
    while publishable is not None:
        if hasattr(publishable, "children"):
            items.extend(publishable.children)
        if publishable.parent is None:
            items.append(publishable)
        publishable = publishable.parent
    
    return items

def file_date(publishable):
    try:
        ts = os.stat(publishable.file_path).st_mtime
    except IOError, OSError:
        return None

    return datetime.fromtimestamp(ts)

