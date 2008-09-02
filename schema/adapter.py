#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from operator import getitem, setitem
from magicbullet.modeling import ListWrapper
from magicbullet.schema.schemastrings import String

_do_nothing = lambda member: None

_undefined = object()

def default_getter(obj):
    if isinstance(obj, dict):
        return getitem
    else:
        return getattr

def default_setter(obj):
    
    if isinstance(obj, dict):
        return setitem
    else:
        return setattr


class Adapter(object):

    copy_validations = True

    def __init__(self):
        self.__implicit_copy = True
        self.import_rules = RuleSet()
        self.export_rules = RuleSet()

    def import_schema(self, source_schema, target_schema):
        self.import_rules.adapt_schema(source_schema, target_schema)

    def export_schema(self, source_schema, target_schema):
        self.export_rules.adapt_schema(source_schema, target_schema)

    def import_object(self,
        source_object,
        target_object,
        source_schema = None,
        get_value = None,
        set_value = None):
        
        self.import_rules.adapt_object(
            source_object,
            target_object,
            source_schema,
            get_value,
            set_value)

    def export_object(self,        
        source_object,
        target_object,
        source_schema = None,
        get_value = None,
        set_value = None):
        
        self.export_rules.adapt_object(
            source_object,
            target_object,
            source_schema,
            get_value,
            set_value)

    def _get_implicit_copy(self):
        return self.__implicit_copy

    def _set_implicit_copy(self, value):
        self.__implicit_copy = value
        self.import_rules.implicit_copy = value
        self.export_rules.implicit_copy = value

    implicit_copy = property(_get_implicit_copy, _set_implicit_copy)

    def copy(self,
        mapping,
        export_transform = None,
        import_transform = None,
        copy_validations = None):
        
        if copy_validations is None:
            copy_validations = self.copy_validations

        export_rule = Copy(
                        mapping,
                        copy_validations = copy_validations,
                        transform = export_transform)

        import_rule = Copy(
                        dict((value, key)
                            for key, value in export_rule.mapping.iteritems()),
                        copy_validations = copy_validations,
                        transform = import_transform)

        self.export_rules.add_rule(export_rule)
        self.import_rules.add_rule(import_rule)

    def exclude(self, members):
        
        if isinstance(members, basestring):
            members = [members]

        exclusion = Exclusion(members)
        self.import_rules.add_rule(exclusion)
        self.export_rules.add_rule(exclusion)
    
    def split(self, source_member, separator, target_members):
        
        self.export_rules.add_rule(
            Split(source_member, separator, target_members))

        self.import_rules.add_rule(
            Join(target_members, separator, source_member))

    def join(self, source_members, glue, target_member):
        
        self.export_rules.add_rule(
            Join(source_members, glue, target_member))
        
        self.import_rules.add_rule(
            Split(target_member, glue, source_members))


class RuleSet(object):

    implicit_copy = True
    
    def __init__(self, *rules):
        self.__rules = list(rules)
        self.rules = ListWrapper(rules)

    def add_rule(self, rule):
        self.__rules.append(rule)

    def remove_rule(self, rule):
        self.__rules.remove(rule)
    
    def adapt_schema(self, source_schema, target_schema):
        
        if self.implicit_copy:
            remaining_keys = set(source_schema.members())
            consume_key = remaining_keys.remove
        else:
            consume_key = _do_nothing
        
        for rule in self.__rules:
            rule.adapt_schema(source_schema, target_schema, consume_key)

        if self.implicit_copy:
            copy_rule = Copy(remaining_keys)
            copy_rule.adapt_schema(
                source_schema, target_schema, _do_nothing)

    def adapt_object(self,
        source_object,
        target_object,
        source_schema = None,
        get_value = None,
        set_value = None):
        
        if get_value is None:
            get_value = default_getter(source_object)

        if set_value is None:
            set_value = default_setter(target_object)

        if self.implicit_copy:
            remaining_keys = set(source_schema.members())
            consume_key = remaining_keys.remove
        else:
            consume_key = _do_nothing
        
        for rule in self.__rules:
            rule.adapt_object(
                source_object,
                target_object,
                source_schema,
                get_value,
                set_value,
                consume_key)

        if self.implicit_copy:
            copy_rule = Copy(remaining_keys)
            copy_rule.adapt_object(
                source_object,
                target_object,
                source_schema,
                get_value,
                set_value,
                _do_nothing)


class Rule(object):

    def adapt_schema(self,
        source_schema,
        target_schema,
        consume_key):
        pass

    def adapt_object(self,
        source_object,
        target_object,
        source_schema,        
        get_value,
        set_value,
        consume_key):
        pass

    def _adapt_member(self, schema, properties):

        try:
            member = schema[properties["name"]]
        except KeyError:
            member_type = properties["__class__"]
            member = member_type()
            
        for key, value in properties.iteritems():
            if key != "__class__":
                setattr(member, key, value)

        if not member.schema:
            schema.add_member(member)

        return member


class Copy(Rule):

    def __init__(self,
        mapping,
        properties = None,
        transform = None,
        copy_validations = True):

        self.mapping = mapping
        self.properties = properties
        self.transform = transform

    def __get_mapping(self):
        return self.__mapping

    def __set_mapping(self, mapping):
        if isinstance(mapping, basestring):
            self.__mapping = {mapping: mapping}
        elif hasattr(mapping, "items"):
            self.__mapping = mapping
        else:
            try:
                self.__mapping = dict((entry, entry) for entry in mapping)
            except TypeError:
                raise TypeError(
                    "Expected a string, string sequence or mapping")
    
    mapping = property(__get_mapping, __set_mapping, doc = """
        Gets or sets the mapping detailing the copy operation.
        @type: (str, str) mapping
        """)

    def adapt_schema(self,
        source_schema,
        target_schema,
        consume_key):

        for source_name, target_name in self.mapping.iteritems():
            
            consume_key(source_name)

            try:
                target_member = target_schema[target_name]
            except KeyError:
                source_member = source_schema[source_name]
                target_member = source_member.copy()
                target_member.name = target_name
            
            if self.properties:
                for prop_name, prop_value in self.properties.iteritems():
                    setattr(target_member, prop_name, prop_value)

            if not target_member.schema:
                target_schema.add_member(target_member)

    def adapt_object(self,
        source_object,
        target_object,
        source_schema,        
        get_value,
        set_value,
        consume_key):
        
        for source_name, target_name in self.mapping.iteritems():
            consume_key(source_name)
            value = get_value(source_object, source_name)

            if self.transform:
                value = self.transform(value)

            set_value(target_object, target_name, value)


class Exclusion(Rule):

    def __init__(self, excluded_members):
        self.excluded_members = excluded_members

    def adapt_schema(self,
        source_schema,
        target_schema,
        consume_key):

        for excluded_key in self.excluded_members:
            consume_key(excluded_key)

    def adapt_object(self,
        source_object,
        target_object,
        source_schema,
        get_value,
        set_value,
        consume_key):
        
        for excluded_key in self.excluded_members:
            consume_key(excluded_key)


class Split(Rule):
    
    def __init__(self, source, separator, targets):
        
        self.source = source
        self.separator = separator

        norm_targets = []

        for target in targets:
            if isinstance(target, basestring):
                norm_targets.append({"name": target, "__class__": String})
            elif isinstance(target, dict):
                if "name" not in target:
                    raise ValueError("Split targets must be given a name")
                target.setdefault("__class__", String)
                norm_targets.append(target)
            else:
                raise TypeError("Expected a string or dictionary")

        self.targets = norm_targets
    
    def adapt_schema(self,
        source_schema,
        target_schema,
        consume_key):

        consume_key(self.source)
        
        for target in self.targets:
            self._adapt_member(target_schema, target)

    def adapt_object(self,
        source_object,
        target_object,
        source_schema,
        get_value,
        set_value,
        consume_key):

        consume_key(self.source)

        value = get_value(source_object, self.source)

        if value is not None:
            parts = value.split(self.separator)

            for target, part in zip(self.targets, parts):
                setattr(target_object, target["name"], part)


class Join(Rule):
    
    def __init__(self, sources, glue, target):        
        self.sources = sources
        self.glue = glue

        if isinstance(target, basestring):
            target = {"name": target}

        self.target = target

    def adapt_schema(self,
        source_schema,
        target_schema,
        consume_key):

        for source in self.sources:
            consume_key(source)
        
        self._adapt_member(target_schema, self.target)

    def adapt_object(self,
        source_object,
        target_object,
        source_schema,
        get_value,
        set_value,
        consume_key):

        parts = []

        for source in self.sources:
            consume_key(source)
            value = get_value(source_object, source)

            if value is None:
                break
            else:
                parts.append(value)
        else:
            value = self.glue.join(unicode(part) for part in parts)
            set_value(target_object, self.target["name"], value)


if __name__ == "__main__":
    
    import re
    from magicbullet.schema import Schema, Integer, String, Boolean
   
    adapter = Adapter()
    adapter.copy(
        {"enabled": "disabled"},
        import_transform = lambda value: not value,
        export_transform = lambda value: not value
    )

    user_schema = Schema(members = {
        "id": Integer(
            required = True,
            unique = True,
            min = 1
        ),
        "name": String(
            required = True,
            min = 4,
            max = 20,
            format = re.compile("^[a-zA-Z][a-zA-Z_0-9]*$")
        ),
        "enabled": Boolean(
            required = True,
            default = True
        )
    })    
   
    class User(object):
        pass
    
    user = User()
    user.id = 3
    user.name = "Kurt Russell"
    user.enabled = False

    form_schema = Schema()
    adapter.export_schema(user_schema, form_schema)
    form = {}
    
    adapter.export_object(user, form, user_schema)
    print form
    form["name"] = "Chuck Norris"
    form["disabled"] = False

    adapter.import_object(form, user, form_schema)
    print user.__dict__

