#-*- coding: utf-8 -*-
"""
Provides the base class for all schema members.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""
from itertools import chain
from copy import deepcopy
from magicbullet.modeling import ListWrapper
from magicbullet.pkgutils import import_object
from magicbullet.translations import translate
from magicbullet.schema import exceptions
from magicbullet.schema.expressions import Variable
from magicbullet.schema.validationcontext import ValidationContext

class DynamicDefault(object):

    def __init__(self, factory):
        self.factory = factory

    def __call__(self):
        return self.factory()


class Member(Variable):
    """Schema members are the distinct data units that comprise a
    L{schema<schema.Schema>}.

    Members are bound to a single schema, where they are identified by a unique
    name. The purpose of a member is to describe the nature and constraints of
    a discrete piece of data for the schema they belong to. Typical examples of
    members are fields and collections, and their respective subtypes.
    
    This class acts mostly as an abstract type, used as a base by all the
    different kinds of members that can comprise a schema.

    @ivar default: The default value for the member.
    
    @ivar required: Determines if the field requires a value. When set to true,
        a value of None for this member will trigger a validation error of type
        L{ValueRequiredError<exceptions.ValueRequiredError>}.
    @type required: bool
    
    @ivar require_none: Determines if the field disallows any value other than
        None.  When set to true, a value different than None for this member
        will trigger a validation error of type
        L{NoneRequiredError<exceptions.NoneRequiredError>}.
    @type require_none: bool

    @ivar enumeration: Establishes a limited set of acceptable values for the
        member. If a member with this constraint is given a value not found
        inside the set, an L{EnumerationError<exceptions.EnumerationError>}
        error will be triggered.
    @type enumeration: any container
    """

    type = None
    default = None
    required = False
    require_none = False
    enumeration = None

    # Attributes that deserve special treatment when performing a deep copy
    _special_copy_keys = set(["_validations_wrapper", "_validations"])

    def __init__(self, doc = None, **kwargs):
        self._name = None
        self._schema = None
        self._validations = []
        self._validations_wrapper = ListWrapper(self._validations)
        self.add_validation(Member.member_validation_rule)

        Variable.__init__(self, None)
        self.__type = None

        if doc is not None:
            self.__doc__ = doc

        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        
        member_desc = self._name \
            and "member '%s'" % self._name or "anonymous member"

        if self._schema is None:
            return "unbound " + member_desc
        else:
            schema_name = self._schema.name
            return "%s in %s" % (
                member_desc,
                schema_name
                    and "'%s' schema" % schema_name or "anonymous schema"
            )

    def _get_name(self):
        return self._name

    def _set_name(self, value):

        if self._schema is not None:
            raise exceptions.MemberRenamedError(self, value)
        
        self._name = value

    name = property(_get_name, _set_name, doc = """
        The name that uniquely identifies the member on the schema it is bound
        to. Once set it can't be changed (trying to do so will raise a
        L{MemberRenamedError} exception).
        @type: str
        """)

    def _get_schema(self):
        return self._schema

    def _set_schema(self, value):

        if self._schema is not None:
            raise exceptions.MemberReacquiredError(self, value)

        self._schema = value

    schema = property(_get_schema, _set_schema, doc = """
        The schema that the member is bound to. Once set it can't be changed
        (trying to do so will raise a L{MemberReacquiredError} exception).
        @type: L{Schema<schema.Schema>}
        """)

    def _get_type(self):
        
        # Resolve string references
        if isinstance(self.__type, basestring):
            self.__type = type = import_object(type)
        
        return self.__type

    def _set_type(self, type):
        self.__type = type

    type = property(_get_type, _set_type, doc = """
        Imposes a data type constraint on the member. All values assigned to
        this member must be instances of the specified data type. Breaking this
        restriction will produce a validation error of type
        L{TypeCheckError<exceptions.TypeCheckError>}.
        @type type: type or str
        """)

    def produce_default(self):
        """Generates a default value for the member. Can be overridden (ie. to
        produce dynamic default values).
        """
        if isinstance(self.default, DynamicDefault):
            return self.default()
        else:
            return self.default

    def copy(self):
        """Creates a deep, unbound copy of the member.

        @return: The resulting copy.
        @rtype: L{Member}
        """
        copied_member = deepcopy(self)
        copied_member._schema = None
        return copied_member
    
    def __deepcopy__(self, memo):

        copy = self.__class__()
        memo[id(self)] = copy

        for key, value in self.__dict__.iteritems():
            if key not in self._special_copy_keys:
                copy.__dict__[key] = deepcopy(value, memo)
        
        copy._validations = list(self._validations)
        memo[id(self._validations)] = copy._validations
        
        copy._validations_wrapper = ListWrapper(copy._validations)
        memo[id(copy._validations_wrapper)] = copy._validations_wrapper

        return copy

    def add_validation(self, validation):
        """Adds a validation function to the member.
        
        @param validation: A callable that will be added as a validation rule
            for the member. Takes two positional parameters (a reference to the
            member itself, and the value assigned to the member), plus any
            additional number of keyword arguments used to refine validation
            options and context. The callable should produce a sequence of
            L{ValidationError<exceptions.ValidatitonError>} instances.
        @type validation: callable

        @return: The validation rule, as provided.
        @rtype: callable
        """
        self._validations.append(validation)
        return validation
    
    def remove_validation(self, validation):
        """Removes one of the validation rules previously added to a member.

        @param validation: The validation to remove, as previously passed to
            L{add_validation}.
        @type validation: callable

        @raise ValueError: Raised if the member doesn't have the indicated
            validation.
        """
        self._validations.remove(validation)

    def validations(self, recursive = True):
        """Iterates over all the validation rules that apply to the member.

        @param recursive: Indicates if the produced set of validations should
            include those declared on members contained within the member. This
            parameter is only meaningful on L{compound members<>}, but is made
            available globally in order to allow the method to be called
            polymorphically using a consistent signature.

        @return: The sequence of validation rules for the member.
        @rtype: callable iterable
        """
        return self._validations_wrapper

    def validate(self, value, context = None):
        """Indicates if the given value fulfills all the validation rules
        imposed by the member.
        
        @param value: The value to validate.
        
        @param context: Additional parameters used to fine tune the validation
            process.
        @type context: L{ValidationContext<validationcontext.ValidationContext>}
        """
        if context is None:
            context = ValidationContext()

        for error in self.get_errors(value, context):
            return False

        return True
 
    def get_errors(self, value, context = None):
        """Tests the given value with all the validation rules declared by the
        member, iterating over the resulting set of errors.

        @param value: The value to evaluate.
        @param context: Additional parameters used to fine tune the validation
            process.
        @type context: L{ValidationContext<validationcontext.ValidationContext>}

        @return: An iterable sequence of validation errors.
        @rtype: L{ValidationError<exceptions.ValidationError>}
            iterable
        """
        if context is None:
            context = ValidationContext()

        if self._validations:
            for validation in self._validations:
                for error in validation(self, value, context):
                    yield error

    @classmethod
    def resolve_constraint(cls, expr, context):
        """Resolves a constraint expression for the given context.
        
        Most constraints can assigned dynamic expressions instead of static
        values, allowing them to adapt to different validation contexts. For
        example, a field may state that it should be required if and only if
        another field is set to a certain value. This method normalizes any
        constraint (either static or dynamic) to a static value, given a
        certain validation context.

        Dynamic expressions are formed by assigning a callable object to a
        constraint value.

        @param expr: The constraint expression to resolve.
        
        @param context: The validation context that will be made available to
            dynamic constraint expressions (the same set of additional
            parameters used to add context to most validation methods).
        @type context: L{ValidationContext<validationcontext.ValidationContext>}

        @return: The normalized expression value.
        """
        if callable(expr) and not isinstance(expr, type):
            return expr(context)
        else:
            return expr

    def member_validation_rule(self, value, context):
        """
        The base validation rule for all members. Tests the L{required},
        L{require_none}, L{enumeration} and L{type} constraints.
        """
        # Value required
        if value is None:
            if self.resolve_constraint(self.required, context):
                yield exceptions.ValueRequiredError(self, value, context)

        # None required
        elif self.resolve_constraint(self.require_none, context):
            yield exceptions.NoneRequiredError(self, value, context)

        else:
            # Enumeration
            enumeration = self.resolve_constraint(self.enumeration, context)
            
            if enumeration is not None and value not in enumeration:
                yield exceptions.EnumerationError(
                    self, value, context, enumeration)

            # Type check
            type = self.resolve_constraint(self.type, context)

            if type and not isinstance(value, type):
                yield exceptions.TypeCheckError(self, value, context, type)

    def __translate__(self, language, **kwargs):        
        try:            
            return translate(self.schema.name + "." + self.name)
        except KeyError:
            copy_source = getattr(self, "copy_source", None)
            if copy_source:
                return translate(copy_source)
            else:
                raise

