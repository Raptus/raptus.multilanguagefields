from persistent.dict import PersistentDict

from BTrees.IOBTree import IOBTree
import BTrees.Length
from BTrees.OOBTree import OOBTree

from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.common.UnIndex import UnIndex, _marker

class MultilanguageUnIndex(UnIndex):
    """Multilanguage aware forward and reverse index.
    """
    
    _v_lang = None
    _d_length = PersistentDict()
    _d_index = PersistentDict()
    _d_unindex = PersistentDict()
        
    def _getCurrentLanguage(self):
        return getToolByName(getSite(), 'portal_languages').getPreferredLanguage()
    
    def _get_lang_length(self, lang):
        if not self._d_length.has_key(lang):
            self._d_length[lang] = BTrees.Length.Length()
        return self._d_length[lang]

    def _set_length(self, value):
        if not self._v_lang:
            self._d_length[self._getCurrentLanguage()] = value
        else:
            self._d_length[self._v_lang] = value

    def _get_length(self):
        if not self._v_lang:
            return self._get_lang_length(self._getCurrentLanguage())
        return self._get_lang_length(self._v_lang)

    def _del_length(self):
        if not self._v_lang:
            del self._d_length[self._getCurrentLanguage()]
        else:
            del self._d_length[self._v_lang]

    _length = property(fget=_get_length,
                       fset=_set_length,
                       fdel=_del_length)
    
    def _get_lang_index(self, lang):
        if not self._d_index.has_key(lang):
            self._d_index[lang] = OOBTree()
        return self._d_index[lang]

    def _set_index(self, value):
        if not self._v_lang:
            self._d_index[self._getCurrentLanguage()] = value
        else:
            self._d_index[self._v_lang] = value

    def _get_index(self):
        if not self._v_lang:
            return self._get_lang_index(self._getCurrentLanguage())
        return self._get_lang_index(self._v_lang)

    def _del_index(self):
        if not self._v_lang:
            del self._d_index[self._getCurrentLanguage()]
        del self._d_index[self._v_lang]

    _index = property(fget=_get_index,
                      fset=_set_index,
                      fdel=_del_index)
    
    def _get_lang_unindex(self, lang):
        if not self._d_unindex.has_key(lang):
            self._d_unindex[lang] = IOBTree()
        return self._d_unindex[lang]

    def _set_unindex(self, value):
        if not self._v_lang:
            self._d_unindex[self._getCurrentLanguage()] = value
        else:
            self._d_unindex[self._v_lang] = value

    def _get_unindex(self):
        if not self._v_lang:
            return self._get_lang_unindex(self._getCurrentLanguage())
        return self._get_lang_unindex(self._v_lang)

    def _del_unindex(self):
        if not self._v_lang:
            del self._d_unindex[self._getCurrentLanguage()]
        del self._d_unindex[self._v_lang]

    _unindex = property(fget=_get_unindex,
                        fset=_set_unindex,
                        fdel=_del_unindex)
        
    def clear(self):
        self._v_lang = None
        self._d_length = PersistentDict()
        self._d_index = PersistentDict()
        self._d_unindex = PersistentDict()

    @property
    def languages(self):
        ltool = getToolByName(getSite(), 'portal_languages', None)
        if ltool is None:
            return []
        return ltool.getSupportedLanguages()

    def index_object(self, documentId, obj, threshold=None):
        """ wrapper to handle indexing of multiple attributes """
        res = 0
        for lang in self.languages:
            self._v_lang = lang
            res += UnIndex.index_object(self, documentId, obj, threshold)
        self._v_lang = None
        return res > 0

    def unindex_object(self, documentId):
        """ Unindex the object with integer id 'documentId' and don't
        raise an exception if we fail
        """
        try:
            for lang in self.languages:
                self._v_lang = lang
                UnIndex.unindex_object(self, documentId)
        finally:
            self._v_lang = None
    
    def _get_object_datum(self, obj, attr):
        # self.id is the name of the index, which is also the name of the
        # attribute we're interested in.  If the attribute is callable,
        # we'll do so.
        try:
            datum = getattr(obj, attr)
            if safe_callable(datum):
                datum = datum()
                try:
                    datum = getattr(obj, attr)(lang=self._v_lang)
                except:
                    pass
        except AttributeError:
            datum = _marker
        return datum
