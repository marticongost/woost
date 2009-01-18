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
    Resource,
    Template
)

def init_site(
    admin_email = "admin@localhost",
    admin_password = "",
    languages = ("en",),
    uri = "/"):
 
    datastore.root.clear()

    def set_translations(item, member, key, **kwargs):
        for language in languages:
            item.set(member, translate(key, language, **kwargs), language)

    # Create standard actions
    create = Action()
    create.identifier = "create"
    set_translations(create, "title", "Create action title")

    read = Action()
    read.identifier = "read"
    set_translations(read, "title", "Read action title")

    modify = Action()
    modify.identifier = "modify"
    set_translations(modify, "title", "Modify action title")

    delete = Action()
    delete.identifier = "delete"
    set_translations(delete, "title", "Delete action title")

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
        
        changeset.author = admin
        site.author = site.owner = admin
        site.default_language = languages[0]
    
        # Create languages
        for code in languages:
            language = Language(iso_code = code)
            language.iso_code = code
 
        # Create the administrators group
        administrators = Group()
        administrators.critical = True
        set_translations(administrators, "title", "Administrators group title")
        administrators.group_members.append(admin)

        # Create standard users and roles
        anonymous_role = datastore.root["anonymous_role"] = Role()
        anonymous_role.anonymous = True
        anonymous_role.critical = True
        set_translations(anonymous_role, "title", "Anonymous role title")

        authenticated_role = datastore.root["authenticated_role"] = Role()
        authenticated_role.critical = True
        set_translations(authenticated_role, "title",
            "Authenticated role title")

        author_role = datastore.root["author_role"] = Role()
        author_role.critical = True
        set_translations(author_role, "title", "Author role title")

        owner_role = datastore.root["owner_role"] = Role()
        owner_role.critical = True
        set_translations(owner_role, "title", "Owner role title")
    
        # Create the back office interface
        back_office = Document()
        back_office.handler = "sitebasis.controllers.backoffice" \
                              ".backofficecontroller.BackOfficeController"
        back_office.critical = True
        back_office.path = "cms"
        set_translations(back_office, "title", "Back office title")
     
        # Create standard templates
        empty_template = Template()
        empty_template.identifier = "sitebasis.views.EmptyPage"
        empty_template.engine = "genshi"
        set_translations(empty_template, "title", "Empty template title")

        # Create standard resources
        message_stylesheet = Resource()
        message_stylesheet.uri = uri + "resources/styles/message.css"
        set_translations(message_stylesheet, "title",
            "Message style sheet title")        

        # Create the temporary home page
        site.home = StandardPage()
        site.home.template = empty_template
        set_translations(site.home, "title", "Home page title")            
        set_translations(
            site.home, "body", "Home page body",
            uri = uri + back_office.path
        )
        site.home.resources.append(message_stylesheet)

        # Create the 'content not found' page
        site.not_found_error_page = StandardPage()
        site.not_found_error_page.template = empty_template
        set_translations(site.not_found_error_page, "title",
            "Not found error page title")
        set_translations(site.not_found_error_page, "body",
            "Not found error page body")            
        site.not_found_error_page.resources.append(message_stylesheet)

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
        set_translations(login_page, "title", "Login page title")
        set_translations(login_page, "body", "Login page body",
            form = login_form)

        login_page.resources.append(message_stylesheet)
        site.forbidden_error_page = login_page  

        # Add standard access rules:
        rules = site.access_rules_by_priority

        # - by default, all content can be viewed by anybody
        rules.insert(0, AccessRule(
            action = read,
            allowed = True,
            author = admin,
            owner = admin
        ))

        # - access to the back office requires special privileges
        rules.insert(0, AccessRule(
            target_instance = back_office,
            allowed = False,
            author = admin,
            owner = admin
        ))

        # - administrators have full control
        rules.insert(0, AccessRule(
            role = administrators,
            allowed = True,
            author = admin,
            owner = admin
        ))

        # - content owners have full control
        rules.insert(0, AccessRule(
            role = owner_role,
            allowed = True,
            author = admin,
            owner = admin
        ))

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

