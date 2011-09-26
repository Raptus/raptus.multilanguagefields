# Use those methods to patch traversing methods of content types
# using multilanguage image or file fields

from raptus.multilanguagefields import LOG
from raptus.multilanguagefields.interfaces import IMultilanguageField
from Products.Archetypes.BaseObject import BaseObject
def __bobo_traverse__(self, REQUEST, name):
    """Transparent access to multilanguage image scales for
       content types holding an multilanguage ImageField named
       'image'
       
       NO BLOBS
    """
    if name.startswith('image_') or name == 'image':
        field = self.getField('image')
        if not IMultilanguageField.providedBy(field):
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
                return REQUEST.RESPONSE.redirect(self.absolute_url()+'/'+fieldname+'___'+field._getCurrentLanguage(self)+'____'+str(scale))
            else:
                lang = field._getCurrentLanguage(self)
        lang_before = field._v_lang
        field.setLanguage(lang)
        image = None
        if scale:
            if scale in field.getAvailableSizes(self):
                image = field.getScale(self, scale=scale)
        else:
            image = field.getScale(self)
        field.setLanguage(lang_before)
        if image is not None and not isinstance(image, basestring):
            # image might be None or '' for empty images
            return image
    return BaseObject.__bobo_traverse__(self, REQUEST, name)

from Products.ATContentTypes.content.image import ATImage
ATImage.__bobo_traverse__ = __bobo_traverse__
LOG.info("Products.ATContentTypes.content.image.ATImage.__bobo_traverse__ patched")
