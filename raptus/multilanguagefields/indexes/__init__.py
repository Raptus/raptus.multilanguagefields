from Products import PluginIndexes

import FieldIndex
import KeywordIndex
import DateIndex
import DateRangeIndex
import ZCTextIndex

from Products.ZCTextIndex import getIndexTypes

from Products.CMFPlone.utils import safe_callable, safe_unicode
from Products.CMFPlone.CatalogTool import registerIndexableAttribute, num_sort_regex, zero_fill

_wwwPath = '%s/www' % PluginIndexes.__path__[0]

_indexes =  ('KeywordIndex',
             'FieldIndex',
             'DateIndex',
             'DateRangeIndex',
            )

class multilanguage_sortable_title:
    def __init__(self, obj):
        self.obj = obj
    def __call__(self, **kwargs):
        title = getattr(self.obj, 'Title', None)
        if title is not None:
            if safe_callable(title):
                if kwargs.has_key('lang'):
                    try: title = title(lang=kwargs['lang'])
                    except: title = title()
                else:
                    title = title()
            if isinstance(title, basestring):
                sortabletitle = title.lower().strip()
                # Replace numbers with zero filled numbers
                sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
                # Truncate to prevent bloat
                sortabletitle = safe_unicode(sortabletitle)[:30].encode('utf-8')
                return sortabletitle
        return ''

class multilanguage_sortable_title_indexer(object):
    def __init__(self, obj, catalog):
        self.obj = obj
    def __call__(self):
        return multilanguage_sortable_title(self.obj)

def initialize(context):

    for idx in _indexes:

        s = "context.registerClass( \
            %s.Multilanguage%s,\
            permission='Add Pluggable Index', \
            constructors=(manage_addMultilanguage%sForm,\
                          manage_addMultilanguage%s),\
            icon='%s/index.gif',\
            visibility=None\
         )" % (idx,idx,idx,idx,_wwwPath)

        exec(s)

    context.registerClass(
        ZCTextIndex.MultilanguageZCTextIndex,
        permission = 'Add Pluggable Index',
        constructors = (ZCTextIndex.manage_addMultilanguageZCTextIndexForm,
                        ZCTextIndex.manage_addMultilanguageZCTextIndex,
                        getIndexTypes),
        icon='%s/index.gif' % _wwwPath,
        visibility=None
    )


for idx in _indexes:

    exec("manage_addMultilanguage%sForm = %s.manage_addMultilanguage%sForm" % (idx,idx,idx))
    exec("manage_addMultilanguage%s     = %s.manage_addMultilanguage%s" % (idx,idx,idx))
