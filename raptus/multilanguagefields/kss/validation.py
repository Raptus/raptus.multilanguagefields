from Acquisition import aq_inner

from zope.interface import implements
from zope.deprecation import deprecated
from archetypes.kss.validation import SKIP_KSSVALIDATION_FIELDTYPES, \
                                      missing_uid_deprecation

from plone.app.kss.plonekssview import PloneKSSView
from plone.app.kss.interfaces import IPloneKSSView

from raptus.multilanguagefields.interfaces import IMultilanguageField

class ValidationView(PloneKSSView):

    implements(IPloneKSSView)
    
    def kssValidateMultilanguageField(self, fieldname, uid=None):
        '''Validate a given multilanguage field
        '''
        # validate the field, actually

        if uid is not None:
            rc = getToolByName(aq_inner(self.context), 'reference_catalog')
            instance = rc.lookupObject(uid)
        else:
            deprecated(ValidationView, missing_uid_deprecation)
            instance = aq_inner(self.context)

        field = instance.getField(fieldname)
        if field.type in SKIP_KSSVALIDATION_FIELDTYPES or \
           not IMultilanguageField.providedBy(field):
            return self.render()
        value = dict([(key[key.find('___')+3:-3], value) for key, value in self.request.form.items() if key.startswith(fieldname)])
        error = field.validate(value, instance, {}, REQUEST=self.request)
        # XXX
        if isinstance(error, str):
            error = error.decode('utf', 'replace')
        # replace the error on the page
        self.getCommandSet('atvalidation').issueFieldError(fieldname, error)
        return self.render()
