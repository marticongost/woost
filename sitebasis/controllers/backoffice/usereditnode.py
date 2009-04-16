#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from sitebasis.controllers.backoffice.editstack import EditNode


class UserEditNode(EditNode):

    @cached_getter
    def form_adapter(self):

        form_adapter = EditNode.form_adapter(self)
        
        form_adapter.exclude([
            "password_confirmation"
        ])
        
        if self.item.is_inserted:
            form_adapter.exclude([
                "change_password"
            ])

            form_adapter.copy("password",
                export_condition = False,
                import_condition =
                    lambda context: context.get("change_password")
            )

        return form_adapter

    @cached_getter
    def form_schema(self):
        
        form_schema = EditNode.form_schema(self)
        form_schema.members_order = [
            "email",
            "change_password",
            "password",
            "password_confirmation"
        ] if self.item.is_inserted else [
            "email",
            "password",
            "password_confirmation"
        ]

        form_schema.add_member(schema.String(
            name = "password_confirmation",            
            edit_control = "cocktail.html.PasswordBox"
        ))
        
        if self.item.is_inserted:
            form_schema.add_member(schema.Boolean(
                name = "change_password",
                required = True,
                default = False
            ))
                
            form_schema["password"].exclusive = form_schema["change_password"]

            form_schema["password_confirmation"].exclusive = form_schema["change_password"]
        
        @form_schema.add_validation
        def validate_password_confirmation(form_schema, value, ctx):

            password = ctx.get_value("password")               
            password_confirmation = ctx.get_value("password_confirmation")

            if password and password_confirmation \
            and password != password_confirmation:
                yield PasswordConfirmationError(
                        form_schema, value, ctx)

        return form_schema

    def iter_changes(self):
        
        # Discard differences in the password field
        for member, language in EditNode.iter_changes(self):
            if member.name not in (
                "change_password", "password", "password_confirmation"
            ):
                yield (member, language)


class PasswordConfirmationError(schema.exceptions.ValidationError):
    """A validation error produced when the password and its confirmation field
    are given different values."""

