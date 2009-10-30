import urllib
import re

from Acquisition import aq_inner, aq_parent
from htmlentitydefs import name2codepoint as n2cp

from zope.i18n import translate

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from raptus.multilanguagefields import multilanguagefieldsMessageFactory as _

def substitute_entity(match):
    ent = match.group(3)
    if match.group(2) == "#":
        return unichr(int(ent))
    else:
        cp = n2cp.get(ent)

        if cp:
            return unichr(cp)
        else:
            return match.group()

entity_re = re.compile("(&|\\\\u0026)(#?)(\d{1,5}|\w{1,8});")
def decode_htmlentities(string):
    return entity_re.subn(substitute_entity, string)[0]

class Translation(BrowserView):
    
    def getRawTranslation(self, string, source, dest):
        url = 'http://ajax.googleapis.com/ajax/services/language/translate'
        params = {'v': '1.0',
                  'q': string,
                  'langpair': '%s|%s' % (source[:2], dest[:2])}
        return urllib.urlopen(url, urllib.urlencode(params)).read()
    
    def getTranslation(self, string, source, dest, id=0):
        result = self.getRawTranslation(string, source, dest);
        return """{
            id: %s,
            source: '%s',
            dest: '%s',
            message: '%s',
            result: %s
            }""" % (id, 
                    source, 
                    dest, 
                    translate(_('message_translate', default=u'Are you sure you want to replace the current value for the language "{language}" by the generated translation "{translation}"?'), context=self.request), 
                    decode_htmlentities(result.decode('utf-8')))

    def getTranslator(self, fieldName, widgetType, lang, id):
        context = aq_inner(self.context)
        while not getattr(context, 'Schema', None):
            context = aq_parent(context)
        field = context.Schema().getField(fieldName)
        languages = [l for l in field.getAvailableLanguages(context) if not l['name'] == lang]
        return """{
            id: %s,
            data: '%s'
            }""" % (id, context.translator(fieldName=fieldName, widgetType=widgetType, languages=languages, lang=lang, id=id).replace("\n", ""))
        