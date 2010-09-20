import logging
from Products.CMFPlone import utils
from Products.CMFPlone.browser.ploneview import Plone
#from raptus.multilanguagefields import config    
import config
LOG = logging.getLogger(config.PROJECT_NAME)

from zope.i18nmessageid import MessageFactory
multilanguagefieldsMessageFactory = MessageFactory(config.I18N_DOMAIN)

from indexes import FieldIndex, \
                    KeywordIndex, \
                    DateIndex, \
                    DateRangeIndex, \
                    ZCTextIndex

from Products.ZCTextIndex import getIndexTypes

# initialize validators
from raptus.multilanguagefields.validators import initialize
from Products.validation.config import validation
initialize(validation)

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import Field

import criteria
from raptus.multilanguagefields.interfaces import IMultilanguageField

# monkey patches
import patches 

_indexes =  ('KeywordIndex',
             'FieldIndex',
             'DateIndex',
             'DateRangeIndex',
            )

def initialize(context):

    for idx in _indexes:

        s = "context.registerClass( \
            %s.Multilanguage%s,\
            permission='Add Pluggable Index', \
            constructors=(manage_addMultilanguage%sForm,\
                          manage_addMultilanguage%s),\
            icon='www/index.gif',\
            visibility=None\
         )" % (idx,idx,idx,idx)

        exec(s)

    context.registerClass(
        ZCTextIndex.MultilanguageZCTextIndex,
        permission = 'Add Pluggable Index',
        constructors = (ZCTextIndex.manage_addMultilanguageZCTextIndexForm,
                        ZCTextIndex.manage_addMultilanguageZCTextIndex,
                        getIndexTypes),
        icon='www/index.gif',
        visibility=None
    )

    if config.REGISTER_DEMO_TYPES:
        
        # CMF imports
        from Products.CMFCore.utils import ContentInit
        # Archetypes imports
        from Products.Archetypes.public import process_types, listTypes
        import samples
        from permissions import permissions
        from permissions import wireAddPermissions
        # Initialize permissions
        wireAddPermissions()
        from Products.GenericSetup import EXTENSION, profile_registry
        LOG.info('registering a GS test profile to install demo types') 
        profile_registry.registerProfile('sample_types',
            'MultilanguageFields Sample Types',
            '',
            'profiles/tests',
            'raptus.multilanguagefields',
            EXTENSION)   
        
        LOG.info('demo types initialization for tests purpose') 
        # Initialize demo types for tests only
        type_list = listTypes(config.PROJECT_NAME)
        content_types, constructors, ftis = process_types(type_list, config.PROJECT_NAME)

        # Assign an own permission to all content types
        all_types = zip(content_types, constructors)
        for atype, constructor in all_types:
            kind = "%s: %s" % (config.PROJECT_NAME, atype.archetype_name)
            ContentInit(
                kind,
                content_types      = (atype,),
                permission         = permissions[atype.portal_type],
                extra_constructors = (constructor,),
                fti                = ftis,
                ).initialize(context)


for idx in _indexes:

    exec("manage_addMultilanguage%sForm = %s.manage_addMultilanguage%sForm" % (idx,idx,idx))
    exec("manage_addMultilanguage%s     = %s.manage_addMultilanguage%s" % (idx,idx,idx))
