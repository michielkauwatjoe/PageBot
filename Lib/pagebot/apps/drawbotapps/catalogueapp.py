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
#     catalogueapp.py
#
from pagebot.apps.drawbotapps.baseapp import BaseApp
from pagebot.publications.catalogue import Catalogue

class CatalogueApp(BaseApp):
    u"""Will be developed."""
    PUBLICATION_CLASS = Catalogue

if __name__ == '__main__':
    app = CatalogueApp()
    app.build()

