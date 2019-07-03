"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from mimetypes import guess_type
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.header import Header
from email.utils import formatdate, parseaddr, formataddr
from email.encoders import encode_base64

from pkg_resources import iter_entry_points
from cocktail import schema
from cocktail.translations import language_context
from cocktail.controllers.renderingengines import get_rendering_engine

from .item import Item
from .configuration import Configuration
from .file import File


class EmailTemplate(Item):

    type_group = "customization"
    encoding = "utf-8"
    admin_show_descriptions = False

    members_order = [
        "title",
        "mime_type",
        "sender",
        "receivers",
        "bcc",
        "template_engine",
        "subject",
        "body",
        "language_expression",
        "initialization_code",
        "condition"
    ]

    title = schema.String(
        required=True,
        unique=True,
        indexed=True,
        normalized_index=True,
        full_text_indexed=True,
        descriptive=True,
        translated=True,
        spellcheck=True
    )

    mime_type = schema.String(
        required=True,
        default="html",
        listed_by_default=False,
        enumeration=[
            "plain",
            "html"
        ],
        translatable_enumeration=False,
        text_search=False
    )

    sender = schema.CodeBlock(
        language="python"
    )

    receivers = schema.CodeBlock(
        language="python",
        required=True
    )

    bcc = schema.CodeBlock(
        language="python",
        listed_by_default=False
    )

    template_engine = schema.String(
        enumeration=[
            engine.name
            for engine in iter_entry_points("python.templating.engines")
        ],
        translatable_enumeration=False,
        text_search=False,
        listed_by_default=False
    )

    subject = schema.String(
        translated=True,
        edit_control="cocktail.html.TextArea",
        spellcheck=True,
        listed_by_default=False
    )

    body = schema.CodeBlock(
        language="html",
        translated=True,
        listed_by_default=False,
        spellcheck=True
    )

    initialization_code = schema.CodeBlock(
        language="python"
    )

    language_expression = schema.CodeBlock(
        language="python"
    )

    condition = schema.CodeBlock(
        language="python"
    )

    def send(self, context=None):

        if context is None:
            context = {}

        condition = self.condition
        if condition:
            condition_context = context.copy()
            condition_context["should_send"] = True
            label = "%s #%s.condition" % (self.__class__.__name__, self.id)
            code = compile(condition, label, "exec")
            exec(code, condition_context)
            if not condition_context["should_send"]:
                return False

        if context.get("attachments") is None:
            context["attachments"] = {}

        def eval_member(key):
            expr = self.get(key)
            return eval(expr, context.copy()) if expr else None

        # MIME block
        mime_type = self.mime_type
        pos = mime_type.find("/")

        if pos != -1:
            mime_type = mime_type[pos + 1:]

        # Language (python expression)
        language = eval_member("language_expression")
        if language not in self.translations:
            language = None

        with language_context(language):

            # Custom initialization code
            init_code = self.initialization_code
            if init_code:
                label = "%s #%s.initialization_code" % (
                    self.__class__.__name__,
                    self.id
                )
                init_code = compile(init_code, label, "exec")
                exec(init_code, context)

            # Subject and body (templates)
            if self.template_engine:
                engine = get_rendering_engine(
                    self.template_engine,
                    options={"mako.output_encoding": self.encoding}
                )

                def render(field_name):
                    markup = self.get(field_name)
                    if markup:
                        template = engine.load_template(
                            "EmailTemplate." + field_name,
                            self.get(field_name)
                        )
                        return engine.render(context, template=template)
                    else:
                        return ""

                subject = render("subject").strip()
                body = render("body")
            else:
                subject = self.subject
                body = self.body

            message = MIMEText(body, _subtype=mime_type, _charset=self.encoding)

            # Attachments
            attachments = context.get("attachments")
            if attachments:
                attachments = dict(
                    (cid, attachment)
                    for cid, attachment in attachments.items()
                    if attachment is not None
                )
                if attachments:
                    message_text = message
                    message = MIMEMultipart("related")
                    message.attach(message_text)

                    for cid, attachment in attachments.items():

                        if isinstance(attachment, File):
                            file_path = attachment.file_path
                            file_name = attachment.file_name
                            mime_type = attachment.mime_type
                        else:
                            file_path = attachment
                            file_name = os.path.basename(file_path)
                            mime_type_guess = guess_type(file_path)
                            if mime_type_guess:
                                mime_type = mime_type_guess[0]
                            else:
                                mime_type = "application/octet-stream"

                        main_type, sub_type = mime_type.split('/', 1)
                        message_attachment = MIMEBase(main_type, sub_type)
                        message_attachment.set_payload(open(file_path).read())
                        encode_base64(message_attachment)
                        message_attachment.add_header("Content-ID", "<%s>" % cid)
                        message_attachment.add_header(
                            'Content-Disposition',
                            'attachment; filename="%s"' % file_name
                        )
                        message.attach(message_attachment)

            def format_email_address(address, encoding):
                name, address = parseaddr(address)
                name = Header(name, encoding).encode()
                return formataddr((name, address))

             # Receivers (python expression)
            receivers = eval_member("receivers")
            if receivers:
                receivers = set(r.strip() for r in receivers)

            if not receivers:
                return set()

            message["To"] = ", ".join([
                format_email_address(receiver, self.encoding)
                for receiver in receivers
            ])

            # Sender (python expression)
            sender = eval_member("sender")
            if sender:
                message['From'] = format_email_address(sender, self.encoding)

            # BCC (python expression)
            bcc = eval_member("bcc")
            if bcc:
                receivers.update(r.strip() for r in bcc)

            if subject:
                message["Subject"] = Header(subject, self.encoding).encode()

            message["Date"] = formatdate()

            # Send the message
            smtp = Configuration.instance.connect_to_smtp()
            smtp.sendmail(sender, list(receivers), message.as_string())
            smtp.quit()

        return receivers

