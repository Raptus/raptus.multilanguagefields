# -*- coding: utf-8 -*-

__author__  = ''
__docformat__ = 'restructuredtext'

# CMF imports
from Products.CMFCore.permissions import setDefaultRoles

# Archetypes imports
from Products.Archetypes.public import listTypes

# Products imports
from config import PROJECT_NAME

TYPE_ROLES = ('Manager', 'Owner')

permissions = {}
def wireAddPermissions():
    """Creates a list of add permissions for all types in this project
    
    Must be called **after** all types are registered!
    """
    
    global permissions
    all_types = listTypes(PROJECT_NAME)
    for atype in all_types:
        permission = "%s: Add %s" % (PROJECT_NAME, atype['portal_type'])
        setDefaultRoles(permission, TYPE_ROLES)
        permissions[atype['portal_type']] = permission
    return permissions
