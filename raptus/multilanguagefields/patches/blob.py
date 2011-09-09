# Patches for plone.app.blob (if available)

from raptus.multilanguagefields import LOG
try:
    from plone.app.imaging.interfaces import IImageScaleHandler
    from plone.app.blob.interfaces import IATBlobImage
    from plone.app.blob.content import ATBlob
    from Products.Archetypes.BaseObject import BaseObject
    from Products.ATContentTypes.content.file import ATFile
    
    from raptus.multilanguagefields.patches.archetypes import _redirect
    
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
        if isinstance(REQUEST, dict):
            lang = None
            lang_before, lang_set = None, 0
            image = None
            fieldname, scale = name, None
            if '___' in name:
                fieldname, lang, scalename = name.split('___')
                if scalename:
                    scale = scalename[1:]
            elif '_' in name:
                fieldname, scale = name.split('_', 1)
            field = self.getField(fieldname)
            if lang is not None:
                lang_before, lang_set = field._v_lang, 1
                field.setLanguage(lang)
            handler = IImageScaleHandler(field, None)
            if handler is not None:
                image = handler.getScale(self, scale)
            if lang_set:
                field.setLanguage(lang_before)
            if image is not None:
                return image
        return BaseObject.__bobo_traverse__(self, REQUEST, name)

    ATBlob.__bobo_traverse__ = __blob__bobo_traverse__
    LOG.info("plone.app.blob.content.ATBlob.__bobo_traverse__ patched")
except ImportError:
    pass
