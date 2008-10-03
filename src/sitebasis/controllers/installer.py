#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import socket
import re
from os import listdir, mkdir
from os.path import join, dirname, abspath, exists, isdir, isfile
from subprocess import Popen
from shutil import copytree
import cherrypy
from cocktail import schema
from cocktail.translations import set_language
from cocktail.html.templates import TemplateLoader
from cocktail.controllers import read_form
from sitebasis import __file__ as sitebasis_file
from sitebasis.translations import installerstrings


class Installer(object):

    base_path = join(dirname(sitebasis_file), "..", "..")

    skeleton_path = abspath(
        join(base_path, "scripts","project_skeleton")
    )
    
    views_path = join(base_path, "src", "sitebasis", "views")

    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        root = views_path,
        dir = "resources"
    )

    def __init__(self):
        self._templates = TemplateLoader()
        self._templates.paths.append(self.views_path)

    @cherrypy.expose
    def index(self, **params):

        set_language("en")
        submitted = params.pop("submit", False)
        successful = False
        errors = []
 
        HOST_FORMAT = \
            re.compile(r"^([a-z]+(\.[a-z]+)*)|(\d{1,3}(\.\d{1,3}){3})$")

        form_schema = schema.Schema(
            name = "Installer",
            members = [
                schema.String(
                    name = "project_name",
                    required = True,
                    format = r"^[A-Za-z][A-Za-z_0-9]*$"
                ),
                schema.String(
                    name = "project_path",
                    required = True
                ),
                schema.String(
                    name = "admin_email",
                    required = True,
                    default = "admin@localhost"
                ),
                schema.String(
                    name = "admin_password",
                    required = True,
                    min = 8
                ),
                schema.String(
                    name = "webserver_host",
                    required = True,
                    format = HOST_FORMAT,
                    default = "127.0.0.1"
                ),
                schema.Integer(
                    name = "webserver_port",
                    required = True,
                    default = 8080
                ),
                schema.Boolean(
                    name = "validate_webserver_address",
                    default = True
                ),
                schema.String(
                    name = "database_host",
                    required = True,
                    format = HOST_FORMAT,
                    default = "127.0.0.1"
                ),
                schema.Integer(
                    name = "database_port",
                    required = True,
                    default = 8081
                ),
                schema.Boolean(
                    name = "validate_database_address",
                    default = True
                )
            ]
        )

        def make_address_validation(host_field, port_field, check_field):

            def validate_address(schema, validable, context):

                if validable[check_field]:
                    host = validable[host_field]
                    port = validable[port_field]
                    host_member = schema[host_field]
                    port_member = schema[port_field]

                    if host_member.validate(host) \
                    and port_member.validate(port) \
                    and not self._is_valid_local_address(host, port):
                        yield WrongAddressError(
                            schema, validable, context,
                            host_member, port_member
                        )

            return validate_address

        form_schema.add_validation(make_address_validation(
            "webserver_host",
            "webserver_port",
            "validate_webserver_address"
        ))

        form_schema.add_validation(make_address_validation(
            "database_host",
            "database_port",
            "validate_database_address"
        ))

        form_data = {}

        if submitted:
            read_form(form_schema, form_data)
            errors = list(form_schema.get_errors(form_data))

            if not errors:
                try:
                    if exists(form_data["project_path"]):
                        raise InstallFolderExists()

                    self.install(form_data)

                except Exception, ex:
                    errors.append(ex)
                else:
                    successful = True
        else:
            form_schema.init_instance(form_data)

        view = self._templates.new("Installer.xml")
        view.submitted = submitted
        view.successful = successful
        view.schema = form_schema
        view.data = form_data
        view.errors = errors
        return view.render_page()

    def install(self, params):
        
        self._create_project(params)
        self._start_database(params)
        self._init_project(params)

    def _create_project(self, params):

        vars = dict(
            ("_%s_" % key.upper(), unicode(value))
            for key, value in params.iteritems()
        )

        vars["_PROJECT_MODULE_"] = params["project_name"].lower()

        keys_expr = re.compile("|".join(vars))

        def expand_vars(text):
            return keys_expr.sub(lambda match: vars[match.group(0)], text)

        def copy(source, target):

            if isdir(source):
                mkdir(target)
                for name in listdir(source):
                    copy(join(source, name), join(target, expand_vars(name)))

            elif isfile(source):
                source_file = file(source, "r")
                try:
                    source_data = source_file.read().decode("utf-8")
                    target_data = expand_vars(source_data).encode("utf-8")
                    target_file = file(target, "w")
                    try:
                        target_file.write(target_data)
                    finally:
                        target_file.close()
                finally:
                    source_file.close()

        copy(self.skeleton_path, params["project_path"])

        # Create the folder for the database
        mkdir(join(params["project_path"], "data"))

        # Copy the sitebasis package to the site
        copytree(
            join(self.base_path, "src", "sitebasis"),
            join(params["project_path"], "src", "sitebasis")
        )

    def _start_database(self, params):
        cmd = "runzeo -f %s -a %s:%d" % (
            join(params["project_path"], "data", "database.fs"),
            params["database_host"],
            params["database_port"]
        )
        Popen(cmd, shell = True)

    def _init_project(self, params):
        cmd = "python %s" \
            % join(params["project_path"], "scripts", "initsite.py")
        proc = Popen(cmd, shell = True)
        proc.wait()    

    def _is_valid_local_address(self, host, port):
        s = socket.socket()
        try:
            s.bind((host, port))
        except socket.error:
            return False
        else:
            s.close()

        return True

    def run(self):

        cherrypy.config.update({
            "global": {
                "server.socket_port": 8082,
                "tools.encode.on": True,
                "tools.encode.encoding": "utf-8",
                "tools.decode.on": True,
                "tools.decode.encoding": 'utf-8'
            }
        })

        cherrypy.quickstart(self, "/")


class InstallFolderExists(Exception):
    pass


class WrongAddressError(schema.exceptions.ValidationError):
 
    def __init__(self, member, value, context, host_member, port_member):
        
        schema.exceptions.ValidationError.__init__(
            self, member, value, context
        )

        self.host_member = host_member
        self.port_member = port_member

