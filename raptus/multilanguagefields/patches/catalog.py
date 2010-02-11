# -*- coding: utf-8 -*-
#===============================================================================
# Patch Catalog 
#===============================================================================
from Missing import MV
from Record import Record
from Products.ZCatalog import CatalogBrains
from Products.ZCatalog.Catalog import Catalog, safe_callable
from raptus.multilanguagefields.interfaces import IMultilanguageAware
from raptus.multilanguagefields import MultilanguageAware
from raptus.multilanguagefields import LOG

# CatalogBrain monkey patch
def __new_init__(self, data):
    ndata = []
    for v in data:
        if IMultilanguageAware.providedBy(v):
            v = v()
        ndata.append(v)
    Record.__init__(self, tuple(ndata))   
CatalogBrains.AbstractCatalogBrain.__old_init__ = CatalogBrains.AbstractCatalogBrain.__init__ 
CatalogBrains.AbstractCatalogBrain.__init__ = __new_init__
LOG.info("Products.ZCatalog.CatalogBrains.AbstractCatalogBrain.__init__ patched") 

# catalog monkey patch to support languageaware metadata
def new_recordify(self, object):
    """ turns an object into a record tuple """
    record = []
    # the unique id is always the first element
    for x in self.names:
        attr=getattr(object, x, MV)
        if(attr is not MV and safe_callable(attr)):
            try:
                attr = attr(lang='all')
                if isinstance(attr, dict):
                    attr = MultilanguageAware(attr)
            except:
                attr = attr()
        record.append(attr)
    return tuple(record)

Catalog.old_recordify = Catalog.recordify   
Catalog.recordify = new_recordify
LOG.info("Products.ZCatalog.Catalog.Catalog.recordify patched")    