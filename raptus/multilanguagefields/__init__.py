from Products.CMFPlone import utils
from Products.CMFPlone.browser.ploneview import Plone

from zope.i18nmessageid import MessageFactory
multilanguagefieldsMessageFactory = MessageFactory('raptus.multilanguagefields')
from Products.PlacelessTranslationService.utility import PTSTranslationDomain
multilanguagefieldsdomain = PTSTranslationDomain('raptus.multilanguagefields')

from config import *

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
from raptus.multilanguagefields.interfaces import IMultilanguageAware, IMultilanguageField

from proxy import MultilanguageAware

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


for idx in _indexes:

    exec("manage_addMultilanguage%sForm = %s.manage_addMultilanguage%sForm" % (idx,idx,idx))
    exec("manage_addMultilanguage%s     = %s.manage_addMultilanguage%s" % (idx,idx,idx))
    