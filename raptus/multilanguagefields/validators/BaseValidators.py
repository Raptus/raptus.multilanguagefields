from RegexValidator import MultilanguageRegexValidator
from RangeValidator import MultilanguageRangeValidator
from Products.validation.validators.BaseValidators import protocols, EMAIL_RE

baseValidators = [
    MultilanguageRangeValidator('inNumericRangeMultilanguage', title='', description=''),
    MultilanguageRegexValidator('isDecimalMultilanguage',
                   r'^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$',
                   title='', description='',
                   errmsg='is not a decimal number.'),
    MultilanguageRegexValidator('isIntMultilanguage', r'^([+-])?\d+$', title='', description='',
                   errmsg='is not an integer.'),
    MultilanguageRegexValidator('isPrintableMultilanguage', r'[a-zA-Z0-9\s]+$', title='', description='',
                   errmsg='contains unprintable characters'),
    MultilanguageRegexValidator('isSSNMultilanguage', r'^\d{9}$', title='', description='',
                   errmsg='is not a well formed SSN.'),
    MultilanguageRegexValidator('isUSPhoneNumberMultilanguage', r'^\d{10}$', ignore='[\(\)\-\s]',
                   title='', description='',
                   errmsg='is not a valid us phone number.'),
    MultilanguageRegexValidator('isInternationalPhoneNumberMultilanguage', r'^\d+$', ignore='[\(\)\-\s\+]',
                   title='', description='',
                   errmsg='is not a valid international phone number.'),
    MultilanguageRegexValidator('isZipCodeMultilanguage', r'^(\d{5}|\d{9})$',
                   title='', description='',
                   errmsg='is not a valid zip code.'),
    MultilanguageRegexValidator('isURLMultilanguage', r'(%s)s?://[^\s\r\n]+' % '|'.join(protocols),
                   title='', description='',
                   errmsg='is not a valid url.'),
    MultilanguageRegexValidator('isEmailMultilanguage', '^'+EMAIL_RE,
                   title='', description='',
                   errmsg='is not a valid email address.'),
    MultilanguageRegexValidator('isMailtoMultilanguage', '^mailto:'+EMAIL_RE,
                   title='', description='',
                   errmsg='is not a valid email address.'),
    MultilanguageRegexValidator('isUnixLikeNameMultilanguage', r"^[A-Za-z][\w\d\-\_]{0,7}$",
                   title="", description="",
                   errmsg="this name is not a valid identifier"),
    ]

__all__ = ('baseValidators', )
