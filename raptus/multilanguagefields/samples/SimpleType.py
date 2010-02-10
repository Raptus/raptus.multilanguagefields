from Products.Archetypes.atapi import *
from raptus.multilanguagefields import fields, widgets

# a simple schema with multilanguage fields
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
    fields.StringField('ptype',
              default_method='Type'
              ),
    ))


class SimpleType(BaseContent):
    """A simple archetype"""
    schema = schema

registerType(SimpleType, 'raptus.multilanguagefields')
