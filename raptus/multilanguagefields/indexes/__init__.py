from Products import PluginIndexes

import FieldIndex
import KeywordIndex
import DateIndex
import DateRangeIndex
import ZCTextIndex

from Products.CMFPlone.utils import safe_callable, safe_unicode
from Products.CMFPlone.CatalogTool import num_sort_regex, zero_fill

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

