# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#     P A G E B O T
#
#     Copyright (c) 2016+ Type Network, www.typenetwork.com, www.pagebot.io
#     Licensed under MIT conditions
#     Made for usage in DrawBot, www.drawbot.com
# -----------------------------------------------------------------------------
#
#     element.py
#
import weakref

from drawBot import rect, oval, line, newPath, moveTo, lineTo, drawPath, save, restore, scale, textSize, fill, text, stroke, strokeWidth

from pagebot.conditions.score import Score
from pagebot import getFormattedString, setFillColor, setStrokeColor, x2cx, cx2x, y2cy, cy2y, z2cz, cz2z, w2cw, cw2w, h2ch, ch2h, d2cd, cd2d
from pagebot.toolbox.transformer import point3D, pointOffset, uniqueID, point2D
from pagebot.style import makeStyle, ORIGIN_POINT, MIDDLE, CENTER, RIGHT, TOP, BOTTOM, LEFT, NO_COLOR, \
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEAULT_DEPTH, XXXL
from pagebot.toolbox.transformer import asFormatted

class Element(object):

    # Initialize the default Element behavior flags.
    # These flags can be overwritten by inheriting classes, or dynamically in instances,
    # e.g. where the settings of TextBox.nextBox and TextBox.nextPage define if a TextBox
    # instance can operate as a flow.
    isContainer = False
    isText = False
    isTextBox = False
    isFlow = False

    def __init__(self, point=None, parent=None, name=None, eId=None, style=None, **kwargs):  
        u"""Basic initialize for every Element constructor. Element always have a location, even if not defined here."""  
        assert point is None or isinstance(point, (tuple, list)), point
        self.point = point3D(point or ORIGIN_POINT) # Always store self._point position property as 3D-point (x, y, z). Missing values are 0
        self.style = makeStyle(style, **kwargs)
        self.name = name
        self.eId = eId or uniqueID(self)
        self.parent = parent # Weak ref to parent element or None if it is the root.
        self.report = [] # Area for conditions and drawing methods to report errors and warnings.

    def __repr__(self):
        if self.name:
            name = ':'+self.name
        elif self.eId:
            name = ':'+self.eId
        else:
            name = ''
        return '%s%s(%d, %d)' % (self.__class__.__name__, name, int(round(self.point[0])), int(round(self.point[1])))


    def _get_elements(self):
        u"""Default element does not have children."""
        return []
    def _set_elements(self, elements):
        raise KeyError('Only containers can hold other elements.')
    elements = property(_get_elements, _set_elements)

    # Answer the cascaded style value, looking up the chain of ancestors, until style value is defined.

    def css(self, name, default=None):
        u"""In case we are looking for a plain css value, cascading from the main ancestor styles
        of self, then follow the parent links until document or root, if self does not contain
        the requested value."""
        if name in self.style:
            return self.style[name]
        if self.parent is not None:
            return self.parent.css(name, default)
        return default

    def getNamedStyle(self, styleName):
        u"""In case we are looking for a named style (e.g. used by the Typesetter to build a stack
        of cascading tag style, then query the ancestors for the named style. Default behavior
        of all elements is that they pass the request on to the root, which is nornally the document."""
        if self.parent:
            return self.parent.getNamedStyle(styleName)
        return None

    def _get_lib(self):
        u"""Answer the shared document.lib dictionary, used for share global entry by elements."""
        parent = self.parent
        if parent is not None:
            return parent.lib # Either parent element or document.lib.
        return None # Document cannot be found, there is not document as root.

    # Most common properties

    def _get_parent(self):
        if self._parent is not None:
            return self._parent()
        return None
    def _set_parent(self, parent):
        if parent is not None:
            parent = weakref.ref(parent)
        self._parent = parent
    parent = property(_get_parent, _set_parent)

    def _get_siblings(self): # Answer all elements that share self.parent, without self.
        siblings = []
        for e in self.parent.elements:
            if not e is self:
                siblings.append(e)
        return siblings
    siblings = property(_get_siblings)

    def _get_point(self):
        return point2D(self._point) # Answer as 2D
    def _set_point(self, point):
        self._point = point3D(point) # Always store as 3D-point, z = 0 if missing
    point = property(_get_point, _set_point)

    def _get_point3D(self):
        return self._point
    def _set_point3D(self, point):
        self._point = point3D(point) # Always store as 3D-point, z = 0 if missing.
    point3D = property(_get_point3D, _set_point3D)

    # Plain coordinates

    def _get_x(self):
        return self._point[0]
    def _set_x(self, x):
        self._point = point3D(self._point) # Make sure it is a 3D list.
        self._point[0] = x
    x = property(_get_x, _set_x)
    
    def _get_y(self):
        return self._point[1] 
    def _set_y(self, y):
        self._point = point3D(self._point) # Make sure it is a 3D list.
        self._point[1] = y
    y = property(_get_y, _set_y)
    
    def _get_z(self):
        return self._point[2] # We know that self._point is always 3D
    def _set_z(self, z):
        self._point = point3D(self._point) # Make sure it is a 3D list.
        self._point[2] = z # self._point is always 3D
    z = property(_get_z, _set_z)
    
    # Origin compensated by alignment. This is used for easy solving of conditions,
    # where the positioning can be compenssaring the element alignment type.

    def _get_left(self):
        if self.css('vacuumW'): # Get vaccum left from child elements.
            ex, _, _, _ = self.getElementsBox()
            return self.x + ex
        xAlign = self.xAlign
        if xAlign == CENTER:
            return self.x - self.w/2
        if xAlign == RIGHT:
            return self.x - self.w
        return self.x
    def _set_left(self, x):
        xAlign = self.xAlign
        if xAlign == CENTER:
            self.x = x + self.w/2
        elif xAlign == RIGHT:
            self.x = x + self.w
        else:
            self.x = x
    left = property(_get_left, _set_left)

    def _get_mLeft(self): # Left, including left margin
        return self.left - self.css('ml')
    def _set_mLeft(self, x):
        self.left = x + self.css('ml')
    mLeft = property(_get_mLeft, _set_mLeft)

    def _get_center(self):
        if self.css('vacuumW'): # Get vaccum left/right from child elements.
            ex, _, ew, _ = self.getElementsBox()
            return self.x + ex + ew/2
        xAlign = self.xAlign
        if xAlign == LEFT:
            return self.x + self.w/2
        if xAlign == RIGHT:
            return self.x + self.w
        return self.x
    def _set_center(self, x):
        xAlign = self.xAlign
        if xAlign == LEFT:
            self.x = x - self.w/2
        elif xAlign == RIGHT:
            self.x = x - self.w
        else:
            self.x = x
    center = property(_get_center, _set_center)

    def _get_right(self):
        if self.css('vacuumW'): # Get vaccum left from child elements.
            ex, _, ew, _ = self.getElementsBox()
            return self.x + ex + ew
        xAlign = self.xAlign
        if xAlign == LEFT:
            return self.x + self.w
        if xAlign == CENTER:
            return self.x + self.w/2
        return self.x
    def _set_right(self, x):
        xAlign = self.xAlign
        if xAlign == LEFT:
            self.x = x - self.w
        elif xAlign == CENTER:
            self.x = x - self.w/2
        else:
            self.x = x
    right = property(_get_right, _set_right)

    def _get_mRight(self): # Right, including right margin
        return self.right - self.mr
    def _set_mRight(self, x):
        self.right = x + self.mr
    mRight = property(_get_mRight, _set_mRight)

    # Vertical

    def _get_top(self):
        yAlign = self.yAlign
        if yAlign == MIDDLE:
            return self.y - self.h/2
        if yAlign == BOTTOM:
            if self.originTop:
                return self.y - self.h
            return self.y + self.h
        return self.y
    def _set_top(self, y):
        yAlign = self.yAlign
        if yAlign == MIDDLE:
            self.y = y + self.h/2
        elif yAlign == BOTTOM:
            if self.originTop:
                self.y = y + self.h
            else:
                self.y = y - self.h
        else:
            self.y = y
    top = property(_get_top, _set_top)

    def _get_mTop(self): # Top, including top margin
        if self.originTop:
            return self.top - self.mt
        return self.top + self.mt
    def _set_mTop(self, y):
        if self.originTop:
            self.top = y + self.mt
        else:
            self.top = y - self.mt
    mTop = property(_get_mTop, _set_mTop)

    def _get_middle(self): # On bounding box, not including margins.
        yAlign = self.yAlign
        if yAlign == TOP:
            if self.originTop:
                return self.y + self.h/2
            return self.y - self.h/2
        if yAlign == BOTTOM:
            if self.originTop:
                return self.y - self.h/2
            return self.y + self.h/2
        return self.y
    def _set_middle(self, y):
        yAlign = self.yAlign
        if yAlign == TOP:
            if self.originTop:
                self.y = y - self.h/2
            else:
                self.y = y + self.h/2
        elif yAlign == BOTTOM:
            if self.originTop:
                self.y = y + self.h/2
            else:
                self.y = y - self.h/2
        else:
            self.y = y
    middle = property(_get_middle, _set_middle)

    def _get_bottom(self):
        yAlign = self.yAlign
        if yAlign == TOP:
            if self.originTop:
                return self.y + self.h
            return self.y - self.h
        if yAlign == MIDDLE:
            return self.y + self.h/2
        return self.y
    def _set_bottom(self, y):
        yAlign = self.yAlign
        if yAlign == TOP:
            if self.originTop:
                self.y = y - self.h
            else:
                self.y = y + self.h
        elif yAlign == MIDDLE:
            self.y = y - self.h/2
        else:
            self.y = y
    bottom = property(_get_bottom, _set_bottom)

    def _get_mBottom(self): # Bottom, including bottom margin
        if self.originTop:
            return self.bottom + self.mb
        return self.bottom - self.mb
    def _set_mBottom(self, y):
        if self.originTop:
            self.bottom = y - self.mb
        else:
            self.bottom = y + self.mb
    mBottom = property(_get_mBottom, _set_mBottom)

    # Depth, running  in vertical z-axis dirction. Viewer is origin, posistive value is perpendicular to the screen.
    # Besides future usage in real 3D rendering, the z-axis is used to compare conditional status in element layers.

    def _get_front(self):
        zAlign = self.css('zAlign')
        if zAlign == MIDDLE:
            return self.z - self.d/2
        if zAlign == BACK:
            return self.z - self.d
        return self.z
    def _set_front(self, z):
        zAlign = self.css('zAlign')
        if zAlign == MIDDLE:
            self.z = z + self.d/2
        elif zAlign == BACK:
            self.z = z + self.d
        else:
            self.z = z
    front = property(_get_front, _set_front)

    def _get_mFront(self): # Front, including front margin
        return self.front + self.css('mzf')
    def _set_mFront(self, z):
        self.front = z + self.css('mzf')
    mFront = property(_get_mFront, _set_mFront)

    # Alignment types, defines where the origin of the element is located.

    def _get_xAlign(self): # Answer the type of x-alignment. For compatibility allow align and xAlign as equivalents.
        return self.css('align')
    def _set_xAlign(self, xAlign):
        self.style['align'] = xAlign # Save locally, blocking CSS parent scope for this param.
    align = xAlign = property(_get_xAlign, _set_xAlign)
     
    def _get_yAlign(self): # Answer the type of x-alignment.
        return self.css('yAlign')
    def _set_yAlign(self, yAlign):
        self.style['yAlign'] = yAlign # Save locally, blocking CSS parent scope for this param.
    yAlign = property(_get_yAlign, _set_yAlign)
     
    def _get_zAlign(self): # Answer the type of x-alignment.
        return self.css('zAlign')
    def _set_zAlign(self, zAlign):
        self.style['zAlign'] = zAlign # Save locally, blocking CSS parent scope for this param.
    zAlign = property(_get_zAlign, _set_zAlign)
     
    # Position by column + gutter size index.

    def _get_cx(self): # Answer the x-position, defined in columns. Can be fractional for elements not on grid.
        return x2cx(self.x, self)
    def _set_cx(self, cx): # Set the x-position, defined in columns.
        x = cx2x(cx, self)
        if x is not None:
            self.x = x
    cx = property(_get_cx, _set_cx)

    def _get_cy(self): # Answer the y-position, defined in columns. Can be fractional for elements not on grid.
        return y2cy(self.y, self)
    def _set_cy(self, cy): # Set the x-position, defined in columns.
        y = cy2y(cy, self)
        if y is not None:
            self.y = y
    cy = property(_get_cy, _set_cy)

    def _get_cz(self): # Answer the z-position, defined in columns. Can be fractional for elements not on 3D-grid.
        return z2cz(self.y, self)
    def _set_cz(self, cz): # Set the z-position, defined in style['cz'] columns.
        z = cz2z(cz, self)
        if z is not None:
            self.z = z
    cz = property(_get_cz, _set_cz)


    def _get_cw(self):
        return w2cw(self.w, self)
    def _set_cw(self, cw):
        w = cw2w(cw, self)
        if w is not None:
            self.w = w
    cw = property(_get_cw, _set_cw)

    def _get_ch(self):
        return h2ch(self.h, self)
    def _set_ch(self, ch):
        h = ch2h(ch, self)
        if h is not None:
            self.h = h
    ch = property(_get_ch, _set_ch)

    def _get_cd(self):
        return d2cd(self.d, self)
    def _set_cd(self, cd):
        d = cd2d(cd, self)
        if d is not None:
            self.d = d
    cd = property(_get_cd, _set_cd)

    # Absolute posiitons

    def _get_rootX(self): # Answer the root value of local self.x, from whole tree of ancestors.
        parent = self.parent
        if parent is not None:
            return self.x + parent.rootX # Add relative self to parents position.
        return self.x
    rootX = property(_get_rootX)

    def _get_rootY(self): # Answer the absolute value of local self.y, from whole tree of ancestors.
        parent = self.parent
        if parent is not None:
            return self.y + parent.rootY # Add relative self to parents position.
        return self.y
    rootY = property(_get_rootY)

    def _get_rootZ(self): # Answer the absolute value of local self.z, from whole tree of ancestors.
        parent = self.parent
        if parent is not None:
            return self.z + parent.rootZ # Add relative self to parents position.
        return self.z
    rootZ = property(_get_rootZ)

    def _get_w(self): # Width
        if self.css('vacuumW'): # If vacuum forming, this overwrites css or style width.
            return self.right - self.left
        return self.css('w', DEFAULT_WIDTH) # Should not be 0 or None
    def _set_w(self, w):
        self.style['w'] = w # Overwrite element local style from here, parent css becomes inaccessable.
    w = property(_get_w, _set_w)

    def _get_mw(self): # Width, including margins
        return self.w + self.ml + self.mr # Add margins to width
    def _set_mw(self, w):
        self.style['w'] = max(0, w - self.ml - self.mr) # Cannot become < 0
    mw = property(_get_mw, _set_mw)

    def _get_h(self): # Height
        if self.css('vacuumH'): # If vacuum forming, this overwrites css or style width.
            if self.originTop:
                return self.bottom - self.top
            return self.top - self.bottom
        return self.css('h', DEFAULT_HEIGHT) # Should not be 0 or None
    def _set_h(self, h):
        self.style['h'] = h # Overwrite element local style from here, parent css becomes inaccessable.
    h = property(_get_h, _set_h)

    def _get_mh(self): # Height, including margins
        return self.h + self.mt + self.mb # Add margins to height
    def _set_mh(self, h):
        self.style['h'] = max(0, h - self.mt - self.mb) # Cannot become < 0
    mh = property(_get_mh, _set_mh)

    def _get_d(self): # Depth
        return self.css('d') 
        if self.css('vacuumD'): # If vacuum forming, this overwrites css or style depth.
            return self.back - self.front
        return self.css('d', DEAULT_DEPTH) # Should not be 0 or None
    def _set_d(self, d):
        self.style['d'] = d # Overwrite element local style from here, parent css becomes inaccessable.
    d = property(_get_d, _set_d)

    def _get_md(self): # Depth, including margin front and margin back in z-axis.
        return self.d + self.mzb + self.mzf # Add front and back margins to depth
    def _set_md(self, d):
        self.style['d'] = max(0, d - self.mzf - self.mzb) # Cannot become < 0, behind viewer?
    md = property(_get_md, _set_md)

    # Margin properties

    # TODO: Add support of "auto" values, doing live centering.

    def _get_margin(self): # Tuple of margins in CSS order, direction of clock
        return self.mt, self.mr, self.mb, self.ml
    def _set_margin(self, margin):
        if len(margin) == 1:
            margin = (margin, margin, margin, margin)
        elif len(margin) == 2:
            margin = (margin[0], marign[1], margin[0], margin[1])
        else:
            raise ValueError
        self.mt, self.mr, self.mb, self.ml = margin
    margin = property(_get_margin, _set_margin)

    def _get_margin3D(self): # Tuple of margins in CSS order + (front, back), direction of clock
        return self.mt, self.mr, self.mb, self.ml, self.mzf, self.mzb
    def _set_margin3D(self, margin3D):
        if len(margin3D) == 1:
            margin3D = (margin3D, margin3D, margin3D, margin3D, margin3D, margin3D)
        elif len(margin3D) == 2:
            margin3D = (margin[0], marign[1], margin[0], margin[1], margin[0], margin[1])
        else:
            raise ValueError
        self.mt, self.mr, self.mb, self.ml, self.mzf, self.margin.mzb = margin3D
    margin3D = property(_get_margin3D, _set_margin3D)

    def _get_mt(self): # Margin top
        return self.css('mt')
    def _set_mt(self, mt):
        self.style['mt'] = mt  # Overwrite element local style from here, parent css becomes inaccessable.
    mt = property(_get_mt, _set_mt)
    
    def _get_mb(self): # Margin bottom
        return self.css('mb')
    def _set_mb(self, mb):
        self.style['mb'] = mb  # Overwrite element local style from here, parent css becomes inaccessable.
    mb = property(_get_mb, _set_mb)
    
    def _get_mzf(self): # Margin z-axis front
        return self.css('mzf')
    def _set_mzf(self, mzf):
        self.style['mzf'] = mzf  # Overwrite element local style from here, parent css becomes inaccessable.
    mzf = property(_get_mzf, _set_mzf)
    
    def _get_mzb(self): # Margin z-axis back
        return self.css('mzb')
    def _set_mzb(self, mzb):
        self.style['mzb'] = mzb  # Overwrite element local style from here, parent css becomes inaccessable.
    mzb = property(_get_mzb, _set_mzb)
    
    def _get_ml(self): # Margin left
        return self.css('ml')
    def _set_ml(self, ml):
        self.style['ml'] = ml # Overwrite element local style from here, parent css becomes inaccessable.
    ml = property(_get_ml, _set_ml)
    
    def _get_mr(self): # Margin right
        return self.css('mr')
    def _set_mr(self, mr):
        self.style['mr'] = mr  # Overwrite element local style from here, parent css becomes inaccessable.
    mr = property(_get_mr, _set_mr)

    # Padding properties

    # TODO: Add support of "auto" values, doing live centering.
    
    def _get_padding(self): # Tuple of paddings in CSS order, direction of clock
        return self.pt, self.pr, self.pb, self.pl
    def _set_padding(self, padding):
        if len(padding) == 1:
            padding = (padding, padding, padding, padding)
        elif len(padding) == 2:
            padding = (padding[0], padding[1], padding[0], padding[1])
        else:
            raise ValueError
        self.pt, self.pr, self.pb, self.pl = padding
    padding = property(_get_padding, _set_padding)

    def _get_padding3D(self): # Tuple of padding in CSS order + (front, back), direction of clock
        return self.pt, self.pr, self.pb, self.pl, self.pzf, self.pzb
    def _set_padding3D(self, padding3D):
        if len(padding3D) == 1:
            padding3D = (padding3D, padding3D, padding3D, padding3D, padding3D, padding3D)
        elif len(padding3D) == 2:
            margin3D = (margin3D[0], margin3D[1], margin3D[0], margin3D[1], margin3D[0], margin3D[1])
        else:
            raise ValueError
        self.pt, self.pr, self.pb, self.pl, self.pzf, self.pzb = padding3D
    padding3D = property(_get_padding3D, _set_padding3D)

    def _get_pt(self): # Padding top
        return self.css('pt', 0)
    def _set_pt(self, pt):
        self.style['pt'] = pt  # Overwrite element local style from here, parent css becomes inaccessable.
    pt = property(_get_pt, _set_pt)
    
    def _get_pb(self): # Padding bottom
        return self.css('pb', 0)
    def _set_pb(self, pb):
        self.style['pb'] = pb  # Overwrite element local style from here, parent css becomes inaccessable.
    pb = property(_get_pb, _set_pb)
    
    def _get_pzf(self): # Padding z-axis front
        return self.css('pzf', 0)
    def _set_pzf(self, pzf):
        self.style['pzf'] = pzf  # Overwrite element local style from here, parent css becomes inaccessable.
    pzf = property(_get_pzf, _set_pzf)
    
    def _get_pzb(self): # Padding z-axis back
        return self.css('pzb', 0)
    def _set_pzb(self, pzb):
        self.style['pzb'] = pzb  # Overwrite element local style from here, parent css becomes inaccessable.
    pzb = property(_get_pzb, _set_pzb)
    
    def _get_pl(self): # Padding left
        return self.css('pl', 0)
    def _set_pl(self, pl):
        self.style['pl'] = pl # Overwrite element local style from here, parent css becomes inaccessable.
    pl = property(_get_pl, _set_pl)
    
    def _get_pr(self): # Margin right
        return self.css('pr', 0)
    def _set_pr(self, pr):
        self.style['pr'] = pr  # Overwrite element local style from here, parent css becomes inaccessable.
    pr = property(_get_pr, _set_pr)
    
    def _get_originTop(self):
        u"""Answer the style flag if all point y values should measure top-down (typographic page
        orientation), instead of bottom-up (mathematical orientation). For Y-axis only. 
        The axes in X and Z directions are fixed."""
        return self.css('originTop')
    def _set_originTop(self, flag):
        self.style['originTop'] = flag # Overwrite element local style from here, parent css becomes inaccessable.
    originTop = property(_get_originTop, _set_originTop)

    def getSize(self):
        u"""Answer the size of the element by calling properties self.w and self.h.
        This allows element to dynamically calculate the size if necessary, by redefining the
        self.w and/or self.h properties."""
        return self.w, self.h

    def getSize3D(self):
        u"""Answer the 3D size of the element."""
        return self.w, self.h, self.d

    def setSize(self, w, h, d=0):
        u"""Set the size of the element by calling by properties self.w and self.h. 
        If set, then overwrite access from style width and height. self.d is optional attribute."""
        self.w = w # Set by property
        self.h = h
        self.d = d # By default elements have 0 depth.

    def _get_paddedBox(self):
        u"""Calculate the padded position and padded resized box of the element, after applying the
        style padding. Answered format (x, y, w, h)."""
        pl = self.pl
        pt = self.pt
        pb = self.pb
        if self.originTop:
            y = self.y + pt
        else:
            y = self.y + pb
        return (self.x + pl, y, self.w - pl - self.pr, self.h - pt - pb)
    paddedBox = property(_get_paddedBox)

    def _get_padded3DBox(self):
        u"""Calculate the padded position and padded resized box in 3D of the lement, after applying
        the style padding. Answered format (x, y, z, w, h, d)."""
        x, y, w, h = self.paddedBox
        pzf = self.pzf
        return x, y, self.z + pzf, w, h, self.d - pzf - self.pzb
    padded3DBox = property(_get_padded3DBox)

    def _get_boundingBox(self):
        u"""Construct the bounding box from (self.x, self.y, self.w, self.h) properties."""
        return self.x or 0, self.y or 0, self.w or 0, self.h or 0
    boundingBox = property(_get_boundingBox)

    def _get_marginBox(self):
        u"""Calculate the margin position and margin resized box of the element, after applying the
        option style margin."""
        mt = self.mt
        mb = self.mb
        ml = self.ml
        if self.originTop:
            y = self.y - mt
        else:
            y = self.y - mb
        return (self.x - ml, y,
            self.w + ml + self.mr, 
            self.h + mt - mb)
    marginBox = property(_get_marginBox)

    def _get_minW(self):
        return self.css('minW', DEFAULT_WIDTH)
    def _set_minW(self, minW):
        self.style['minW'] = minW # Set on local style, shielding parent self.css value.
    minW = property(_get_minW, _set_minW)

    def _get_minH(self):
        return self.css('minH', DEFAULT_HEIGHT)
    def _set_minH(self, minH):
        self.style['minH'] = minH # Set on local style, shielding parent self.css value.
    minH = property(_get_minH, _set_minH)

    def _get_minD(self): # Set/get the minimal depth, in case the element has 3D dimensions.
        return self.css('minD', DEFAULT_DEPTH)
    def _set_minD(self, minD):
        self.style['minD'] = minD # Set on local style, shielding parent self.css value.
    minD = property(_get_minD, _set_minD)

    def getMinSize(self):
        u"""Answer the minW and minW of this element."""
        return self.minW, self.minH

    def getMinSize3D(self):
        u"""Answer the minW and minW of this element."""
        return self.minW, self.minH, self.minD

    def setMinSize(self, minW, minH, minD=0):
        self.minW = minW
        self.minH = minH
        self.minD = minD # Optional minimum depth of the element.

    def _get_maxW(self):
        return self.css('maxW', XXXL)
    def _set_maxW(self, maxW):
        self.style['maxW'] = maxW # Set on local style, shielding parent self.css value.
    maxW = property(_get_maxW, _set_maxW)

    def _get_maxH(self):
        return self.css('maxH', XXXL)
    def _set_maxH(self, maxH):
        self.style['maxH'] = maxH # Set on local style, shielding parent self.css value.
    maxH = property(_get_maxH, _set_maxH)

    def _get_maxD(self):
        return self.css('maxD', XXXL)
    def _set_maxD(self, maxD):
        self.style['maxD'] = maxD # Set on local style, shielding parent self.css value.
    maxD = property(_get_maxD, _set_maxD)

    def getMaxSize(self):
        return self.maxW, self.maxH # No limit if value is None

    def setMaxSize(self, maxW, maxH):
        self.maxW = maxW # No limit if value is None
        self.maxH = maxH

    def _get_scaleX(self):
        return self.css('scaleX', 1)
    def _set_scaleX(self, scaleX):
        self.style['scaleX'] = scaleX # Set on local style, shielding parent self.css value.
    scaleX = property(_get_scaleX, _set_scaleX)

    def _get_scaleY(self):
        return self.css('scaleX', 1)
    def _set_scaleY(self, scaleY):
        self.style['scaleY'] = scaleY # Set on local style, shielding parent self.css value.
    scaleY = property(_get_scaleY, _set_scaleY)

    def _get_scaleZ(self):
        return self.css('scaleZ', 1)
    def _set_scaleZ(self, scaleY):
        self.style['scaleZ'] = scaleZ # Set on local style, shielding parent self.css value.
    scaleZ = property(_get_scaleZ, _set_scaleZ)

    def getFloatTopSide(self, previousOnly=True):
        u"""Answer the max y that can float to top, without overlapping previous sibling elements.
        This means we are just looking at the vertical projection of (self.left, self.right).
        Note that the y may be outside the parent box. Only elements with identical z-value are compared."""
        if self.originTop:
            y = 0
        else:
            y = self.parent.h
        for e in self.parent.elements: 
            if previousOnly and e is self: # Only look at sublings that are ealier in the list.
                break 
            if e.z != self.z or e.right < self.left or self.right < e.left:
                continue # Not equal z-layer or not in window of vertical projection.
            if self.originTop:
                y = max(y, e.bottom)
            else:
                y = min(y, e.bottom)
        return y

    def getFloatBottomSide(self, previousOnly=True):
        u"""Answer the max y that can float to bottom, without overlapping previous sibling elements.
        This means we are just looking at the vertical projection of (self.left, self.right).
        Note that the y may be outside the parent box. Only elements with identical z-value are compared."""
        if self.originTop:
            y = self.parent.h
        else:
            y = 0
        for e in self.parent.elements: # All elements that share self.parent, except self.
            if previousOnly and e is self: # Only look at sublings that are ealier in the list.
                break 
            if e.z != self.z or e.right < self.left or self.right < e.left:
                continue # Not equal z-layer or not in window of vertical projection.
            if self.originTop:
                y = min(y, e.top)
            else:
                y = max(y, e.top)
        return y

    def getFloatLeftSide(self, previousOnly=True):
        u"""Answer the max x that can float to the left, without overlapping previous sibling elements.
        This means we are just looking at the horizontal projection of (self.top, self.bottom).
        Note that the x may be outside the parent box. Only elements with identical z-value are compared."""
        x = 0
        for e in self.parent.elements: # All elements that share self.parent, except self.
            if previousOnly and e is self: # Only look at sublings that are ealier in the list.
                break 
            if e.z != self.z or e.bottom < self.top or self.bottom < e.top:
                continue # Not equal z-layer or not in window of horizontal projection.
            x = max(e.right, x)
        return x

    def getFloatRightSide(self, previousOnly=True):
        u"""Answer the max Y that can float to the right, without overlapping previous sibling elements.
        This means we are just looking at the vertical projection of (self.left, self.right).
        Note that the y may be outside the parent box. Only elements with identical z-value are compared."""
        x = self.parent.w
        for e in self.parent.elements: # All elements that share self.parent, except self.
            if previousOnly and e is self: # Only look at sublings that are ealier in the list.
                break 
            if e.z != self.z or e.bottom < self.top or self.bottom < e.top:
                continue # Not equal z-layer or not in window of horizontal projection.
            x = min(e.left, x)
        return x

    def _applyAlignment(self, p):
        u"""Answer the p according to the alignment status nin the css.""" 
        px, py, pz = point3D(p)
        # Horizontal
        xAlign = self.xAlign
        if xAlign == CENTER:
            px -= self.w/2/self.scaleX
        elif xAlign == RIGHT:
            px -= self.w/self.scaleX
        # Vertical
        yAlign = self.yAlign
        if yAlign == MIDDLE:
            py -= self.h/2/self.scaleY
        elif yAlign == TOP:
            py -= self.h/self.scaleY
        # Currently no alignment in z-axis implemented
        return px, py, pz

    def _applyOrigin(self, p):
        u"""If self.originTop is False, then the y-value is interpreted as mathemtcs, 
        starting at the bottom of the parent element, moving up.
        If the flag is True, then move from top down, where the origin of the element becomes
        top-left of the parent."""
        px, py, pz = point3D(p)
        if self.originTop and self.parent:
            py = self.parent.h - py
        return px, py, pz

    def _applyRotation(self, mx, my, angle):
        u"""Apply the rotation for angle, where (mx, my) is the rotation center."""
        save()
        # TODO: Working on this.

    def _restoreRotation(self):
        u"""Reset graphics state from rotation mode."""
        if self.css('rotationX') and self.css('rotationY') and self.css('rotationAngle'):
            restore()

    def _applyScale(self, p):
        u"""Apply the scale, if both self.scaleX and self.scaleY are set. Use this
        method paired with self._restoreScale(). The (x, y) answered as reversed scaled tuple,
        so drawing elements can still draw on "real size", while the other element is in scaled mode."""
        sx = self.scaleX
        sy = self.scaleY
        sz = self.scaleZ
        p = point3D(p)
        if sx and sy and sz and (sx != 1 or sy != 1 or sz != 1): # Make sure these are value scale values.
            save()
            scale(sx, sy)
            p = (p[0] / sx, p[1] / sy, p[2] / sz) # Scale point in 3 dimensions.
        return p

    def _restoreScale(self):
        u"""Reset graphics state from svaed scale mode. Make sure to match the call of self._applyScale.
        If one of (self.scaleX, self.scaleY, self.scaleZ) is not 0 or 1, then do the restore."""
        sx = self.scaleX
        sy = self.scaleY
        sz = self.scaleZ
        if sx and sy and sz and (sx != 1 or sy != 1 or sz != 1): # Make sure these are value scale values.
            restore()

    def _setShadow(self):
        u"""Set the DrawBot graphics state for shadow if all parameters are set. Pair the call of this
        method with self._resetShadow()"""
        shadowOffset = self.css('shadowOffset') # Use DrawBot graphic state switch on shadow mode.
        if shadowOffset is not None:
            save() # DrawBot graphics state push
            shadowBlur = self.css('shadowBlur') # Should be integer.
            shadowFill = self.css('shadowFill') # Should be color, different from NO_COLOR
            shadow(shadowOffset, shadowBlur, shadowFill)

    def _resetShadow(self):
        u"""Restore the shadow mode of DrawBot. Should be paired with call self._setShadow()."""
        if self.css('shadowOffset') is not None:
            restore() # DrawBot graphics state pop.

    def copy(self):
        u"""Answer a copy of self and self.style. Note that any child elements will not be copied,
        keeping reference to the same instance."""
        e = copy.copy(self)
        e.style = copy.copy(self.style)
        e.eId = None # Must be unique. Caller needs to set it to a new one.
        return e

    #   Default drawing methods.

    def _drawElementBox(self, origin):
        u"""When designing templates and pages, this will draw a rectangle on the element
        bounding box if self.css('showElementBox') is True."""
        if self.css('showElementBox'):
            # Draw crossed rectangle.
            p = pointOffset(self.point, origin)
            p = self._applyOrigin(p)    
            p = self._applyScale(p)    
            px, py, _ = self._applyAlignment(p) # Ignore z-axis.

            setFillColor(None)
            setStrokeColor(0, 0.5)
            rect(px, py, self.w, self.h)

            self._restoreScale()
    
    def _getElementInfoString(self):
        u"""Answer a single string with info about the element. Default is to show the posiiton
        and size (in points and columns). This method can be redefined by inheriting elements
        that want to show additional information."""
        s = '%s\nPosition: %s, %s, %s\nSize: %s, %s\nColumn point: %s, %s\nColumn size: %s, %s\nAlign: %s, %s' % \
            (self.__class__.__name__ + ' ' + (self.name or ''), asFormatted(self.x), asFormatted(self.y), asFormatted(self.z), 
             asFormatted(self.w), asFormatted(self.h), 
             asFormatted(self.cx), asFormatted(self.cy), asFormatted(self.cw), asFormatted(self.ch),
             self.xAlign, self.yAlign)
        conditions = self.css('conditions')
        if conditions:
            score = self.evaluate()
            s += '\nConditions: %d | Evaluate %d' % (len(conditions), score.result)
            if score.fails:
                s += ' Fails: %d' % len(score.fails)
                for eFail in score.fails:
                    s += '\n%s %s' % eFail
        return s

    def _drawBackgroundFrame(self, origin):
        u"""If parameters defined, draw container background and/or stroke."""
        if self.css('fill') != NO_COLOR or self.css('stroke') != NO_COLOR:
            p = pointOffset(self.point, origin)
            p = op = self._applyOrigin(p)    
            p = self._applyScale(p)    
            px, py, _ = self._applyAlignment(p) # Ignore z-axis for now.

            setFillColor(self.css('fill', NO_COLOR))
            setStrokeColor(self.css('stroke', NO_COLOR), self.css('strokeWidth'))
            rect(px, py, self.w, self.h)

            self._restoreScale()

    def _drawElementInfo(self, origin):
        u"""For debugging this will make the elements show their info. The css flag "showElementOrigin"
        defines if the origin marker of an element is drawn."""
        if self.css('showElementInfo'):
             # Draw crossed rectangle.
            p = pointOffset(self.point, origin)
            p = op = self._applyOrigin(p)    
            p = self._applyScale(p)    
            px, py, _ = self._applyAlignment(p) # Ignore z-axis for now.

            fs = getFormattedString(self._getElementInfoString(), style=dict(font=self.css('infoFont'), 
                fontSize=self.css('infoFontSize'), leading=self.css('infoLeading'), textFill=0.1))
            tw, th = textSize(fs)
            Pd = 4 # Padding in box and shadow offset.
            tpx = px - Pd/2 # Make info box outdent the element. Keeping shadow on the element top left corner.
            tpy = py + self.h - th - Pd
            # Tiny shadow
            fill(0.3, 0.3, 0.3, 0.5)
            stroke(None)
            rect(tpx+Pd/2, tpy, tw+2*Pd, th+1.5*Pd)
            # Frame
            setFillColor(self.css('infoFill'))
            stroke(0.3)
            strokeWidth(0.25)
            rect(tpx, tpy, tw+2.5*Pd, th+1.5*Pd)
            text(fs, (tpx+Pd, tpy+1.5*Pd))
            self._restoreScale()

        if self.css('showElementOrigin'):
            # Draw origin of the element
            p = pointOffset(self.point, origin)
            opx, opy, _ = self._applyOrigin(p)    
            S = self.css('infoOriginMarkerSize', 4)
            fill(None)
            stroke(0)
            fill(0.5,0.5,0.5,0.5) # Transparant fill, so we can see the marker on dark backgrounds.
            strokeWidth(0.25)
            oval(opx-S, opy-S, 2*S, 2*S)
            line((opx-S, opy), (opx+S, opy))
            line((opx, opy-S), (opx, opy+S))

            
    def _drawMissingElementRect(self, origin):
        u"""When designing templates and pages, this will draw a filled rectangle on the element
        bounding box (if self.css('missingElementFill' is defined) and a cross, indicating
        that this element has missing content (as in unused image frames).
        Only draw if self.css('showGrid') is True."""
        if self.css('showGrid'):

            p = pointOffset(self.point, origin)
            p = self._applyOrigin(p)    
            p = self._applyScale(p)    
            px, py, _ = self._applyAlignment(p) # Ignore z-axis for now.
            self._setShadow()

            sMissingElementFill = self.css('missingElementFill', NO_COLOR)
            if sMissingElementFill is not NO_COLOR:
                setFillColor(sMissingElementFill)
                setStrokeColor(None)
                rect(px, py, self.w, self.h)
            # Draw crossed rectangle.
            setFillColor(None)
            setStrokeColor(0, 0.5)
            rect(px, py, self.w, self.h)
            newPath()
            moveTo((px, py))
            lineTo((px + self.w, py + self.h))
            moveTo((px + self.w, py))
            lineTo((px, py + self.h))
            drawPath()

            self._resetShadow()
            self._restoreScale()

    def getElementsBox(self):
        u"""Answer the vacuum bounding box around all child elements."""
        x1 = y1 = x2 = y2 = None
        for e in self.elements:
            if x1 is None or x1 > e.left:
                x1 = e.left
            if e.originTop:
                if y1 is None or y1 < e.top:
                    y1 = e.top
                if y2 is None or y1 > e.bottom:
                    y2 = e.bottom
            else:
                if y1 is None or y1 > e.top:
                    y1 = e.top
                if y2 is None or y2 < e.bottom:
                    y2 = e.bottom

        return x1, y1, x2 - x1, y2 - y1

    #   V A L I D A T I O N

    def evaluate(self, score=None):
        u"""Evaluate the content of element e with the total sum of conditions."""
        if score is None:
            score = Score()
        for condition in self.css('conditions', []): # Skip in case there are no conditions in the style.
            condition.evaluate(self, score)
        for e in self.elements: # Also works if element is not a container.
            e.evaluate(score)
        return score
         
    def solve(self, score=None):
        u"""Evaluate the content of element e with the total sum of conditions."""
        if score is None:
            score = Score()
        for condition in self.css('conditions', []): # Skip in case there are no conditions in the style.
            condition.solve(self, score)
        for e in self.elements: # Also works if element is not a container.
            e.solve(score)
        return score
         
    #   C O N D I T I O N S

    def isBottomOnBottom(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h - self.parent.pb - self.bottom) <= tolerance
        return abs(self.parent.pb - self.bottom) <= tolerance

    def isBottomOnBottomSide(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h - self.bottom) <= tolerance
        return abs(self.bottom) <= tolerance
        
    def isBottomOnTop(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.pt - self.bottom) <= tolerance
        return abs(self.parent.h - self.parent.pt - self.bottom) <= tolerance

    def isCenterOnCenter(self, tolerance=0):
        pl = self.parent.pl # Get parent padding left
        center = (self.parent.w - self.parent.pr - pl)/2
        return abs(pl + center - self.center) <= tolerance

    def isCenterOnCenterSides(self, tolerance=0):
        return abs(self.parent.w/2 - self.center) <= tolerance
  
    def isCenterOnLeft(self, tolerance=0):
        return abs(self.parent.pl - self.center) <= tolerance

    def isCenterOnRight(self, tolerance=0):
        return abs(self.parent.w - self.parent.pr - self.center) <= tolerance
   
    def isCenterOnRightSide(self, tolerance=0):
        return abs(self.parent.w - self.center) <= tolerance

    def isMiddleOnBottom(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h - self.parent.pb - self.middle) <= tolerance
        return abs(self.parent.pb - self.middle) <= tolerance

    def isMiddleOnBottomSide(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h - self.middle) <= tolerance
        return abs(self.middle) <= tolerance

    def isMiddleOnTop(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.pt - self.middle) <= tolerance
        return abs(self.parent.h - self.parent.pt - self.middle) <= tolerance

    def isMiddleOnTopSide(self, tolerance=0):
        if self.originTop:
            return abs(self.middle) <= tolerance
        return abs(self.parent.h - self.middle) <= tolerance

    def isMiddleOnMiddle(self, tolerance=0):
        pt = self.parent.pt # Get parent padding top
        pb = self.parent.pb 
        middle = (self.parent.h - pt - pb)/2
        if self.originTop:
            return abs(pt + middle - self.middle) <= tolerance
        return abs(pb + middle - self.middle) <= tolerance

    def isMiddleOnMiddleSides(self, tolerance=0):
        if self.originTop:
            return abs(self.middle) <= tolerance
        return abs(self.parent.h - self.middle) <= tolerance
  
    def isLeftOnCenter(self, tolerance=0):
        pl = self.parent.pl # Get parent padding left
        center = (self.parent.w - self.parent.pr - pl)/2
        return abs(pl + center - self.left) <= tolerance

    def isLeftOnCenterSides(self, tolerance=0):
        return abs(self.parent.w/2 - self.left) <= tolerance

    def isLeftOnLeft(self, tolerance=0):
        return abs(self.parent.pl - self.left) <= tolerance

    def isLeftOnLeftSide(self, tolerance=0):
        return abs(self.left) <= tolerance

    def isLeftOnRight(self, tolerance=0):
        return abs(self.parent.w - self.parent.pr - self.left) <= tolerance

    def isCenterOnLeftSide(self, tolerance=0):
        return abs(self.parent.left - self.center) <= tolerance

    def isTopOnMiddle(self, tolerance=0):
        pt = self.parent.pt # Get parent padding top
        pb = self.parent.pb 
        middle = (self.parent.h - pb - pt)/2
        if self.originTop:
            return abs(pt + middle - self.top) <= tolerance
        return abs(pb + middle - self.top) <= tolerance

    def isTopOnMiddleSides(self, tolerance=0):
        return abs(self.parent.h/2 - self.top) <= tolerance

    def isOriginOnBottom(self, tolerance=0):
        pb = self.parent.pb # Get parent padding left
        if self.originTop:
            return abs(self.parent.h - pb - self.y) <= tolerance
        return abs(pb - self.y) <= tolerance

    def isOriginOnBottomSide(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h - self.y) <= tolerance
        return abs(self.y) <= tolerance

    def isOriginOnCenter(self, tolerance=0):
        pl = self.parent.pl # Get parent padding left
        center = (self.parent.w - self.parent.pr - pl)/2
        return abs(pl + center - self.x) <= tolerance

    def isOriginOnCenterSides(self, tolerance=0):
        return abs(self.parent.w/2 - self.x) <= tolerance

    def isOriginOnLeft(self, tolerance=0):
        return abs(self.parent.pl - self.x) <= tolerance

    def isOriginOnLeftSide(self, tolerance=0):
        return abs(self.x) <= tolerance

    def isOriginOnRight(self, tolerance=0):
        return abs(self.parent.w - self.parent.pr - self.x) <= tolerance

    def isOriginOnRightSide(self, tolerance=0):
        return abs(self.parent.w - self.x) <= tolerance

    def isOriginOnTop(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.pt - self.y) <= tolerance
        return abs(self.parent.h - self.parent.pt - self.y) <= tolerance

    def isOriginOnTopSide(self, tolerance=0):
        if self.originTop:
            return abs(self.y) <= tolerance
        return abs(self.parent.h - self.y) <= tolerance

    def isOriginOnMiddle(self, tolerance=0):
        if self.originTop:
            return abs(mt + (self.parent.h - self.parent.pb - self.parent.pt)/2 - self.y) <= tolerance
        return abs(mb + (self.parent.h - self.parent.pb - self.parent.pt)/2 - self.y) <= tolerance
 
    def isOriginOnMiddleSides(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h/2 - self.y) <= tolerance
        return abs(self.parent.h/2 - self.y) <= tolerance
 
    def isRightOnCenter(self, tolerance=0):
        return abs(self.parent.w - self.x) <= tolerance

    def isRightOnCenterSides(self, tolerance=0):
        return abs(self.parent.w/2 - self.right) <= tolerance

    def isRightOnLeft(self, tolerance=0):
        return abs(self.parent.pl - self.right) <= tolerance

    def isRightOnRight(self, tolerance=0):
        padR = self.parent.css('pr')
        return abs(self.parent.w - padR - self.right) <= tolerance

    def isRightOnRightSide(self, tolerance=0):
        return abs(self.parent.w - self.right) <= tolerance

    def isBottomOnMiddle(self, tolerance=0):
        pt = self.parent.pt # Get parent padding top
        pb = self.parent.pb
        middle = (self.parent.h - pb - pt)/2
        if self.originTop:
            return abs(pt + middle - self.bottom) <= tolerance
        return abs(pb + middle - self.bottom) <= tolerance

    def isBottomOnMiddleSides(self, tolerance=0):
        return abs(self.parent.h/2 - self.bottom) <= tolerance

    def isTopOnBottom(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.h - self.parent.pb - self.top) <= tolerance
        return abs(self.parent.pb - self.top) <= tolerance

    def isTopOnTop(self, tolerance=0):
        if self.originTop:
            return abs(self.parent.pt - self.top) <= tolerance
        return abs(self.parent.h - self.parent.pt - self.top) <= tolerance

    def isTopOnTopSide(self, tolerance=0):
        if self.originTop:
            return abs(self.top) <= tolerance
        return abs(self.parent.h - self.top) <= tolerance

    def isFloatTop(self, tolerance=0):
        if self.originTop:
            return abs(max(self.getFloatTopSide(), self.parent.pt) - self.top) <= tolerance
        return abs(min(self.getFloatTopSide(), self.parent.h - self.parent.pt) - self.top) <= tolerance

    def isFloatTopSide(self, tolerance=0):
        return abs(self.getFloatTopSide() - self.top) <= tolerance

    def isFloatBottom(self, tolerance=0):
        if self.originTop:
            return abs(min(self.getFloatBottomSide(), self.parent.h - self.parent.pb) - self.bottom) <= tolerance
        return abs(max(self.getFloatTopSide(), self.parent.pb) - self.bottom) <= tolerance

    def isFloatBottomSide(self, tolerance=0):
        return abs(self.getFloatBottomSide() - self.bottom) <= tolerance

    def isFloatLeft(self, tolerance=0):
        return abs(max(self.getFloatLeftSide(), self.parent.pl) - self.left) <= tolerance

    def isFloatLeftSide(self, tolerance=0):
        return abs(self.getFloatLeftSide() - self.left) <= tolerance

    def isFloatRight(self, tolerance=0):
        return abs(min(self.getFloatRightSide(), self.parent.w - self.parent.pr) - self.right) <= tolerance

    def isFloatRightSide(self, tolerance=0):
        return abs(self.getFloatRightSide() - self.right) <= tolerance

    #   T R A N S F O R M A T I O N S 

    def bottom2Bottom(self):
        if self.originTop:
            self.bottom = self.parent.h - self.parent.pb
        else:
            self.bottom = self.parent.pb
        return True

    def bottom2BottomSide(self):
        if self.originTop:
            self.bottom = self.parent.h
        else:
            self.bottom = 0
        return True

    def bottom2top(self):
        if self.originTop:
            self.bottom = self.parent.pt 
        else:
            self.bottom = self.parent.h - self.parent.pt
        return True
    
    def middle2Bottom(self):
        if self.originTop:
            self.middle = self.parent.h - self.parent.pb
        else:
            self.middle = self.parent.pb
        return True
    
    def middle2BottomSide(self):
        if self.originTop:
            self.middle = self.parent.h
        else:
            self.middle = 0
        return True

    def center2Center(self):
        pl = self.parent.pl # Get parent padding left
        self.center = pl + (self.parent.w - self.parent.pr - pl)/2
        return True
    
    def center2CenterSides(self):
        self.center = self.parent.w/2
        return True

    def center2Left(self):
        self.center = self.parent.pl # Padding left
        return True

    def center2LeftSide(self):
        self.center = 0
        return True

    def center2Right(self):
        self.center = self.parent.w - self.parent.pr
        return True

    def center2RightSide(self):
        self.center = self.parent.w
        return True

    def middle2Top(self):
        if self.originTop:
            self.middle = self.parent.pt
        else:
            self.middle = self.parent.h - self.parent.pt
        return True       

    def middle2TopSide(self):
        if self.originTop:
            self.middle = 0
        else:
            self.middle = self.parent.h
        return True       

    def middle2Middle(self): # Vertical center, following CSS naming.
        pt = self.parent.pt # Get parent padding top
        pb = self.parent.pb
        middle = (self.parent.h - pb - pt)/2
        if self.originTop:
            self.middle = pt + middle
        else:
            self.middle = pb + middle
        return True

    def middle2MiddleSides(self):
        self.middle = self.parent.h/2

    def fitBottom(self):
        if self.originTop:
            self.h += self.parent.h - self.parent.pb - self.bottom
        else:
            top = self.top
            self.bottom = self.parent.pb
            self.h += top - self.top
        return True

    def fitBottomSide(self):
        if self.originTop:
            self.h += self.parent.h - self.bottom
        else:
            top = self.top
            self.bottom = 0
            self.h += top - self.top
        return True

    def fitLeft(self):
        right = self.right
        self.left = self.parent.pl # Padding left
        self.w += right - self.right
        return True

    def fitLeftSide(self):
        right = self.right
        self.left = 0
        self.w += right - self.right
        return True

    def fitRight(self):
        self.w += self.parent.w - self.parent.pr - self.right
        return True

    def fitRightSide(self):
        self.w += self.parent.w - self.right
        return True

    def fitTop(self):
        if self.originTop:
            bottom = self.bottom
            self.top = self.parent.pt
            self.h += bottom - self.bottom
        else:
            self.h += self.parent.h - self.parent.pt - self.top
        return True

    def fitTopSide(self):
        if self.originTop:
            bottom = self.bottom
            self.top = 0
            self.h += bottom - self.bottom
        else:
            self.h += self.parent.h - self.top
        return True

    def left2Center(self):
        pl = self.parent.pl # Get parent padding left
        self.left = pl + (self.parent.w - self.parent.pr - pl)/2
        return True       

    def left2CenterSides(self):
        self.left = self.parent.w/2
        return True       

    def left2Left(self):
        self.left = self.parent.pl # Padding left
        return True       

    def left2Right(self):
        self.left = self.parent.w - self.parent.pr
        return True       

    def left2LeftSide(self):
        self.left = 0
        return True       

    def top2Middle(self):
        pt = self.parent.pt # Get parent padding left
        pb = self.parent.pb
        middle = (self.parent.h - pb - pt)/2
        if self.originTop:
            self.top = pt + middle
        else:
            self.top = pb + middle
        return True       

    def top2MiddleSides(self):
        self.top = self.parent.h/2
        return True       

    def origin2Bottom(self):
        if self.originTop:
            self.y = self.parent.h - self.parent.pb
        else:
            self.y = self.parent.pb
        return True

    def origin2BottomSide(self):
        if self.originTop:
            self.y = self.parent.h
        else:
            self.y = 0
        return True       

    def origin2Center(self):
        self.x = ml + (self.parent.w - self.parent.pr - sepf.parent.pl)/2
        return True       

    def origin2CenterSides(self):
        self.x = self.parent.w/2
        return True       

    def origin2Left(self):
        self.x = self.parent.pl # Padding left
        return True       

    def origin2LeftSide(self):
        self.x = 0
        return True       

    def origin2Right(self):
        self.x = self.parent.w - self.parent.pr
        return True

    def origin2RightSide(self):
        self.x = self.parent.w
        return True

    def origin2Top(self):
        if self.originTop:
            self.y = self.parent.pt
        else:
            self.y = self.parent.h - self.parent.pt
        return True

    def origin2TopSide(self):
        if self.originTop:
            self.y = 0
        else:
            self.y = self.parent.h
        return True

    def origin2Middle(self):
        pt = self.parent.pt # Get parent padding top
        pb = self.parent.pb
        middle = (self.parent.h - pb - pt)/2
        if self.originTop:
            self.y = pt + middle
        else:
            self.y = pb + middle
        return True
 
    def origin2MiddleSides(self):
        self.y = self.parent.h/2
        return True

    def right2Center(self):
        pl = self.parent.pl # Get parent padding left
        self.right = pl + (self.parent.w - self.parent.pr - pl)/2
        return True

    def right2CenterSides(self):
        self.right = self.parent.w/2
        return True

    def right2Left(self):
        self.right = self.parent.pl # Padding left
        return True

    def right2Right(self):
        self.right = self.parent.w - self.parent.pr
        return True
    
    def right2RightSide(self):        
        self.right = self.parent.w
        return True

    def bottom2Middle(self):
        pt = self.parent.pt # Get parent padding top
        pb = self.parent.pb
        middle = (self.parent.h - pb - pt)/2
        if self.originTop:
            self.bottom = pt + middle
        else:
            self.bottom = pg + middle
        return True

    def bottom2MiddleSides(self):
        self.bottom = self.parent.h/2
        return True

    def top2Bottom(self):
        if self.originTop:
            self.top = self.parent.h - self.parent.pb
        else:
            self.top = self.parent.pb
        return True
    
    def top2Top(self):
        if self.originTop:
            self.top = self.parent.pt
        else:
            self.top = self.parent.h - self.parent.pt
        return True
    
    def top2TopSide(self):
        if self.originTop:
            self.top = 0
        else:
            self.top = self.parent.h
        return True

    def float2Top(self):
        if self.originTop:
            self.top = max(self.getFloatTopSide(), self.parent.pt)
        else:
            self.top = min(self.getFloatTopSide(), self.parent.h - self.parent.pt)
        return True

    def float2TopSide(self):
        self.top = self.getFloatTopSide()
        return True

    def float2Bottom(self):
        if self.originTop:
            self.bottom = min(self.getFloatBottomSide(), self.parent.h - self.parent.pb)
        else:
            self.bottom = max(self.getFloatTopSide(), self.parent.pb)
        return True

    def float2BottomSide(self):
        self.bottom = self.getFloatBottomSide()
        return True

    def float2Left(self):
        self.left = max(self.getFloatLeftSide(), self.parent.pl) # padding left
        return True

    def float2LeftSide(self):
        self.left = self.getFloatLeftSide()
        return True

    def float2Right(self):
        self.right = min(self.getFloatRightSide(), self.parent.w - self.parent.pr)
        return True

    def float2RightSide(self):
        self.right = self.getFloatRightSide()
        return True



