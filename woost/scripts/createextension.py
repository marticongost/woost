#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
import os
from argparse import ArgumentParser
from cocktail.pkgutils import resource_filename

def create_extension(name, module_header = ""):
    """Creates a skeleton directory structure for a new Woost extension.

    :param name: The name of the extension to create. Will be used to determine
        the name of the generated package, so it should be a valid Python
        module name. A name of 'foobar' will create a 'woost-foobar' folder,
        containing a 'woost.extensions.foobar' package.
    :type name: str
    """
    src = resource_filename("woost.scripts", "extension_skeleton")
    dest = "woost-" + name
    skeleton = DirectorySkeleton()
    skeleton.vars = {
        "extension_name": name,
        "module_header": module_header
    }
    skeleton.copy(src, dest)


class DirectorySkeleton(object):

    vars = {}
    var_reg_expr = re.compile(r"--(?P<key>[A-Z0-9_]+)--")

    def expand_vars(self, string):
        return self.var_reg_expr.sub(self._inject_var, string)

    def _inject_var(self, match):
        key = match.group("key").lower()
        try:
            return self.vars[key]
        except KeyError:
            raise KeyError("Undefined variable: %s" % match.group(0))

    def copy(self, source, target):

        # Copy folders recursively
        if os.path.isdir(source):
            if not os.path.exists(target):
                os.mkdir(target)
            for name in os.listdir(source):
                self.copy(
                    os.path.join(source, name),
                    os.path.join(target, self.expand_vars(name))
                )
        # Copy files, expanding variables
        elif os.path.isfile(source):
            if os.path.splitext(source)[1] != ".pyc":
                with open(source, "r") as source_file:
                    source_data = source_file.read()
                    target_data = self.expand_vars(source_data)
                    with open(target, "w") as target_file:
                        target_file.write(target_data)


def main():

    parser = ArgumentParser()

    parser.add_argument(
        "name",
        help = """
            The name of the extension. Will be used to determine the name of
            the generated package, so it should be a valid Python module name.
            """
    )

    parser.add_argument(
        "--module-header",
        help = """
            A header to add to all Python modules generated by the script. Can
            be set to a file's contents by using a 'file:PATH' value.
            """,
        default = "#-*- coding: utf-8 -*-"
    )

    args = parser.parse_args()

    name = args.name

    module_header = args.module_header
    if module_header and module_header.startswith("file:"):
        with open(module_header[5:]) as f:
            module_header = f.read().strip()

    create_extension(name, module_header)

if __name__ == "__main__":
    main()

