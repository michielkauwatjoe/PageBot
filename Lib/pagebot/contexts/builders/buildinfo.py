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
#     buildinfo.py
#
import copy

def newBuildInfo(info=None, **kwargs):
	u"""Answer a filled BuildInfo instance.

	>>> url = 'images/favIcon.ico'
	>>> bi = newBuildInfo(favIconUrl=url)
	>>> bi.favIconUrl == url
	True
	"""
	if isinstance(info, dict):
		info = BuildInfo(**info)
	elif info is None:
		info = BuildInfo(**kwargs)
	assert isinstance(info, BuildInfo)
	return info

class BuildInfo(object):
    u"""Container with builder flags and data, as stored in elements, to guide conditional 
    e.build( ) and e.buildCss( ) and e.buildFlat( ) calls.
    Note that these attribute and flags can be defined specifically per element, so they
    cannot be part of a view.
    """
    
    def __init__(self, **kwargs):
    	self._d = {}
    	for key, value in kwargs.items():
    		assert hasattr(self, key)
    		setattr(self, key, value)

    def copy(self):
    	u"""Answer a deep copy of self."""
    	return copy.deepcopy(self)

    def items(self):
    	return self._d.items()

    def __getitem__(self, key):
    	return self._d.get(key)

    def __setitem__(self, key, value):
    	self._d[key] = value
    	
    def _get_favIconUrl(self):
    	return self._d.get('favIconUrl')
    def _set_favIconUrl(self, favIconUrl):
    	self._d['favIconUrl'] = favIconUrl
    favIconUrl = property(_get_favIconUrl, _set_favIconUrl)

    # Info defined a code chunks

    def _get_cssCode(self):
    	return self._d.get('cssCode')
    def _set_cssCode(self, cssCode):
    	self._d['cssCode'] = cssCode
    cssCode = property(_get_cssCode, _set_cssCode)

    def _get_jsCode(self):
    	return self._d.get('jsCode')
    def _set_jsCode(self, jsCode):
    	self._d['jsCode'] = jsCode
    jsCode = property(_get_jsCode, _set_jsCode)

    def _get_headHtmlCode(self):
    	return self._d.get('headHtmlCode')
    def _set_headHtmlCode(self, headHtmlCode):
    	self._d['headHtmlCode'] = headHtmlCode
    headHtmlCode = property(_get_headHtmlCode, _set_headHtmlCode)

    def _get_bodyHtmlCode(self):
    	return self._d.get('bodyHtmlCode')
    def _set_bodyHtmlCode(self, bodyHtmlCode):
    	self._d['bodyHtmlCode'] = bodyHtmlCode
    bodyHtmlCode = property(_get_bodyHtmlCode, _set_bodyHtmlCode)

    # Info defined as file paths 

    def _get_cssPath(self):
    	return self._d.get('cssPath')
    def _set_cssPath(self, cssPath):
    	self._d['cssPath'] = cssPath
    cssPath = property(_get_cssPath, _set_cssPath)

    def _get_jsPath(self):
    	return self._d.get('jsPath')
    def _set_jsPath(self, jsPath):
    	self._d['jsPath'] = jsPath
    jsPath = property(_get_jsPath, _set_jsPath)

    def _get_htmlPath(self):
    	return self._d.get('htmlPath')
    def _set_htmlPath(self, htmlPath):
    	self._d['htmlPath'] = htmlPath
    htmlPath = property(_get_htmlPath, _set_htmlPath)

    # Info defined as url 

    def _get_cssUrl(self):
    	return self._d.get('cssUrl')
    def _set_cssUrl(self, cssUrl):
    	self._d['cssUrl'] = cssUrl
    cssUrl = property(_get_cssUrl, _set_cssUrl)

    def _get_jsUrl(self):
    	return self._d.get('jsUrl')
    def _set_jsUrl(self, jsUrl):
    	self._d['jsUrl'] = jsUrl
    jsUrl = property(_get_jsUrl, _set_jsUrl)

    def _get_webFontsUrl(self):
    	return self._d.get('webFontsUrl')
    def _set_webFontsUrl(self, webFontsUrl):
    	self._d['webFontsUrl'] = webFontsUrl
    webFontsUrl = property(_get_webFontsUrl, _set_webFontsUrl)

    # Generic resource file paths

    def _get_resourcePaths(self):
    	return self._d.get('resourcePaths')
    def _set_resourcePaths(self, resourcePaths):
    	self._d['resourcePaths'] = resourcePaths
    resourcePaths = property(_get_resourcePaths, _set_resourcePaths)



if __name__ == "__main__":
    import sys
    import doctest
    sys.exit(doctest.testmod()[0])

