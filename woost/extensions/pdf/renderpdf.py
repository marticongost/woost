#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import sys
import pdfkit

def main():

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: %s URL DEST\n" % sys.argv[0])
        sys.exit(1)

    url = sys.argv[1]
    dest = sys.argv[2]
    pdfkit.from_url(url, dest)

if __name__ == "__main__":
    main()

