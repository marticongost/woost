#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.translations import translate
from magicbullet.html.element import Element, Content
from magicbullet.html.table import MULTIPLE_SELECTION
from magicbullet.html.selectors import LinkSelector
from magicbullet.views.contenttypetree import (
    ContentTypePath,
    ContentTypeSelector,
    ContentTypeTree
)


class ContentView(CollectionView):

    collection_params = None
    available_content_views = None

    def _build(self):

        CollectionView._build(self)

        self.content_type_path = self.create_content_type_path()
        self.insert(0, self.content_type_path)

    def _ready(self):

        Element._ready(self)

        self.content_type_path.value = self.user_collection.entity_type

        # Content views
        if self.available_content_views \
        and len(self.available_content_views) > 1:
            self.content_view_selector.items = self.available_content_views
            self.content_view_selector.value = self
        else:
            self.content_view_control.visible = False
 
    class ContentTypePath(ContentTypePath):
        class Selector(ContentTypeSelector):
            class Tree(ContentTypeTree):
                plural_labels = True
                def create_label(self, item):
                    label = ContentTypeTree.create_label(self, item)
                    label.tag = "a"
                    label["href"] = "?type=" + item.__name__
                    return label

    def create_content_type_path(self):
        ct_path = self.ContentTypePath()
        ct_path.add_class("content_type_path")
        return ct_path

    def create_toolbar(self):

        toolbar = CollectionView.create_toolbar(self)
        
        # Content views        
        self.content_view_control = self.create_content_view_control()
        self.settings_box.append(self.content_view_control)

        return toolbar
    
    def create_toolbar_button(self, action):
        
        if action == "new":
            button = Element("div", "selector", [
                Element("span", "label", [
                    Element("img",
                        src = self.cms.uri("resources", "images", "new.png")),
                    translate("New item")
                ]),
                Element("div", "selector_content", [
                    self.create_new_item_selector()
                ])
            ])
            button.add_class("toolbar_button")
            button.add_class(action)
        else:
            button = CollectionView.create_button(self, action)

        return button

    def create_new_item_selector(self):
        selector = self.NewItemSelector()
        selector.content_view = self
        selector.root = self.user_collection.entity_type
        return selector

    class NewItemSelector(ContentTypeTree):
        
        def create_label(self, content_type):
            label = ContentTypeTree.create_label(self, content_type)
            label.tag = "a"
            label["href"] = self.content_view.cms.uri(
                self.content_view.backoffice.path, 'new'
            ) + "?type=" + content_type.__name__
            return label

    def create_content_view_control(self):
        
        self.content_view_selector = self.create_content_view_selector()

        return Element("div", "toolbar_button selector content_view", [
            Element("span", "label", [translate("View as")]),
            Element("div", "selector_content", [
                self.content_view_selector
            ])
        ])

    class ContentViewSelector(LinkSelector):

        def get_item_label(self, content_view):
            return translate(content_view.content_view_id + " content view")
        
        def get_item_value(self, content_view):
            return content_view.content_view_id

    def create_content_view_selector(self):
        selector = self.ContentViewSelector()
        selector.name = "content_view"
        return selector

