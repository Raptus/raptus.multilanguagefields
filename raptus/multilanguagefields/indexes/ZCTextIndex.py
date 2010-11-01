from Acquisition import aq_base
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile

from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex
from Products.ZCTextIndex.interfaces import ILexicon

from zope.app.component.hooks import getSite

from Products.PluginIndexes.common import safe_callable
from Products.CMFCore.utils import getToolByName

class MultilanguageZCTextIndex(ZCTextIndex):
    """Multilanguage Persistent text index.
    """

    meta_type = 'MultilanguageZCTextIndex'

    _v_lang = None

    def _getCurrentLanguage(self):
        return getToolByName(getSite(), 'portal_languages').getPreferredLanguage()

    @property
    def languages(self):
        ltool = getToolByName(getSite(), 'portal_languages', None)
        if ltool is None:
            return []
        return ltool.getSupportedLanguages()
    
    def _get_lang_index(self, lang):
        if not hasattr(self, '_index_%s' % lang):
            setattr(self, '_index_%s' % lang, self._index_factory(aq_base(self.getLexicon())))
        return getattr(self, '_index_%s' % lang)

    def _set_index(self, value):
        if not self._v_lang:
            setattr(self, '_index_%s' % self._getCurrentLanguage(), value)
        else:
            setattr(self, '_index_%s' % self._v_lang, value)

    def _get_index(self):
        if not self._v_lang:
            return self._get_lang_index(self._getCurrentLanguage())
        return self._get_lang_index(self._v_lang)

    def _del_index(self):
        if not self._v_lang:
            for lang in self.languages:
                delattr(self, '_index_%s' % lang)
        else:
            delattr(self, '_index_%s' % self._v_lang)

    index = property(fget=_get_index,
                     fset=_set_index,
                     fdel=_del_index)

    def getLexicon(self):
        """Get the lexicon for this index
        """
        try:
            return ZCTextIndex.getLexicon(self)
        except:
            lexicon = getattr(getToolByName(getSite(), 'portal_catalog'), self.lexicon_id)
            if not ILexicon.providedBy(lexicon):
                raise TypeError('Object "%s" is not a ZCTextIndex Lexicon'
                                % repr(lexicon))
            self._v_lexicon = lexicon
            return lexicon

    ## Pluggable Index APIs ##

    def index_object(self, documentId, obj, threshold=None):
        try: fields = self._indexed_attrs
        except: fields  = [ self._fieldname ]
        res = 0
        
        for lang in self.languages:
            all_texts = []
            for attr in fields:
                text = getattr(obj, attr, None)
                if text is None:
                    continue
                if safe_callable(text):
                    try: text = text(lang=lang)
                    except: text = text()
                if text is None:
                    continue
                if text:
                    if isinstance(text, (list, tuple, )):
                        all_texts.extend(text)
                    else:
                        all_texts.append(text)
    
            # Check that we're sending only strings
            all_texts = filter(lambda text: isinstance(text, basestring), \
                               all_texts)
            if all_texts:
                self._v_lang = lang
                res += self.index.index_doc(documentId, all_texts)
        self._v_lang = None
        return res > 0

    def unindex_object(self, docid):
        for lang in self.languages:
            self._v_lang = lang
            if self.index.has_doc(docid):
                self.index.unindex_doc(docid)
        self._v_lang = None

InitializeClass(MultilanguageZCTextIndex)

def manage_addMultilanguageZCTextIndex(self, id, extra=None, REQUEST=None,
                          RESPONSE=None):
    """Add a multilanguage text index"""
    if REQUEST is None:
        URL3 = None
    else:
        URL3 = REQUEST.URL3
    return self.manage_addIndex(id, 'MultilanguageZCTextIndex', extra,
                                REQUEST, RESPONSE, URL3)

manage_addMultilanguageZCTextIndexForm = DTMLFile('dtml/addZCTextIndex', globals())
