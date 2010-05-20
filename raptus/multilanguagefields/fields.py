from ExtensionClass import Base
from AccessControl import ClassSecurityInfo
from Acquisition import aq_get

from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.app.component.hooks import getSite
from zope.i18n import translate
from zope.i18nmessageid import Message

from Products.Archetypes.ClassGen import Generator, ClassGenerator
from Products.Archetypes.utils import shasattr
from Products.Archetypes import Field as fields
from Products.Archetypes.Registry import registerField

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.CMFPlone import PloneMessageFactory as _
from Products.Archetypes.Layer import DefaultLayerContainer

from raptus.multilanguagefields import MultilanguageAware
from raptus.multilanguagefields.interfaces import IMultilanguageField

class MultilanguageFieldMixin(Base):
    implements(IMultilanguageField)
    
    security = ClassSecurityInfo()
    _v_lang = None
    
    def _getCurrentLanguage(self, context):
        try:
            return getToolByName(context, 'portal_languages').getPreferredLanguage()
        except AttributeError:
            return 'en';
        
    def getDefaultLang(self, context):
        try:
            portal_languages = getToolByName(context, 'portal_languages')
        except:
            return None
        if portal_languages.allow_content_language_fallback:
            return portal_languages.getDefaultLanguage()
        else:
            return None

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
        """
        set all lang values
        if value is not a dict, set the value for the current language
        """
        current_lang = self._getCurrentLanguage(instance)
        if not value :
            return
        if value and not isinstance(value, dict):
            neutralValue = value
            value = {current_lang: neutralValue} 
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
            if not value:
                defaultLang = self.getDefaultLang(instance)
                if defaultLang:
                    self.setLanguage(defaultLang)
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
            if not value:
                defaultLang = self.getDefaultLang(instance)
                if defaultLang:
                    self.setLanguage(defaultLang)
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

    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        """
        very simple multilingual validation for required fields             
        """
        languages = self.getAvailableLanguages(instance)
        defaultLang = self.getDefaultLang(instance)
        name = self.getName()
        if not isinstance(value, dict):
            lang_values = {'all' : value}
        else :
            lang_values = {}
            for lang in languages :
                if lang['name'] in value.keys() :
                    lang_values[lang['name']]= value[lang['name']]         
            if not len(lang_values) :
                lang_values = {'all' : value}
        if defaultLang and lang_values.get(defaultLang, 0):
            return None
        for key, value in lang_values.items():    
            if not value:
                request = aq_get(instance, 'REQUEST')
                label = self.widget.Label(instance)
                if isinstance(label, Message):
                    label = translate(label, context=request)
                error = _(u'error_required',
                          default=u'${name} is required, please correct.',
                          mapping={'name': label})
                error = translate(error, context=request)
                errors[name] = error
                return error
        return None

    def __repr__(self):
        """
        Return a string representation consisting of name of the  class, 
        type and permissions.
        """
        name = self.__name__
        return "<Field %s(%s:%s)>" % (name, self.type, self.mode)
    
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
    
    security = ClassSecurityInfo()
    
    security.declareProtected(View, 'getScale')
    def getScale(self, instance, scale=None, **kwargs):
        """Get scale by name or original
        """
        if self._v_lang and not kwargs.has_key('lang'):
            return super(ImageField, self).getScale(instance, scale, **kwargs)
        if not kwargs.has_key('lang'):
            kwargs['lang'] = self._getCurrentLanguage(instance)
        self.setLanguage(kwargs['lang'])
        image = super(ImageField, self).getScale(instance, scale, **kwargs)
        if not image:
            defaultLang = self.getDefaultLang(instance)
            if defaultLang:
                self.setLanguage(defaultLang)
                image = super(MultilanguageFieldMixin, self).getScale(instance, scale, **kwargs)
        self.resetLanguage()
        return image
    
    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        value = self._wrapValue(instance, super(ImageField, self).get(instance, **kwargs))
        if (shasattr(value, '__of__', acquire=True)
            and not kwargs.get('unwrapped', False)):
            return value.__of__(instance)
        return value

    security.declareProtected(View, 'tag')
    def tag(self, instance, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        """Create a tag including scale
        """
        if self._v_lang and not kwargs.has_key('lang'):
            return super(ImageField, self).tag(instance, scale, height, width, alt, css_class, title, **kwargs)
        if not kwargs.has_key('lang'):
            kwargs['lang'] = self._getCurrentLanguage(instance)
        self.setLanguage(kwargs['lang'])
        value = self.get(instance, **kwargs)
        if not value or not value.get_size():
            defaultLang = self.getDefaultLang(instance)
            if defaultLang:
                kwargs['lang'] = defaultLang
                self.setLanguage(kwargs['lang'])
        tag = super(ImageField, self).tag(instance, scale, height, width, alt, css_class, title, **kwargs)
        self.resetLanguage()
        return tag
    
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
