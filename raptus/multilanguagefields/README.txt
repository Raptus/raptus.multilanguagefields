raptus.multilanguagefields
==========================

Installation
------------

Login as Manager and try to install product raptus.multilanguagefields
To verify that nothing's wrong is happening

Login as manager
    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> from Products.CMFCore.utils import getToolByName
    
We set a multilingual site ('en' and 'fr'), with default lang = 'fr'  
    >>> langtool = getToolByName(self.portal, 'portal_languages')
    >>> langtool.manage_setLanguageSettings(supportedLanguages = ('en', 'fr'), defaultLanguage='fr') 

Install raptus.multilanguagefields via quickinstaller
    >>> qi = getToolByName(self.portal, 'portal_quickinstaller')
    >>> _ = qi.installProducts(products=['raptus.multilanguagefields'])
    >>> qi.isProductInstalled('raptus.multilanguagefields')
    True


    
Test catalog
------------

See if indexes are available for catalog tool
    >>> from zope.interface.verify import verifyClass
    >>> from Products.PluginIndexes.interfaces import IPluggableIndex
    >>> from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> from OFS.ObjectManager import ObjectManager
    >>> all_indexes_type = [o['name'] for o in ObjectManager.all_meta_types(catalog, interfaces=(PluggableIndexInterface, IPluggableIndex))]
    >>> 'MultilanguageZCTextIndex' in all_indexes_type
    True

Try to add a multilingual field index in catalog
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> catalog.addIndex('getSomeField', 'MultilanguageFieldIndex')
    
Try to add a multilingual zctext index    
    >>> from ZPublisher.HTTPRequest import record
    >>> extra = record()
    >>> extra.lexicon_id = 'plone_lexicon'
    >>> extra.index_type = 'Okapi BM25 Rank' 
    >>> catalog.addIndex('getSomeText', 'MultilanguageZCTextIndex', extra)
