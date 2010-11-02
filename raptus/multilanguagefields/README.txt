
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

'title' and 'body' are multilingual fields
    >>> sample1.edit(title={'fr': 'FRENCH TITLE', 'en': 'ENGLISH TITLE'},
    ...              body={'fr': '<p>FRENCH CONTENT</p>', 'en': '<p>ENGLISH CONTENT</p>'})

Test the getAll method on body field which render all lang values in a dict
    >>> schema = sample1.Schema()
    >>> field = schema['body']
    >>> field.getAll(sample1)
    {'fr': '<p>FRENCH CONTENT</p>', 'en': '<p>ENGLISH CONTENT</p>'}

Test the accessors, which render only the current user language content
    >>> sample1.getBody()
    '<p>FRENCH CONTENT</p>'
    >>> sample1.Title()
    'FRENCH TITLE'


Test catalog
------------

MultiLingual indexes must be available in catalog tool
    >>> from zope.interface.verify import verifyClass
    >>> from Products.PluginIndexes.interfaces import IPluggableIndex
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> from OFS.ObjectManager import ObjectManager
    >>> all_indexes_type = [o['name'] for o in ObjectManager.all_meta_types(catalog, interfaces=(IPluggableIndex,))]
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

Test some Archetypes standard methods on schemas
------------------------------------------------

Copy a Schema
    >>> from raptus.multilanguagefields.samples.SimpleType import schema as simpleSchema
    >>> newSchema = simpleSchema.copy()
    >>> 'body' in newSchema.keys()
    True

Create a new class using this schema
    >>> from raptus.multilanguagefields.samples.SimpleType import SimpleMultilingualType
    >>> from Products.Archetypes.atapi import *
    >>> class NewType(SimpleMultilingualType) :
    ...     schema = newSchema
    >>> registerType(NewType, 'raptus.multilanguagefields')
    >>> toto = NewType('toto')


Test Fields and Widgets at low level
------------------------------------

    >>> from raptus.multilanguagefields import fields, widgets
    >>> MultiLangRichWidget = widgets.RichWidget
    >>> MultiLangTextField = fields.TextField

We got this error when trying to serialize objects with multilanguage
widgets inside.
"ExtensionClass.Base.__new__(RichWidget) is not safe, use object.__new__()"
This is fixed when MultilanguageWidgetMixin inherit from ExtensionClass.Base
    >>> from ExtensionClass import Base
    >>> Base.__new__(MultiLangRichWidget)
    <raptus.multilanguagefields.widgets.RichWidget object at ...

Same error with fields :
"ExtensionClass.Base.__new__(TextField) is not safe, use object.__new__()"
This is fixed when MultilanguageFieldMixin inherit from ExtensionClass.Base
    >>> from Products.Archetypes.Layer import DefaultLayerContainer
    >>> NewFieldObject = DefaultLayerContainer.__new__(MultiLangTextField)
    >>> NewFieldObject.__name__ = 'test'
    >>> NewFieldObject.type = 'MultiLangTextField'
    >>> NewFieldObject.mode = 'rw'
    >>> NewFieldObject
    <Field test(MultiLangTextField:rw)>    


Test standard rename method used in plone rename forms
------------------------------------------------------
Plone rename forms pass string as argument for title to rename the objects
We do not want to overload rename forms, but just 
get the good title in current language when using these
forms when title is a multilanguage field

Try to change sample1 title using the method used by folder_rename script
(putils.renameObjectsByPaths)
We must get a new french title (current language)
    >>> putils = self.portal.plone_utils
    >>> path1 = '/'.join(sample1.getPhysicalPath())
    >>> newTitleFr = 'NEW FRENCH TITLE'
    >>> putils.renameObjectsByPaths(paths=[path1],new_ids=['sample1'],new_titles=[newTitleFr])
    ({'/plone/sample1': ('sample1', 'NEW FRENCH TITLE')}, {})
    >>> sample1.Title()
    'NEW FRENCH TITLE'