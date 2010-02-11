from Products.Archetypes.atapi import *
from raptus.multilanguagefields import fields, widgets
from SimpleType import SimpleMultilingualType
from raptus.multilanguagefields.config import *

schema = Schema((
    fields.LinesField('selectionlinesfield1',
               vocabulary='_get_selection_vocab',
               enforceVocabulary=1,
               widget=widgets.SelectionWidget(label='Selection'),
               ),
    fields.LinesField('selectionlinesfield2',
               vocabulary='_get_selection_vocab',
               widget=widgets.SelectionWidget(label='Selection'),
               ),
    fields.LinesField('selectionlinesfield3',
               vocabulary='_get_selection_vocab2',
               widget=widgets.MultiSelectionWidget(label='MultiSelection'),
               ),
    fields.TextField('textarea_appendonly',
              widget=widgets.TextAreaWidget( label='TextArea',
                                     append_only=1,),
              ),
    fields.TextField('textarea_appendonly_timestamp',
              widget=widgets.TextAreaWidget( label='TextArea',
                                     append_only=1,
                                     timestamp=1,),
              ),                                          
    fields.TextField('textarea_maxlength',
              widget=widgets.TextAreaWidget( label='TextArea',
                                     maxlength=20,),
              ),                                          
    fields.TextField('richtextfield',
              allowable_content_types=('text/plain',
                                       'text/structured',
                                       'text/restructured',
                                       'text/html',
                                       'application/msword'),
              widget=widgets.RichWidget(label='rich'),
              ),
    fields.ReferenceField('referencefield',
                   relationship='complextype',
                   widget=widgets.ReferenceWidget(addable=1),
                   allowed_types=('ComplexType', ),
                   multiValued=1,
                  ),
    )) + ExtensibleMetadata.schema

class ComplexMultilingualType(SimpleMultilingualType):
    """A simple archetype"""
    schema = SimpleMultilingualType.schema + schema

    def _get_selection_vocab(self):
        return DisplayList((('Test','Test'), ))

    def _get_selection_vocab2(self):
        return DisplayList((('Test','Test'),('Test2','Test2'), ))


registerType(ComplexMultilingualType, PROJECT_NAME)
