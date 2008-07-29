#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.persistence import datastore
from magicbullet.models import (
    Action,
    AccessRule,
    User,
    StandardPage,
    Resource,
    Template
)
from magicbullet.controllers import Site
from magicbullet.controllers.backoffice import BackOffice

def init_site(admin_identifier, admin_password):

    # Create the site
    site = Site()
    
    # Create the back office interface
    back_office = BackOffice()    
    back_office.critical = True
    back_office.path = "cms"
    back_office_uri = site.uri(back_office.path)

    back_office.set("title", u"MagicBullet CMS", "ca")
    back_office.set("title", u"MagicBullet CMS", "es")
    back_office.set("title", u"MagicBullet CMS", "en")
 
    # Create standard templates
    empty_template = Template()
    empty_template.identifier = "empty_page"
    empty_template.set_translations("title",
        ca = u"Plantilla buida",
        es = u"Plantilla vacía",
        en = u"Empty template"
    )

    # Create the temporary home page
    site.home = StandardPage()
    site.home.template = empty_template
    site.home.set_translations("title",
        ca = u"Benvingut!",
        es = u"Bienvenido!",
        en = u"Welcome!"
    )
    site.home.set_translations("body",
        ca = u"El teu lloc web s'ha creat correctament. Ja pots començar a "
            u"<a href='%s'>treballar-hi</a> i substituir aquesta pàgina amb "
            u"els teus propis continguts." % back_office_uri,
        es = u"Tu sitio web se ha creado correctamente. Ya puedes empezar a "
            u"<a href='%s'>trabajar</a> en él y sustituir esta página "
            u"con tus propios contenidos." % back_office_uri,
        en = u"Your web site has been created successfully. You can start "
            u"<a href='%s'>working on it</a> and replace this page with your "
            u"own content." % back_office_uri        
    )

    greeting_stylesheet = Resource()
    greeting_stylesheet.set_translations("title",
        ca = u"Full d'estils de benvinguda",
        es = u"Hoja de estilos de bienvenida",
        en = u"Greeting stylesheet"
    )
    greeting_stylesheet.html = \
        u"""<link rel="Stylesheet" type="text/css" href="%s"/>""" \
        % site.uri("resources", "styles", "greeting.css")

    site.home.resources.append(greeting_stylesheet)

    # Create the authentication form
    login_page = StandardPage()
    login_page.template = empty_template
    login_page.set_translations("title",
        ca = u"Autenticació d'usuari",
        es = u"Autenticación de usuario",
        en = u"User authentication"
    )
    login_form = """
<form method="post">
    <label for="user">%s:</label>
    <input type="text" name="user" value=""/>
    <label for="password">%s:</label>
    <input type="password" name="password"/>
    <input type="submit" name="authenticate" value="%s"/>
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

    site.forbidden_error_page = login_page
    
    # Create standard users and roles
    anonymous_role = datastore.root["anonymous_role"] = User()    
    anonymous_role.critical = True
    anonymous_role.set_translations("title",
        ca = u"Anònim",
        es = u"Anónimo",
        en = u"Anonymous"
    )

    authenticated_role = datastore.root["authenticated_role"] = User()
    authenticated_role.critical = True
    authenticated_role.set_translations("title",
        ca = u"Autenticat",
        es = u"Autenticado",
        en = u"Authenticated"
    )

    author_role = datastore.root["author_role"] = User()
    author_role.critical = True
    author_role.set_translations("title",
        ca = u"Autor",
        es = u"Autor",
        en = u"Author"
    )

    owner_role = datastore.root["owner_role"] = User()
    owner_role.critical = True
    owner_role.set_translations("title",
        ca = u"Propietari",
        es = u"Propietario",
        en = u"Owner"
    )
 
    admin = User()
    admin.critical = True
    admin.set(site.auth.identifier_field, admin_identifier)
    admin.password = site.auth.encryption.new(admin_password).digest()
    admin.set_translations("title",
        ca = u"Administrador",
        es = u"Administrador",
        en = u"Administrator"
    )

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

    # Add standard access rules:
    rules = AccessRule.registry()

    # - by default, all content can be viewed by anybody
    rules.append(AccessRule(action = read, allowed = True))

    # - access to the back office requires special privileges
    rules.append(AccessRule(target_instance = back_office, allowed = False))

    # - the administrator has full control
    rules.append(AccessRule(role = admin, allowed = True))

    # - content owners have full control
    rules.append(AccessRule(role = owner_role, allowed = True))

    datastore.commit()

if __name__ == "__main__":
    
    from string import letters, digits
    from random import choice
 
    def random_string(length, source = letters + digits + "!?.-$#&@*"):
        return "".join(choice(source) for i in range(length))

    admin_identifier = "admin@localhost"
    admin_password = random_string(8)

    init_site(admin_identifier, admin_password)
    
    print u"Your site has been successfully created. You can start it by " \
          u"executing the 'run.py' script. An administrator account for the " \
          u"content manager interface has been generated, with the " \
          u"following credentials:\n\n" \
          u"\tIdentifier: %s\n" \
          u"\tPassword:   %s\n\n" % (admin_identifier, admin_password)

