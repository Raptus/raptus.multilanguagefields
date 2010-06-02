from persistent.dict import PersistentDict

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_zcatalog_indexes
from BTrees.IIBTree import IITreeSet
from BTrees.IOBTree import IOBTree
import BTrees.Length
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile

from Products.PluginIndexes.common import safe_callable

from Products.PluginIndexes.DateRangeIndex.DateRangeIndex import DateRangeIndex
from raptus.multilanguagefields.indexes.UnIndex import MultilanguageUnIndex

class MultilanguageDateRangeIndex(MultilanguageUnIndex, DateRangeIndex):
    security = ClassSecurityInfo()

    meta_type = "MultilanguageDateRangeIndex"

    manage_options=DateRangeIndex.manage_options
    query_options=DateRangeIndex.query_options
    
    _apply_index = DateRangeIndex._apply_index
    uniqueValues = DateRangeIndex.uniqueValues
    numObjects = DateRangeIndex.numObjects
    indexSize = DateRangeIndex.indexSize
    __init__ = DateRangeIndex.__init__
    getEntryForObject = DateRangeIndex.getEntryForObject
    
    def _get_lang_always(self, lang):
        if not self._d_always.has_key(lang):
            self._d_always[lang] = IITreeSet()
        return self._d_always[lang]

    def _set_always(self, value):
        if not self._v_lang:
            self._d_always[self._getCurrentLanguage()] = value
        else:
            self._d_always[self._v_lang] = value

    def _get_always(self):
        if not self._v_lang:
            return self._get_lang_always(self._getCurrentLanguage())
        return self._get_lang_always(self._v_lang)

    def _del_always(self):
        if not self._v_lang:
            del self._d_always[self._getCurrentLanguage()]
        else:
            del self._d_always[self._v_lang]

    _always = property(fget=_get_always,
                       fset=_set_always,
                       fdel=_del_always)
    
    def _get_lang_since_only(self, lang):
        if not self._d_since_only.has_key(lang):
            self._d_since_only[lang] = IOBTree()
        return self._d_since_only[lang]

    def _set_since_only(self, value):
        if not self._v_lang:
            self._d_since_only[self._getCurrentLanguage()] = value
        else:
            self._d_since_only[self._v_lang] = value

    def _get_since_only(self):
        if not self._v_lang:
            return self._get_lang_since_only(self._getCurrentLanguage())
        return self._get_lang_since_only(self._v_lang)

    def _del_since_only(self):
        if not self._v_lang:
            del self._d_since_only[self._getCurrentLanguage()]
        else:
            del self._d_since_only[self._v_lang]

    _since_only = property(fget=_get_since_only,
                           fset=_set_since_only,
                           fdel=_del_since_only)

    def _get_lang_until_only(self, lang):
        if not self._d_until_only.has_key(lang):
            self._d_until_only[lang] = IOBTree()
        return self._d_until_only[lang]

    def _set_until_only(self, value):
        if not self._v_lang:
            self._d_until_only[self._getCurrentLanguage()] = value
        else:
            self._d_until_only[self._v_lang] = value

    def _get_until_only(self):
        if not self._v_lang:
            return self._get_lang_until_only(self._getCurrentLanguage())
        return self._get_lang_until_only(self._v_lang)

    def _del_until_only(self):
        if not self._v_lang:
            del self._d_until_only[self._getCurrentLanguage()]
        else:
            del self._d_until_only[self._v_lang]

    _until_only = property(fget=_get_until_only,
                           fset=_set_until_only,
                           fdel=_del_until_only)

    def _get_lang_since(self, lang):
        if not self._d_since.has_key(lang):
            self._d_since[lang] = IOBTree()
        return self._d_since[lang]

    def _set_since(self, value):
        if not self._v_lang:
            self._d_since[self._getCurrentLanguage()] = value
        else:
            self._d_since[self._v_lang] = value

    def _get_since(self):
        if not self._v_lang:
            return self._get_lang_since(self._getCurrentLanguage())
        return self._get_lang_since(self._v_lang)

    def _del_since(self):
        if not self._v_lang:
            del self._d_since[self._getCurrentLanguage()]
        else:
            del self._d_since[self._v_lang]

    _since = property(fget=_get_since,
                      fset=_set_since,
                      fdel=_del_since)

    def _get_lang_until(self, lang):
        if not self._d_until.has_key(lang):
            self._d_until[lang] = IOBTree()
        return self._d_until[lang]

    def _set_until(self, value):
        if not self._v_lang:
            self._d_until[self._getCurrentLanguage()] = value
        else:
            self._d_until[self._v_lang] = value

    def _get_until(self):
        if not self._v_lang:
            return self._get_lang_until(self._getCurrentLanguage())
        return self._get_lang_until(self._v_lang)

    def _del_until(self):
        if not self._v_lang:
            del self._d_until[self._getCurrentLanguage()]
        else:
            del self._d_until[self._v_lang]

    _until = property(fget=_get_until,
                      fset=_set_until,
                      fdel=_del_until)

    security.declareProtected(manage_zcatalog_indexes, 'clear')
    def clear( self ):
        self._d_always        = PersistentDict()
        self._d_since_only    = PersistentDict()
        self._d_until_only    = PersistentDict()
        self._d_since         = PersistentDict()
        self._d_until         = PersistentDict()
        self._d_unindex       = PersistentDict()
        self._d_length        = PersistentDict()

    def index_object( self, documentId, obj, threshold=None ):
        if self._since_field is None:
            return 0
        
        since_attr = getattr(obj, self._since_field, None)
        until_attr = getattr(obj, self._until_field, None)
        if not since_attr and not until_attr:
            return 0
        for lang in self.languages:
            self._v_lang = lang
            if safe_callable(since_attr):
                since = since_attr()
                try: since = since_attr(lang=lang)
                except: pass
            else:
                since = since_attr
            since = self._convertDateTime( since )
            if safe_callable( until_attr ):
                until = until_attr()
                try: until = until_attr(lang=lang)
                except: pass
            else:
                until = until_attr
            until = self._convertDateTime( until )
    
            datum = ( since, until )
    
            old_datum = self._unindex.get( documentId, None )
            if datum == old_datum: # No change?  bail out!
                return 0
    
            if old_datum is not None:
                old_since, old_until = old_datum
                self._removeForwardIndexEntry( old_since, old_until, documentId )
    
            self._insertForwardIndexEntry( since, until, documentId )
            self._unindex[ documentId ] = datum
        self._v_lang = None
        return 1

    def unindex_object( self, documentId ):
        for lang in self.languages:
            self._v_lang = lang
            DateRangeIndex.unindex_object(self, documentId)
        self._v_lang = None

InitializeClass( MultilanguageDateRangeIndex )

manage_addMultilanguageDateRangeIndexForm = DTMLFile( 'dtml/addFieldIndex', globals() )

def manage_addMultilanguageDateRangeIndex(self, id, extra=None,
        REQUEST=None, RESPONSE=None, URL3=None):
    """
        Add a multilanguage date range index to the catalog, using the incredibly icky
        double-indirection-which-hides-NOTHING.
    """
    return self.manage_addIndex(id, 'MultilanguageDateRangeIndex', extra,
        REQUEST, RESPONSE, URL3)
