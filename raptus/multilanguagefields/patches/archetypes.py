# -*- coding: utf-8 -*-
#===============================================================================
# Patch Archetypes 
#===============================================================================
from urlparse import urlparse

from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Products.Archetypes import BaseObject, Schema
from Products.Archetypes.Storage import annotation
from Products.Archetypes.utils import shasattr
from Products.ATContentTypes.content.file import ATCTFileContent
from raptus.multilanguagefields.interfaces import IMultilanguageField
from raptus.multilanguagefields import LOG

try:
    from plone.app.blob.interfaces import IBlobField
except ImportError:
    from zope.interface import Interface
    class IBlobField(Interface):
        """"""

# ATCTFileContent index_html monkey patch to make caching language aware
ATCTFileContent.__old__index_html = ATCTFileContent.index_html
def __new__index_html(self, REQUEST=None, RESPONSE=None):
    """Make it directly viewable when entering the objects URL
    """
    field = self.getPrimaryField()
    if not IBlobField.providedBy(field) and IMultilanguageField.providedBy(field):
        if REQUEST is None and hasattr(self, 'REQUEST'):
            REQUEST = self.REQUEST
        if REQUEST is not None and not 'lang' in REQUEST.keys():
            url = REQUEST['ACTUAL_URL']
            url += urlparse(url).query and '&' or '?'
            url += 'lang='+field._getCurrentLanguage(self)
            return REQUEST.response.redirect(url)
    return self.__old__index_html(REQUEST, RESPONSE)
ATCTFileContent.index_html = __new__index_html
LOG.info("Products.ATContentTypes.content.base.ATCTFileContent.index_html patched")

# BaseObject SearchableText monkey patch to support languageaware searches
BaseObject.BaseObject.__old_SearchableText = BaseObject.BaseObject.SearchableText 
def __new_SearchableText(self, lang=None):
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
BaseObject.BaseObject.SearchableText = __new_SearchableText
LOG.info("Products.Archetypes.BaseObject.BaseObject.SearchableText patched") 

# getField patch to return the field object
# when key is fieldname____lang___
BaseObject.BaseObject.__old_getField = BaseObject.BaseObject.getField   
def __new_getField(self, key, wrapped=False):
    """Returns a field object.
    """
    if key.endswith('___'):
        key = key[:key.find('___')]
    return self.__old_getField(key, wrapped)
BaseObject.BaseObject.getField = __new_getField
LOG.info("Products.Archetypes.BaseObject.BaseObject.getField patched") 

# Patch to get the good field when moving fields
Schema.Schema.__old_moveField = Schema.Schema.moveField 
def __new_moveField(self, name, direction=None, pos=None, after=None, before=None):
    if name.endswith('___'):
        name = name[:name.find('___')]
    self.__old_moveField(name, direction, pos, after, before)
Schema.Schema.moveField = __new_moveField
LOG.info("Products.Archetypes.Schema.Schema.moveField patched") 

# patch for Schema.__getitem__ with the good key
# this method is used by schemaextender
Schema.Schema.__old___getitem__ = Schema.Schema.__getitem__ 
def __new___getitem__(self, name):
    if name.endswith('___'):
        name = name[:name.find('___')]
    return self.__old___getitem__(name)
Schema.Schema.__getitem__ = __new___getitem__
LOG.info("Products.Archetypes.Schema.Schema.__getitem__ patched")

# patch for Schema.__setitem__ with the good key
# this method is used by schemaextender
Schema.Schema.__old___setitem__ = Schema.Schema.__setitem__
def __new___setitem__(self, name, field):
    lang = None
    if IMultilanguageField.providedBy(field):
        lang = field._v_lang
        field.resetLanguage()
    assert name == field.getName()
    self.addField(field)
    if lang is not None:
        field.setLanguage(lang)
Schema.Schema.__setitem__ = __new___setitem__
LOG.info("Products.Archetypes.Schema.Schema.__setitem__ patched")

# patch for validate images and file upload
# without this patch we can't keep an image by editing the content
Schema.BasicSchema.__old_validate = Schema.BasicSchema.validate
_marker = Schema._marker
def __new_validate__(self, instance, REQUEST, errors, data, metadata):
    """Validate the state of the entire object.

    The passed dictionary ``errors`` will be filled with human readable
    error messages as values and the corresponding fields' names as
    keys.

    If a REQUEST object is present, validate the field values in the
    REQUEST.  Otherwise, validate the values currently in the object.
    """
    if REQUEST:
        fieldset = REQUEST.form.get('fieldset', None)
        fieldsets = REQUEST.form.get('fieldsets', None)
    else:
        fieldset = fieldsets = None
    fields = []

    if fieldsets is not None:
        schemata = instance.Schemata()
        for fieldset in fieldsets:
            fields += [(field.getName(), field)
                       for field in schemata[fieldset].fields()]            
    elif fieldset is not None:
        schemata = instance.Schemata()
        fields = [(field.getName(), field)
                  for field in schemata[fieldset].fields()]            
    else:
        if data:
            fields.extend([(field.getName(), field)
                           for field in self.filterFields(isMetadata=0)])
        if metadata:
            fields.extend([(field.getName(), field)
                           for field in self.filterFields(isMetadata=1)])

    if REQUEST:
        form = REQUEST.form
    else:
        form = None
        
    for name, field in fields:
        
        # Should not validate something we can't write to anyway
        if not field.writeable(instance):
            continue
        
        error = 0
        value = None
        widget = field.widget
        
        if widget.isVisible(widget, 'edit') != 'visible':
            continue
        
        if form:
            result = widget.process_form(instance, field, form,
                                         empty_marker=_marker)
        else:
            result = None
        if IMultilanguageField.providedBy(field):
            value = {}
            for l, r in result[0].items():
                if r is None or r is _marker:
                    accessor = field.getEditAccessor(instance) or field.getAccessor(instance)
                    if accessor is not None:
                        r = accessor()
                    else:
                        # can't get value to validate -- bail
                        continue
                value[l] = r
        else:
            if result is None or result is _marker:
                accessor = field.getEditAccessor(instance) or field.getAccessor(instance)
                if accessor is not None:
                    value = accessor()
                else:
                    # can't get value to validate -- bail
                    continue
            else:
                value = result[0]

        res = field.validate(instance=instance,
                             value=value,
                             errors=errors,
                             REQUEST=REQUEST)
        if res:
            errors[field.getName()] = res
    return errors
Schema.BasicSchema.validate = __new_validate__
LOG.info("Products.Archetypes.Schema.BasicSchema.validate patched")

# Archetypes Schemata monkey patch to use the good field names
Schema.Schemata.__old_addField = Schema.Schemata.addField
def __new_addField(self, field):
    lang = None
    if IMultilanguageField.providedBy(field):
        lang = field._v_lang
        field.resetLanguage()
    self.__old_addField(field)
    if lang is not None:
        field.setLanguage(lang)
Schema.Schemata.addField = __new_addField
LOG.info("Products.Archetypes.Schema.Schemata.addField patched") 

# Archetypes Schemata monkey patch to use the good field names
Schema.Schemata.__old__validateOnAdd = Schema.Schemata._validateOnAdd
def __new__validateOnAdd(self, field):
    """Validates fields on adding and bootstrapping
    """
    lang = None
    if IMultilanguageField.providedBy(field):
        lang = field._v_lang
        field.resetLanguage()
    try:
        self.__old__validateOnAdd(field)
    finally:
        if lang is not None:
            field.setLanguage(lang)
Schema.Schemata._validateOnAdd = __new__validateOnAdd
LOG.info("Products.Archetypes.Schema.Schemata._validateOnAdd patched") 

# Archetypes Schemata monkey patch to use the good field names
Schema.Schemata.__old__checkPropertyDupe = Schema.Schemata._checkPropertyDupe
def __new__checkPropertyDupe(self, field, propname):
    lang = None
    if IMultilanguageField.providedBy(field):
        lang = field._v_lang
        field.resetLanguage()
    r = self.__old__checkPropertyDupe(field, propname)
    if lang is not None:
        field.setLanguage(lang)
    return r
Schema.Schemata._checkPropertyDupe = __new__checkPropertyDupe
LOG.info("Products.Archetypes.Schema.Schemata._checkPropertyDupe patched") 

# Archetypes AnnotationStorage monkey patch
annotation.AnnotationStorage.__old__cleanup = annotation.AnnotationStorage._cleanup
def __new__cleanup(self, name, instance, value, **kwargs):
    if shasattr(instance, name) and not callable(getattr(instance, name)):
        delattr(instance, name)
annotation.AnnotationStorage._cleanup = __new__cleanup
LOG.info("Products.Archetypes.Storage.annotation.AnnotationStorage._cleanup patched") 

# ATContentTypes criteria monkey patch
# something todo here ?