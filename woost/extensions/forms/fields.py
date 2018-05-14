#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import event_handler
from cocktail.modeling import extend, call_base
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.exceptions import ValidationError
from cocktail.html import templates
from cocktail.html.uigeneration import display_factory
from woost.models import Item, File, AccessLevel
from woost.models.publishableobject import get_category_from_mime_type

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

    def _edit_control_suggestion_list(ui_generation, obj, member, value, **context):
        field = context.get("persistent_object")
        controls = field and field.field_edit_controls
        if controls:
            control = templates.new("cocktail.html.SuggestionList")
            control.suggestions_selector.empty_option_displayed = True
            control.suggestions = controls
        else:
            control = templates.new("cocktail.html.TextBox")
        return control

    field_edit_control = schema.String(
        translatable_values = True,
        edit_control = _edit_control_suggestion_list,
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
        related_key = "derived_field_sets",
        member_group = "field_structure",
        listed_by_default = False
    )

    derived_field_sets = schema.Collection(
        items = "woost.extensions.forms.fields.FieldSet",
        bidirectional = True,
        related_key = "base_field_set",
        editable = schema.NOT_EDITABLE,
        member_group = "field_structure",
        listed_by_default = False
    )

    fields = schema.Collection(
        items = "woost.extensions.forms.fields.Field",
        bidirectional = True,
        integral = True,
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
        def translate_group(member, group, suffix = None):
            try:
                field_set_id = int(group.split(".")[-1])
            except:
                return call_base(group, suffix = suffix)
            else:
                fieldset = FieldSet.require_instance(field_set_id)
                if suffix == ".explanation":
                    return fieldset.explanation
                else:
                    return fieldset.visible_title or translations(fieldset)

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

    field_edit_controls = [
        "cocktail.html.NumberBox",
        "cocktail.html.DropdownSelector",
        "cocktail.html.RadioSelector"
    ]

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
                listed_by_default = False,
                member_group = "field_properties",
                custom_translation_key =
                    "woost.extensions.forms.fields.NumericField.members.min"
            )
            max_member = cls.member_type("max",
                min = min_member,
                listed_by_default = False,
                member_group = "field_properties",
                custom_translation_key =
                    "woost.extensions.forms.fields.NumericField.members.max"
            )
            cls.add_member(min_member, append = True)
            cls.add_member(max_member, append = True)

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


class UploadField(Field):

    visible_from_root = False
    member_type = schema.Reference

    members_order = [
        "max_file_size",
        "accepted_file_types",
        "file_access_level"
    ]

    max_file_size = schema.Integer(
        member_group = "field_properties",
        min = 1
    )

    accepted_file_types = schema.Collection(
        items = schema.String(
            enumeration = [
                "document",
                "image",
                "audio",
                "video",
                "package"
            ],
            translate_value = (
                lambda value, language = None, **kwargs:
                    translations(
                        UploadField.accepted_file_types,
                        suffix = ".items.values." + value,
                        language = language,
                        **kwargs
                    )
                    if value else ""
            )
        ),
        min = 1,
        edit_control = "cocktail.html.CheckList",
        member_group = "field_properties"
    )

    file_access_level = schema.Reference(
        type = AccessLevel,
        related_end = schema.Collection(),
        default = schema.DynamicDefault(lambda:
            AccessLevel.get_instance(qname = "woost.editor_access_level")
        ),
        member_group = "field_properties"
    )

    def _init_member(self, member):

        Field._init_member(self, member)

        member.type = File
        member.display = display_factory(
            "woost.views.PublishableLink",
            host = "!",
            content_check = 0
        )
        member.upload_options = {
            "max_size": "%dMB" % self.max_file_size,
            "accepted_file_types": self.accepted_file_types,
            "validations": [_validate_accepted_file_types]
        }

        def _init_uploaded_file(file):
            file.access_level = self.file_access_level
            file.insert()

        member.init_uploaded_file = _init_uploaded_file

    @classmethod
    def create_field_default_member(cls):
        return None

    @classmethod
    def create_field_enumeration_member(cls):
        return None


def _validate_accepted_file_types(context):

    if context.value:
        mime_type = context.get_value("mime_type")
        category = mime_type and get_category_from_mime_type(mime_type)

        if (
            not category
            or category not in context.member.accepted_file_types
        ):
            yield FileTypeNotAcceptedError(context)


class FileTypeNotAcceptedError(ValidationError):

    def __str__(self):
        return "%s (not an accepted file type)" % ValidationError.__str__(self)

