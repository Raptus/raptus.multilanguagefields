from zope.interface import Interface

class IMultilanguageField(Interface):
    """ marker interface for multilanguage fields
    """
    
class IMultilanguageAware(Interface):
    """ marker interface for multilanguage aware strings
    """