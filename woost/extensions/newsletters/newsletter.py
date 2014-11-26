#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""

from cocktail import schema
from cocktail.iteration import first
from woost.models import (
    Configuration,
    Document, 
    Template, 
    Controller,
    CustomBlock,
    HTMLBlock,
    block_type_groups
)
from woost.extensions.blocks.block import Block
from woost.extensions.blocks.slot import Slot
from woost.extensions.newsletters.newsletterbox import NewsletterBox
from woost.extensions.newsletters.newslettercontent import NewsletterContent
from woost.extensions.newsletters.newsletterseparator \
    import NewsletterSeparator
from woost.extensions.newsletters.mailingplatform import MailingPlatform
from woost.extensions.newsletters.members import Spacing


class Newsletter(Document):

    default_template = schema.DynamicDefault(
        lambda: Template.get_instance(
            qname = "woost.extensions.newsletters.newsletter_template"
        )
    )

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(
            qname = "woost.extensions.newsletters.newsletter_controller"
        )
    )
    
    members_order = [
        "mailing_platform",
        "root_spacing_factor",
        "blocks"
    ]

    mailing_platform = schema.Reference(
        type = MailingPlatform,
        member_group = "content",
        enumeration = lambda ctx: Configuration.instance.mailing_platforms,
        edit_control = "cocktail.html.RadioSelector",
        listed_by_default = False,
        indexed = True,
        default = schema.DynamicDefault(
            lambda: first(Configuration.instance.mailing_platforms)
        )
    )

    root_spacing_factor = Spacing(
        required = True,
        member_group = "content",
        listed_by_default = False
    )

    blocks = Slot()

    allowed_block_types = (
        NewsletterBox,
        NewsletterContent,
        NewsletterSeparator,
        CustomBlock,
        HTMLBlock
    )

    def allows_block_type(self, block_type):
        return issubclass(block_type, self.allowed_block_types)

    def get_unsubscription_tag(self):
        return (
            self.mailing_platform
            and self.mailing_platform.unsubscription_tag
        )

    def get_online_version_tag(self):
        return (
            self.mailing_platform
            and self.mailing_platform.online_version_tag
        )

