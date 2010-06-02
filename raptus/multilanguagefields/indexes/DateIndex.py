from logging import getLogger

from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from ZODB.POSException import ConflictError
from App.special_dtml import DTMLFile

from Products.PluginIndexes.common import safe_callable

from Products.PluginIndexes.DateIndex.DateIndex import DateIndex, _marker
from raptus.multilanguagefields.indexes.UnIndex import MultilanguageUnIndex

LOG = getLogger('DateIndex')

class MultilanguageDateIndex(MultilanguageUnIndex, DateIndex):

    meta_type = 'MultilanguageDateIndex'

    manage_options=DateIndex.manage_options
    query_options=DateIndex.query_options
    manage=DateIndex.manage
    manage_browse=DateIndex.manage_browse
    
    _apply_index = DateIndex._apply_index
    
    def _get_lang_index(self, lang):
        if not self._d_index.has_key(lang):
            self._d_index[lang] = IOBTree()
        return self._d_index[lang]

    def _get_lang_unindex(self, lang):
        if not self._d_unindex.has_key(lang):
            self._d_unindex[lang] = OIBTree()
        return self._d_unindex[lang]

    def index_object(self, documentId, obj, threshold=None):
        """index an object, normalizing the indexed value to an integer

           o Normalized value has granularity of one minute.

           o Objects which have 'None' as indexed value are *omitted*,
             by design.
        """
        returnStatus = 0
        date_attr = getattr( obj, self.id, None )
        if not date_attr:
            return returnStatus
        for lang in self.languages:
            self._v_lang = lang
            try:
                if safe_callable( date_attr ):
                    date = date_attr()
                    try: date = date(lang=lang)
                    except: pass
                else:
                    date = date_attr
                ConvertedDate = self._convert( value=date, default=_marker )
            except AttributeError:
                ConvertedDate = _marker
    
            oldConvertedDate = self._unindex.get( documentId, _marker )
    
            if ConvertedDate != oldConvertedDate:
                if oldConvertedDate is not _marker:
                    self.removeForwardIndexEntry(oldConvertedDate, documentId)
                    if ConvertedDate is _marker:
                        try:
                            del self._unindex[documentId]
                        except ConflictError:
                            raise
                        except:
                            LOG.error("Should not happen: ConvertedDate was there,"
                                      " now it's not, for document with id %s" %
                                      documentId)
    
                if ConvertedDate is not _marker:
                    self.insertForwardIndexEntry( ConvertedDate, documentId )
                    self._unindex[documentId] = ConvertedDate
                    
                returnStatus = 1
        self._v_lang = None
        return returnStatus

manage_addMultilanguageDateIndexForm = DTMLFile( 'dtml/addDateIndex', globals() )

def manage_addMultilanguageDateIndex( self, id, REQUEST=None, RESPONSE=None, URL3=None):
    """Add a Multilanguage Date index"""
    return self.manage_addIndex(id, 'MultilanguageDateIndex', extra=None, \
                    REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
