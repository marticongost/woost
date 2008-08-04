#-*- coding: utf-8 -*-
"""
Provides a member that handles compound values.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from magicbullet.modeling import empty_dict, empty_list, \
                              ListWrapper, DictWrapper
from magicbullet.schema.member import Member
from magicbullet.schema.exceptions import SchemaIntegrityError

class Schema(Member):
    """A data structure, made up of one or more L{members<member.Member>}.
    Schemas are themselves members, which allows them to be nested arbitrarely
    (ie. in other schemas or L{collections<schemacollections.Collection>} to
    assemble more complex compound types.

    Schemas support inheritance. All members defined by a base schema will be
    reflected on their derived schemas. This is done dynamically: new members
    added to base schemas automatically appear as members of any derived
    schema, recursively. Derived schemas can override member definitions with
    their own, simply adding a new member matching the name of a existing one.

    Schemas can use multiple inheritance; in case of conflicting member
    definitions, the one defined by the foremost base schema (as passed to the
    L{inherit} method) will take precedence.

    @ivar bases: The list of base schemas that the schema inherits from. This
        is a shallow list; to obtain the full inheritance tree, use the
        L{ascend_inheritance} method instead.
    """
    members_order = None

    def __init__(self, **kwargs):

        members = kwargs.pop("members", None)
        Member.__init__(self, **kwargs)
        
        self.add_validation(Schema.schema_validation_rule)

        self.__bases = None
        self.bases = ListWrapper(empty_list)

        self.__members = None

        if members:
            self.expand(members)
            
    def inherit(self, *bases):
        """Declare an inheritance relationship towards one or more base
        schemas.

        @param bases: The list of base schemas to inherit from.
        @type bases: L{Schema}
        """

        def prevent_cycle(bases):
            for base in bases:
                if base is self:
                    raise SchemaInheritanceCycleError(self)
                if base.__bases:
                    prevent_cycle(base.__bases)

        prevent_cycle(bases)

        if self.__bases is None:
            self.__bases = bases
            self.bases = ListWrapper(bases)
        else:
            self.__bases.extend(bases)        

    def ascend_inheritance(self, include_self = False):
        
        if include_self:
            yield self

        if self.__bases:
            for base in self.__bases:
                for ascendant in base.ascend_inheritance(True):
                    yield ascendant

    def add_member(self, member):
        """Adds a new member to the schema.

        @param member: The member to add.
        @type member: L{Member<member.Member>}

        @raise SchemaIntegrityError: Raised when trying to add an anonymous
            member to the schema. All members must have a unique name.
        """
        self._check_member(member)
        self._add_member(member)

    def _check_member(self, member):
        if member.name is None:
            raise SchemaIntegrityError(
                "Can't add an anonymous member to %s" % self
            )

    def _add_member(self, member):
        if self.__members is None:
            self.__members = {}

        self.__members[member.name] = member
        member._schema = self

    def expand(self, members):
        """Adds several members to the schema.
        
        @param members: A list or mapping of additional members to add to the
            copy. When given as a mapping, the keys will be used for the member
            names.
        @type members: L{Member<member.Member>} list
            or (str, L{Member<member.Member>}) dict
        """
        
        # From a dictionary
        if isinstance(members, dict):
            for name, member in members.iteritems():

                if isinstance(member, type):
                    member = member()

                member.name = name
                self.add_member(member)

        # From a list
        else:
            for member in members:
                self.add_member(member)

    def remove_member(self, member):
        """Removes a member from the schema.

        @param member: The member to remove. Can be specified using a reference
            to the member object itself, or giving its name.
        @type member: L{Member<member.Member>} or str

        @raise L{SchemaIntegrityError<exceptions.SchemaIntegrityError>}:
            Raised if the member doesn't belong to the schema.
        """

        # Normalize string references to member objects
        if isinstance(member, basestring):
            member = self[member]

        if member._schema is not self:
            raise SchemaIntegrityError(
                "Trying to remove %s from a schema it doesn't belong to (%s)"
                % (member, self)
            )

        member._schema = None
        del self.__members[member]

    def members(self, recursive = True):
        """A dictionary with all the members defined by the schema and its
        bases.

        @param recursive: Indicates if the returned dictionary should contain
            members defined by the schema's bases. This is the default
            behavior; Setting this parameter to False will exclude all
            inherited members.
        @type recursive: False

        @return: A mapping containing the members for the schema, indexed by
            member name.
        @rtype: (str, L{Member<members.Member>}) read only dict
        """
        if recursive and self.__bases:

            members = {}

            def descend(schema):

                if schema.__bases:
                    for base in schema.__bases:
                        descend(base)

                if schema.__members:
                    for name, member in schema.__members.iteritems():
                        members[name] = member

            descend(self)           
            return DictWrapper(members)

        else:
            return DictWrapper(self.__members or empty_dict)

    def copy(self,
        inheritance = True,
        validations = True,
        include = None,
        exclude = None,
        members = None):
        """Creates a copy of the schema. By default, inheritance information,
        validations and members directly declared by the model will be copied.

        @param inheritance: Indicates if the copy will inherit from the same
            bases that the model schema inherits from (this is the default
            behavior). When set to False, the copy will be created without it
            inheriting from any schema, but the set of validations and members
            to copy will be expanded to include inherited members.
        @type include: bool

        @param validations: Determines if validation rules defined by the model
            will be copied (this is the default behavior). The set of copied
            validations will depend on the value of the L{inheritance}
            parameter (a value of True will copy just the validations directly
            defined by the model, whereas False will also include validations
            inherited from base schemas).
        @type include: bool

        @param include: Limits the members that will be copied from the model.
            This list can be further restricted if the L{exclude} parameter is
            given a value. Members can be indicated either by name or through
            an object reference.
        @type include: (L{Member<member.Member>} or str) sequence

        @param exclude: Indicates a set of members that should not be copied.
            Members can be indicated either by name or through an object
            reference.
        @type exclude: (L{Member<member.Member>} or str) sequence

        @param members: A list or mapping of additional members to add to the
            copy. When given as a mapping, the keys will be used for the member
            names.
        @type members: L{Member<member.Member>} list
                       or (str, L{Member<member.Member>}) dict
        """ 
        
        # Get available members
        copied_members = self.members(recursive = not inheritance)
        
        # Normalize inclusions to member references
        include = include and set(
            self[member] if isinstance(member, basestring) else member
            for member in include
        )
        
        # Normalize exclusions to member references
        exclude = exclude and set(
            self[member] if isinstance(member, basestring) else member
            for member in exclude
        )
        
        # Create member copies
        member_copies = []

        for member in (include or copied_members.itervalues()):
            if not exclude or member not in exclude:
                member_copy = member.copy()
                member_copy.copy_source = member
                member_copies.append(member_copy)
        
        # Create the copy
        copy = Schema(members = member_copies)

        if inheritance:
            copy.inherit(*self.bases)
            copy.members_order = self.members_order
        else:
            members_order = []

            def get_members_order(schema):

                if schema and schema.__bases:
                    for base in schema.__bases:
                        get_members_order(schema)    
                        
                schema_order = (
                    (
                        member
                        if isinstance(member, basestring)
                        else member.name
                    )
                    for member in schema.members_order
                )

                members_order.extend(
                    member
                    for member in schema_order
                    if member in copy.__members)

            get_members_order(self)
            copy.members_order = members_order

        if members:
            copy.expand(members)

        if validations:
            for validation in self.validations(recursive = not inheritance):
                copy.add_validation(validation)

        return copy

    def __getitem__(self, name):
        """Overrides the indexing operator to retrieve members by name.

        @param name: The name of the member to retrieve.
        @rtype name: str

        @return: A reference to the requested member.
        @rtype: L{Member<member.Member>}

        @raise KeyError: Raised if neither the schema or its bases possess a
            member with the specified name.
        """
        def find_member(schema):

            member = schema.__members and schema.__members.get(name)

            if member is None and schema.__bases:
                for base in schema.__bases:
                    member = find_member(base)                    
                    if member:
                        break

            return member

        member = find_member(self)

        if member is None:
            raise KeyError("%s doesn't define a '%s' member" % (self, name))
            
        return member
    
    def __setitem__(self, name, member):
        """Overrides the indexing operator to bind members to the schema under
        the specified name.

        @param name: The name to assign to the member.
        @type name: str

        @param member: The member to add to the schema.
        @type member: L{Member<member.Member>}
        """
        member.name = name
        self.add_member(member)

    def validations(self, recursive = True):
        """Iterates over all the validation rules that apply to the schema.

        @param recursive: Indicates if validations inherited from base schemas
            should be included. This is the default behavior.

        @return: The sequence of validation rules for the member.
        @rtype: callable iterable
        """        
        if self.__bases:

            validations = []

            def descend(schema):

                if schema.__bases:
                    for base in schema.__bases:
                        descend(base)

                if schema.__validations:
                    validations.extend(schema.__validations)
            
            descend(self)
            return ListWrapper(validations)

        elif self.__validations:
            return ListWrapper(self.__validations)
        
        else:
            return empty_list

    def schema_validation_rule(self, validable, context):
        """Validation rule for schemas. Applies the validation rules defined by
        all members in the schema, propagating their errors."""

        getter = context.get("getter", getattr)

        if self.__members:
            
            context.enter(self, validable)

            try:
                for name, member in self.__members.iteritems():
                    value = getter(validable, name)
                    for error in member.get_errors(value, context):
                        yield error
            finally:
                context.leave()

    def ordered_members(self, recursive = True):
        """Gets a list containing all the members defined by the schema, in
        order.
        
        Schemas can define the ordering for their members by supplying a
        L{members_order} attribute, which should contain a series of object or
        string references to members defined by the schema. Members not in that
        list will be appended at the end, sorted by name. Inherited members
        will be prepended, in the order defined by their parent schema.
        
        Alternatively, schema subclasses can override this method to allow for
        more involved sorting logic.
        
        @param recursive: Indicates if the returned list should contain members
            inherited from base schemas (True) or if only members directly
            defined by the schema should be included.
        @type recursive: bool

        @return: The list of members in the schema, in order.
        @rtype: L{Member<member.Member>} list
        """
        ordered_members = []
        
        if recursive and self.__bases:
            for base in self.__bases:
                ordered_members.extend(base.ordered_members(True))
        
        ordering = self.members_order

        if ordering:
            ordering = [
                (
                    self.__members[member]
                    if isinstance(member, basestring)
                    else member
                )
                for member in ordering
            ]
            ordered_members.extend(ordering)
            remaining_members = \
                set(self.__members.itervalues()) - set(ordering)
        else:
            remaining_members = self.__members.itervalues() \
                                if self.__members \
                                else ()

        if remaining_members:
            ordered_members.extend(
                sorted(remaining_members, key = lambda m: m.name)
            )

        return ordered_members

