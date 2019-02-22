#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
A script that imports a set of local files as CMS items.
"""
from sys import argv, exit
from glob import glob
from cocktail.pkgutils import resource_filename
from cocktail.styled import styled
from cocktail.persistence import datastore
from woost.models import File
import --SETUP-PACKAGE--

def main():

    params = argv[1:]

    if not params:
        print "Usage: %s filelist" % argv[0]
        exit(1)

    for param in params:
        for path in glob(param):
            print "Importing " + styled(path, style = "bold") + "...",
            try:
                file = File.from_path(
                    path,
                    resource_filename("--SETUP-PACKAGE--", "upload")
                )
                file.insert()
            except Exception, ex:
                print styled(str(ex), "red")
            else:
                print styled("File #" + str(file.id), "green")

    datastore.commit()

if __name__ == "__main__":
    main()

