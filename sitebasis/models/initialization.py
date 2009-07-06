#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import sha
from optparse import OptionParser
from cocktail.translations import translations
from cocktail.persistence import datastore
from sitebasis.models import (
    changeset_context,
    Site,
    Language,
    Action,
    Document,
    AccessRule,
    Agent,
    User,
    Role,
    Group,
    StandardPage,
    URI,
    Template,
    UserView
)

standard_template_identifiers = {
    "cocktail": "sitebasis.views.StandardView",
    "genshi": "sitebasis.views.StandardView"
}

def init_site(
    admin_email = "admin@localhost",
    admin_password = "",
    languages = ("en",),
    uri = "/",
    template_engine = "cocktail"):
 
    datastore.root.clear()
    datastore.commit()
    datastore.close()
    
    def set_translations(item, member, key, **kwargs):
        for language in languages:
            value = translations(
                "sitebasis.models.initialization " + key,
                language,
                **kwargs
            )
            if value:
                item.set(member, value, language)

    # Create standard actions
    create = Action()
    create.identifier = "create"
    set_translations(create, "title", "Create action title")
    create.insert()

    read = Action()
    read.identifier = "read"
    set_translations(read, "title", "Read action title")
    read.insert()

    modify = Action()
    modify.identifier = "modify"
    set_translations(modify, "title", "Modify action title")
    modify.insert()

    delete = Action()
    delete.identifier = "delete"
    set_translations(delete, "title", "Delete action title")
    delete.insert()

    confirm_draft = Action()
    confirm_draft.identifier = "confirm_draft"
    set_translations(confirm_draft, "title", "Confirm draft title")
    confirm_draft.insert()

    # ???
    visible = Action()
    visible.identifier = "visible"
    set_translations(visible, "title", "Visible action title")
    visible.insert()

    with changeset_context() as changeset:
        
        # Create the site
        site = Site()
        site.qname = "sitebasis.main_site"
        site.insert()

        # Create the administrator user
        admin = User()
        admin.author = admin
        admin.qname = "sitebasis.administrator"
        admin.owner = admin
        admin.critical = True
        admin.email = admin_email
        admin.password = admin_password
        admin.insert()
        
        changeset.author = admin
        site.author = site.owner = admin
        site.default_language = languages[0]

        # Create languages
        for code in languages:
            language = Language(iso_code = code)
            language.iso_code = code
            language.insert()
 
        # Create the administrators group
        administrators = Group()
        administrators.qname = "sitebasis.administrators"
        administrators.critical = True
        set_translations(administrators, "title", "Administrators group title")
        administrators.group_members.append(admin)
        administrators.insert()

        # Create standard users and roles
        anonymous_role = Role()
        anonymous_role.anonymous = True
        anonymous_role.critical = True
        anonymous_role.qname = "sitebasis.anonymous"
        set_translations(anonymous_role, "title", "Anonymous role title")
        anonymous_role.insert()

        authenticated_role = Role()
        authenticated_role.critical = True
        authenticated_role.qname = "sitebasis.authenticated"
        set_translations(authenticated_role, "title",
            "Authenticated role title")
        authenticated_role.insert()

        author_role = Role()
        author_role.critical = True
        author_role.qname = "sitebasis.author"
        set_translations(author_role, "title", "Author role title")
        author_role.insert()

        owner_role = Role()
        owner_role.critical = True
        owner_role.qname = "sitebasis.owner"
        set_translations(owner_role, "title", "Owner role title")
        owner_role.insert()
     
        # Create standard templates
        std_template = Template()
        std_template.identifier = standard_template_identifiers.get(
            template_engine, "StandardView"
        )
        std_template.engine = template_engine
        set_translations(std_template, "title", "Standard template title")
        std_template.insert()

        # Create standard resources
        site_stylesheet = URI()
        site_stylesheet.uri = uri + "resources/styles/site.css"
        site_stylesheet.qname = "sitebasis.site_stylesheet"
        site_stylesheet.resource_type = "html_resource"
        set_translations(site_stylesheet, "title", "Site style sheet title")
        site_stylesheet.insert()

        # Create the temporary home page
        site.home = StandardPage()
        site.home.template = std_template
        site.home.qname = "sitebasis.home"
        set_translations(site.home, "title", "Home page title")
        set_translations(site.home, "inner_title", "Home page inner title")
        set_translations(
            site.home, "body", "Home page body",
            uri = uri + "cms"
        )
        site.home.branch_resources.append(site_stylesheet)
        site.home.insert()
    
        # Create the back office interface
        back_office = Document()
        back_office.handler = "sitebasis.controllers.backoffice" \
                              ".backofficecontroller.BackOfficeController"
        back_office.critical = True
        back_office.qname = "sitebasis.backoffice"
        back_office.parent = site.home
        back_office.hidden = True
        back_office.path = u"cms"
        set_translations(back_office, "title", "Back office title")
        back_office.insert()

        # Create the 'content not found' page
        site.not_found_error_page = StandardPage()
        site.not_found_error_page.parent = site.home
        site.not_found_error_page.hidden = True
        site.not_found_error_page.template = std_template
        site.not_found_error_page.qname = "sitebasis.not_found_error_page"
        set_translations(site.not_found_error_page, "title",
            "Not found error page title")
        set_translations(site.not_found_error_page, "body",
            "Not found error page body")            
        site.not_found_error_page.insert()

        # Create the login page
        site.forbidden_error_page = StandardPage()
        site.forbidden_error_page.parent = site.home
        site.forbidden_error_page.hidden = True
        site.forbidden_error_page.template = std_template
        site.forbidden_error_page.qname = "sitebasis.forbidden_error_page"
        set_translations(site.forbidden_error_page, "title",
            "Forbidden error page title")
        set_translations(site.forbidden_error_page, "body",
            "Forbidden error page body")
        site.forbidden_error_page.insert()

        # Create the authentication form
        login_form = u"""
        <form method="post" class="login_form">
            <label for="user">%s:</label>
            <input type="text" name="user" value=""/>
            <label for="password">%s:</label>
            <input type="password" name="password"/>
            <div class="buttons">
                <input type="submit" name="authenticate" value="%s"/>
            </div>
        </form>
        """
        site.login_page = StandardPage()
        site.login_page.parent = site.home
        site.login_page.hidden = True
        site.login_page.template = std_template
        site.login_page.qname = "sitebasis.login_page"
        set_translations(site.login_page, "title", "Login page title")
        set_translations(site.login_page, "body", "Login page body",
            form = login_form
        )
        site.login_page.insert()

        # Create site-wide user views
        own_items_view = UserView()
        own_items_view.sites.append(site)
        own_items_view.parameters = {
            "type": "sitebasis.models.item.Item",
            "content_view": "flat",
            "filter": "own-items",
            "order": "-last_update_time",
            "members": None
        }
        set_translations(
            own_items_view,
            "title",
            "Own items user view"
        )
        own_items_view.insert()
        
        document_tree_view = UserView()
        document_tree_view.sites.append(site)
        document_tree_view.parameters = {
            "type": "sitebasis.models.document.Document",
            "content_view": "tree",
            "filter": None,
            "members": None
        }
        set_translations(
            document_tree_view,
            "title",
            "Document tree user view"
        )
        document_tree_view.insert()

        resource_gallery_view = UserView()
        resource_gallery_view.sites.append(site)
        resource_gallery_view.parameters = {
            "type": "sitebasis.models.resource.Resource",
            "content_view": "thumbnails",
            "filter": None,
            "order": None,
            "members": None
        }
        set_translations(
            resource_gallery_view,
            "title",
            "Resource gallery user view"
        )
        resource_gallery_view.insert()

        # Add standard access rules:
        site.access_rules_by_priority = [

            # - administrators have full control
            AccessRule(
                role = administrators,
                allowed = True
            ),

            # - the 'owner' field can't be set by no one
            AccessRule(
                target_member = "owner",
                action = modify,
                allowed = False
            ),

            # - content owners have full control
            AccessRule(
                role = owner_role,
                allowed = True
            ),

            AccessRule(
                target_type = User,
                target_member = "password",
                allowed = False
            ),

            # - access to the back office requires special privileges
            AccessRule(
                target_instance = back_office,
                allowed = False
            ),

            # - global site configuration can't be accessed by regular users
            AccessRule(
                target_type = Site,
                allowed = False
            ),

            # - access rules can't be accessed by regular users
            AccessRule(
                target_type = AccessRule,
                allowed = False
            ),

            # - users can be read...
            AccessRule(
                target_type = User,
                action = read,
                allowed = True
            ),

            # - ...but otherwise, agents can't be accessed by any body
            AccessRule(
                target_type = Agent,
                allowed = False
            ),

            # - by default, all content can be viewed by anybody
            AccessRule(
                action = read,
                allowed = True
            )
        ]

        for rule in site.access_rules_by_priority:
            rule.insert()

    datastore.commit()

def main():

    from string import letters, digits
    from random import choice
 
    parser = OptionParser()
    parser.add_option("-u", "--user", help = "Administrator email")
    parser.add_option("-p", "--password", help = "Administrator password")
    parser.add_option("-l", "--languages",
        help = "Comma separated list of languages")
    parser.add_option("-t", "--template-engine",
        default = "cocktail",
        help = "The buffet templating engine to use by default")
    
    options, args = parser.parse_args()

    def random_string(length, source = letters + digits + "!?.-$#&@*"):
        return "".join(choice(source) for i in range(length))  

    admin_email = options.user
    admin_password = options.password
    
    if admin_email is None:
        admin_email = raw_input("Administrator email: ") or "admin@localhost"

    if admin_password is None:
        admin_password = raw_input("Administrator password: ") \
            or random_string(8)

    languages = options.languages \
        and options.languages.replace(",", " ") \
        or raw_input("Languages: ") or "en"

    init_site(
        admin_email,
        admin_password,
        languages.split(),
        template_engine = options.template_engine
    )
    
    print u"Your site has been successfully created. You can start it by " \
          u"executing the 'run.py' script. An administrator account for the " \
          u"content manager interface has been generated, with the " \
          u"following credentials:\n\n" \
          u"\tEmail:     %s\n" \
          u"\tPassword:  %s\n\n" % (admin_email, admin_password)

if __name__ == "__main__":
    main()

