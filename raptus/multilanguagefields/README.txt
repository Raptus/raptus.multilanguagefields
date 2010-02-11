
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
    >>> langtool.manage_setLanguageSettings(supportedLanguages = ['en', 'fr'], defaultLanguage='fr')

Install raptus.multilanguagefields via quickinstaller
    >>> qi = getToolByName(self.portal, 'portal_quickinstaller')
    >>> _ = qi.installProducts(products=['raptus.multilanguagefields'])
    >>> qi.isProductInstalled('raptus.multilanguagefields')
    True

Install tests profile to install
some multilingual content types
    >>> portal_setup = getToolByName(self.portal, 'portal_setup')
    >>> _ = portal_setup.runAllImportStepsFromProfile('profile-raptus.multilanguagefields:sample_types')

Test samples types
------------------

Create a SimpleMultilingualType
    >>> self.portal.invokeFactory('SimpleMultilingualType', 'sample1')
    'sample1'
    >>> sample1 = self.portal.sample1

The field 'body' is multilingual
    >>> sample1.edit(body={'fr': '<p>FRENCH CONTENT</p>', 'en': '<p>ENGLISH CONTENT</p>'})

Test the getAll method on field which render all lang values in a dict
    >>> schema = sample1.Schema()
    >>> field = schema['body']
    >>> field.getAll(sample1)
    {'fr': '<p>FRENCH CONTENT</p>', 'en': '<p>ENGLISH CONTENT</p>'}

Test the accessor, which render only the current user language content
    >>> sample1.getBody()
    '<p>FRENCH CONTENT</p>'


Test catalog
------------

MultiLingual indexes must be available in catalog tool
    >>> from zope.interface.verify import verifyClass
    >>> from Products.PluginIndexes.interfaces import IPluggableIndex
    >>> from Products.PluginIndexes.common.PluggableIndex import PluggableIndexInterface
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> from OFS.ObjectManager import ObjectManager
    >>> all_indexes_type = [o['name'] for o in ObjectManager.all_meta_types(catalog, interfaces=(PluggableIndexInterface, IPluggableIndex))]
    >>> 'MultilanguageZCTextIndex' in all_indexes_type
    True

Add a multilingual field index in catalog
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> catalog.addIndex('getSomeField', 'MultilanguageFieldIndex')

Try to add a multilingual zctext index called getBody
    >>> from ZPublisher.HTTPRequest import record
    >>> extra = record()
    >>> extra.lexicon_id = 'plone_lexicon'
    >>> extra.index_type = 'Okapi BM25 Rank'
    >>> catalog.addIndex('getBody', 'MultilanguageZCTextIndex', extra)

Reindex the getBody index
    >>> catalog.reindexIndex('getBody', None)

Search in catalog using getBody multilingual index
    >>> crit = {}
    >>> crit['getBody'] = 'FRENCH'
    >>> results = catalog.searchResults(**crit)
    >>> len(results)
    1
    >>> results[0].getId
    'sample1'

Replace the current SearchableText index
by a multilingual index
and make a search on it, 'getBody' is searchable field,
so we must get a response
    >>> catalog.manage_delIndex(ids=['SearchableText'])
    >>> catalog.addIndex('SearchableText', 'MultilanguageZCTextIndex', extra)
    >>> catalog.reindexIndex('SearchableText', None)
    >>> crit = {}
    >>> crit['SearchableText'] = 'FRENCH'
    >>> results = catalog.searchResults(**crit)
    >>> len(results)
    1
    >>> results[0].getId
    'sample1'