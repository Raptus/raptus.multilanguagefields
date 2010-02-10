from Products.Archetypes.atapi import *
from raptus.multilanguagefields import fields, widgets
from SimpleType import SimpleType

fields = ['StringField',
          'FileField', 'TextField', 'DateTimeField', 'LinesField',
          'IntegerField', 'FloatField', 'FixedPointField',
          'BooleanField', 'ImageField'
          ]

field_instances = []

for f in fields:
    field_instances.append(getattr(fields, f)(f.lower()))

schema = Schema(tuple(field_instances) + (
    LinesField('selectionlinesfield1',
               vocabulary='_get_selection_vocab',
               enforceVocabulary=1,
               widget=widgets.SelectionWidget(label='Selection'),
               ),
    LinesField('selectionlinesfield2',
               vocabulary='_get_selection_vocab',
               widget=widgets.SelectionWidget(label='Selection'),
               ),
    LinesField('selectionlinesfield3',
               vocabulary='_get_selection_vocab2',
               widget=widgets.MultiSelectionWidget(label='MultiSelection'),
               ),
    TextField('textarea_appendonly',
              widget=widgets.TextAreaWidget( label='TextArea',
                                     append_only=1,),
              ),
    TextField('textarea_appendonly_timestamp',
              widget=widgets.TextAreaWidget( label='TextArea',
                                     append_only=1,
                                     timestamp=1,),
              ),                                          
    TextField('textarea_maxlength',
              widget=widgets.TextAreaWidget( label='TextArea',
                                     maxlength=20,),
              ),                                          
    TextField('richtextfield',
              allowable_content_types=('text/plain',
                                       'text/structured',
                                       'text/restructured',
                                       'text/html',
                                       'application/msword'),
              widget=widgets.RichWidget(label='rich'),
              ),
    ReferenceField('referencefield',
                   relationship='complextype',
                   widget=widgets.ReferenceWidget(addable=1),
                   allowed_types=('ComplexType', ),
                   multiValued=1,
                  ),
    )) + ExtensibleMetadata.schema

class ComplexType(SimpleType):
    """A simple archetype"""
    schema = SimpleType.schema + schema
    archetype_name = meta_type = "ComplexType"
    portal_type = 'ComplexType'

    def _get_selection_vocab(self):
        return DisplayList((('Test','Test'), ))

    def _get_selection_vocab2(self):
        return DisplayList((('Test','Test'),('Test2','Test2'), ))


registerType(ComplexType, 'raptus.multilanguagefields')
