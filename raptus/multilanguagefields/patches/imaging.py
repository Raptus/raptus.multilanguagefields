# Patches for plone.app.imaging (if available)

from raptus.multilanguagefields import LOG
try:
    from plone.app.imaging.interfaces import IImageScaleHandler
    from zope.app.component.hooks import getSite
    from raptus.multilanguagefields.interfaces import IMultilanguageField

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

    def scale(self, fieldname=None, scale=None, **parameters):
        field = self.context.getField(fieldname)
        if IMultilanguageField.providedBy(field):
            fieldname = '%s___%s___' % (fieldname, field._v_lang or field._getCurrentLanguage(getSite()))
        return self.__old_scale(fieldname, scale, **parameters)
    from plone.app.imaging.scaling import ImageScaling
    ImageScaling.__old_scale = ImageScaling.scale
    ImageScaling.scale = scale
    LOG.info("plone.app.imaging.scaling.ImageScaling.scale patched")

except ImportError:
    pass
