import urllib
import urllib2
import re
try:
    import json
except ImportError: # Python <= 2.5
    import simplejson as json

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
        url = 'http://mymemory.translated.net/api/get'
        params = urllib.urlencode({'q': string,
                                   'langpair': '%s|%s' % (source[:2], dest[:2])})
        header = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'}
        
        req  = urllib2.Request(u'%s?%s' % (url, params), None, header)
        self.request.response.setHeader("Content-type","application/json")
        return urllib2.urlopen(req).read()

    def getTranslation(self, string, source, dest, id=0):
        result = json.loads(self.getRawTranslation(string, source, dest).decode('utf-8'));
        result[u'responseData'][u'translatedText'] = decode_htmlentities(result[u'responseData'][u'translatedText'])
        self.request.response.setHeader("Content-type","application/json")
        return json.dumps({
            'id': id,
            'source': source,
            'dest': dest,
            'message': translate(_('message_translate', default=u'Are you sure you want to replace the current value for the language "{language}" by the generated translation "{translation}"?'), context=self.request),
            'result': result})

    def getTranslator(self, fieldName, widgetType, lang, id):
        context = aq_inner(self.context)
        while not getattr(context, 'Schema', None):
            context = aq_parent(context)
        field = context.Schema().getField(fieldName)
        if field is None:
            return
        languages = [l for l in field.getAvailableLanguages(context) if not l['name'] == lang]
        self.request.response.setHeader("Content-type","application/json")
        return json.dumps({
            'id': id,
            'data': context.translator(fieldName=fieldName, widgetType=widgetType, languages=languages, lang=lang, id=id).replace("\n", "")})
