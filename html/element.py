#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2007
"""
from inspect import getmro
from magicbullet.modeling import getter, empty_list, empty_dict, empty_set
from magicbullet.iteration import first
from magicbullet.html.resources import Resource

default = object()

class Element(object):
    
    tag = "div"
    page_title = default
    styled_class = False
    scripted = True
    styled = True
    theme = None
    visible = True
    collapsible = False

    def __init__(self,
        tag = default,
        class_name = None,
        children = None,
        **attributes):
        
        self.__parent = None
        self.__children = None

        if children:
            for child in children:
                self.append(child)
        
        if attributes:
            self.__attributes = dict(attributes)
        else:
            self.__attributes = None
    
        if self.class_css:
            self["class"] = self.class_css

        if class_name:
            self.add_class(class_name)

        self.__meta = None
        self.__resources = None
        self.__resource_uris = None
        self.__client_params = None
        self.__is_ready = False
        self.__ready_handlers = None
        self.__value = None

        if tag is not default:
            self.tag = tag
         
        self._build()

    class __metaclass__(type):

        def __init__(cls, name, bases, members):
            type.__init__(cls, name, bases, members)
            
            # Aggregate CSS classes from base types
            classes = reversed(getmro(cls))
            css_classes = []

            if "styled_class" not in members:
                cls.styled_class = True

            for c in getmro(cls):
                if getattr(c, "styled_class", False):                
                    css_classes.insert(0, c.__name__)

            cls.class_css = css_classes and " ".join(css_classes) or None

    def __str__(self):

        if self.tag is None:
            return "html block"
        else:
            desc = "<" + self.tag
            
            id = self["id"]

            if id:
                desc += " id='%s'" % id

            css = self["class"]

            if css:
                desc += " class='%s'" % css

            desc += ">"
            return desc

    # Data binding
    #------------------------------------------------------------------------------
    def _get_value(self):
        return self.__value.value
    
    def _set_value(self, value):

        if value is None:
            value = ""

        if self.__value is None:
            self.__value = Content(value)
            self.append(self.__value)
        else:
            self.__value.value = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the text content of the element.
        @type: str
        """)
    
    item = None
    member = None

    # Rendering
    #--------------------------------------------------------------------------

    def make_page(self, renderer = None):
 
        if not renderer:
            renderer = self._get_default_renderer()

        return renderer.make_page(self)

    def render_page(self, renderer = None):
        
        if not renderer:
            renderer = self._get_default_renderer()
        
        return self.make_page(renderer).render(renderer)

    def render(self, renderer = None):
        
        if not renderer:
            renderer = self._get_default_renderer()
        
        self.ready()
        canvas = []
        out = canvas.append
        self._render(renderer, out)
        return u"".join(canvas)

    def _get_default_renderer(self):
        from magicbullet.html.renderers import DEFAULT_RENDERER_TYPE
        return DEFAULT_RENDERER_TYPE()

    def _render(self, renderer, out):
        if self.rendered:
            renderer.write_element(self, out)

    def _build(self):
        pass

    def ready(self, observers = None):
        
        if not self.__is_ready:
            self._ready()        
            self.__is_ready = True

        if self.__children:

            descendant_observer = self._descendant_ready

            if descendant_observer is not Element._descendant_ready:
                
                observer_added = True

                if observers is None:
                    observers = [descendant_observer]
                else:
                    observers.append(descendant_observer)
            else:
                observer_added = False

            for child in self.__children:
                child.ready(observers)

            if observer_added:
                observers.pop(-1)

        self._content_ready()

        if observers:
            for observer in observers:
                observer(self)
    
    def add_ready_handler(self, handler):
        if self.__ready_handlers is None:
            self.__ready_handlers = [handler]
        else:
            self.__ready_handlers.append(handler)

    def _ready(self):
        
        if self.member:
            self.add_class(self.member.__class__.__name__)

        if self.__ready_handlers:
            for handler in self.__ready_handlers:
                handler()

    def _content_ready(self):
        pass

    def _descendant_ready(self, descendant):
        pass

    # Attributes
    #--------------------------------------------------------------------------
    
    @getter
    def attributes(self):
        if self.__attributes is None:
            return empty_dict
        else:
            return self.__attributes

    def __getitem__(self, key):
        if self.__attributes is None:
            return None
        else:
            return self.__attributes.get(key)

    def __setitem__(self, key, value):
        if self.__attributes is None:
            if value is not None:
                self.__attributes = {key: value}
        else:
            if value is None:
                self.__attributes.pop(key, None)
            else:
                self.__attributes[key] = value

    def __delitem__(self, key):
        if self.__attributes is not None:
            self.__attributes.pop(key, None)

    # Visibility
    #--------------------------------------------------------------------------
    
    @getter
    def rendered(self):
        return self.visible \
            and (not self.collapsible or self.has_rendered_children())

    def has_rendered_children(self):

        for child in self.children:
            if child.rendered:
                return True

        return False

    # Tree
    #--------------------------------------------------------------------------

    @getter
    def parent(self):
        return self.__parent

    @getter
    def children(self):
        if self.__children is None:
            return empty_list
        else:
            return self.__children
    
    def append(self, child):
     
        if isinstance(child, basestring):
            child = Content(child)
        else:
            child.release()

        if self.__children is None:
            self.__children = [child]
        else:
            self.__children.append(child)
        
        child.__parent = self

    def insert(self, index, child):
        
        if isinstance(child, basestring):
            child = Content(child)
        else:
            child.release()

        if self.__children is None:
            self.__children = []

        self.__children.insert(index, child)
        child.__parent = self

    def place_before(self, sibling):
        
        if sibling.__parent is None:
            raise ElementTreeError()

        self.release()

        sibling.__parent.__children.insert(
            sibling.__parent.__children.index(sibling),
            self
        )

        self.__parent = sibling.__parent

    def place_after(self, sibling):
        
        if sibling.__parent is None:
            raise ElementTreeError()

        self.release()

        sibling.__parent.__children.insert(
            sibling.__parent.__children.index(sibling) + 1,
            self
        )

        self.__parent = sibling.__parent

    def empty(self):

        if self.__children is not None:
            for child in self.__children:
                child.__parent = None

            self.__children = None

    def release(self):
        
        if self.__parent is not None:
            self.__parent.__children.remove(self)
            self.__parent = None

    # CSS classes
    #--------------------------------------------------------------------------

    @getter
    def classes(self):
        
        css_class = self["class"]

        if css_class is None:
            return empty_list
        else:
            return css_class.split()

    def add_class(self, name):
        
        css_class = self["class"]

        if css_class is None:
            self["class"] = name
        else:
            if name not in css_class.split():
                self["class"] = css_class + " " + name

    def remove_class(self, name):
        
        css_class = self["class"]
        
        if css_class is not None:
            classes = css_class.split()
            try:
                css_class = classes.remove(name)
            except ValueError:
                pass
            else:
                if classes:
                    self["class"] = " ".join(classes)
                else:
                    del self["class"]

    # Inline CSS styles
    #--------------------------------------------------------------------------
    
    @getter
    def style(self):
        
        style = self["style"]

        if style is None:
            return empty_dict
        else:
            style_dict = {}

            for declaration in style.split(";"):
                prop, value = declaration.split(":")
                style_dict[prop.strip()] = value.strip()

            return style_dict

    def get_style(self, property):
        return self.style.get(property)

    def set_style(self, property, value):
        style = self.style

        if style:
            if value is None:
                style.pop(property, None)
            else:
                style[property] = value

            if style:
                self["style"] = \
                    "; ".join("%s: %s" % decl for decl in style.iteritems())
            else:
                del self["style"]
        else:
            self["style"] = "%s: %s" % (property, value)

    # Resources
    #--------------------------------------------------------------------------
    
    @getter
    def resources(self):
        if self.__resources is None:
            return empty_list
        else:
            return self.__resources

    @getter
    def resource_uris(self):
        if self.__resource_uris is None:
            return empty_set
        else:
            return self.__resource_uris

    def add_resource(self, resource):
        
        # Normalize the resource
        if isinstance(resource, basestring):
            uri = resource
            resource = Resource.from_uri(uri)
        else:
            uri = resource.uri
            
            if uri is None:
                raise ValueError("Can't add a resource without a defined URI.")

        if self.__resources is None:
            self.__resources = [resource]
            self.__resource_uris = set([uri])
            return True
        elif uri not in self.__resource_uris:
            self.__resources.append(resource)
            self.__resource_uris.add(resource.uri)
            return True
        else:
            return False

    def remove_resource(self, resource):

        if isinstance(resource, basestring):
            removed_uri = resource
            resource = first(self.__resources, uri = removed_uri)

            if resource is None:
                raise ValueError("Error removing '%s' from %s: "
                    "the element doesn't have a resource with that URI")
            else:
                self.__resources.remove(resource)
                self.__resource_uris.remove(removed_uri)
        else:
            self.__resources.remove(resource)
            self.__resource_uris.remove(resource.uri)

    # Meta attributes
    #--------------------------------------------------------------------------
    
    @getter
    def meta(self):
        if self.__meta is None:
            return empty_dict
        else:
            return self.__meta

    def get_meta(self, key):
        if self.__meta is None:
            return None
        else:
            return self.__meta.get(key)

    def set_meta(self, key, value):
        if self.__meta is None:
            if value is not None:
                self.__meta = {key: value}
        else:
            if value is None:
                self.__meta.pop(key, None)
            else:
                self.__meta[key] = value

    # Client parameters
    #--------------------------------------------------------------------------
    
    @getter
    def client_params(self):
        if self.__client_params is None:
            return empty_dict
        else:
            return self.__client_params
    
    def get_client_param(self, key):
        if self.__client_params is None:
            raise KeyError("Trying to read an undefined "
                "client param '%s' on %s" % (key, self))
        else:
            return self.__client_params[key]

    def set_client_param(self, key, value):
        if self.__client_params is None:
            self.__client_params = {key: value}
        else:
            self.__client_params[key] = value

    def remove_client_param(self, key):
        if self.__client_params is None:
            raise KeyError("Trying to remove an undefined "
                "client param '%s' on %s" % (key, self))
        else:
            del self.__client_params[key]

class Content(Element):
 
    styled_class = False
    value = None

    def __init__(self, value, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.value = value
        
    def _render(self, render, out):
        out(self.value)

class PlaceHolder(Content):

    def __init__(self, expression):
        Content.__init__(self, None)
        self.expression = expression

    def _ready(self):
        self.value = self.expression()

class ElementTreeError(Exception):
    pass

if __name__ == "__main__2":
 
    from time import time
    from magicbullet.modeling import refine
    
    start = time()
 
    i = 0
    j = 0
    
    table = Element("table")
    table_content = Element()
    table.append(table_content)
    
    row = Element("tr")
    row_content = Element()
    row.append(row_content)
    alternate_classes = ("even", "odd")

    td = Element("td")

    @refine(table_content)
    def _render(self, renderer, out):
        for i in range(15):
            renderer.write_element(row, out)
    
    @refine(row_content)
    def _render(self, renderer, out):
        for j in range(10):
            td.empty()
            td.append("Cell %d,%d" % (i, j))
            renderer.write_element(td, out)

#    for i in range(15):
#        row = Element("tr")
#        row.add_class(alternate_classes[i % 2])

#        for j in range(10):
#            td = Element("td")
#            td.append("Cell %d,%d" % (i, j))
#            row.append(td)

#        table.append(row)
    
    html = table.render()
    print time() - start
    print html

if __name__ == "__main__":

    from guppy import hpy
    h = hpy()
    h.setrelheap()

    for n in range(10):
        table = Element("table")     
        alternate_classes = ("even", "odd")

        for i in range(15):
            row = Element("tr")
            row.add_class(alternate_classes[i % 2])

            for j in range(10):
                td = Element("td")
                td.append("Cell %d,%d" % (i, j))
                row.append(td)

            table.append(row)
        
        html = table.render()

