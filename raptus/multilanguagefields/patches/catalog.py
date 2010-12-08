# -*- coding: utf-8 -*-
#===============================================================================
# Patch Catalog 
#===============================================================================
from Missing import MV
from Record import Record
from zope.app.component.hooks import getSite
from Products.ZCatalog import CatalogBrains
from Products.ZCatalog.Catalog import Catalog, safe_callable
from Products.CMFCore.utils import getToolByName
from raptus.multilanguagefields import LOG

try:
    import json
except:
    import simplejson as json

# CatalogBrain monkey patch
def __new_init__(self, data):
    ndata = []
    lang = getToolByName(getSite(), 'portal_languages').getPreferredLanguage()
    try:
        encoding = getToolByName(self, "portal_properties").site_properties.default_charset
    except AttributeError:
        encoding = 'ascii'
    for v in data:
        try:
            value = json.loads(v)
            value = value['___multilanguage___']
            v = value.get(lang, '')
            if isinstance(v, basestring):
                v = v.encode(encoding)
        except:
            pass
        ndata.append(v)
    Record.__init__(self, tuple(ndata))
CatalogBrains.AbstractCatalogBrain.__old_init__ = CatalogBrains.AbstractCatalogBrain.__init__ 
CatalogBrains.AbstractCatalogBrain.__init__ = __new_init__
LOG.info("Products.ZCatalog.CatalogBrains.AbstractCatalogBrain.__init__ patched") 

# catalog monkey patch to support languageaware metadata
def __new_recordify(self, object):
    """ turns an object into a record tuple """
    record = []
    # the unique id is always the first element
    for x in self.names:
        attr=getattr(object, x, MV)
        if(attr is not MV and safe_callable(attr)):
            try:
                attr = attr(lang='all')
                if isinstance(attr, dict):
                    attr = json.dumps(dict(___multilanguage___ = attr))
            except:
                attr = attr()
        record.append(attr)
    return tuple(record)

Catalog.old_recordify = Catalog.recordify
Catalog.recordify = __new_recordify
LOG.info("Products.ZCatalog.Catalog.Catalog.recordify patched")
