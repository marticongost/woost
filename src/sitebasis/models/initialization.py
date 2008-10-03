#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from cocktail.persistence import datastore
from sitebasis.models import (
    changeset_context,
    Site,
    Action,
    AccessRule,
    User,
    Role,
    Group,
    StandardPage,
    Resource,
    Template
)
from sitebasis.controllers.backoffice import BackOffice

def init_site(
    admin_email = "admin@localhost",
    admin_password = "",
    uri = "/"):
 
    datastore.root.clear()

    # Create standard actions
    create = Action()
    create.identifier = "create"
    create.set_translations("title",
        ca = u"Crear",
        es = u"Crear",
        en = u"Create"
    )

    read = Action()
    read.identifier = "read"
    read.set_translations("title",
        ca = u"Veure",
        es = u"Ver",
        en = u"Read"
    )

    modify = Action()
    modify.identifier = "modify"
    modify.set_translations("title",
        ca = u"Modificar",
        es = u"Modificar",
        en = u"Modify"
    )

    delete = Action()
    delete.identifier = "delete"
    delete.set_translations("title",
        ca = u"Eliminar",
        es = u"Eliminar",
        en = u"Delete"
    )

    with changeset_context() as changeset:
        
        # Create the site
        site = Site()
        site.languages = ["ca", "es", "en"]
        datastore.root["main_site"] = site

        # Create the administrator user and groups
        admin = User()
        admin.author = admin
        admin.owner = admin
        admin.critical = True
        admin.email = admin_email
        admin.password = sha.new(admin_password).digest()
        
        changeset.author = admin
        site.author = site.owner = admin
    
        administrators = Group()
        administrators.critical = True
        administrators.set_translations("title",
            ca = u"Administradors",
            es = u"Administradores",
            en = u"Administrators"
        )
        administrators.group_members.append(admin)
                
        # Create standard users and roles
        anonymous_role = datastore.root["anonymous_role"] = Role()
        anonymous_role.anonymous = True
        anonymous_role.critical = True
        anonymous_role.set_translations("title",
            ca = u"Anònim",
            es = u"Anónimo",
            en = u"Anonymous"
        )

        authenticated_role = datastore.root["authenticated_role"] = Role()
        authenticated_role.critical = True
        authenticated_role.set_translations("title",
            ca = u"Autenticat",
            es = u"Autenticado",
            en = u"Authenticated"
        )

        author_role = datastore.root["author_role"] = Role()
        author_role.critical = True
        author_role.set_translations("title",
            ca = u"Autor",
            es = u"Autor",
            en = u"Author"
        )

        owner_role = datastore.root["owner_role"] = Role()
        owner_role.critical = True
        owner_role.set_translations("title",
            ca = u"Propietari",
            es = u"Propietario",
            en = u"Owner"
        )
    
        # Create the back office interface
        back_office = Document()
        back_office.handler = BackOffice
        back_office.critical = True
        back_office.path = "cms"
        back_office.set_translations("title",
            ca = u"Gestor de continguts",
            es = u"Gestor de contenidos",
            en = u"Content Manager"
        )
     
        # Create standard templates
        empty_template = Template()
        empty_template.identifier = "empty_page"
        empty_template.set_translations("title",
            ca = u"Plantilla buida",
            es = u"Plantilla vacía",
            en = u"Empty template"
        )

        # Create standard resources
        message_stylesheet = Resource()
        message_stylesheet.set_translations("title",
            ca = u"Full d'estils de benvinguda",
            es = u"Hoja de estilos de bienvenida",
            en = u"Greeting stylesheet"
        )
        message_stylesheet.uri = uri + "resources/styles/message.css"

        # Create the temporary home page
        site.home = StandardPage()
        site.home.template = empty_template
        site.home.set_translations("title",
            ca = u"Benvingut!",
            es = u"Bienvenido!",
            en = u"Welcome!"
        )
        site.home.set_translations("body",
            ca = u"El teu lloc web s'ha creat correctament. Ja pots començar "
                u"a <a href='%s'>treballar-hi</a> i substituir aquesta pàgina "
                u"amb els teus propis continguts."
                % (uri + back_office.path),
            es = u"Tu sitio web se ha creado correctamente. Ya puedes empezar "
                u"a <a href='%s'>trabajar</a> en él y sustituir esta página "
                u"con tus propios contenidos."
                % (uri + back_office.path),
            en = u"Your web site has been created successfully. You can start "
                u"<a href='%s'>working on it</a> and replace this page with "
                u"your own content."
                % (uri + back_office.path)
        )
        site.home.resources.append(message_stylesheet)

        # Create the 'content not found' page
        site.not_found_error_page = StandardPage()
        site.not_found_error_page.template = empty_template
        site.not_found_error_page.set_translations("title",
            ca = u"Pàgina no trobada",
            es = u"Página no encontrada",
            en = u"Page not found"
        )
        site.not_found_error_page.set_translations("body",
            ca = u"La direcció indicada no coincideix amb cap dels continguts "
                 u"del web. Si us plau, revísa-la i torna-ho a provar.",
            es = u"La dirección indicada no coincide con ninguno de los "
                 u"contenidos del web. Por favor, revísala y intentalo de nuevo.",
            en = u"Couldn't find the indicated address. Please, verify it and try "
                 u"again."
        )
        site.not_found_error_page.resources.append(message_stylesheet)

        # Create the authentication form
        login_page = StandardPage()
        login_page.template = empty_template
        login_page.set_translations("title",
            ca = u"Autenticació d'usuari",
            es = u"Autenticación de usuario",
            en = u"User authentication"
        )
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
        login_page.set_translations("body",
            ca = u"""
<p>
    L'accés a aquesta secció del web està restringit. Per favor,
    introdueix les teves credencials d'usuari per continuar.
</p>
""" + (login_form % (u"Usuari", u"Contrasenya", u"Entrar")),
            es = u"""
<p>
    El acceso a esta sección del sitio está restringido. Por favor,
    introduce tus credenciales de usuario para continuar.
</p>
""" + (login_form % (u"Usuario", u"Contraseña", u"Entrar")),
            en = u"""
<p>
    Access to this part of the website is restricted. Please, introduce
    your user credentials to proceed.
</p>
""" + (login_form % (u"User", u"Password", u"Enter"))
        )
        login_page.resources.append(message_stylesheet)
        site.forbidden_error_page = login_page  

        # Add standard access rules:
        rules = AccessRule.registry()

        # - by default, all content can be viewed by anybody
        rules.append(
            AccessRule(
                action = read,
                allowed = True,
                author = admin,
                owner = admin
            )
        )

        # - access to the back office requires special privileges
        rules.append(
            AccessRule(
                target_instance = back_office,
                allowed = False,
                author = admin,
                owner = admin
            )
        )

        # - administrators have full control
        rules.append(
            AccessRule(
                role = administrators,
                allowed = True,
                author = admin,
                owner = admin
            )
        )

        # - content owners have full control
        rules.append(
            AccessRule(
                role = owner_role,
                allowed = True,
                author = admin,
                owner = admin
            )
        )

    datastore.commit()

def main():

    from string import letters, digits
    from random import choice
 
    def random_string(length, source = letters + digits + "!?.-$#&@*"):
        return "".join(choice(source) for i in range(length))

    admin_email = "admin@localhost"
    admin_password = random_string(8)

    init_site(admin_email, admin_password)
    
    print u"Your site has been successfully created. You can start it by " \
          u"executing the 'run.py' script. An administrator account for the " \
          u"content manager interface has been generated, with the " \
          u"following credentials:\n\n" \
          u"\tEmail:     %s\n" \
          u"\tPassword:  %s\n\n" % (admin_email, admin_password)

if __name__ == "__main__":
    main()

