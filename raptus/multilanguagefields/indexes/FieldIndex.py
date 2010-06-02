from App.special_dtml import DTMLFile

from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex, manage_addFieldIndexForm

from raptus.multilanguagefields.indexes.UnIndex import MultilanguageUnIndex

class MultilanguageFieldIndex(MultilanguageUnIndex, FieldIndex):
    """Index for simple fields.
    """

    meta_type="MultilanguageFieldIndex"

    manage_options=FieldIndex.manage_options
    query_options=FieldIndex.query_options
    manage=FieldIndex.manage
    manage_browse=FieldIndex.manage_browse

manage_addMultilanguageFieldIndexForm = DTMLFile('dtml/addFieldIndex', globals())

def manage_addMultilanguageFieldIndex(self, id, extra=None,
                REQUEST=None, RESPONSE=None, URL3=None):
    """Add a field index"""
    return self.manage_addIndex(id, 'MultilanguageFieldIndex', extra=extra, \
             REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
