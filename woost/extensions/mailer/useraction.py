#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from woost.models import Document
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.mailer.sendemailpermission import \
    SendEmailPermission


class SendEmailAction(UserAction):
    included = frozenset(["toolbar_extra", "item_buttons"])
    content_type = Document

    def is_permitted(self, user, target):
        return target.template and user.has_permission(SendEmailPermission)

SendEmailAction("send_email").register()

