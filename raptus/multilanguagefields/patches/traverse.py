# Use those methods to patch traversing methods of content types
# using multilanguage image or file fields

from raptus.multilanguagefields import LOG

from Products.ATContentTypes.content.base import ATCTFileContent
def __bobo_traverse__(self, REQUEST, name):
    """Transparent access to multilanguage image scales for
       content types holding an multilanguage ImageField named
       'image'
       
       NO BLOBS
    """
    if name.startswith('image'):
        field = self.getField('image')
        image = None
        if name == 'image':
            image = field.getScale(self)
        elif '___' in name:
            name, lang, scalename = name.split('___')
            if scalename:
                scalename = scalename[1:]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename, lang=lang)
            else:
                image = field.getScale(self, lang=lang)
        else:
            scalename = name[len('image_'):]
            if scalename in field.getAvailableSizes(self):
                image = field.getScale(self, scale=scalename)
        if image is not None and not isinstance(image, basestring):
            # image might be None or '' for empty images
            return image
    return ATCTFileContent.__bobo_traverse__(self, REQUEST, name)

from Products.ATContentTypes.content.image import ATImage
ATImage.__bobo_traverse__ = __bobo_traverse__
LOG.info("Products.ATContentTypes.content.image.ATImage.__bobo_traverse__ patched")

try:
    """ Patch methods for content types having blob ImageFields or FileFields
    """
    from plone.app.imaging.interfaces import IImageScaleHandler

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

    from plone.app.blob.content import ATBlob
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
        return super(ATBlob, self).__bobo_traverse__(REQUEST, name)

    ATBlob.__bobo_traverse__ = __blob__bobo_traverse__
    LOG.info("plone.app.blob.content.ATBlob.__bobo_traverse__ patched")

    def publishTraverse(self, request, name):
        """ Patched traverse method for plone.app.imaging.traverse.ImageTraverser
        """
        lang = None
        lang_before, lang_set = None, 0
        image = None
        schema = self.context.Schema()
        fieldname, scale = name, None
        if '___' in name:
            fieldname, lang, scalename = name.split('___')
            if scalename:
                scale = scalename[1:]
        elif '_' in name:
            fieldname, scale = name.split('_', 1)
        field = schema.get(fieldname)
        if lang is not None:
            lang_before, lang_set = field._v_lang, 1
            field.setLanguage(lang)
        handler = IImageScaleHandler(field, None)
        if handler is not None:
            image = handler.getScale(self.context, scale)
        if lang_set:
            field.setLanguage(lang_before)
        if image is not None:
            return image
        return self.fallback(request, name)

    from plone.app.imaging.traverse import ImageTraverser
    ImageTraverser.publishTraverse = publishTraverse
    LOG.info("plone.app.imaging.traverse.ImageTraverser.publishTraverse patched")

except ImportError:
    pass