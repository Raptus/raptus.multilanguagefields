from ExtensionClass import Base
from AccessControl import ClassSecurityInfo

from Products.Archetypes import Widget as widgets
from Products.Archetypes.Registry import registerWidget

try:
    from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget as BaseReferenceBrowserWidget
except ImportError: # Plone 3.x
    from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget as BaseReferenceBrowserWidget

class MultilanguageWidgetMixin(Base):
    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """
        """
        values = {}
        kwargs = {}
        languages = field.getAvailableLanguages(instance)
        for lang in languages:
            field.setLanguage(lang['name'])
            result = super(MultilanguageWidgetMixin, self).process_form(instance, field, form, empty_marker, emptyReturnsMarker, validating)
            if result and isinstance(result, tuple):
                values[lang['name']] = result[0]
                kwargs[lang['name']] = result[1]
            elif result and not result is empty_marker:
                values[lang['name']] = result
            field.resetLanguage()
        return values, kwargs
    
class StringWidget(MultilanguageWidgetMixin, widgets.StringWidget):
    _properties = widgets.StringWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/string',
        })

class DecimalWidget(MultilanguageWidgetMixin, widgets.DecimalWidget):
    _properties = widgets.DecimalWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/decimal',
        })
    
class IntegerWidget(MultilanguageWidgetMixin, widgets.IntegerWidget):
    _properties = widgets.IntegerWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/integer',
        })
    
class ReferenceWidget(MultilanguageWidgetMixin, widgets.ReferenceWidget):
    _properties = widgets.ReferenceWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/reference',
        })
    
class TextAreaWidget(MultilanguageWidgetMixin, widgets.TextAreaWidget):
    _properties = widgets.TextAreaWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/textarea',
        })
    
class LinesWidget(MultilanguageWidgetMixin, widgets.LinesWidget):
    _properties = widgets.LinesWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/lines',
        })
    
class BooleanWidget(MultilanguageWidgetMixin, widgets.BooleanWidget):
    _properties = widgets.BooleanWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/boolean',
        })
    
class CalendarWidget(MultilanguageWidgetMixin, widgets.CalendarWidget):
    _properties = widgets.CalendarWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/calendar',
        })
    
class SelectionWidget(MultilanguageWidgetMixin, widgets.SelectionWidget):
    _properties = widgets.SelectionWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/selection',
        })
    
class MultiSelectionWidget(MultilanguageWidgetMixin, widgets.MultiSelectionWidget):
    _properties = widgets.MultiSelectionWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/multiselection',
        })
    
class KeywordWidget(MultilanguageWidgetMixin, widgets.KeywordWidget):
    _properties = widgets.KeywordWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/keyword',
        })
    
class FileWidget(MultilanguageWidgetMixin, widgets.FileWidget):
    _properties = widgets.FileWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/file',
        })
    
class RichWidget(MultilanguageWidgetMixin, widgets.RichWidget):
    _properties = widgets.RichWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/rich',
        })
    
class ImageWidget(MultilanguageWidgetMixin, widgets.ImageWidget):
    _properties = widgets.ImageWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/image',
        })

class ReferenceBrowserWidget(MultilanguageWidgetMixin, BaseReferenceBrowserWidget):
    _properties = BaseReferenceBrowserWidget._properties.copy()
    _properties.update({
        'macro' : 'multilanguage_widgets/referencebrowser',
        })

registerWidget(StringWidget,
               title='Multilanguage String',
               description=('Renders a HTML text input box which '
                            'accepts a single line of text'),
               used_for=('raptus.multilanguagefields.fields.StringField',)
               )

registerWidget(DecimalWidget,
               title='Multilanguage Decimal',
               description=('Renders a HTML text input box which '
                            'accepts a fixed point value'),
               used_for=('raptus.multilanguagefields.fields.FixedPointField',)
               )

registerWidget(IntegerWidget,
               title='Multilanguage Integer',
               description=('Renders a HTML text input box which '
                            'accepts a integer value'),
               used_for=('raptus.multilanguagefields.fields.IntegerField',)
               )

registerWidget(ReferenceWidget,
               title='Multilanguage Reference',
               description=('Renders a HTML text input box which '
                            'accepts a reference value'),
               used_for=('raptus.multilanguagefields.fields.ReferenceField',)
               )

registerWidget(TextAreaWidget,
               title='Multilanguage Text Area',
               description=('Renders a HTML Text Area for typing '
                            'a few lines of text'),
               used_for=('raptus.multilanguagefields.fields.StringField',
                         'raptus.multilanguagefields.fields.TextField')
               )

registerWidget(LinesWidget,
               title='Multilanguage Lines',
               description=('Renders a HTML textarea for a list '
                            'of values, one per line'),
               used_for=('raptus.multilanguagefields.fields.LinesField',)
               )

registerWidget(BooleanWidget,
               title='Multilanguage Boolean',
               description='Renders a HTML checkbox',
               used_for=('raptus.multilanguagefields.fields.BooleanField',)
               )

registerWidget(CalendarWidget,
               title='Multilanguage Calendar',
               description=('Renders a HTML input box with a helper '
                            'popup box for choosing dates'),
               used_for=('raptus.multilanguagefields.fields.DateTimeField',)
               )

registerWidget(SelectionWidget,
               title='Multilanguage Selection',
               description=('Renders a HTML selection widget, which '
                            'can be represented as a dropdown, or as '
                            'a group of radio buttons'),
               used_for=('raptus.multilanguagefields.fields.StringField',
                         'raptus.multilanguagefields.fields.LinesField',)
               )

registerWidget(MultiSelectionWidget,
               title='Multilanguage Multi Selection',
               description=('Renders a HTML selection widget, where '
                            'you can be choose more than one value'),
               used_for=('raptus.multilanguagefields.fields.LinesField',)
               )

registerWidget(KeywordWidget,
               title='Multilanguage Keyword',
               description='Renders a HTML widget for choosing keywords',
               used_for=('raptus.multilanguagefields.fields.LinesField',)
               )

registerWidget(RichWidget,
               title='Multilanguage Rich Widget',
               description=('Renders a HTML widget that allows you to '
                            'type some content, choose formatting '
                            'and/or upload a file'),
               used_for=('raptus.multilanguagefields.fields.TextField',)
               )

registerWidget(FileWidget,
               title='Multilanguage File',
               description='Renders a HTML widget upload a file',
               used_for=('raptus.multilanguagefields.fields.FileField',)
               )

registerWidget(ImageWidget,
               title='Multilanguage Image',
               description=('Renders a HTML widget for '
                            'uploading/displaying an image'),
               used_for=('raptus.multilanguagefields.fields.ImageField',)
               )

registerWidget(ReferenceBrowserWidget,
               title='Multilanguage Reference Browser',
               description=('Reference widget that allows you to browse or search the portal for objects to refer to.'),
               used_for=('raptus.multilanguagefields.fields.ReferenceField',)
               )
