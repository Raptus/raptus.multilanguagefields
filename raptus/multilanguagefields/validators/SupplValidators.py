from Products.validation.validators.SupplValidators import MaxSizeValidator, DateValidator
from raptus.multilanguagefields.validators.base import MultilanguageValidatorMixin

class MultilanguageMaxSizeValidator(MultilanguageValidatorMixin, MaxSizeValidator):
    base_class = MaxSizeValidator

class MultilanguageDateValidator(MultilanguageValidatorMixin, DateValidator):
    base_class = DateValidator

validatorList = [
    MultilanguageMaxSizeValidator('isMaxSizeMultilanguage', title='', description=''),
    MultilanguageDateValidator('isValidDateMultilanguage', title='', description=''),
    ]

__all__ = ('validatorList', )
