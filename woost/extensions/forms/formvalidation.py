#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.schema.exceptions import ValidationError
from woost.models import Item


class FormValidation(Item):

    members_order = [
        "field",
        "title",
        "code",
        "message"
    ]

    field = schema.Reference(
        type = "woost.extensions.forms.fields.Field",
        bidirectional = True,
        required = True,
        editable = schema.NOT_EDITABLE
    )

    title = schema.String(
        required = True,
        translated = True,
        descriptive = True
    )

    code = schema.CodeBlock(
        language = "python",
        required = True
    )

    message = schema.String(
        required = True,
        translated = True
    )

    def add_to_member(self, member):

        def validation(context):
            evaluation = {
                "form_validation": self,
                "member": member,
                "context": context,
                "message": self.message,
                "failed": False
            }
            self.__class__.code.execute(self, evaluation)
            if evaluation["failed"]:
                yield FormValidationError(evaluation)

        member.add_validation(validation)


class FormValidationError(ValidationError):

    def __init__(self, evaluation):
        ValidationError.__init__(self, evaluation["context"])
        self.evaluation = evaluation

