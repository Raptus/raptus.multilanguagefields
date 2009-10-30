from Missing import MV
from persistent import Persistent
from persistent.dict import PersistentDict
from ZODB.POSException import ConflictError
from zope.interface import implements
from zope.app.component.hooks import getSite

from Products.Archetypes import BaseObject, Schema
from Products.ZCatalog.Catalog import Catalog, safe_callable
from Products.CMFPlone import utils
from Products.CMFPlone.browser.ploneview import Plone

from zope.i18nmessageid import MessageFactory
multilanguagefieldsMessageFactory = MessageFactory('raptus.multilanguagefields')
from Products.PlacelessTranslationService.utility import PTSTranslationDomain
multilanguagefieldsdomain = PTSTranslationDomain('raptus.multilanguagefields')

# initialize validators
from raptus.multilanguagefields.validators import initialize
from Products.validation.config import validation
initialize(validation)

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import Field

from raptus.multilanguagefields.interfaces import IMultilanguageAware, IMultilanguageField

class MultilanguageAware(Persistent):
    """a multilanguage aware persistent proxy"""
    implements(IMultilanguageAware)
    def __init__(self, values):
        self._values = PersistentDict(values)
        Persistent.__init__(self)
    def __call__(self):
        return self.data
    def _getCurrentLanguage(self):
        return getToolByName(getSite(), 'portal_languages').getPreferredLanguage()
    def getLang(self, lang):
        if self._values.has_key(lang):
            return self._values[lang]
        return ''
    @property
    def data(self):
        return self.getLang(self._getCurrentLanguage())
    def __getattr__(self, attr):
        return getattr(self.data, attr)
    def __unicode__(self):
        return unicode(self.data)
    def __str__(self):
        return str(self.data)
    def getclass(self):
        return self.data.getclass()
    __class__ = property(getclass)

# monkey patches

# catalog monkey patch to support languageaware metadata
def _recordify(self, object):
    """ turns an object into a record tuple """
    record = []
    # the unique id is allways the first element
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
Catalog.recordify = _recordify

# safe_unicode monkey patch
_base_safe_unicode = utils.safe_unicode
def _safe_unicode(value, encoding='utf-8'):
    if IMultilanguageAware.providedBy(value):
        value = str(value)
    return _base_safe_unicode(value, encoding)
utils.safe_unicode = _safe_unicode

# cropText monkey patch
Plone._cropText = Plone.cropText
def _cropText(self, text, length, ellipsis='...'):
    if IMultilanguageAware.providedBy(text):
        text = str(text)
    return self._cropText(text, length, ellipsis)
Plone.cropText = _cropText

# Archetypes monkey patch
def _decode(value, instance, **kwargs):
    """ensure value is an unicode string"""
    if isinstance(value, str):
        encoding = kwargs.get('encoding')
        if encoding is None:
            try:
                encoding = instance.getCharset()
            except AttributeError:
                # that occurs during object initialization
                # (no acquisition wrapper)
                encoding = 'UTF8'
        if IMultilanguageAware.providedBy(value):
            # we have a multilanguage aware string
            value = value.data
        value = unicode(value, encoding)
    return value
Field.decode = _decode

# SearchableText monkey patch to support languageaware searches
def _SearchableText(self, lang=None):
    """All fields marked as 'searchable' are concatenated together
    here for indexing purpose.
    """
    data = []
    charset = self.getCharset()
    for field in self.Schema().fields():
        if not field.searchable:
            continue
        method = field.getIndexAccessor(self)
        if IMultilanguageField.providedBy(field) and lang:
            field.setLanguage(lang)
        try:
            datum = method(mimetype="text/plain")
        except TypeError:
            # Retry in case typeerror was raised because accessor doesn't
            # handle the mimetype argument
            try:
                datum =  method()
            except (ConflictError, KeyboardInterrupt):
                raise
            except:
                continue
        if datum:
            type_datum = type(datum)
            vocab = field.Vocabulary(self)
            if isinstance(datum, list) or isinstance(datum, tuple):
                # Unmangle vocabulary: we index key AND value
                vocab_values = map(lambda value, vocab=vocab: vocab.getValue(value, ''), datum)
                datum = list(datum)
                datum.extend(vocab_values)
                datum = ' '.join(datum)
            elif isinstance(datum, basestring):
                if isinstance(datum, unicode):
                    datum = datum.encode(charset)
                value = vocab.getValue(datum, '')
                if isinstance(value, unicode):
                    value = value.encode(charset)
                datum = "%s %s" % (datum, value, )

            if isinstance(datum, unicode):
                datum = datum.encode(charset)
                
            data.append(str(datum))
        if IMultilanguageField.providedBy(field) and lang:
            field.resetLanguage()
            
    data = ' '.join(data)
    return data
BaseObject.BaseObject.SearchableText = _SearchableText

def _getField(self, key, wrapped=False):
    """Returns a field object.
    """
    if key.endswith('___'):
        key = key[:key.find('___')]
    return self.Schema().get(key)
BaseObject.BaseObject.getField = _getField

# Schemata monkey patch
def _checkPropertyDupe(self, field, propname):
    check_value = getattr(field, propname, Schema._marker)
    # None is fine too.
    if check_value is Schema._marker or check_value is None:
        return False
    check_name = field.getName()
    if IMultilanguageField.providedBy(field) and \
       check_name.endswith('___'):
        check_name = check_name[:check_name.find('___')]
    for f in self.fields():
        got = getattr(f, propname, Schema._marker)
        if got == check_value and f.getName() != check_name:
            return f, got
    return False
Schema.Schemata._checkPropertyDupe = _checkPropertyDupe