#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Pepe Osca <pepe.osca@whads.com>
"""
from ZODB.POSException import ConflictError
from cocktail.events import Event
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import Item, User

MAX_COMMIT_ATTEMPTS = 5


class IdentityProvider(Item):

    instantiable = False
    visible_from_root = False

    user_created = Event(
        """An event triggered when a new `user <woost.models.User>` is
        created by the provider.

        .. attribute:: user

            The `user <woost.models.User>` created by the provider.

        .. attribute:: data

            The profile data obtained by the provider (a dictionary with
            provider specific keys).
        """
    )

    members_order = [
        "title",
        "debug_mode"
    ]

    title = schema.String(
        descriptive = True
    )

    debug_mode = schema.Boolean(
        required = True,
        default = False
    )

    provider_name = None
    user_data_id_field = "id"
    user_data_email_field = "email"
    user_identifier = None

    def get_auth_url(self, target_url = None):
        raise ValueError(
            "%s doesn't implement the get_auth_url() method"
            % self
        )

    def process_user_data(self, data):

        conflict_error = None

        for i in range(MAX_COMMIT_ATTEMPTS):
            try:
                user = self.user_from_data(data)
                if not user.is_inserted:
                    user.insert()
                    datastore.commit()
            except ConflictError, error:
                conflict_error = error
                datastore.sync()
            else:
                conflict_error = None
                break

        if conflict_error:
            raise conflict_error

        return user

    def user_from_data(self, data):

        id = data[self.user_data_id_field]
        email = data.get(self.user_data_email_field)
        user = (
            User.get_instance(**{self.user_identifier: id})
            or (
                email
                and User.get_instance(email = email)
            )
        )

        if user is None:
            user = self.create_user(data)

        return user

    def create_user(self, data):
        # TODO: store additional user data (need to add the extra fields in
        # the User model)
        user = User()
        setattr(user, self.user_identifier, data[self.user_data_id_field])
        user.email = data.get(self.user_data_email_field)
        self.user_created(user = user, data = data)
        return user
