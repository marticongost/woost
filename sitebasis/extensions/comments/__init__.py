#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from __future__ import with_statement
import cherrypy
from cocktail import schema
from cocktail.events import event_handler, when
from cocktail.translations import translations
from cocktail.persistence import datastore
from cocktail.controllers import UserCollection, get_parameter
from cocktail.pkgutils import resolve
from sitebasis.models import Extension, Document, Role, get_current_user
from sitebasis.models.changesets import changeset_context
from sitebasis.models.permission import CreatePermission
from sitebasis.controllers.basecmscontroller import BaseCMSController

translations.define("CommentsExtension",
    ca = u"Comentaris",
    es = u"Comentarios",
    en = u"Comments"
)

translations.define("CommentsExtension-plural",
    ca = u"Comentaris",
    es = u"Comentarios",
    en = u"Comments"
)

translations.define("CommentsExtension.captcha_enabled",
    ca = u"Captcha activat",
    es = u"Captcha activado",
    en = u"Captcha enabled"
)


class CommentsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Afegeix suport per comentaris.""",
            "ca"
        )
        self.set("description",            
            u"""Añade soporte para comentarios.""",
            "es"
        )
        self.set("description",
            u"""Adds support for comments.""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):
        
        # Import the extension's models
        from sitebasis.extensions.comments import strings
        from sitebasis.extensions.comments.comment import Comment

        # Captcha
        #------------------------------------------------------------------------------
        try:
            from sitebasis.extensions.recaptcha import ReCaptchaExtension
        except ImportError:
            pass
        else:
            from sitebasis.extensions.recaptcha.schemarecaptchas import ReCaptcha
            if ReCaptchaExtension.instance.enabled:
                CommentsExtension.add_member(
                    schema.Boolean("captcha_enabled", default = False)
                )

        # Permissions
        #--------------------------------------------------------------------------
        q = "sitebasis.models.permission.CreatePermission " \
                "anonymous_comments_permission"
        anonymous_comments_permission = CreatePermission.get_instance(qname = q)

        if anonymous_comments_permission is None:

            anonymous = Role.get_instance(qname = "sitebasis.anonymous")

            anonymous_comments_permission = CreatePermission(
                authorized = True,
                role = anonymous,
                matching_items = {
                    "type": "sitebasis.extensions.comments.comment.Comment"
                },
                qname = q
            )
            
            anonymous_comments_permission.insert()
            datastore.commit()

        # Extend Document model
        Document.add_member(
            schema.Boolean(
                "allow_comments",
                default = False
            )
        )

        Document.add_member(
            schema.Collection(
                "comments",
                items = schema.Reference(type = Comment),
                bidirectional = True,
                related_key = "document",
                integral = True
            )
        )

        @when(BaseCMSController.processed)
        def _process_comments(event):

            controller = event.source
            comment_model = resolve(getattr(controller, "comment_model", Comment))
            document = controller.context["document"]
            user = get_current_user()

            if document is not None and \
            document.allow_comments and \
            user.has_permission(CreatePermission, target = comment_model):

                # Comments collection
                comments_user_collection = UserCollection(comment_model)
                comments_user_collection.allow_type_selection = False
                comments_user_collection.allow_filters = False
                comments_user_collection.allow_language_selection = False
                comments_user_collection.allow_member_selection = False
                comments_user_collection.params.prefix = "comments_"
                comments_user_collection.base_collection = document.comments

                # Show the last comments page if not specified
                if "comments_page" not in cherrypy.request.params:
                    div, mod = divmod(
                        len(comments_user_collection.subset),
                        comments_user_collection.page_size
                    )
                    comments_page = div if mod else div - 1
                    cherrypy.request.params.update(
                        comments_page = str(comments_page)
                    )
                
                # Adapting the comments model
                adapter = schema.Adapter()
                adapter.exclude(
                    member.name
                    for member in comment_model.members().itervalues()
                    if not member.visible 
                    or not member.editable
                    or not issubclass(member.schema, comment_model)
                )
                adapter.exclude("document")

                comments_schema = schema.Schema(comment_model.name + "Form")
                adapter.export_schema(comment_model, comments_schema)

                if user.anonymous \
                and getattr(CommentsExtension.instance, "captcha_enabled", False):
                    comments_schema.add_member(
                        ReCaptcha("captcha")
                    )
    
                # Insert a new comment
                if cherrypy.request.method == "POST" \
                and "post_comment" in cherrypy.request.params:

                    with changeset_context(user):
                        comment_data = {}

                        get_parameter(
                            comments_schema, 
                            target = comment_data, 
                            strict = False
                        )

                        comment_errors = schema.ErrorList(
                            comments_schema.get_errors(comment_data)
                        )

                        if not comment_errors:
                            comment = comment_model()
                            comment_id = comment.id

                            adapter.import_object(                                                                                                                                                                       
                                comment_data,
                                comment,
                                source_schema = comment_model
                            )

                            comment.id = comment_id
                            comment.document = document
                            comment.insert()
                            datastore.commit()
                else:
                    comment_errors = schema.ErrorList([])
                
                # Update the output
                controller.output.update(
                    comments_user_collection = comments_user_collection,
                    comments_schema = comments_schema,
                    comment_errors = comment_errors
                )

