# Use those methods to patch traversing methods of content types
# using multilanguage image or file fields

from raptus.multilanguagefields import LOG
from Products.Archetypes.BaseObject import BaseObject
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
    return BaseObject.__bobo_traverse__(self, REQUEST, name)

from Products.ATContentTypes.content.image import ATImage
ATImage.__bobo_traverse__ = __bobo_traverse__
LOG.info("Products.ATContentTypes.content.image.ATImage.__bobo_traverse__ patched")
