#-*- coding: utf-8 -*-
"""
Visual elements for data binding.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.modeling import getter
from magicbullet.translations import translations
from magicbullet.html import Element


class DataDisplay(object):
    """Base class for all visual components that can display schema-based data.
    """
    data = None
    schema = None
    editable = True

    def __init__(self):
        self.__member_displayed = {}
        self.__member_labels = {}
        self.__member_editable = {}
        self.__member_display = {}
        self.__member_type_display = {}

    def _resolve_member(self, member):

        if isinstance(member, basestring):
            if self.schema is None:
                raise ValueError(
                    "Can't resolve a member by name on an unbound data display"
                )
            return self.schema[member]
        else:
            return member

    @getter
    def displayed_members(self):
        return (member for member in self.schema.members(True).itervalues()
                if self.get_member_displayed(member))

    def get_member_displayed(self, member):
        """Indicates if the specified member should be displayed. By default,
        all members in the schema are displayed. The precise meaning of hiding
        a member will change between different implementors of the
        L{DataDisplay} interface. For example, a data table may still generate
        the HTML for a hidden column, but hide it using a CSS declaration, so
        that its visibility can be toggled later on using client side
        scripting. Members that shouldn't be shown at all shouldn't appear on
        the schema provided to the data display (possibly taking advantadge of
        the L{subset<magicbullet.schema.member.Member.copy>} functionality).
        
        @param member: The member to get the display state for. Can be
            specified using a direct reference to the member object, or by
            name.
        @type member: str or L{Member<magicbullet.schema.member.Member>}
        
        @return: True if the member should be displayed, False otherwise.
        @rtype: bool
        """
        return self.__member_displayed.get(
                    self._resolve_member(member),
                    True)
    
    def set_member_displayed(self, member, displayed):
        """Establishes if the indicated member should be displayed. See
        L{get_member_displayed} for more details.
        
        @param member: The member to get the display state for. Can be
            specified using a direct reference to the member object, or by
            name.
        @type member: str or L{Member<magicbullet.schema.member.Member>}

        @param displayed: True if the member should be displayed, False
            otherwise.
        @type displayed: bool
        """
        self.__member_displayed[self._resolve_member(member)] = displayed

    def get_member_label(self, member):
        """Gets the descriptive, human readable title for the member, as shown
        by the data display.
        
        @param member: The member to get the label for. Can be specified using
            a direct reference to the member object, or by name.
        @type member: str or L{Member<magicbullet.schema.member.Member>}

        @return: The descriptive title for the member.
        @rtype: unicode
        """
        member = self._resolve_member(member)
        label = self.__member_labels.get(member, None)

        if label is None:
            label = translations.request(
                "%s.%s" % (member.schema.name, member.name)
            )

        return label

    def set_member_label(self, member, label):
        """Sets the descriptive, human readable title for the member.
        
        @param member: The member to set the label for. Can be specified using
            a direct reference to the member object, or by name.
        @type member: str or L{Member<magicbullet.schema.member.Member>}

        @param label: The descriptive title that will be assigned to the
            member.
        @type label: unicode
        """
        self.__member_labels[self._resolve_member(member)] = label

    def get_member_editable(self, member):
        """Indicates if the given member should be editable by users. This
        affects the kind of display used by the member (for example, a text
        entry widget for an editable member, a static text label for a non
        editable one).

        @param member: The member to check the editable state for.
        @type member: str or L{Member<magicbullet.schema.member.Member>}

        @return: True if the member should be displayed as a user editable
            control, False if it should be displayed as a static, unmodifiable
            piece of data.
        @rtype: bool
        """
        return self.__member_editable.get(
                    self._resolve_member(member),
                    self.editable)

    def set_member_editable(self, member, editable):
        """Determines if the given member should be editable by users. This
        affects the kind of display used by the member (for example, a text
        entry widget for an editable member, a static text label for a non
        editable one).

        @param member: The member to check the editable state for.
        @type member: str or L{Member<magicbullet.schema.member.Member>}

        @param editable: True if the member should be displayed as a user
            editable control, False if it should be displayed as a static,
            unmodifiable piece of data.
        @type editable: bool
        """
        self.__member_editable[self._resolve_member(member)] = editable

    def get_member_value(self, obj, member):
        return getattr(obj, member.name, None)
        
    def get_member_display(self, obj, member, value):
        
        member = self._resolve_member(member)
        display = self.__member_display.get(member)

        if display is None:
            display = self.get_member_type_display(member.__class__)
        
        display = (display or Element)()
        display.column = member
        display.item = obj
        display.value = str(value)
        return display

    def set_member_display(self, member, display):
        self.__member_display[self._resolve_member(member)] = display

    def get_member_type_display(self, member_type):
        return self.__member_type_display.get(member_type)

    def set_member_type_display(self, member_type, display):
        self.__member_type[member_type] = display


class CollectionDisplay(DataDisplay):

    order = None
    sortable = True

    def __init__(self):
        self.__member_sortable = {}
        self.__filters = []
        self.filters = ListWrapper(self.__filters)

    def get_member_sortable(self, member):
        return self.__member_sortable.get(
            self._resolve_member(member),
            self.sortable)

    def set_member_sortable(self, member, sortable):
        self.__member_sortable[self._resolve_member(member)] = editable

    def add_filter(self, filter):
        self.__filters.append(filter)
    

