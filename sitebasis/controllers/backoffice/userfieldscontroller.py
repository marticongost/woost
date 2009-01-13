#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from sitebasis.controllers.backoffice.itemfieldscontroller import \
    ItemFieldsController


class UserFieldsController(ItemFieldsController):

    @cached_getter
    def form_adapter(self):

        form_adapter = ItemFieldsController.form_adapter(self)
        
        form_adapter.exclude([
            "change_password",
            "password_confirmation"
        ])

        form_adapter.copy("password",
            export_condition = False,
            import_condition =
                lambda context: context.get("change_password")
        )

        return form_adapter

    @cached_getter
    def form_schema(self):
        
        form_schema = ItemFieldsController.form_schema(self)
        form_schema.members_order = [
            "email",
            "change_password",
            "password",
            "password_confirmation"
        ]
        
        form_schema.add_member(schema.Boolean(
            name = "change_password",
            required = True,
            default = False
        ))
                
        form_schema["password"].exclusive = form_schema["change_password"]

        form_schema.add_member(schema.String(
            name = "password_confirmation",
            exclusive = form_schema["change_password"],
            edit_control = "cocktail.html.PasswordBox"
        ))
        
        @form_schema.add_validation
        def validate_password_confirmation(form_schema, value, ctx):

            if ctx.get_value("change_password"):
                password = ctx.get_value("password")               
                password_confirmation = ctx.get_value("password_confirmation")

                if password and password_confirmation \
                and password != password_confirmation:
                    yield PasswordConfirmationError(
                            form_schema, value, ctx)

        return form_schema

    @cached_getter
    def differences(self):
        differences = ItemFieldsController.differences(self)

        # Discard differences in the password field
        differences.discard((self.edited_content_type.password, None))

        return differences


class PasswordConfirmationError(schema.exceptions.ValidationError):
    """A validation error produced when the password and its confirmation field
    are given different values."""

