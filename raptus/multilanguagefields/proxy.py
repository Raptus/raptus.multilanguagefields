from AccessControl import ClassSecurityInfo
from persistent import Persistent
from persistent.dict import PersistentDict
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View
from zope.app.component.hooks import getSite
from raptus.multilanguagefields.interfaces import IMultilanguageAware

class MultilanguageAware(Persistent):
    """a multilanguage aware persistent proxy"""
    implements(IMultilanguageAware)
    security = ClassSecurityInfo()
    def __init__(self, values):
        self._values = PersistentDict(values)
        Persistent.__init__(self)
    security.declareProtected(View, "__call__")
    def __call__(self):
        """
        """
        return self.data
    def _getCurrentLanguage(self):
        return getToolByName(getSite(), 'portal_languages').getPreferredLanguage()
    def getLang(self, lang):
        if self._values.has_key(lang):
            return self._values[lang]
        return ''
    @property
    def data(self):
        return self.getLang(self._getCurrentLanguage())
    def __getattr__(self, attr):
        return getattr(self.data, attr)
    def __unicode__(self):
        return unicode(self.data)
    def __str__(self):
        return str(self.data)
    def getclass(self):
        return self.data.getclass()
    __class__ = property(getclass)
