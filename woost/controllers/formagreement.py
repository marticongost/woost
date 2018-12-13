#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.exceptions import ValidationError
from woost import app
from woost.models import Publishable

translations.load_bundle("woost.controllers.formagreement")

default_document = object()

def requires_agreement(target = None, **kwargs):

    # Form subclass
    if isinstance(target, type):

        def handler(e):
            add_agreement(e.source, **kwargs)

        target.declared.append(handler)
        return target

    # Form instance
    elif target:
        add_agreement(target, **kwargs)
        return target

    # No form: return a decorator expecting a subclass of Form
    else:
        def decorator(form_class, **further_kwargs):
            merged_kwargs = kwargs.copy()
            merged_kwargs.update(further_kwargs)
            requires_agreement(form_class, **merged_kwargs)
            return form_class

        return decorator

def add_agreement(form, name = "terms", document = default_document):

    if document is default_document:
        document = "%s.%s" % (app.package, name)

    if isinstance(document, basestring):
        document = Publishable.require_instance(qname = document)

    member = FormAgreement(
        name = name,
        agreement_document = document
    )

    form.schema.add_member(member)

    if form.schema.groups_order:
        if "form_agreement" not in form.schema.groups_order:
            if not isinstance(form.schema.groups_order, list):
                form.schema.groups_order = list(form.schema.groups_order)
            form.schema.groups_order.append("form_agreement")

    form.adapter.exclude(name)
    return member


class FormAgreement(schema.Boolean):

    agreement_document = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", True)
        kwargs.setdefault("member_group", "form_agreement")
        schema.Boolean.__init__(self, *args, **kwargs)

    def _default_validation(self, context):
        if not context.value:
            yield ConsentNotGivenError(context)

    def parse_request_value(self, reader, value):
        return schema.Boolean.parse_request_value(self, reader, value) or False


class ConsentNotGivenError(ValidationError):
    """A validation error produced by forms that enforce an agreement to a
    terms and conditions document when the user attempts to submit the form
    without acknowledging the agreement.
    """

