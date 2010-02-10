# -*- coding: utf-8 -*-
#===============================================================================
# Patch Archetypes 
#===============================================================================
import logging
LOG = logging.getLogger('raptus.multilanguagefields')
from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from raptus.multilanguagefields.interfaces import IMultilanguageField
from Products.Archetypes import BaseObject, Schema

# BaseObject SearchableText monkey patch to support languageaware searches
BaseObject.BaseObject.old_SearchableText = BaseObject.BaseObject.SearchableText 
def new_SearchableText(self, lang=None):
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
BaseObject.BaseObject.SearchableText = new_SearchableText
LOG.info("Products.Archetypes.BaseObject.BaseObject.SearchableText patched") 

# getField patch to return the field object
# when key is fieldname____lang___
BaseObject.BaseObject.old_getField = BaseObject.BaseObject.getField   
def new_getField(self, key, wrapped=False):
    """Returns a field object.
    """
    if key.endswith('___'):
        key = key[:key.find('___')]
    
    return self.Schema().get(key)
     
BaseObject.BaseObject.getField = new_getField
LOG.info("Products.Archetypes.BaseObject.BaseObject.getField patched") 

# Patch to get the good field when moving fields
old_moveField = Schema.Schema.moveField 
def new_moveField(self, name, direction=None, pos=None, after=None, before=None):
    if name.endswith('___'):
        name = name[:name.find('___')]
    old_moveField(self, name, direction, pos, after, before)
Schema.Schema.moveField = new_moveField
LOG.info("Products.Archetypes.Schema.Schema.moveField patched") 

# patch for Schema.__getitem__ with the good key
# this method is used by schemaextender
Schema.Schema.__old_getitem__ = Schema.Schema.__getitem__ 
def __new__getitem__(self, name):
    if name.endswith('___'):
        name = name[:name.find('___')]
    return self._fields[name]
Schema.Schema.__getitem__ = __new__getitem__
LOG.info("Products.Archetypes.Schema.Schema.__getitem__  patched") 

# Archetypes Schemata monkey patch to use the good field names
Schema.Schemata._old__checkPropertyDupe = Schema.Schemata._checkPropertyDupe
def _new_checkPropertyDupe(self, field, propname):
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
Schema.Schemata._checkPropertyDupe = _new_checkPropertyDupe
LOG.info("Products.Archetypes.Schema.Schemata._checkPropertyDupe  patched") 

# ATContentTypes criteria monkey patch
# something todo here ?