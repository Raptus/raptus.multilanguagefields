from Products.validation.validators.RegexValidator import RegexValidator
from raptus.multilanguagefields.validators.base import MultilanguageValidatorMixin

class MultilanguageRegexValidator(MultilanguageValidatorMixin, RegexValidator):
    base_class = RegexValidator
