#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from io import BytesIO
from warnings import warn
from collections import Sequence, Mapping, Set, defaultdict, Counter
from datetime import date, time, datetime
from contextlib import contextmanager
from itertools import zip_longest
import sys
import base64
import json
import argparse
import enum
from decimal import Decimal
from cocktail.typemapping import TypeMapping
from cocktail.styled import styled, ProgressBar
from cocktail.pkgutils import get_full_name, resolve
from cocktail.modeling import (
    ListWrapper,
    SetWrapper,
    DictWrapper,
    GenericMethod,
    GenericClassMethod,
    frozen
)
from cocktail import schema
from cocktail.persistence import datastore, transaction
from woost.models import (
    Item,
    File,
    User,
    Slot,
    Template,
    Controller,
    Publishable,
    Document,
    Block,
    changeset_context
)


@enum.unique
class ExportMode(enum.Enum):
    ignore = 1
    export = 2
    expand = 3


@enum.unique
class UnknownMemberPolicy(enum.Enum):
    ignore = 1
    warn = 2
    report = 3
    fail = 4


@enum.unique
class MissingObjectPolicy(enum.Enum):
    ignore = 1
    warn = 2
    report = 3
    fail = 4
    create = 5


@GenericMethod
def get_object_ref(obj):

    ref = {
        "@class": get_full_name(obj.__class__)
    }

    for member in obj.__class__.iter_members():
        if (
            member is not Item.id
            and member.unique
            and not member.translated
            and isinstance(member, (schema.String, schema.Integer))
        ):
            value = obj.get(member)
            if value is not None and value != "":
                ref[member.name] = value

    return ref

@GenericClassMethod
def resolve_object_ref(cls, ref):

    for key, value in ref.items():
        if value is not None and value != "" and not key.startswith("@"):
            member = cls.get_member(key)
            if (
                member.unique
                and not member.translated
                and isinstance(member, (schema.String, schema.Integer))
            ):
                obj = cls.get_instance(**{key: value})
                if obj is not None:
                    return obj

    return None

@GenericClassMethod
def create_object_from_ref(cls, ref):
    obj = cls()

    for key, value in ref.items():
        if not key.startswith("@"):
            member = obj.__class__.get_member(key)
            if (
                member.unique
                and not member.translated
                and isinstance(member, (schema.String, schema.Integer))
            ):
                obj.set(key, value)

    obj.insert()
    return obj


class ObjectExporter(object):

    verbose = False
    _depth = 0
    language_subset = None
    date_format = "%Y-%m-%d"
    time_format = "%H:%M:%S"
    datetime_format = date_format + " " + time_format
    json_encoder_defaults = {"check_circular": False}

    default_model_export_modes = {
        File: ExportMode.expand
    }

    default_model_colors = {
        Publishable: "slate_blue",
        File: "pink",
        Item: "brown",
        Block: "cyan"
    }

    default_model_styles = {
        Item: "normal",
        Document: "bold"
    }

    default_member_export_modes = {
        Item.id: ExportMode.ignore,
        Item.translations: ExportMode.ignore,
        Item.last_update_time: ExportMode.ignore,
        Item.last_translation_update_time: ExportMode.ignore,
        Item.changes: ExportMode.ignore,
        Controller.published_items: ExportMode.ignore,
        Template.documents: ExportMode.ignore,
        Document.children: ExportMode.expand
    }

    def __init__(self, verbose = False):
        self.__member_export_modes = self.default_member_export_modes.copy()
        self.__model_export_modes = TypeMapping(self.default_model_export_modes)
        self.__model_colors = TypeMapping(self.default_model_colors)
        self.__model_styles = TypeMapping(self.default_model_styles)
        self.__exported_data = {}
        self.verbose = verbose
        self.json_encoder_defaults = self.json_encoder_defaults.copy()

    @contextmanager
    def _description(self, message, visible = True):

        if self.verbose and message and visible:
            if self.verbose:
                print(" " * self._depth * 2 + message)

            self._depth += 1
            try:
                yield None
            finally:
                self._depth -= 1
        else:
            yield None

    def dump(self, dest, **kwargs):

        options = self.json_encoder_defaults.copy()
        options.update(kwargs)

        if isinstance(dest, str):
            with open(dest, "w") as file:
                json.dump(list(self.__exported_data.values()), file, **options)
        else:
            json.dump(list(self.__exported_data.values()), dest, **options)

    def dumps(self, **kwargs):
        options = self.json_encoder_defaults.copy()
        options.update(kwargs)
        return json.dumps(list(self.__exported_data.values()), **options)

    def add_all(self, objects):
        for obj in objects:
            self.add(obj)

    def add(self, obj):

        if isinstance(obj, ExportNode):
            node = obj
            obj = node.value
        else:
            node = ExportNode(self, obj)
            node._export_mode = ExportMode.expand

        if obj in self.__exported_data:
            return False

        with self._description(
            styled(
                repr(obj),
                self.__model_colors[obj.__class__],
                style = self.__model_styles[obj.__class__]
            )
            if self.verbose
            else None
        ):
            self.__exported_data[obj] = data = {
                "@class": get_full_name(node.value.__class__)
            }
            self._export_object_data(node, data)

        return True

    def _export_object_data(self, node, data):

        obj = node.value

        for member in obj.__class__.iter_members():
            if member.translated:
                translated_values = {}
                for lang in obj.translations:
                    member_node = ExportNode(
                        self,
                        obj.get(member, lang),
                        parent = node,
                        member = member,
                        language = lang
                    )
                    if member_node.export_mode != ExportMode.ignore:
                        translated_values[lang] = self._export_value(
                            member_node,
                            expand_object = (member_node.export_mode == ExportMode.expand)
                        )
                if translated_values:
                    data[member.name] = translated_values
            else:
                member_node = ExportNode(
                    self,
                    obj.get(member),
                    parent = node,
                    member = member
                )
                if member_node.export_mode != ExportMode.ignore:
                    data[member.name] = self._export_value(
                        member_node,
                        expand_object =
                            member_node.export_mode == ExportMode.expand
                    )

        # Encode file contents
        if isinstance(obj, File):
            buffer = BytesIO()
            with open(obj.file_path, "rb") as file:
                base64.encode(file, buffer)
            buffer.seek(0)
            data["@file_data"] = buffer.getvalue().decode("ascii")

    def _get_object_ref(self, node):
        return get_object_ref(node.value)

    def _export_value(self, node, expand_object = False):

        value = node.value

        if value is not None:
            if isinstance(value, type):
                value = get_full_name(value)
            elif isinstance(value, schema.SchemaObject):
                value = self._get_object_ref(node)
                if expand_object:
                    with self._description(
                        node.member and node.member.name,
                        visible = node.member
                    ):
                        self.add(node)
            elif isinstance(node.member, schema.Tuple):
                value = [
                    self._export_value(
                        ExportNode(
                            self,
                            item,
                            parent = node,
                            member = item_member,
                            index = index
                        )
                    )
                    for index, (item, item_member) in enumerate(
                        zip_longest(value, node.member.items)
                    )
                ]
            elif (
                not isinstance(value, str)
                and not isinstance(value, (Mapping, DictWrapper))
                and isinstance(
                    value,
                    (
                        Sequence,
                        Set,
                        ListWrapper,
                        SetWrapper
                    )
                )
            ):
                items = None

                if node.member and node.member.items:
                    item_nodes = []
                    has_expansion = False

                    for index, item in enumerate(value):
                        item_node = ExportNode(
                            self,
                            item,
                            parent = node,
                            member = node.member.items,
                            language = node.language,
                            index = index
                        )
                        if item_node.export_mode != ExportMode.ignore:
                            item_nodes.append(item_node)
                            if item_node.export_mode == ExportMode.expand:
                                has_expansion = True

                    if item_nodes:
                        with self._description(
                            (
                                node.member.name
                                + styled(" (%s)" % len(item_nodes), "dark_gray")
                            ),
                            visible = has_expansion
                        ):
                            items = [
                                self._export_value(
                                    item_node,
                                    expand_object =
                                        (item_node.export_mode == ExportMode.expand)
                                )
                                for item_node in item_nodes
                            ]
                        value = items

                value = list(value) if items is None else items

            elif isinstance(value, DictWrapper):
                items = {}
                for k, v in value.items():
                    v_node = ExportNode(
                        self,
                        v,
                        parent = node,
                        member = node.member.values,
                        language = node.language,
                        index = k
                    )
                    if v_node.export_mode != ExportMode.ignore:
                        k_node = ExportNode(
                            self,
                            k,
                            parent = node,
                            member = node.member.keys,
                            language = node.language
                        )
                        k = self._export_value(k_node)
                        v = self._export_value(
                            v_node,
                            expand_object =
                                (v_node.export_mode == ExportMode.expand)
                        )
                        items[k] = v
                value = items
            elif isinstance(value, Decimal):
                return str(value)
            elif isinstance(value, datetime):
                return value.strftime(self.datetime_format)
            elif isinstance(value, date):
                return value.strftime(self.date_format)
            elif isinstance(value, time):
                return value.strftime(self.time_format)

        return value

    def get_node_export_mode(self, node):

        # Limit exported languages
        if (
            node.language
            and self.language_subset is not None
            and node.language not in self.language_subset
        ):
            return ExportMode.ignore

        if node.member:

            # Custom per member rules
            mode = self.get_member_export_mode(node.member)
            if mode:
                return mode

            # Exclude calculated fields
            if node.member.expression is not None:
                return ExportMode.ignore

            # Ignore anonymous relations
            if (
                isinstance(node.member, schema.RelationMember)
                and node.member.anonymous
            ):
                return ExportMode.ignore

        # Custom per model rules
        if isinstance(node.value, schema.SchemaObject):
            mode = self.get_model_export_mode(node.value.__class__)
            if mode:
                return mode

        # Standard member rules
        if node.member:

            # Always expand slots
            if isinstance(node.member, Slot):
                return ExportMode.expand

            # Always expand integral relations
            elif (
                isinstance(node.member, schema.RelationMember)
                and node.member.integral
            ):
                return ExportMode.expand

            # If the member is the item descriptor for a collection, apply the
            # behavior set by the collection
            if (
                node.parent
                and node.parent.member
                and isinstance(node.parent.member, schema.Collection)
                and node.parent.export_mode == ExportMode.expand
            ):
                return ExportMode.expand

        # If no other rule applies, assume a shallow copy
        return ExportMode.export

    def set_member_export_mode(self, member, mode):
        self.__member_export_modes[member] = mode

    def get_member_export_mode(self, member):
        return self.__member_export_modes.get(member)

    def set_model_export_mode(self, model, mode):
        self.__model_export_modes[model] = mode

    def get_model_export_mode(self, model):
        return self.__model_export_modes.get(model)

    def expand(self, *args):
        """Convenience method to set the export mode for several elements to
        `ExportMode.expand`.
        """
        self._set_mode(args, ExportMode.expand)

    def export(self, *args):
        """Convenience method to set the export mode for several elements to
        `ExportMode.export`.
        """
        self._set_mode(args, ExportMode.export)

    def ignore(self, *args):
        """Convenience method to set the export mode for several elements to
        `ExportMode.ignore`.
        """
        self._set_mode(args, ExportMode.ignore)

    def export_only(self, model, exported_members):
        """Export only the given members of a model, ignore all others."""

        exported_members = set(
            (
                model.get_member(member)
                if isinstance(member, str)
                else member
            )
            for member in exported_members
        )

        for member in model.iter_members():

            if member is Item.id or member is Item.global_id:
                continue

            if member in exported_members:
                mode = ExportMode.export
            else:
                mode = ExportMode.ignore
            self.set_member_export_mode(member, mode)

    def expand_only(self, model, expanded_members):
        """Expand only the given members of a model, ignore all others."""

        expanded_members = set(
            (
                model.get_member(member)
                if isinstance(member, str)
                else member
            )
            for member in expanded_members
        )

        for member in model.iter_members():

            if member is Item.id or member is Item.global_id:
                continue

            if member in expanded_members:
                mode = ExportMode.expand
            else:
                mode = ExportMode.ignore
            self.set_member_export_mode(member, mode)

    def _set_mode(self, lst, mode):
        for obj in lst:
            if isinstance(obj, schema.SchemaClass):
                self.set_model_export_mode(obj, mode)
            elif isinstance(obj, schema.Member):
                self.set_member_export_mode(obj, mode)
            else:
                raise ValueError(
                    "Expected a model or a member, got %r instead"
                    % obj
                )

    @classmethod
    def expand_by_default(cls, *args):
        """Convenience method to set the default export mode for several
        elements to `ExportMode.expand`.
        """
        cls._set_default_mode(args, ExportMode.expand)

    @classmethod
    def export_by_default(cls, *args):
        """Convenience method to set the default export mode for several
        elements to `ExportMode.export`.
        """
        cls._set_default_mode(args, ExportMode.export)

    @classmethod
    def ignore_by_default(cls, *args):
        """Convenience method to set the default export mode for several
        elements to `ExportMode.ignore`.
        """
        cls._set_default_mode(args, ExportMode.ignore)

    @classmethod
    def _set_default_mode(cls, lst, mode):
        for obj in lst:
            if isinstance(obj, schema.SchemaClass):
                cls.default_model_export_modes[obj] = mode
            elif isinstance(obj, schema.Member):
                cls.default_member_export_modes[obj] = mode
            else:
                raise ValueError(
                    "Expected a model or a member, got %r instead"
                    % obj
                )

    def run_cli(self, func):
        parser = self._cli_create_parser()
        args = parser.parse_args()
        self._cli_process_args(args)
        func()
        self.dump(args.file)

    def _cli_create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "file",
            nargs = "?",
            type = argparse.FileType("w"),
            default = sys.stdout
        )
        parser.add_argument(
            "--verbose", "-v",
            action = "store_true",
            default = self.verbose
        )
        parser.add_argument(
            "--pretty-print", "-p",
            action = "store_true",
            default = False
        )
        return parser

    def _cli_process_args(self, args):

        self.verbose = args.verbose

        if args.pretty_print:
            self.json_encoder_defaults["indent"] = 2
            self.json_encoder_defaults["sort_keys"] = True


class ExportNode(object):

    _export_mode = None

    def __init__(self,
        exporter,
        value,
        parent = None,
        member = None,
        language = None,
        index = None
    ):
        self._exporter = exporter
        self._value = value
        self._parent = parent
        self._member = member
        self._language = language
        self._index = index

    def __repr__(self):

        props = []

        desc = "%s(%r" % (self.__class__.__name__, self._value)

        if self._parent:
            desc += ", parent=%r" % self._parent

        if self._member:
            desc += ", member=%r" % self._member

        if self._language:
            desc += ", language=%r" % self._language

        if self._index:
            desc += ", index=%r" % self._index

        return desc + ")"

    @property
    def exporter(self):
        return self._exporter

    @property
    def value(self):
        return self._value

    @property
    def schema_object(self):

        node = self

        while node is not None:
            if isinstance(node._value, schema.SchemaObject):
                return node._value
            node = node._parent

        return None

    @property
    def parent(self):
        return self._parent

    @property
    def member(self):
        return self._member

    @property
    def language(self):
        return self._language

    @property
    def index(self):
        return self._index

    @property
    def export_mode(self):
        if self._export_mode is None:
            self._export_mode = self._exporter.get_node_export_mode(self)
        return self._export_mode


class ObjectImporter(object):

    verbose = False
    unknown_member_policy = UnknownMemberPolicy.fail
    missing_object_policy = MissingObjectPolicy.fail
    language_subset = None
    date_format = ObjectExporter.date_format
    time_format = ObjectExporter.time_format
    datetime_format = ObjectExporter.datetime_format

    def __init__(self,
        file = None,
        string = None,
        unknown_member_policy = UnknownMemberPolicy.fail,
        missing_object_policy = MissingObjectPolicy.fail,
        language_subset = None,
        date_format = ObjectExporter.date_format,
        time_format = ObjectExporter.time_format,
        datetime_format = ObjectExporter.datetime_format,
        verbose = False
    ):
        self.__qname_mapping = {}
        self.missing_references = Counter()
        self.missing_members = defaultdict(Counter)
        self.objects = []

        self.unknown_member_policy = unknown_member_policy
        self.missing_object_policy = missing_object_policy
        self.language_subset = language_subset
        self.date_format = date_format
        self.time_format = time_format
        self.datetime_format = datetime_format
        self.verbose = verbose

        if file is not None:
            self.load(file)

        if string is not None:
            self.loads(string)

    def load(self, file, encoding = "utf-8"):

        if isinstance(file, str):
            with open(file, "r") as file:
                string = file.read()
        else:
            string = file.read()

        return self.loads(string, encoding)

    def loads(self, string, encoding = "utf-8"):
        if isinstance(string, bytes):
            data = string.decode(encoding)
        data = json.loads(string)
        return self.load_objects(data)

    def load_objects(self, object_list):

        # Make a first pass to pregenerate all new objects
        if self.verbose:
            print("Resolving or creating %d objects" % len(object_list))
            bar = ProgressBar(len(object_list))
            bar.update()

        objects = []

        for object_data in object_list:
            obj = self.resolve_object_ref(
                object_data,
                missing_object_policy = MissingObjectPolicy.create
            )
            self.objects.append(obj)
            objects.append((
                obj,
                object_data
            ))
            if self.verbose:
                bar.update(1)

        if self.verbose:
            bar.finish()

        # And a second pass to load object state
        if self.verbose:
            print("Importing object state")
            bar = ProgressBar(len(objects))
            bar.update()

        for obj, object_data in objects:
            self.import_object_data(obj, object_data)
            if self.verbose:
                bar.update(1)

        if self.verbose:
            bar.finish()

        self.print_missing_references_report()
        self.print_missing_members_report()

    def print_missing_references_report(self):
        if self.missing_references:
            print("\nThe following references couldn't be resolved:\n")
            for ref, count in self.missing_references.most_common():
                print("  %s (%d)" % (ref, count))

    def print_missing_members_report(self):
        if self.missing_members:
            print("\nThe following members aren't defined:")
            for cls, keys in self.missing_members.items():
                print("\n  %s:" % cls.__name__)
                for key, count in keys.most_common():
                    print("  -%s (%d)" % (key, count))
            print()

    def import_object_data(self, obj, data):
        for key, value in data.items():
            try:
                self.import_object_key(obj, key, value)
            except Exception as e:
                if self.verbose:
                    sys.stderr.write(
                        styled(
                            "Error while parsing %s.%s = %r\n"
                            % (
                                obj.__class__.__name__,
                                key,
                                value
                            ),
                            "magenta"
                        )
                    )
                raise

    def import_object_key(self, obj, key, value):
        if isinstance(key, str):
            key = str(key)

        if key.startswith("@"):

            # Store file contents once the current transaction is comitted
            # successfully
            if key == "@file_data":

                datastore.unique_after_commit_hook(
                    "woost.models.objectio.store_file_contents",
                    _store_file_contents_after_commit
                )

                file_contents = datastore.get_transaction_value(
                    "woost.models.objectio.file_contents"
                )

                if file_contents is None:
                    file_contents = {}
                    datastore.set_transaction_value(
                        "woost.models.objectio.file_contents",
                        file_contents
                    )

                bdata = base64.decodestring(value)
                file_contents[obj.id] = bdata

            return

        member = obj.__class__.get_member(key)
        if member is None:
            self._handle_unknown_member(obj, key)
            return

        if member.translated:
            for lang, lang_value in value.items():
                if (
                    self.language_subset is None
                    or lang in self.language_subset
                ):
                    imported_value = self.import_object_value(
                        obj,
                        member,
                        lang_value,
                        lang
                    )
                    if imported_value is not ExportMode.ignore:
                        member.apply_imported_value(
                            obj,
                            imported_value,
                            lang
                        )
        else:
            imported_value = self.import_object_value(obj, member, value)
            if imported_value is not ExportMode.ignore:
                member.apply_imported_value(
                    obj,
                    imported_value
                )

    def _handle_unknown_member(self, obj, key):
        if self.unknown_member_policy == UnknownMemberPolicy.fail:
            raise ValueError(
                "The schema for %r doesn't define member %s"
                % (obj, key)
            )
        elif self.unknown_member_policy == UnknownMemberPolicy.warn:
            warn("The schema for %s doesn't define member %s" % (obj, key))
        elif self.unknown_member_policy == UnknownMemberPolicy.report:
            self.missing_members[obj.__class__][key] += 1
        elif self.unknown_member_policy == UnknownMemberPolicy.ignore:
            pass
        else:
            raise ValueError(
                "The schema for %r doesn't define member %s, and the "
                "object importer has set an invalid policy for "
                "dealing with unknown members (%r); it should be one "
                "of the values provided by the UnknownMemberPolicy "
                "enumeration"
                % (obj, key, self.unknown_member_policy)
            )

    def import_object_value(self, obj, member, value, language = None):
        if value is None:
            return None
        elif (
            not isinstance(value, str)
            and isinstance(value, (
                Sequence,
                Set,
                ListWrapper,
                SetWrapper
            ))
        ):
            if isinstance(member, schema.Tuple):
                sequence_type = tuple
                imported_items = (
                    self.import_object_value(
                        obj,
                        item_member,
                        item
                    )
                    for item, item_member in zip_longest(value, member.items)
                )
            else:
                sequence_type = member.default_type
                imported_items = (
                    self.import_object_value(
                        obj,
                        member.items,
                        item
                    )
                    for item in value
                )

            return sequence_type(
                imported_item
                for imported_item in imported_items
                if imported_item is not ExportMode.ignore
            )
        elif isinstance(member, schema.Mapping) and isinstance(value, dict):
            return dict(
                (
                    self.import_object_value(obj, member.keys, k),
                    self.import_object_value(obj, member.values, v)
                )
                for k, v in value.items()
            )
        elif isinstance(member, schema.Reference):
            if member.class_family:
                return resolve(value)
            else:
                return self.resolve_object_ref(value)
        elif isinstance(member, schema.Decimal):
            return Decimal(value)
        elif isinstance(member, schema.DateTime):
            return datetime.strptime(value, self.datetime_format)
        elif isinstance(member, schema.Date):
            return datetime.strptime(value, self.date_format).date()
        elif isinstance(member, schema.Time):
            return datetime.strptime(value, self.time_format).time()

        return value

    def resolve_object_ref(self, ref, missing_object_policy = None):

        cls = resolve(ref["@class"])
        obj = resolve_object_ref(cls, ref)

        if obj is None:
            obj = self._handle_missing_object(
                cls,
                ref,
                missing_object_policy or self.missing_object_policy
            )

        return obj

    def _handle_missing_object(self, cls, ref, policy):

        if policy == MissingObjectPolicy.create:

            if cls is None:
                raise ValueError(
                    "Can't create missing object %r; no class specified"
                    % ref
                )

            return create_object_from_ref(cls, ref)

        elif policy == MissingObjectPolicy.warn:
            warn("Can't find an object matching the reference %r" % ref)
            return ExportMode.ignore

        elif policy == MissingObjectPolicy.report:
            self.missing_references[frozen(ref)] += 1
            return ExportMode.ignore

        elif policy == MissingObjectPolicy.fail:
            raise ValueError(
                "Can't find an object matching the reference %r" % ref
            )

        elif policy == MissingObjectPolicy.ignore:
            return ExportMode.ignore

        else:
            raise ValueError(
                "Can't find an object matching the reference %r, and the "
                "object importer has set an invalid policy for dealing "
                "with missing objects (%r); expected one of the values of "
                "the MissingObjectPolicy enumeration"
                % (ref, policy)
            )

    def map_qname(self, original, replacement):
        self.__qname_mapping[original] = replacement

    def run_cli(self):
        parser = self._cli_create_parser()
        args = parser.parse_args()
        self._cli_process_args(args)

        @transaction
        def load_files():

            if args.author:
                author = User.require_instance(email = args.author)
            else:
                author = None

            with changeset_context(author):
                for file in args.files:
                    self.load(file)

    def _cli_create_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "files",
            nargs = "+",
            type = argparse.FileType("r"),
            default = sys.stdout
        )
        parser.add_argument(
            "--verbose", "-v",
            action = "store_true",
            default = self.verbose
        )
        parser.add_argument(
            "--author"
        )
        parser.add_argument(
            "--errors", "-e"
        )
        parser.add_argument(
            "--missing-objects",
            choices = [
                choice
                for choice in MissingObjectPolicy.__members__
                if choice != "create"
            ]
        )
        parser.add_argument(
            "--unknown-members",
            choices = list(UnknownMemberPolicy.__members__.keys())
        )
        return parser

    def _cli_process_args(self, args):

        self.verbose = args.verbose

        missing_objects_key = args.missing_objects or args.errors
        if missing_objects_key:
            self.missing_object_policy = getattr(
                MissingObjectPolicy,
                missing_objects_key
            )

        unknown_members_key = args.unknown_members or args.errors
        if unknown_members_key:
            self.unknown_member_policy = getattr(
                UnknownMemberPolicy,
                unknown_members_key
            )


def _store_file_contents_after_commit(successful):

    if not successful:
        return

    file_contents = datastore.get_transaction_value(
        "woost.models.objectio.file_contents"
    )

    if file_contents is not None:

        for id, data in file_contents.items():
            file = File.get_instance(id)
            if file is None:
                continue

            with open(file.file_path, "wb") as f:
                f.write(data)


def _apply_imported_value(member, obj, value, language = None):
    obj.set(member, value, language = language)

schema.Member.apply_imported_value = _apply_imported_value

