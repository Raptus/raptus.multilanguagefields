from RegexValidator import MultilanguageRegexValidator
from RangeValidator import MultilanguageRangeValidator

validators = []

from BaseValidators import baseValidators
validators.extend(baseValidators)

from SupplValidators import validatorList
validators.extend(validatorList)

def initialize(service):
    for validator in validators:
        service.register(validator)
