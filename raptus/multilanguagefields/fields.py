from ExtensionClass import Base
from AccessControl import ClassSecurityInfo
from Acquisition import aq_get

from zope.interface import implements
from zope.component import queryMultiAdapter
from zope.app.component.hooks import getSite
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.site.hooks import getSite

from Products.Archetypes.ClassGen import Generator, ClassGenerator
from Products.Archetypes.utils import shasattr
from Products.Archetypes import Field as fields
from Products.Archetypes.Registry import registerField
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes.Layer import DefaultLayerContainer

from raptus.multilanguagefields import multilanguagefieldsMessageFactory as _
from raptus.multilanguagefields.interfaces import IMultilanguageField

def is_blob(obj):
    return False
try:
    from plone.app.blob.interfaces import IBlobField
    def is_blob(field):
        return IBlobField.providedBy(field)
except ImportError:
    pass

class MultilanguageFieldMixin(Base):
    implements(IMultilanguageField)
    
    security = ClassSecurityInfo()
    _v_lang = None

    # making required fields not required if language fallback is enabled
    # and the current language is not the default one
    def __init__(self, name=None, **kwargs):
        self._required = kwargs.has_key('required') and kwargs['required'] or self._properties['required']
        super(MultilanguageFieldMixin, self).__init__(name, **kwargs)
    def _set_required(self, value):
        self._required = value
    def _get_required(self):
        context = getSite()
        if self.haveLanguageFallback(context):
            current = self._v_lang
            if current is None:
                current = self._getCurrentLanguage(context)
            default = self.getDefaultLang(context)
            return default == current and getattr(self, '_required', False)
        return getattr(self, '_required', False)
    required = property(fget=_get_required,
                        fset=_set_required)
    
    def _getTool(self, context):
        try:
            return getToolByName(context, 'portal_languages')
        except:
            try:
                return getToolByName(getSite(), 'portal_languages')
            except:
                pass
        return None
    
    def _getCurrentLanguage(self, context):
        try:
            return self._getTool(context).getPreferredLanguage()
        except AttributeError:
            return 'en'

    def haveLanguageFallback(self, context):
         try:
             return self._getTool(context).allow_content_language_fallback
         except:
             return False

    def getDefaultLang(self, context):
        if self.haveLanguageFallback(context):
            try:
                return self._getTool(context).getDefaultLanguage()
            except AttributeError:
                pass
        return None

    security.declarePublic('getName')
    def getName(self):
        """Return the name of this field as a string"""
        if self._v_lang is not None:
            return '%s___%s___' % (self.__name__, self._v_lang)
        return self.__name__
    
    security.declarePrivate('getAvailableLanguages')
    def getAvailableLanguages(self, context):
        request = aq_get(context, 'REQUEST')
        default = self.getDefaultLang(context)
        portal_state = queryMultiAdapter((context, request), name=u'plone_portal_state')
        languages = portal_state.locale().displayNames.languages
        if self.haveLanguageFallback(context):
            default_marker = " (%s)" % translate(_(u"default language"), context=request)
        else:
            default_marker = ""
        langs = [{'name': name, 
                  'title': translate(languages.get(name, title), context=request) +
                           (name == default and default_marker or "")} for name, title in self._getTool(context).listSupportedLanguages()]
        def default_first(x, y):
            if x['name'] == default:
                return -1
            return 0
        langs.sort(default_first)
        return langs

    security.declarePrivate('setLanguage')
    def setLanguage(self, lang):
        self.resetLanguage()
        if not lang == 'original':
            self._v_lang = lang
    
    security.declarePrivate('resetLanguage')
    def resetLanguage(self):
        self._v_lang = None
        
    security.declarePrivate('getCallable')
    def getCallable(self, instance, lang):
        def callable(**kwargs):
            return self.get(instance, lang=lang, **kwargs)
        return callable
    
    def _getLangFromStorage(self, instance, lang):
        try:
            return self.getStorage(instance).get('%s___%s___' % (self.__name__, lang), instance)
        except AttributeError:
            return None
    
    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        set all lang values
        if value is not a dict, set the value for the current language
        """
        reset = True
        if kwargs.get('_initializing_', False) and not isinstance(value, dict) and isinstance(self, TextField):
            try:
                languages = self._getTool(instance).listSupportedLanguages()
            except AttributeError:
                return
            new_value = {}
            for lang, name in languages:
                if not self._getLangFromStorage(instance, lang):
                    new_value[lang] = value
            value = new_value
        if not value and kwargs.get('_initializing_', False):
            return
        if not isinstance(value, dict):
            if self._v_lang:
                reset = False
                value = {self._v_lang: value}
            else:
                value = {self._getCurrentLanguage(instance): value}
        for lang, val in value.items():
            self.setLanguage(lang)
            kw = kwargs.copy()
            kw.update(kwargs.get(lang, {}))
            super(MultilanguageFieldMixin, self).set(instance, val, **kw)
        if reset:
            self.resetLanguage()
        if not hasattr(instance, self.getName()):
            generator = Generator()
            classgenerator = ClassGenerator()
            generator.makeMethod(type(instance.aq_base), self, 'r', self.getName())
            classgenerator.updateSecurity(type(instance.aq_base), self, 'r', self.getName())
    
    def _get_lang(self, instance, **kwargs):
        if kwargs.has_key('lang'):
            return kwargs['lang']
        try:
            lang = instance.REQUEST.get('lang', None)
            if lang is not None:
                return lang
        except:
            pass
        return self._getCurrentLanguage(instance)
    
    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        if self._v_lang:
            value = super(MultilanguageFieldMixin, self).get(instance, **kwargs)
        else:
            kwargs['lang'] = self._get_lang(instance, **kwargs)
            if kwargs['lang'] == 'all':
                return self.getAll(instance, **kwargs)
            self.setLanguage(kwargs['lang'])
            # prevent overriding of default language when getting the original one
            if kwargs['lang'] == 'original' and self.getDefault(instance):
                kwargs['_initializing_'] = True
            value = super(MultilanguageFieldMixin, self).get(instance, **kwargs)
            if not value:
                defaultLang = self.getDefaultLang(instance)
                if defaultLang and not defaultLang == self._v_lang:
                    try: # close possible open empty blob
                        if is_blob(self) and value.blob.opened():
                            value.blob._p_invalidate()
                    except:
                        pass
                    self.setLanguage(defaultLang)
                    value = super(MultilanguageFieldMixin, self).get(instance, **kwargs)
            self.resetLanguage()
        return value

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        if self._v_lang:
            value = super(MultilanguageFieldMixin, self).getRaw(instance, **kwargs)
        else:
            kwargs['lang'] = self._get_lang(instance, **kwargs)
            self.setLanguage(kwargs['lang'])
            value = super(MultilanguageFieldMixin, self).getRaw(instance, **kwargs)
            if not value:
                defaultLang = self.getDefaultLang(instance)
                if defaultLang and not defaultLang == self._v_lang:
                    try: # close possible open empty blob
                        if is_blob(self) and value.blob.opened():
                            value.blob._p_invalidate()
                    except:
                        pass
                    self.setLanguage(defaultLang)
                    value = super(MultilanguageFieldMixin, self).getRaw(instance, **kwargs)
            self.resetLanguage()
        return value
    
    security.declarePrivate('getAll')
    def getAll(self, instance, **kwargs):
        languages = self.getAvailableLanguages(instance)
        value = {}
        for lang in languages:
            value[lang['name']] = self.get(instance, lang=lang['name'])
        return value
    
    security.declarePrivate('validate')
    def validate(self, value, instance, errors=None, **kwargs):
        """ multilingual validation respecting language fallback
        """
        defaultLang = self.getDefaultLang(instance)
        request = kwargs.get('REQUEST')
        if not isinstance(value, dict):
            return super(MultilanguageFieldMixin, self).validate(value, instance, errors, **kwargs)
        else:
            for lang, val in value.items():
                val = val or value.get(defaultLang, 0)
                self.setLanguage(lang)
                res = super(MultilanguageFieldMixin, self).validate(val, instance, errors, **kwargs)
                self.resetLanguage()
                # return the first error if langFallback is deactivated
                if res is not None and defaultLang is None:
                    if request.form.get('form.button.save', False):
                        return res
                    # request came from ajax validation
                    # only validate a single language field
                    # need a helper javascript validation_helper.js
                    fieldname = request.form.get('fieldname')
                    if request.form.get('multilanguagefield_validation','') == '%s___%s___' % (fieldname, lang):
                        return res
                if res is not None and lang == defaultLang:
                    return res

    security.declarePrivate('validate_required')
    def validate_required(self, instance, value, errors):
        res = super(MultilanguageFieldMixin, self).validate_required(instance, value, errors)
        if self.haveLanguageFallback(instance) and res:
            defaultLang = self.getDefaultLang(instance)
            if self._v_lang == defaultLang:
                request = aq_get(instance, 'REQUEST')
                label = self.widget.Label(instance)
                name = self.getName()
                if isinstance(label, Message):
                    label = translate(label, context=request)
                res = _(u'error_required_default',
                        default=u'${name} is required, please provide at least the default language.',
                        mapping={'name': label})
                res = translate(res, context=request)
                errors[name] = res
        return res

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
        if self._v_lang:
            return super(ImageField, self).getScale(instance, scale, **kwargs)
        if not kwargs.has_key('lang'):
            kwargs['lang'] = self._getCurrentLanguage(instance)
        self.setLanguage(kwargs['lang'])
        image = super(ImageField, self).getScale(instance, scale, **kwargs)
        if not image or not image.get_size():
            defaultLang = self.getDefaultLang(instance)
            if defaultLang:
                self.setLanguage(defaultLang)
                image = super(MultilanguageFieldMixin, self).getScale(instance, scale, **kwargs)
        self.resetLanguage()
        return image

    security.declareProtected(View, 'tag')
    def tag(self, instance, scale=None, height=None, width=None, alt=None,
            css_class=None, title=None, **kwargs):
        """Create a tag including scale
        """
        if self._v_lang:
            return super(ImageField, self).tag(instance, scale, height, width, alt, css_class, title, **kwargs)
        if not kwargs.has_key('lang'):
            kwargs['lang'] = self._getCurrentLanguage(instance)
        self.setLanguage(kwargs['lang'])
        value = self.get(instance, **kwargs)
        if not value or not value.get_size():
            defaultLang = self.getDefaultLang(instance)
            if defaultLang:
                self.setLanguage(defaultLang)
        tag = super(ImageField, self).tag(instance, scale, height, width, alt, css_class, title, **kwargs)
        self.resetLanguage()
        return tag
    
try:
    from urlparse import urlparse
    from plone.app.blob.field import ImageField as BaseBlobImageField, FileField as BaseBlobFileField
    from plone.app.blob.interfaces import IATBlobFile, IATBlobImage
    from plone.app.imaging.interfaces import IImageScaleHandler
    
    class MultilanguageBlobFieldMixin(Base):
        
        security = ClassSecurityInfo()
        
        security.declareProtected(View, 'index_html')
        def index_html(self, instance, REQUEST=None, RESPONSE=None, disposition='inline'):
            """ make it directly viewable when entering the objects URL """
            if REQUEST is None and hasattr(instance, 'REQUEST'):
                REQUEST = instance.REQUEST
            if REQUEST is not None and not 'lang' in REQUEST.keys():
                url = REQUEST['ACTUAL_URL']
                url += urlparse(url).query and '&' or '?'
                url += 'lang='+self._getCurrentLanguage(instance)
                return REQUEST.response.redirect(url)
            return super(MultilanguageBlobFieldMixin, self).index_html(instance, REQUEST, RESPONSE, disposition)
    
    class BlobFileField(MultilanguageFieldMixin, MultilanguageBlobFieldMixin, BaseBlobFileField):
        _properties = BaseBlobFileField._properties.copy()

        security = ClassSecurityInfo()

        security.declarePrivate('getUnwrapped')
        def getUnwrapped(self, instance, **kwargs):
            return super(BlobFileField, self).get(instance, **kwargs)
    
        def set(self, instance, value, **kwargs):
            super(BlobFileField, self).set(instance, value, **kwargs)
            if not kwargs.get('_initializing_', False) and (IATBlobFile.providedBy(instance) or isinstance(instance, ATFile)):
                self.fixAutoId(instance)
    
    class BlobImageField(MultilanguageFieldMixin, MultilanguageBlobFieldMixin, BaseBlobImageField):
        _properties = BaseBlobImageField._properties.copy()
    
        security = ClassSecurityInfo()

        security.declarePrivate('getUnwrapped')
        def getUnwrapped(self, instance, **kwargs):
            return super(BlobImageField, self).get(instance, **kwargs)
    
        def set(self, instance, value, **kwargs):
            super(BlobImageField, self).set(instance, value, **kwargs)
            if not kwargs.get('_initializing_', False) and (IATBlobImage.providedBy(instance) or isinstance(instance, ATImage)):
                self.fixAutoId(instance)
    
        security.declareProtected(View, 'tag')
        def tag(self, instance, scale=None, height=None, width=None, alt=None,
                css_class=None, title=None, **kwargs):
            """Create a tag including scale
            """
            if self._v_lang:
                return super(BlobImageField, self).tag(instance, scale, height, width, alt, css_class, title, **kwargs)
            if not kwargs.has_key('lang'):
                kwargs['lang'] = self._getCurrentLanguage(instance)
            self.setLanguage(kwargs['lang'])
            value = self.get(instance, **kwargs)
            if not value or not value.get_size():
                defaultLang = self.getDefaultLang(instance)
                if defaultLang:
                    self.setLanguage(defaultLang)
            tag = super(BlobImageField, self).tag(instance, scale, height, width, alt, css_class, title, **kwargs)
            self.resetLanguage()
            return tag
    
        security.declareProtected(View, 'getScale')
        def getScale(self, instance, scale=None, **kwargs):
            """ get scale by name or original """
            if self._v_lang:
                return super(BlobImageField, self).getScale(instance, scale, **kwargs)
            if not kwargs.has_key('lang'):
                kwargs['lang'] = self._getCurrentLanguage(instance)
            self.setLanguage(kwargs['lang'])
            image = super(BlobImageField, self).getScale(instance, scale, **kwargs)
            if not image or not image.get_size():
                defaultLang = self.getDefaultLang(instance)
                if defaultLang:
                    self.setLanguage(defaultLang)
                    image = super(BlobImageField, self).getScale(instance, scale, **kwargs)
            self.resetLanguage()
            return image

    registerField(BlobFileField,
                  title='Multilanguage Blob File',
                  description='Used for storing files in blobs')

    registerField(BlobImageField,
                  title='Multilanguage Blob Image',
                  description='Used for storing images in blobs')
except ImportError:
    pass
    
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
