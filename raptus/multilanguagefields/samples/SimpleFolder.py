from Products.Archetypes.atapi import *
from raptus.multilanguagefields import fields, widgets
from raptus.multilanguagefields.config import *

# a simple folder schema with a multilanguage field inside
schema = BaseSchema + Schema((
    fields.TextField('body',
              required=1,
              searchable=1,
              default_output_type='text/html',
              allowable_content_types=('text/plain',
                                       'text/restructured',
                                       'text/html',
                                       'application/msword'),
              widget  = widgets.RichWidget(description="""Enter or upload text for the Body of the document"""),
              ),
    ))

class SimpleMultilingualFolder(BaseFolder):
    """A simple folderish archetype"""
    schema = schema

    def manage_afterMKCOL(self, id, result, REQUEST=None, RESPONSE=None):
        """For unit tests
        """
        self.called_afterMKCOL_hook = True

    def manage_afterPUT(self, data, marshall_data, file, context, mimetype,
                        filename, REQUEST, RESPONSE):
        """For unit tests
        """
        self.called_afterPUT_hook = True

registerType(SimpleMultilingualFolder, PROJECT_NAME)
