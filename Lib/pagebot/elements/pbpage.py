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
#     page.py
#
import weakref
from pagebot.elements.element import Element
from pagebot.toolbox.transformer import pointOffset
from pagebot.style import ORIGIN

class Page(Element):
    u"""The Page container is typically the root of a tree of Element instances.
    A Document contains a set of pages. 
    Since pages an build into fixed media, such as PDF, PNG and animated GIF, as well
    as HTML pages in a site, there is a mixture of meta data availalbe in a Page.

    """

    isPage = True

    VIEW_PORT = "width=device-width, initial-scale=1.0, user-scalable=yes"
    FAVICON_PATH = 'images/favicon.ico'
    INDEX_HTML = 'index.html'
    INDEX_HTML_URL = INDEX_HTML

    def __init__(self, leftPage=None, rightPage=None, 
        htmlCode=None, htmlPath=None, headCode=None, headPath=None, bodyCode=None, bodyPath=None,
        cssCode=None, cssPath=None, cssUrls=None, jsCode=None, jsPath=None, jsUrls=None,
        viewPort=None, favIconUrl=None, fileName=None, url=None, webFontUrls=None,
        **kwargs):  

        u"""Add specific parameters for a page, besides the parameters for standard Elements.

        >>> page = Page()
        >>> page.w, page.h
        (100, 100)
        >>> page.w = 1111
        >>> page.w, page.h
        (1111, 100)
        """
        Element.__init__(self,  **kwargs)
        self.cssClass = self.cssClass or 'page' # Defined default CSS class for pages.
        self._isLeft = leftPage # Undefined if None, let self.doc decide instead
        self._isRight = rightPage 

        # Site stuff
        self.viewPort = viewPort or self.VIEW_PORT
        self.appleTouchIconUrl = None
        self.favIconUrl = favIconUrl or self.FAVICON_PATH

        self.fileName = fileName or self.INDEX_HTML
        self.url = url or self.INDEX_HTML_URL # Used for links to home or current page url

        # Optional resources to be included
        # Define string or file paths where to read content, instead of constructing by the builder.
        self.htmlCode = htmlCode # Set to string in case the full HTML is defined in a single file.
        self.htmlPath = htmlPath # Set to string in case the full HTML is defined in a single file.

        self.headCode = headCode # Optional set to string that contains the page <head>...</head>, excluding the tags.
        self.headPath = headPath # Set to path, if head is available in a single file, excluding the tags.
        
        self.cssCode = cssCode # Set to string, if CSS is available as single source. Exported as css file once.
        self.cssPath = cssPath # Set to path, if CSS is available in a single file to be included in the page.
        self.cssUrls = cssUrls # Optional CSS, if different from what is defined by the view. 

        self.bodyCode = bodyCode # Optional set to string that contains the page <body>...</body>, excluding the tags.
        self.bodyPath = bodyPath # Set to path, if body is available in a single file, excluding the tags.

        self.jsCode = jsCode # Set to path, if JS is available in a single file, excluding the tags.
        self.jsPath = jsPath # Optional javascript, to be added at the end of the page, inside <body>...</body> tag.
        self.jsUrls = jsUrls # Optional Javascript Urls, if different from what is defined by the view.

        self.webFontUrls = webFontUrls # Optional set of webfont urls if different from what is in the view.


    def _get_isLeft(self):
        u"""Answer the boolean flag if this is a left page, if that info is stored. 
        Note that pages can be neither left or right.
        Otherwise, the only one who can know that is the document.

        >>> from pagebot.document import Document
        >>> doc = Document(name='TestDoc', autoPages=8)
        >>> page = doc[5]
        >>> page.isLeft
        False
        >>> page.isLeft = True
        >>> page.isLeft
        True
        """
        if self._isLeft is not None:
            return self._isLeft   
        if self.doc is not None:
            return self.doc.isLeftPage(self) # If undefined, query parent document to decide.
        return None
    def _set_isLeft(self, flag):
        self._isLeft = flag
    isLeft = property(_get_isLeft, _set_isLeft)

    def _get_isRight(self):
        u"""Answer the boolean flag if this is a right page, if that info is stored. 
        Note that pages can be neither left or right.
        Otherwise, the only one who can know that is the document.

        >>> from pagebot.document import Document
        >>> doc = Document(name='TestDoc', autoPages=8)
        >>> page = doc[5]
        >>> page.isLeft
        False
        >>> page.isLeft = True
        >>> page.isLeft
        True
        """
        if self._isLeft is not None:
            return self._isLeft   
        if self.doc is not None:
            return self.doc.isLeftPage(self) # If undefined, query parent document to decide.
        return None
    def _set_isRight(self, flag):
        self._isRight = flag
    isRight = property(_get_isRight, _set_isRight)

    #   D R A W B O T  & F L A T  S U P P O R T

    def build(self, view, origin=ORIGIN, drawElements=True):
        u"""Draw all elements of this page in DrawBot."""
        p = pointOffset(self.oPoint, origin) # Ignoe z-axis for now.
        # If there are child elements, draw them over the text.
        if drawElements:
            self.buildChildElements(view, p) # Build child elements, depending in context build implementations.
        # Draw addition page info, such as crop-mark, registration crosses, etc. if parameters are set.
        view.drawPageMetaInfo(self, origin)
        # Check if we are in scaled mode. Then restore.
        #self._restoreScale()

    #   H T M L  /  C S S  S U P P O R T

    def build_html(self, view, origin=None, drawElements=True):
        u"""Build the HTML/CSS code through WebBuilder (or equivalent) that is the closest representation 
        of self. If there are any child elements, then also included their code, using the
        level recursive indent.

        Single page site, exporting to html source, with CSS inside.
        >>> import os
        >>> from pagebot.document import Document
        >>> doc = Document(name='SinglePageSite', viewId='Site')
        >>> page = doc[1]
        >>> page.title = 'Home'
        >>> page.cssCode = 'body {background-color:black}'
        >>> exportPath = '_export/Home' # No extension for site folder if exporting to a website
        >>> doc.export(exportPath)
        >>> result = os.system('open %s/index.html' % exportPath)
        """
        context = view.context # Get current context and builder from this view.
        b = context.b # This is a bit more efficient than self.b once we got the context fixed.
       
        if self.htmlPath is not None:
            b.importHtml(self.htmlPath) # Add HTML content of file, if path is not None and the file exists.
        else:
            b.docType('html')
            b.html()#lang="%s" itemtype="http://schema.org/">\n' % self.css('language'))
            #
            #   H E A D
            #
            # Build the page head. There are 3 option (all not including the <head>...</head>)
            # 1 As html string (info.headHtml is defined as not None)
            # 2 As path a html file, containing the string between <head>...</head>.
            # 3 Constructed from info contect, page attributes and styles.
            #
            b.head()
            if self.headCode is not None:
                b.addHtml(self.headCode)
            elif self.headPath is not None:
                b.importHtml(self.headPath) # Add HTML content of file, if path is not None and the file exists.
            else:
                b.meta(charset=self.css('encoding'))
                # Try to find the page name, in sequence order of importance. 
                b.title_(self.title or self.name)
                
                # Devices
                if self.viewPort is not None: # Not supposed to be None. Check anyway
                    b.meta(name='viewport', content=self.viewPort) 

                # View and pages can both implements Javascript paths
                for jsUrls in (view.jsUrls, self.jsUrls):
                    if jsUrls is not None:
                        for jsUrl in jsUrls.values():
                            b.script(type="text/javascript", src=jsUrl)

                # View and pages can both implements Webfonts urls
                for webFontUrls in (view.webFontUrls, self.webFontUrls):
                    if webFontUrls is not None:
                        for webFontUrl in webFontUrls:
                            b.link(rel='stylesheet', type="text/css", href=webFontUrl, media='all')
                
                # View and pages can both implements CSS paths
                for cssUrls in (view.cssUrls, self.cssUrls):
                    if cssUrls is not None:
                        for cssUrl in cssUrls:
                            b.link(rel='stylesheet', href=cssUrl, type='text/css', media='all')

                # In case CSS needs to copied into the page.
                if self.cssCode is not None:
                    # Add the code directly into the page if it is not None
                    b.style()
                    b.addCss(self.cssCode)
                    b._style()
                if self.cssPath is not None:
                    # Include CSS content of file, if path is not None and the file exists.
                    b.style()
                    b.importCss(self.cssPath) 
                    b._style()

                # Icons
                if self.favIconUrl: # Add the icon link and let the type follow the image extension.
                    b.link(rel='icon', href=self.favIconUrl, type='image/%s' % self.favIconUrl.split('.')[-1])
                if self.appleTouchIconUrl: # Add the icon link and let the type follow the image extension.
                    b.link(rel='apple-touch-icon-precomposed', href=self.appleTouchIconUrl, type='image/%s' % self.appleTouchIconUrl.split('.')[-1])
                
                # Description and keywords
                if self.description:
                    b.meta(name='description', content=self.description)
                if self.keyWords:
                    b.meta(name='keywords', content=self.keyWords)
            b._head()
            #
            #   B O D Y
            #
            # Build the page body. There are 3 option (all excluding the <body>...</body>)
            # 1 As html string (self.bodyCode is defined as not None)
            # 2 As path a html file, containing the string between <body>...</body>, excluding the tags
            # 3 Constructed from view parameter context, page attributes and styles.
            #
            b.body()
            if self.bodyCode is not None:
                b.addHtml(self.bodyCode)
            elif self.bodyPath is not None:
                b.importHtml(self.bodyPath) # Add HTML content of file, if path is not None and the file exists.
            else:
                b.div(cssClass=self.cssClass) # Class is standard 'page' if self.cssClass is undefined as None.
                if drawElements:
                    for e in self.elements:
                        e.build_html(view, origin)
                b._div()
            #
            #   J A V A S C R I P T
            #
            # Build the LS body. There are 3 option (all not including the <body>...</body>)
            # 1 As html string (info.headHtmlCode is defined as not None)
            # 2 As path a html file, containing the string between <head>...</head>.
            # 3 Constructed from info contect, page attributes and styles.
            #
            if self.jsCode is not None:
                b.addHtml(self.jsCode)
            if self.jsPath is not None:
                b.importHtml(self.jsPath) # Add JS content of file, if path is not None and the file exists.
            if b.hasJs():
                b.script()
                b.addHtml('\n'.join(b.getJs()))
                b._script()
            #else no default JS. To be added by the calling application.

            # Close the document
            b._body()
            b._html()

class Template(Page):

    def _get_parent(self):
        u"""Answer the parent of the element, if it exists, by weakref reference. Answer None of there
        is not parent defined or if the parent not longer exists."""
        if self._parent is not None:
            return self._parent()
        return None
    def _set_parent(self, parent):
        u"""Set the parent of the template. Don't call self.appendParent here, as we don't want the 
        parent to add self to the page/element list. Just a simple reference, to connect to styles, etc."""
        if parent is not None:
            parent = weakref.ref(parent)
        self._parent = parent
    parent = property(_get_parent, _set_parent)

 
    def draw(self, origin, view):
        raise ValueError('Templates cannot draw themselves in a view. Apply the template to a page first.')


if __name__ == "__main__":
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
