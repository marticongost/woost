#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail.html import Element, templates
from woost.models import Item, Publishable, News
from woost.views.viewfactory import ViewFactory

view_factories = {
    "text": ViewFactory(),
    "image": ViewFactory(),
    "text_and_image": ViewFactory(),
    "detail": ViewFactory()
}

# Text content factory
#------------------------------------------------------------------------------

text = view_factories["text"]

@text.handler_for(Publishable)
def publishable_text_link(item, parameters):
    view = Element("a")
    view["href"] = item.get_uri()
    view.append(translations(item))
    return view

@text.handler_for(Item)
def item_text(item, parameters):    
    view = Element()
    view.append(translations(item))
    return view

# Image content factory
#------------------------------------------------------------------------------

image = view_factories["image"]

@image.handler_for(Publishable)
def publishable_image_link(item, parameters):
    view = Element("a")
    view["href"] = item.get_uri()
    view.append(item_image(item, parameters))
    return view

@image.handler_for(Item)
def item_image(item, parameters):    
    view = templates.new("woost.views.Image")
    view.image = item
    view.image_factory = parameters.get("image_factory")
    return view

# Text and image content factory
#------------------------------------------------------------------------------

text_and_image = view_factories["text_and_image"]

@text_and_image.handler_for(Publishable)
def publishable_text_and_image_link(item, parameters):    
    view = templates.new("woost.extensions.newsletters.NewsletterContentView")
    view.heading = translations(item)
    view.link = item
    view.image = item
    return view

@text_and_image.handler_for(Item)
def item_text_and_image(item, parameters):
    view = templates.new("woost.extensions.newsletters.NewsletterContentView")
    view.heading = translations(item)
    view.image = item
    return view

# Detail content factory
#------------------------------------------------------------------------------

detail = view_factories["detail"]

@detail.handler_for(News)
def news_detail(item, parameters):    
    view = publishable_text_and_image_link(item, parameters)
    view.text = item.summary
    return view

detail.register(Item, "text_and_image_default", text_and_image)

