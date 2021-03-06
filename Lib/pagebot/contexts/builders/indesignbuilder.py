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
#     Supporting usage of InDesign API-scripting
# -----------------------------------------------------------------------------
#
#     indesignbuilder.py
#
#     Version 0.1
#
#     Documentation for InDesign API is here.
#     https://www.adobe.com/devnet/indesign/documentation.html
#     https://wwwimages2.adobe.com/content/dam/acom/en/devnet/indesign/sdk/cs6/scripting/InDesign_ScriptingGuide_JS.pdf
#
import os
import codecs
from pagebot.contexts.builders.basebuilder import BaseBuilder
from pagebot.toolbox.transformer import value2Bool
from pagebot.toolbox.dating import now
from pagebot.toolbox.units import UNIT_PT
from pagebot.toolbox.color import Color
from pagebot.toolbox.transformer import object2SpacedString, asFormatted
from pagebot.constants import A4Rounded

class BezierPath(object):
    u"""Make BezierPath with the same API for DrawBotBuilder drawing.

    >>> from pagebot.contexts.builders.indesignbuilder import InDesignBuilder
    >>> indesignBuilder = InDesignBuilder()
    >>> path = BezierPath(indesignBuilder)
    >>> path.moveTo((0, 0))
    >>> path.lineTo((0, 100))
    >>> path.lineTo((100, 100))
    >>> path.lineTo((100, 0))
    >>> path.lineTo((0, 0))
    >>> path.closePath()

    """
    def __init__(self, b):
        self.b = b
        self.commands = []

    def append(self, command):
        self.commands.append(command)

    def moveTo(self, p):
        pass

    def lineTo(self, p):
        pass

    def quadTo(self, bcp, p):
        pass

    def curveTo(self, bcp1, bcp2, p):
        pass

    def closePath(self):
        pass
        # TODO Seems to be a problem in direct closing, not storing as command?
        #self.commands.append(self.b.closepath

    def appendPath(self, path):
        self.commands += path.commands

        
class InDesignBuilder(BaseBuilder):
    """
    The InDesignBuilder class implements the all necessary API-Javascript to communicate with InDesign. 

    >>> import os
    >>> W, H = A4Rounded
    >>> b = InDesignBuilder()
    >>> b.compact = True
    >>> b.newDocument(W, H, 'My Document', 23, 'pt')
    >>> b.getJs(newLine=False).startswith('/* Created by PageBot */')
    True
    >>> b.newPage()
    >>> b.oval(100, 100, 200, 200)
    >>> scriptPath = '_export/InDesign.indd.js'
    >>> b.writeJs(scriptPath)
    >>> inDesignPath = '/Applications/Adobe InDesign CC 2018/Adobe InDesign CC 2018.app/Contents/MacOS/Adobe InDesign CC 2018'
    >>> #if os.path.exists(indesignPath):
    >>> #    os.system('%s %s' % (inDesignPath, scriptPath))
    """
    PB_ID = 'indesign' # Id to make build_indesign hook name. Views will be calling e.build_html()
    
    def __init__(self):
        self.title = None
        self._jsOut = []
        self._initialize()
        self.w, self.h = A4Rounded
        self._path = None
        self._hyphenation = False
        self.units = UNIT_PT 

    def _initialize(self):
        self.comment('Created by PageBot')

    #   Chunks of InDesign functions

    def newDocument(self, w, h):
        u"""Create a new document. Store the (w, h) for the moment that pages are created."""
        self.w = w
        self.h = h
        # Creates a new document without showing the document window.
        # The first parameter (showingWindow) controls the visibility of the document.
        # Hidden documents are not minimized, and will not appear until you add a new window to the document.
        if self.title:
            self.comment('--- %s ---' % (self.title or 'Untitled'))
        self.addJs('var myDocument = app.documents.add(false);') # Make document in background
        self.addJs('var myPage;') # Storage of current page
        self.addJs('var myElement;') # Storage of current parent element
        self.addJs('var myTextFrame;') # Storage of current text frame.
        self.comment('-'*60)
        self.addJs('with(myDocument.documentPreferences){')
        self.addJs('    pageWidth = "%s%s";' % (asFormatted(h), self.units))
        self.addJs('    pageHeight = "%s%s";' % (asFormatted(w), self.units))
        self.addJs('    pageOrientation = PageOrientation.%s;' % {False:'landscape', True:'portrait'}[w > h])
        #self.addJs('    pagesPerDocument = %d;' % pageCount)
        self.addJs('}')
        # To show the window
        # var myWindow = myDocument.windows.add();

    def newPage(self, w=None, h=None):
        self.addJs('myPage = myDocument.pages.add();')

    def newDrawing(self):
        pass

    def BezierPath(self):
        if self._path is None:
            self._path = BezierPath(self)
        return self._path

    #   E L E M E N T S

    def line(self, p1, p2):
        self.addJs('myElement = myPage.lines.add();')
      
    def oval(self, x, y, w, h):
        self.addJs('myElement = myPage.ellipses.add();')

    def rect(self, x, y, w, h):
        self.addJs('myElement = myPage.rects.add();')

    #   J S

    def addJs(self, js):
        self._jsOut.append(js)

    def hasJs(self):
        return len(self._jsOut)

    def importJs(self, path):
        u"""Import a chunk of UTF-8 CSS code from the path."""
        if os.path.exists(path):
            f = codecs.open(path, 'r', 'utf-8')
            self.addJs(f.read())
            f.close()
        else:
            self.comment('Cannot find JS file "%s"' % path)

    def copyPath(self, path):
        u"""Collect path of files to copy to the output website."""
        self._copyPaths.append(path)

    def getJs(self, newLine=True):
        u"""Answer the flat string of JS."""
        if newLine:
            newLine = '\n'
        else:
            newLine = ' '
        return newLine.join(self._jsOut)
    
    def writeJs(self, path):
        u"""Write the collected set of css JS to path."""
        try:
            f = codecs.open(path, 'w', 'utf-8')
            f.write(self.getJs())
            f.close()
        except IOError:
            print('[%s.writeCss] Cannot write JS file "%s"' % (self.__class__.__name__, path))

    # N O N - J S

    def comment(self, s):
        if s:
            self.addJs('/* %s */' % object2SpacedString(s))


if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
