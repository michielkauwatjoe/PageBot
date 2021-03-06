#!/usr/bin/env python
# -----------------------------------------------------------------------------
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens & Font Bureau
#     www.pagebot.io
#
#     P A G E B O T
#
#     Licensed under MIT conditions
#
#     Supporting usage of DrawBot, www.drawbot.com
#     Supporting usage of Flat, https://github.com/xxyxyz/flat
# -----------------------------------------------------------------------------
#
#     typespecimen.py
#
#     Generic Type Specimen Publiction. Use straight, if the default behavior
#     and templates are good enough. Inherit the redefine functions and templates
#     otherwise. Example of an inherited publications is FBFamilySpecimen.py
#
# Publication (inheriting from Document) is the main instance holding all information 
# about the document together (pages, styles, etc.)
from pagebot.publications.publication import Publication 

# Page and Template instances are holding all elements of a page together.
# And import all other element constructors.
#from pagebot.elements import *

# Import conditions for layout placements and other element status.
#from pagebot.conditions import *
 
class TypeSpecimen(Publication):
    pass
    
if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
