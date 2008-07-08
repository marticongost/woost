#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import sys
import os.path
from types import ModuleType

PYTHON_EXTENSIONS = ".py", ".pyc", ".pyo", ".pyd"

def get_full_name(obj):
    """Obtains the canonical, fully qualified name of the provided python
    object.
    
    @param obj: The object to determine the name for.
    @type obj: Package, module, class, function or method

    @return: The qualified name of the object.
    @rtype: str

    @raise TypeError: Raised if the provided object is an instance of a type
        that doesn't map its instances to qualified names.
    """   
    if isinstance(obj, ModuleType):
        
        if obj.__name__ == "__main__":
            return get_path_name(sys.argv[0])
        else:
            return get_path_name(obj.__file__)
    else:
        module_name = getattr(obj, "__module__", None)
        
        if module_name:
            base_name = get_full_name(sys.modules[module_name])

            # Classes
            if isinstance(obj, type):
                return base_name + "." + obj.__name__
            
            # Methods
            im_func = getattr(obj, "im_func", None)
            im_class = getattr(obj, "im_class", None)

            if im_func and im_class:
                return "%s.%s.%s" \
                    % (base_name, im_class.__name__, im_func.func_name)

            # Functions
            func_name = getattr(obj, "func_name", None)

            if func_name:
                return base_name + "." + func_name

    raise TypeError("Can't find the path of %r" % obj)

def get_path_name(path):
    """Gets the qualified name of the module or package that maps to the
    indicatedfile or folder.
    
    @param path: The path to the file or folder to evaluate.
    @type path: str

    @return: The fully qualified name of the package or module at the indicated
        location.

    @raise ValueError: Raised if the indicated path doesn't map to a python
        module or package.
    """
    components = []

    # Normalize the path
    path = os.path.abspath(path)

    if path[-1] == os.path.sep:
        path = path[:-1]

    # Descend the filesystem hierarchy
    while path:

        parent_path, path_component = os.path.split(path)
                        
        # Modules
        if os.path.isfile(path):
        
            fname, ext = os.path.splitext(path_component)

            if ext not in PYTHON_EXTENSIONS:
                raise ValueError(
                    "%r doesn't map to a python module or package"
                    % path
                )

            if fname != "__init__":
                components.append(fname)
        
        # Packages
        elif os.path.isdir(path):
            
            if any(
                os.path.isfile(os.path.join(path, "__init__" + ext))
                for ext in PYTHON_EXTENSIONS
            ):
                components.append(path_component)
            else:
                break
        else:
            raise ValueError(
                "Error resolving the python name for path %r: "
                "wrong path"
                % path
            )

        path = parent_path                        

    return ".".join(reversed(components))

if __name__ == "__main__":
    pass

#    assert get_path_name("/home/marti/Projectes/magicbullet") == "magicbullet"
#    assert get_path_name("/home/marti/Projectes/magicbullet/") == "magicbullet"
#    assert get_path_name("/home/marti/Projectes/magicbullet/__init__.py") == "magicbullet"
#    assert get_path_name("/home/marti/Projectes/magicbullet/modeling.py") == "magicbullet.modeling"
#    assert get_path_name("/home/marti/Projectes/magicbullet/schema") == "magicbullet.schema"
#    assert get_path_name("/home/marti/Projectes/magicbullet/schema/") == "magicbullet.schema"
#    assert get_path_name("/home/marti/Projectes/magicbullet/schema/__init__.py") == "magicbullet.schema"
#    assert get_path_name("/home/marti/Projectes/magicbullet/schema/schema.py") == "magicbullet.schema.schema"

