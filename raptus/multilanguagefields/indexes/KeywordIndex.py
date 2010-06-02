from types import StringType, UnicodeType
from logging import getLogger

from BTrees.OOBTree import OOSet
from App.special_dtml import DTMLFile

from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.common.UnIndex import UnIndex
from Products.PluginIndexes.KeywordIndex.KeywordIndex import KeywordIndex

from raptus.multilanguagefields.indexes.UnIndex import MultilanguageUnIndex

class MultilanguageKeywordIndex(MultilanguageUnIndex, KeywordIndex):
    meta_type="MultilanguageKeywordIndex"

    manage_options=KeywordIndex.manage_options
    query_options=KeywordIndex.query_options
    manage=KeywordIndex.manage
    manage_browse=KeywordIndex.manage_browse
    _index_object=KeywordIndex._index_object

    def _get_object_keywords(self, obj, attr):
        newKeywords = getattr(obj, attr, ())
        if safe_callable(newKeywords):
            newKeywords = newKeywords()
            try:
                newKeywords = getattr(obj, attr)(lang=self._v_lang)
            except:
                pass
        if (isinstance(newKeywords, StringType)
            or isinstance(newKeywords, UnicodeType)): #Python 2.1 compat isinstance
            return (newKeywords,)
        else:
            unique = {}
            try:
                for k in newKeywords:
                    unique[k] = None
            except TypeError:
                # Not a sequence
                return (newKeywords,)
            else:
                return unique.keys()

    def unindex_object(self, documentId):
        try:
            for lang in self.languages:
                self._v_lang = lang
                KeywordIndex.unindex_object(self, documentId)
        finally:
            self._v_lang = None

    def uniqueValues(self, name=None, withLengths=0, lang=None):
        if lang:
            self._v_lang = lang
        results = UnIndex.uniqueValues(self, name, withLengths)
        self._v_lang = None
        return results

manage_addMultilanguageKeywordIndexForm = DTMLFile('dtml/addKeywordIndex', globals())

def manage_addMultilanguageKeywordIndex(self, id, extra=None,
        REQUEST=None, RESPONSE=None, URL3=None):
    """Add a multilanguage keyword index"""
    return self.manage_addIndex(id, 'MultilanguageKeywordIndex', extra=extra, \
              REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
