# Patches for plone.app.blob (if available)

from raptus.multilanguagefields import LOG
try:
    from plone.app.imaging.interfaces import IImageScaleHandler
    from plone.app.blob.interfaces import IATBlobImage
    from plone.app.blob.content import ATBlob
    from Products.Archetypes.BaseObject import BaseObject
    from Products.ATContentTypes.content.file import ATFile
    
    from raptus.multilanguagefields.patches.archetypes import _redirect
    from raptus.multilanguagefields.interfaces import IMultilanguageField
    
    ATBlob.__old__index_html = ATBlob.index_html
    def __new__index_html(self, REQUEST=None, RESPONSE=None):
        """ download the file inline or as an attachment """
        field = self.getPrimaryField()
        if IATBlobImage.providedBy(self) or field.getContentType(self) in ATFile.inlineMimetypes:
            return _redirect(self, REQUEST, RESPONSE)
        return self.__old__index_html(REQUEST, RESPONSE)
    ATBlob.index_html = __new__index_html
    LOG.info("plone.app.blob.content.ATBlob.index_html patched")

    def setImage(self, value, **kw):
        if kw.has_key('schema'):
            schema = kw['schema']
        else:
            schema = self.Schema()
            kw['schema'] = schema
        return schema['image'].set(self, value, **kw)

    from plone.app.blob.mixins import ImageMixin
    ImageMixin.setImage = setImage
    LOG.info("plone.app.blob.mixins.ImageMixin.setImage patched")

    def setFile(self, value, **kw):
        if kw.has_key('schema'):
            schema = kw['schema']
        else:
            schema = self.Schema()
            kw['schema'] = schema
        return schema['file'].set(self, value, **kw)

    ATBlob.setFile = setFile
    LOG.info("plone.app.blob.content.ATBlob.setFile patched")

    def __blob__bobo_traverse__(self, REQUEST, name):
        """ helper to access multilanguage image scales the old way during
            `unrestrictedTraverse` calls 
            
            the method to be patched is '__bobo_traverse__'
        """
        field = self.getField(name.split('_')[0])
        if not IMultilanguageField.providedBy(field) or not isinstance(REQUEST, dict):
            return BaseObject.__bobo_traverse__(self, REQUEST, name)
        fieldname, scale = name, None
        if '___' in name:
            fieldname, lang, scalename = name.split('___')
            if scalename:
                scale = scalename[1:]
        else:
            if '_' in name:
                fieldname, scale = name.split('_', 1)
            if REQUEST.get('HTTP_USER_AGENT', False):
                return REQUEST.RESPONSE.redirect(self.absolute_url+'/'+fieldname+'___'+field._getCurrentLanguage(self)+'____'+str(scale))
            else:
                lang = field._getCurrentLanguage(self)
        lang_before = field._v_lang
        field.setLanguage(lang)
        handler = IImageScaleHandler(field, None)
        image = None
        if handler is not None:
            image = handler.getScale(self, scale)
        field.setLanguage(lang_before)
        if image is not None:
            return image
        return BaseObject.__bobo_traverse__(self, REQUEST, name)

    ATBlob.__bobo_traverse__ = __blob__bobo_traverse__
    LOG.info("plone.app.blob.content.ATBlob.__bobo_traverse__ patched")
except ImportError:
    pass
