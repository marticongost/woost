#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import sha
from cocktail.translations import translate
from cocktail.persistence import datastore
from sitebasis.models import (
    changeset_context,
    Site,
    Language,
    Action,
    Document,
    AccessRule,
    User,
    Role,
    Group,
    StandardPage,
    URI,
    Template
)

def init_site(
    admin_email = "admin@localhost",
    admin_password = "",
    languages = ("en",),
    uri = "/"):
 
    datastore.root.clear()
    datastore.commit()
    datastore.close()
    
    def set_translations(item, member, key, **kwargs):
        for language in languages:
            try:
                value = translate(key, language, **kwargs)
            except KeyError:
                pass
            else:
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

    with changeset_context() as changeset:
        
        # Create the site
        site = Site()
        datastore.root["main_site"] = site
        
        # Create the administrator user
        admin = User()
        admin.author = admin
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
        anonymous_role = datastore.root["anonymous_role"] = Role()
        anonymous_role.anonymous = True
        anonymous_role.critical = True
        anonymous_role.qname = "sitebasis.anonymous"
        set_translations(anonymous_role, "title", "Anonymous role title")
        anonymous_role.insert()

        authenticated_role = datastore.root["authenticated_role"] = Role()
        authenticated_role.critical = True
        authenticated_role.qname = "sitebasis.authenticated"
        set_translations(authenticated_role, "title",
            "Authenticated role title")
        authenticated_role.insert()

        author_role = datastore.root["author_role"] = Role()
        author_role.critical = True
        author_role.qname = "sitebasis.author"
        set_translations(author_role, "title", "Author role title")
        author_role.insert()

        owner_role = datastore.root["owner_role"] = Role()
        owner_role.critical = True
        owner_role.qname = "sitebasis.owner"
        set_translations(owner_role, "title", "Owner role title")
        owner_role.insert()
    
        # Create the back office interface
        back_office = Document()
        back_office.handler = "sitebasis.controllers.backoffice" \
                              ".backofficecontroller.BackOfficeController"
        back_office.critical = True
        back_office.qname = "sitebasis.backoffice"
        back_office.path = u"cms"
        set_translations(back_office, "title", "Back office title")
        back_office.insert()
     
        # Create standard templates
        empty_template = Template()
        empty_template.identifier = "sitebasis.views.EmptyPage"
        empty_template.engine = u"genshi"
        set_translations(empty_template, "title", "Empty template title")
        empty_template.insert()

        # Create standard resources
        message_stylesheet = URI()
        message_stylesheet.uri = uri + "resources/styles/message.css"
        message_stylesheet.qname = "sitebasis.message_stylesheet"
        set_translations(message_stylesheet, "title",
            "Message style sheet title")
        message_stylesheet.insert()

        # Create the temporary home page
        site.home = StandardPage()
        site.home.template = empty_template
        site.qname = "sitebasis.home"
        set_translations(site.home, "title", "Home page title")            
        set_translations(
            site.home, "body", "Home page body",
            uri = uri + back_office.path
        )
        site.home.page_resources.append(message_stylesheet)
        site.home.insert()

        # Create the 'content not found' page
        site.not_found_error_page = StandardPage()
        site.not_found_error_page.template = empty_template
        site.not_found_error_page.qname = "sitebasis.notfounderrorpage"
        set_translations(site.not_found_error_page, "title",
            "Not found error page title")
        set_translations(site.not_found_error_page, "body",
            "Not found error page body")            
        site.not_found_error_page.page_resources.append(message_stylesheet)
        site.not_found_error_page.insert()

        # Create the authentication form
        login_form = u"""
        <form method="post">
            <label for="user">%s:</label>
            <input type="text" name="user" value=""/>
            <label for="password">%s:</label>
            <input type="password" name="password"/>
            <div class="buttons">
                <input type="submit" name="authenticate" value="%s"/>
            </div>
        </form>
        """
        login_page = StandardPage()
        login_page.template = empty_template
        login_page.qname = "sitebasis.loginpage"
        set_translations(login_page, "title", "Login page title")
        set_translations(login_page, "body", "Login page body",
            form = login_form)

        login_page.page_resources.append(message_stylesheet)
        site.forbidden_error_page = login_page  
        site.forbidden_error_page.insert()

        # Add standard access rules:
        site.access_rules_by_priority = [

            # - administrators have full control
            AccessRule(
                role = administrators,
                allowed = True
            ),

            # - content owners have full control
            AccessRule(
                role = owner_role,
                allowed = True
            ),

            # - access to the back office requires special privileges
            AccessRule(
                target_instance = back_office,
                allowed = False
            ),

            # - global site configuration can't be accessed by regular users
            AccessRule(
                target_type = AccessRule,
                allowed = False
            ),

            # - access rules can't be accessed by regular users
            AccessRule(
                target_type = AccessRule,
                allowed = False
            ),

            # - the administrators group can't be accessed by regular users
            AccessRule(
                target_instance = administrators,
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
 
    def random_string(length, source = letters + digits + "!?.-$#&@*"):
        return "".join(choice(source) for i in range(length))

    admin_email = raw_input("Administrator email: ") or "admin@localhost"
    admin_password = raw_input("Administrator password: ") or random_string(8)
    languages = raw_input("Languages: ") or "en"

    init_site(admin_email, admin_password, languages.split())
    
    print u"Your site has been successfully created. You can start it by " \
          u"executing the 'run.py' script. An administrator account for the " \
          u"content manager interface has been generated, with the " \
          u"following credentials:\n\n" \
          u"\tEmail:     %s\n" \
          u"\tPassword:  %s\n\n" % (admin_email, admin_password)

if __name__ == "__main__":
    main()

