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
#     indesigncontext.py
#
#     Version 0.1
#
#     Documentation for InDesign API is here.
#     https://www.adobe.com/devnet/indesign/documentation.html
#     https://wwwimages2.adobe.com/content/dam/acom/en/devnet/indesign/sdk/cs6/scripting/InDesign_ScriptingGuide_JS.pdf
#
import os

from pagebot.contexts.basecontext import BaseContext
from pagebot.contexts.builders.indesignbuilder import InDesignBuilder
from pagebot.contexts.strings.babelstring import BabelString
from pagebot.constants import LEFT, CENTER, RIGHT, DEFAULT_FONT_PATH, DEFAULT_FONT_SIZE

class InDesignContext(BaseContext):
    u"""A InDesignContext instance combines the specific functions of the InDesign JS-API
    This way it way it hides e.g. the type of BabelString
    """

    # In case of specific builder addressing, callers can check here.
    isInDesign = True

    # Used by the generic BaseContext.newString( )
    STRING_CLASS = BabelString
    EXPORT_TYPES = ('indd.js',)

    def __init__(self):
        u"""Constructor of InDesignContext.

        >>> context = InDesignContext()
        >>> context.isInDesign
        True
        """
        self.b = InDesignBuilder() # cls.b builder for this canvas.
        self.name = self.__class__.__name__
        self._path = None # Hold current open polygon path

        self._fill = None
        self._stroke = None
        self._strokeWidth = 0
        self._font = DEFAULT_FONT_PATH # Optional setting of the current font and fontSize
        self._fontSize = DEFAULT_FONT_SIZE
        self._frameDuration = 0
        self._ox = 0 # Origin set by self.translate()
        self._oy = 0
        self._rotate = 0
        self._hyphenation = None
        self._openTypeFeatures = None

        self._gState = [] # Stack of graphic states.
        self.save() # Save current set of values on gState stack.

    #   S C R E E N

    def screenSize(self):
        u"""Answer the current screen size. Otherwise default is to do nothing."""
        return None

    #   D O C U M E N T

    def newDocument(self, w, h, title=None, pageCount=None, units='pt'):
        u"""Create a new document"""
        self.title = title
        self.pageCount = pageCount
        self.units = units
        self.b.newDocument(w, h, title, pageCount)

    def saveDocument(self, path, multiPage=None):
        u"""Select other than standard InDesign export builders here.
        Save the current image as path, rendering depending on the extension of the path file.
        In case the path starts with "_export", then create it directories.

        >>> from pagebot.constants import A4Rounded
        >>> H, W = A4Rounded # Initialize as landscape
        >>> context = InDesignContext() 
        >>> context.newDocument(W, H)       
        >>> context.saveImage('_export/MyFile.'+context.EXPORT_TYPES[0])

        """
        if not path.endswith(self.EXPORT_TYPES[0]):
            path += '.'+self.EXPORT_TYPES[0]
        self.checkExportPath(path)
        self.b.writeJs(path)

    saveImage = saveDocument # Compatible API with InDesign

    def newPage(self, w, h):
        u"""Create a new InDesign page.

        >>> context = InDesignContext()
        >>> context.newPage(100, 100)
        """
        self.b.newPage(w, h)

    def newDrawing(self):
        u"""Clear output canvas, start new export file.

        >>> context = InDesignContext()
        >>> context.newDrawing()
        """
        self.b.newDrawing()

    #   V A R I A B L E

    def Variable(self, variableUI , globalVariables):
        """Offers interactive global value manipulation in InDesignContext. 
        Probably to be ignored in other contexts."""
        pass

    #   D R A W I N G

    def rect(self, x, y, w, h):
        u"""Draw a rectangle in the canvas.

        >>> context = InDesignContext()
        >>> context.rect(0, 0, 100, 100)
        """
        self.b.rect(x, y, w, h)

    def oval(self, x, y, w, h):
        u"""Draw an oval in rectangle, where (x,y) is the bottom-left and size (w,h).

        >>> context = InDesignContext()
        >>> context.oval(0, 0, 100, 100)
        """
        self.b.oval(x, y, w, h)

    def circle(self, x, y, r):
        u"""Circle draws an InDesign oval with (x,y) as middle point and radius r."""
        self.b.oval(x-r, y-r, r*2, r*2)

    def line(self, p1, p2):
        u"""Draw a line from p1 to p2.

        >>> context = InDesignContext()
        >>> context.line((100, 100), (200, 200))
        """
        self.b.line(p1, p2)

    def newPath(self):
        u"""Make a new InDesign Bezierpath to draw in.

        >>> context = InDesignContext()
        >>> context.path is not None
        True
        """
        self._path = self.b.BezierPath()
        return self._path

    def _get_path(self):
        u"""Answer the open drawing path. Create one if it does not exist.

        >>> context = InDesignContext()
        >>> context.path is not None
        True
        """
        if self._path is None:
            self.newPath()
        return self._path
    path = property(_get_path)

    def drawPath(self, path=None, p=(0,0), sx=1, sy=None):
        u"""Draw the path, or equivalent in other contexts. Scaled image is drawn on (x, y),
        in that order."""
        if path is None:
            path = self._path
        if path is not None:
            self.save()
        if sy is None:
            sy = sx
            #self.scale(sx, sy)
            #self._translate(p[0]/sx, p[1]/sy)
            #self.b.drawPath(path)
            #self.restore()

    def moveTo(self, p):
        u"""Move to point p. Create a new path if none is open.

        >>> context = InDesignContext()
        >>> path = context.newPath()
        >>> path.moveTo((100, 100))
        """
        if self._path is None:
            self.newPath()
        self._path.moveTo((p[0], p[1]))

    def lineTo(self, p):
        u"""Line to point p. Create a new path if none is open.

        >>> context = InDesignContext()
        >>> # Draw directly on th epath
        >>> # Draw on the context cached path
        >>> _ = context.newPath()
        >>> context.moveTo((100, 100))
        >>> context.curveTo((100, 200), (200, 200), (200, 100))
        >>> context.closePath()
        >>> path = context.newPath()
        >>> path.moveTo((100, 100))
        >>> path.curveTo((100, 200), (200, 200), (200, 100))
        >>> path.closePath()
        >>> context.drawPath(path)
        """
        if self._path is None:
            self.newPath()
        self._path.lineTo((p[0], p[1]))

    def quadTo(bcp, p):
        # TODO: Convert to Bezier with 0.6 rule
        pass

    def curveTo(self, bcp1, bcp2, p):
        u"""Curve to point p. Create a new path if none is open.

        >>> context = InDesignContext()
        >>> # Draw directly on th epath
        >>> # Draw on the context cached path
        >>> _ = context.newPath()
        >>> context.moveTo((100, 100))
        >>> context.curveTo((100, 200), (200, 200), (200, 100))
        >>> context.closePath()
        >>> path = context.newPath()
        >>> path.moveTo((100, 100))
        >>> path.curveTo((100, 200), (200, 200), (200, 100))
        >>> path.closePath()
        """
        if self._path is None:
            self.newPath()
        self._path.curveTo((bcp1[0], bcp1[1]), (bcp2[0], bcp2[1]), (p[0], p[1]))

    def closePath(self):
        u"""Curve to point p. Create a new path if none is open.

        >>> context = InDesignContext()
        >>> # Draw directly on th epath
        >>> # Draw on the context cached path
        >>> _ = context.newPath()
        >>> context.moveTo((100, 100))
        >>> context.curveTo((100, 200), (200, 200), (200, 100))
        >>> context.closePath()
        >>> path = context.newPath()
        >>> path.moveTo((100, 100))
        >>> path.curveTo((100, 200), (200, 200), (200, 100))
        >>> path.closePath()
        """
        if self._path is not None:
            self._path.closePath()

    def bezierPathByFlatteningPath(self, path):
        u"""Use the NSBezier flatten path."""
        return path.getNSBezierPath().bezierPathByFlatteningPath()

    def scale(self, sx, sy=None):
        u"""Set the drawing scale."""
        if sy is None:
            sy = sx
        self.b.scale(sx, sy)

    def translate(self, dx, dy):
        u"""Translate the origin to this point."""
        self.b.translate(dx, dy)

    def transform(self, t):
        u"""Transform canvas over matrix t, e.g. (1, 0, 0, 1, dx, dy) to shift over vector (dx, dy)"""
        self.b.transform(t)

    #   G R A D I E N T  &  S H A D O W

    def setShadow(self, eShadow):
        u"""Set the InDesign graphics state for shadow if all parameters are set."""
        if eShadow is not None and eShadow.offset is not None:
            if eShadow.cmykColor is not None:
                self.b.shadow(eShadow.offset,
                              blur=eShadow.blur,
                              color=eShadow.cmykColor)
            else:
                self.b.shadow(eShadow.offset,
                              blur=eShadow.blur,
                              color=eShadow.color)

    def setGradient(self, gradient, origin, w, h):
        u"""Define the gradient call to match the size of element e., Gradient position
        is from the origin of the page, so we need the current origin of e."""
        b = self.b
        start = origin[0] + gradient.start[0] * w, origin[1] + gradient.start[1] * h
        end = origin[0] + gradient.end[0] * w, origin[1] + gradient.end[1] * h

        if gradient.linear:
            if gradient.cmykColors is None:
                b.linearGradient(startPoint=start, endPoint=end,
                    colors=gradient.colors, locations=gradient.locations)
            else:
                b.cmykLinearGradient(startPoint=start, endPoint=end,
                    colors=gradient.cmykColors, locations=gradient.locations)
        else: # Gradient must be radial.
            if gradient.cmykColors is None:
                b.radialGradient(startPoint=start, endPoint=end,
                    colors=gradient.colors, locations=gradient.locations,
                    startRadius=gradient.startRadius, endRadius=gradient.endRadius)
            else:
                b.cmykRadialGradient(startPoint=start, endPoint=end,
                    colors=gradient.cmykColors, locations=gradient.locations,
                    startRadius=gradient.startRadius, endRadius=gradient.endRadius)

    def lineDash(self, *lineDash):
        self.b.lineDash(*lineDash)

    def miterLimit(self, value):
        self.b.miterLimit(value)

    def lineJoin(self, value):
        """option value"""
        self.b.lineJoin(value)

    def lineCap(self, value):
        """Possible values are butt, square and round."""
        self.b.lineCap(value)

    #   C A N V A S

    def saveGraphicState(self):
        u"""Save the current graphic state.

        >>> from pagebot.fonttoolbox.objects.font import findFont
        >>> context = InDesignContext()
        >>> context._font.endswith('Roboto-Regular.ttf')
        True
        >>> context.save()
        >>> boldFont = findFont('Roboto-Bold')
        >>> context.font(boldFont) # Set by Font instance
        >>> context._font.path.endswith('Roboto-Bold.ttf')
        True
        >>> context.restore() # Restore to original graphic state values
        >>> context._font.endswith('Roboto-Regular.ttf')
        True
        """
        gState = dict(
            font=self._font,
            fontSize=self._fontSize,
            fill=self._fill,
            stroke=self._stroke,
            strokeWidth=self._strokeWidth,
            ox=self._ox,
            oy=self._oy,
            rotate=self._rotate,
            hyphenation=self._hyphenation,
            openTypeFeatures=self._openTypeFeatures,
        )
        self._gState.append(gState)

    save = saveGraphicState

    def restoreGraphicState(self):
        gState = self._gState.pop()
        self._font = gState['font']
        self._fontSize = gState['fontSize']
        self._fill = gState['fill']
        self._stroke = gState['stroke']
        self._strokeWidth = gState['strokeWidth']
        self._ox = gState['ox']
        self._oy = gState['oy']
        self._rotate = gState['rotate']
        self._hyphenation = gState['hyphenation']
        self._openTypeFeatures = gState['openTypeFeatures']
    restore = restoreGraphicState

    #   F O N T S

    def listOpenTypeFeatures(self, fontName):
        u"""Answer the list of opentype features available in the named font."""
        return [] #self.b.listOpenTypeFeatures(fontName)

    #   G L Y P H

    def drawGlyphPath(self, font, glyphName, x, y, fillColor=0, strokeColor=None, strokeWidth=0, fontSize=None, xAlign=CENTER):
        u"""Draw the font[glyphName] at the defined position with the defined fontSize.

        """
        s = fontSize/font.info.unitsPerEm
        glyph = font[glyphName]
        if xAlign == CENTER:
            x -= (glyph.width or 0)/2*s
        elif xAlign == RIGHT:
            x -= glyph.width*s
        self.save()
        self.setFillColor(fillColor)
        self.setStrokeColor(strokeColor, strokeWidth)
        self.transform((1, 0, 0, 1, x, y))
        self.scale(s)
        self.drawPath(glyph.path)
        self.restore()

    #   T E X T

    def fontSize(self, fontSize):
        u"""Set the font size in the context.

        >>> context = InDesignContext()
        >>> context.fontSize(12)
        >>> context._fontSize
        12
        """
        self._fontSize = fontSize

    def font(self, font, fontSize=None):
        self._font = font
        if fontSize is not None:
            self._fontSize = fontSize

    def newBulletString(self, bullet, e=None, style=None):
        return self.newString(bullet, e=e, style=style)

    def text(self, sOrBs, p):
        u"""Draw the sOrBs text string, can be a str or BabelString, including a InDesign FormattedString
        at position p."""
        if not isinstance(sOrBs, str):
            sOrBs = sOrBs.s # Assume here is's a BabelString with a FormattedString inside.
        self.b.text(sOrBs, p)

    def textBox(self, sOrBs, r):
        u"""Draw the sOrBs text string, can be a str or BabelString, including a InDesign FormattedString
        in rectangle r."""
        if not isinstance(sOrBs, str):
            sOrBs = sOrBs.s # Assume here is's a BabelString with a FormattedString inside.
        self.b.textBox(sOrBs, r)

    def textSize(self, bs, w=None, h=None):
        u"""Answer the size tuple (w, h) of the current text. Answer (0, 0) if there is no text defined.
        Answer the height of the string if the width w is given."""
        if w is not None:
            return self.b.textSize(bs.s, width=w)
        if h is not None:
            return self.b.textSize(bs.s, height=h)
        return self.b.textSize(bs.s)

    def textOverflow(self, bs, bounds, align=LEFT):
        u"""Answer the overflowing of from the box (0, 0, w, h)
        as new InDesignString in the current context."""
        return stringClass(self.b.textOverflow(bs.s, bounds, align), self)

    def openTypeFeatures(self, features):
        u"""Set the current of opentype features in the context canvas.

        >>> context = InDesignContext()
        >>> context.openTypeFeatures(dict(smcp=True, zero=True))
        """
        self._openTypeFeatures = features

    def hyphenation(self, onOff=True):
        u"""Set the hyphenation on/off flag.

        >>> context = InDesignContext()
        >>> context.hyphenation(True)
        >>> context.hyphenation(False)
        """
        self._hyphenation = onOff

    #   A N I M A T I O N

    def frameDuration(self, secondsPerFrame):
        u"""Nothing to do in InDesignContext."""
        
    #   C O L O R

    def setTextFillColor(self, fs, c, cmyk=False):
        self.setFillColor(c, cmyk, fs)

    def setTextStrokeColor(self, fs, c, w=1, cmyk=False):
        self.setStrokeColor(c, w, cmyk, fs)

    def setFillColor(self, c, cmyk=False, b=None):
        u"""Set the color for global or the color of the formatted string."""
        if b is None: # Builder can be optional InDesign FormattedString
            b = self.b
        if c is NO_COLOR:
            pass # Color is undefined, do nothing.
        elif c is None or isinstance(c, (float, int)): # Because None is a valid value.
            if cmyk:
                b.cmykFill(c)
            else:
                b.fill(c)
        elif isinstance(c, (list, tuple)) and len(c) in (3, 4):
            if cmyk:
                b.cmykFill(*c)
            else:
                b.fill(*c)
        else:
            raise ValueError('InDesignContext.setFillColor: Error in color format "%s"' % repr(c))

    fill = setFillColor # InDesign compatible API

    def strokeWidth(self, w):
        u"""Set the current stroke width."""
        self.b.strokeWidth(w)

    def setStrokeColor(self, c, w=1, cmyk=False, b=None):
        u"""Set global stroke color or the color of the formatted string."""
        if b is None: # Builder can be optional InDesign FormattedString
            b = self.b
        if c is NO_COLOR:
            pass # Color is undefined, do nothing.
        elif c is None or isinstance(c, (float, int)): # Because None is a valid value.
            if cmyk:
                b.cmykStroke(c)
            else:
                b.stroke(c)
        elif isinstance(c, (list, tuple)) and len(c) in (3, 4):
            if cmyk:
                b.cmykStroke(*c)
            else:
                b.stroke(*c)
        else:
            raise ValueError('InDesignContext.setStrokeColor: Error in color format "%s"' % repr(c))
        if w is not None:
            b.strokeWidth(w)

    stroke = setStrokeColor # InDesign compatible API

    def rotate(self, angle):
        u"""Rotate the canvas by angle."""
        self.b.rotate(angle)

    #   I M A G E

    def imagePixelColor(self, path, p):
        return self.b.imagePixelColor(path, p)

    def imageSize(self, path):
        u"""Answer the (w, h) image size of the image file at path."""
        return self.b.imageSize(path)

    def image(self, path, p, alpha=1, pageNumber=None, w=None, h=None):
        u"""Draw the image. If w or h is defined, then scale the image to fit."""
        iw, ih = self.imageSize(path)
        if w and not h: # Scale proportional
            h = ih * w/iw # iw : ih = w : h
        elif not w and h:
            w = iw * h/ih
        elif not w and not h:
            w = iw
            h = ih
        # else both w and h are defined, scale disproportional
        x, y, = p[0], p[1]
        sx, sy = w/iw, h/ih
        self.save()
        self.scale(sx, sy)
        self.b.image(path, (x*sx, y*sy), alpha=alpha, pageNumber=pageNumber)
        self.restore()

    def getImageObject(self, path):
        u"""Answer the ImageObject that knows about image filters.

        >>> from pagebot import getResourcesPath
        >>> from pagebot.contexts.indesigncontext import InDesignContext
        >>> context = InDesignContext()
        >>> path = getResourcesPath() + '/images/peppertom_lowres_398x530.png'
        >>> imo = context.getImageObject(path)

        """
        #return self.b.ImageObject(path)


if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
