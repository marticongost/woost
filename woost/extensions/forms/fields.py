#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail.modeling import extend, call_base
from cocktail.translations import translations
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Item

translations.load_bundle("woost.extensions.forms.fields")


class Field(Item):

    visible_from_root = False
    show_element_in_listing = False
    type_group = "custom_forms"
    instantiable = False
    member_type = None

    groups_order = [
        "field_description",
        "field_structure",
        "field_properties"
    ]

    members_order = [
        "title",
        "visible_title",
        "empty_label",
        "explanation",
        "field_set",
        "collection",
        "is_required_field",
        "field_edit_control",
        "field_name",
        "field_initialization"
    ]

    title = schema.String(
        translated = True,
        required = True,
        descriptive = True,
        spellcheck = True,
        member_group = "field_description"
    )

    visible_title = schema.String(
        translated = True,
        member_group = "field_description",
        listed_by_default = False
    )

    empty_label = schema.String(
        translated = True,
        member_group = "field_description",
        listed_by_default = False
    )

    explanation = schema.HTML(
        translated = True,
        spellcheck = True,
        edit_control = "woost.views.RichTextEditor",
        member_group = "field_description"
    )

    field_name = schema.String(
        listed_by_default = False,
        member_group = "administration"
    )

    field_set = schema.Reference(
        type = "woost.extensions.forms.fields.FieldSet",
        bidirectional = True,
        editable = schema.NOT_EDITABLE,
        member_group = "field_structure"
    )

    collection = schema.Reference(
        type = "woost.extensions.forms.fields.CollectionField",
        bidirectional = True,
        editable = schema.NOT_EDITABLE,
        member_group = "field_structure",
        listed_by_default = False
    )

    is_required_field = schema.Boolean(
        required = True,
        default = True,
        member_group = "field_properties",
        listed_by_default = False
    )

    field_edit_controls = None

    field_edit_control = schema.String(
        enumeration = lambda ctx:
            ctx.get("persistent_object")
            and ctx.get("persistent_object").field_edit_controls,
        edit_control = display_factory(
            "cocktail.html.RadioSelector",
            empty_option_displayed = True
        ),
        member_group = "field_properties",
        listed_by_default = False
    )

    field_initialization = schema.CodeBlock(
        language = "python",
        listed_by_default = False,
        member_group = "administration"
    )

    @event_handler
    def handle_inherited(cls, e):
        # Add members that depend on the field's type (f. eg. although all
        # fields can have a default value, we can't add the member to represent
        # it until we know the field's type)
        field_class = e.schema
        member_type = getattr(field_class, "member_type", None)
        if member_type is not None:
            field_class.add_generic_members()

    @classmethod
    def add_generic_members(cls):

        # Declare a member for the field's default value
        if cls.get_member("field_default") is None:
            default_member = cls.create_field_default_member()
            if default_member is not None:
                cls.add_member(default_member)

        # Declare a member for the field's enumeration
        if cls.get_member("field_enumeration") is None:
            enumeration_member = cls.create_field_enumeration_member()
            if enumeration_member is not None:
                cls.add_member(enumeration_member)

    @classmethod
    def create_field_default_member(cls):
        return cls.member_type(
            "field_default",
            member_group = "field_properties",
            listed_by_default = False,
            custom_translation_key =
                "woost.extensions.forms.fields.field_default"
        )

    @classmethod
    def create_field_enumeration_member(cls):
        return schema.Collection(
            "field_enumeration",
            items = cls.member_type(),
            member_group = "field_properties",
            listed_by_default = False,
            custom_translation_key =
                "woost.extensions.forms.fields.field_enumeration"
        )

    def generate_members(self):
        yield self.create_member()

    def create_member(self):

        member = self.member_type(
            self.field_name or "field%d" % self.id
        )
        self._init_member(member)

        if self.field_initialization:
            label = "%s #%s.field_initialization" % (
                self.__class__.__name__,
                self.id
            )
            context = {"field": self, "member": member}
            code = compile(self.field_initialization, label, "exec")
            exec code in context

        return member

    def _init_member(self, member):

        member.field_id = self.id
        member.required = self.is_required_field

        if self.__class__.get_member("field_default") is not None:
            member.default = self.field_default

        if self.__class__.get_member("field_enumeration") is not None:
            member.enumeration = self.field_enumeration or None

        member.edit_control = self.field_edit_control
        member.custom_translation_key = \
            "woost.extensions.forms.fields.field_translation"


class FieldSet(Field):

    visible_from_root = True
    member_type = schema.Schema
    members_order = [
        "base_field_set",
        "derived_field_sets",
        "fields"
    ]

    base_field_set = schema.Reference(
        type = "woost.extensions.forms.fields.FieldSet",
        bidirectional = True,
        member_group = "field_structure",
        listed_by_default = False
    )

    derived_field_sets = schema.Collection(
        items = "woost.extensions.forms.fields.FieldSet",
        bidirectional = True,
        editable = schema.NOT_EDITABLE,
        member_group = "field_structure",
        listed_by_default = False
    )

    fields = schema.Collection(
        items = "woost.extensions.forms.fields.Field",
        bidirectional = True,
        member_group = "field_structure",
        listed_by_default = False
    )

    @classmethod
    def create_field_default_member(cls):
        pass

    @classmethod
    def create_field_enumeration_member(cls):
        pass

    def generate_members(self):
        for field in self.fields:
            for member in field.generate_members():
                if not member.member_group:
                    member.member_group = str(self.id)
                else:
                    member.member_group = str(self.id) + "." + member.member_group
                yield member

    def _init_member(self, member):

        Field._init_member(self, member)

        if self.base_field_set:
            member.inherit(self.base_field_set.create_member())

        for child_member in self.generate_members():
            member.add_member(child_member, append = True)

        @extend(member)
        def translate_group(member, group):
            try:
                field_set_id = int(group.split(".")[-1])
            except:
                return call_base(group)
            else:
                return translations(FieldSet.require_instance(field_set_id))

    def create_form_model(self):

        # Create the user defined schema
        form_model = self.create_member()

        # Add the "submit date" member
        form_model.add_member(FormSubmitDateMember("submit_date"))

        return form_model


class FormSubmitDateMember(schema.DateTime):
    pass


class CollectionField(Field):

    visible_from_root = False

    members_order = [
        "items",
        "min",
        "max"
    ]

    member_type = schema.Collection

    field_edit_controls = [
        "cocktail.html.CollectionEditor",
        "cocktail.html.CheckList"
    ]

    items = schema.Reference(
        type = "woost.extensions.forms.fields.Field",
        bidirectional = True,
        integral = True,
        required = True,
        listed_by_default = False,
        member_group = "field_properties"
    )

    min = schema.Integer(
        min = 0,
        listed_by_default = False,
        member_group = "field_properties"
    )

    max = schema.Integer(
        min = min,
        listed_by_default = False,
        member_group = "field_properties"
    )

    @classmethod
    def create_field_default_member(cls):
        pass

    @classmethod
    def create_field_enumeration_member(cls):
        pass

    def _init_member(self, member):
        Field._init_member(self, member)
        member.items = self.items.create_member()
        member.min = self.min
        member.max = self.max


class BooleanField(Field):

    visible_from_root = False
    member_type = schema.Boolean

    field_edit_controls = [
        "cocktail.html.CheckBox",
        "cocktail.html.RadioSelector"
    ]


class TextField(Field):

    visible_from_root = False
    member_type = schema.String

    field_edit_controls = [
        "cocktail.html.TextBox",
        "cocktail.html.TextArea"
    ]

    members_order = [
        "format",
        "min",
        "max"
    ]

    format = schema.String(
        member_group = "field_properties",
        listed_by_default = False
    )

    min = schema.Integer(
        min = 0,
        member_group = "field_properties",
        listed_by_default = False
    )

    max = schema.Integer(
        min = min,
        member_group = "field_properties",
        listed_by_default = False
    )

    def _init_member(self, member):
        Field._init_member(self, member)
        member.format = self.format
        member.min = self.min
        member.max = self.max


class OptionsFieldOption(Item):

    visible_from_root = False
    show_element_in_listing = False

    members_order = [
        "field",
        "title",
        "enabled"
    ]

    field = schema.Reference(
        type = "woost.extensions.forms.fields.OptionsField",
        bidirectional = True,
        required = True,
        listed_by_default = False
    )

    title = schema.String(
        required = True,
        spellcheck = True,
        descriptive = True,
        translated = True
    )

    enabled = schema.Boolean(
        required = True,
        default = True
    )


class OptionsField(Field):

    visible_from_root = False
    member_type = schema.Reference

    field_edit_controls = [
        "cocktail.html.DropdownSelector",
        "cocktail.html.RadioSelector"
    ]

    options = schema.Collection(
        items = "woost.extensions.forms.fields.OptionsFieldOption",
        bidirectional = True,
        integral = True,
        min = 1,
        member_group = "field_properties"
    )

    @classmethod
    def create_field_default_member(cls):
        default_member = Field.create_field_default_member.im_func(cls)
        default_member.type = OptionsFieldOption
        default_member.enumeration = cls.options
        return default_member

    @classmethod
    def create_field_enumeration_member(cls):
        pass

    def _init_member(self, member):
        Field._init_member(self, member)
        member.type = OptionsFieldOption
        member.default_order = None
        member.enumeration = lambda ctx: [
            option
            for option in self.options
            if option.enabled
        ]


class EmailAddressField(Field):
    visible_from_root = False
    member_type = schema.EmailAddress


class PhoneNumberField(Field):
    visible_from_root = False
    member_type = schema.PhoneNumber


class HTMLField(TextField):
    visible_from_root = False
    member_type = schema.HTML
    field_edit_controls = None


class NumericField(Field):

    instantiable = False
    visible_from_root = False

    members_order = [
        "min",
        "max"
    ]

    @classmethod
    def add_generic_members(cls):
        Field.add_generic_members.im_func(cls)
        if cls.get_member("min") is None:
            min_member = cls.member_type(
                "min",
                listed_by_default = False
            )
            max_member = cls.member_type("max",
                min = min_member,
                listed_by_default = False
            )
            cls.add_member(min_member)
            cls.add_member(max_member)

    def _init_member(self, member):
        Field._init_member(self, member)
        member.min = self.min
        member.max = self.max


class IntegerField(NumericField):
    visible_from_root = False
    member_type = schema.Integer


class DecimalField(NumericField):
    visible_from_root = False
    member_type = schema.Decimal


class DateField(Field):

    visible_from_root = False
    member_type = schema.Date

    field_edit_controls = [
        "cocktail.html.DatePicker",
        "cocktail.html.CompoundDateSelector"
    ]


class TimeField(Field):
    visible_from_root = False
    member_type = schema.Time


class DateTimeField(Field):
    visible_from_root = False
    member_type = schema.DateTime

