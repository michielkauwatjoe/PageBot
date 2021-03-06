#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#     P A G E B O T
#
#     Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens & Font Bureau
#     www.pagebot.io
#     Licensed under MIT conditions
#
#     Supporting usage of DrawBot, www.drawbot.com
#     Supporting usage of Flat, https://github.com/xxyxyz/flat
# -----------------------------------------------------------------------------
#
#     basesite.py
#
from __future__ import division # Make integer division result in float.

from pagebot.publications.publication import Publication

class BaseSite(Publication):
    u"""Build a basic website to show the core principles.

    >>> doc = BaseSite(name='Home', padding=30, viewId='Mamp')
    >>> view = doc.view
    >>> page = doc[1]
    >>> doc.export()
    """

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
