from AccessControl import ClassSecurityInfo

from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.app.component.hooks import getSite

from Products.Archetypes.ClassGen import Generator, ClassGenerator
from Products.Archetypes.utils import shasattr
from Products.Archetypes import Field as fields
from Products.Archetypes.Registry import registerField

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.CMFPlone import PloneMessageFactory as _

from raptus.multilanguagefields import MultilanguageAware
from raptus.multilanguagefields.interfaces import IMultilanguageField

class MultilanguageFieldMixin(object):
    implements(IMultilanguageField)
    
    security = ClassSecurityInfo()
    _v_lang = None
    
    def _getCurrentLanguage(self, context):
        try:
            return getToolByName(context, 'portal_languages').getPreferredLanguage()
        except AttributeError:
            return 'en';

    security.declarePublic('getName')
    def getName(self):
        """Return the name of this field as a string"""
        if self._v_lang is not None:
            return '%s___%s___' % (self.__name__, self._v_lang)
        return self.__name__
    
    security.declarePrivate('getAvailableLanguages')
    def getAvailableLanguages(self, context):
        portal_state = queryMultiAdapter((context, context.REQUEST), name=u'plone_portal_state')
        languages = portal_state.locale().displayNames.languages
        current = self._getCurrentLanguage(context)
        def current_first(x, y):
            if x['name'] == current:
                return -1
            return 0
        langs = [{'name': name, 'title': languages.get(name, title)} for name, title in getToolByName(context, 'portal_languages').listSupportedLanguages()]
        langs.sort(current_first)
        return langs

    security.declarePrivate('setLanguage')
    def setLanguage(self, lang):
        self.resetLanguage()
        self._v_lang = lang
    
    security.declarePrivate('resetLanguage')
    def resetLanguage(self):
        self._v_lang = None
        
    security.declarePrivate('getCallable')
    def getCallable(self, instance, lang):
        def callable(**kwargs):
            return self.get(instance, lang=lang, **kwargs)
        return callable

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        if not isinstance(value, dict):
            return
        for lang, val in value.items():
            self.setLanguage(lang)
            kw = kwargs.copy()
            kw.update(kwargs.get(lang, {}))
            super(MultilanguageFieldMixin, self).set(instance, val, **kw)
        self.resetLanguage()
        if not hasattr(instance, self.getName()):
            generator = Generator()
            classgenerator = ClassGenerator()
            generator.makeMethod(type(instance.aq_base), self, 'r', self.getName())
            classgenerator.updateSecurity(type(instance.aq_base), self, 'r', self.getName())
    
    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        name = self.getName()
        if not name.endswith('___'):
            if not kwargs.has_key('lang'):
                kwargs['lang'] = self._getCurrentLanguage(instance)
            if kwargs['lang'] == 'all':
                return self.getAll(instance, **kwargs)
            self.setLanguage(kwargs['lang'])
            value = super(MultilanguageFieldMixin, self).get(instance, **kwargs)
            self.resetLanguage()
        else:
            value = super(MultilanguageFieldMixin, self).get(instance, **kwargs)
        return value

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        name = self.getName()
        if not name.endswith('___'):
            if not kwargs.has_key('lang'):
                kwargs['lang'] = self._getCurrentLanguage(instance)
            self.setLanguage(kwargs['lang'])
            value = super(MultilanguageFieldMixin, self).getRaw(instance, **kwargs)
            self.resetLanguage()
        else:
            value = super(MultilanguageFieldMixin, self).getRaw(instance, **kwargs)
        return value
    
    security.declarePrivate('getAll')
    def getAll(self, instance, **kwargs):
        languages = self.getAvailableLanguages(instance)
        value = {}
        for lang in languages:
            value[lang['name']] = self.get(instance, lang=lang['name'])
        return value
    
class StringField(MultilanguageFieldMixin, fields.StringField):
    _properties = fields.StringField._properties.copy()
    
class FileField(MultilanguageFieldMixin, fields.FileField):
    _properties = fields.FileField._properties.copy()
    
class TextField(MultilanguageFieldMixin, fields.TextField):
    _properties = fields.TextField._properties.copy()
    
class DateTimeField(MultilanguageFieldMixin, fields.DateTimeField):
    _properties = fields.DateTimeField._properties.copy()
    
class LinesField(MultilanguageFieldMixin, fields.LinesField):
    _properties = fields.LinesField._properties.copy()
    
class IntegerField(MultilanguageFieldMixin, fields.IntegerField):
    _properties = fields.IntegerField._properties.copy()
    
class FloatField(MultilanguageFieldMixin, fields.FloatField):
    _properties = fields.FloatField._properties.copy()
    
class FixedPointField(MultilanguageFieldMixin, fields.FixedPointField):
    _properties = fields.FixedPointField._properties.copy()
    _properties.update({
        'validators' : ('isDecimalMultilanguage'),
        })
    
class ReferenceField(MultilanguageFieldMixin, fields.ReferenceField):
    _properties = fields.ReferenceField._properties.copy()
    
    security = ClassSecurityInfo()
    
    def __init__(self, name=None, **kwargs):
        self._relationship = kwargs['relationship']
        super(ReferenceField, self).__init__(name, **kwargs)
    
    @property
    def relationship(self):
        lang = self._v_lang
        if lang is None:
            lang = self._getCurrentLanguage(getSite())
        return '%s___%s___' % (self._relationship, lang)
    
class BooleanField(MultilanguageFieldMixin, fields.BooleanField):
    _properties = fields.BooleanField._properties.copy()
    
class ImageField(MultilanguageFieldMixin, fields.ImageField):
    _properties = fields.ImageField._properties.copy()
    # XXX: Fix me (not working)
    
registerField(StringField,
              title='Multilanguage String',
              description='Used for storing simple strings')

registerField(FileField,
              title='Multilanguage File',
              description='Used for storing files')

registerField(TextField,
              title='Multilanguage Text',
              description=('Used for storing text which can be '
                           'used in transformations'))

registerField(DateTimeField,
              title='Multilanguage Date Time',
              description='Used for storing date/time')

registerField(LinesField,
              title='Multilanguage LinesField',
              description=('Used for storing text which can be '
                           'used in transformations'))

registerField(IntegerField,
              title='Multilanguage Integer',
              description='Used for storing integer values')

registerField(FloatField,
              title='Multilanguage Float',
              description='Used for storing float values')

registerField(FixedPointField,
              title='Multilanguage Fixed Point',
              description='Used for storing fixed point values')

registerField(ReferenceField,
              title='Multilanguage Reference',
              description=('Used for storing references to '
                           'other Archetypes Objects'))

registerField(BooleanField,
              title='Multilanguage Boolean',
              description='Used for storing boolean values')

registerField(ImageField,
              title='Multilanguage Image',
              description=('Used for storing images. '
                           'Images can then be retrieved in '
                           'different thumbnail sizes'))
