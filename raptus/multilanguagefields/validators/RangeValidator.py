from Products.validation.validators.RangeValidator import RangeValidator
from raptus.multilanguagefields.validators.base import MultilanguageValidatorMixin

class MultilanguageRangeValidator(MultilanguageValidatorMixin, RangeValidator):
    base_class = RangeValidator
