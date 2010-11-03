"""
migrate -- migrate an existing single language site to a multilingual
           site using raptus.multilanguagefields

Usage: bin/instance run path_to_this_script path_to_the_desired_plone_instance_in_zope [path_to_the_desired_plone_instance_in_zope] ..

Options:
-h/--help -- print usage message and exit

The script will iterate over all objects in your plone instance and replace
the value of the default language, if non is available, by the one set before
using raptus.multilanguagefields.

Example:
Say you have a plone instance with the ID "Plone" in your zope root folder which
has it's content already populated in english and you need another language, say
german, which you would like to provide using raptus.multilanguagefields and the
additional package raptus.multilanguageplone.

Now if you just install raptus.multilanguageplone your already populated english
content will no longer be visible and that is when you have to run this script.

Shut down your zope and make sure you have a backup of your database and your
third-party storages like blob or sql.

Now run the script as followed:

bin/instance run [path_to_this_script] Plone

This will copy the already populated english content into the default language set
in the portal_languages tool, which in your case should be english. Now start up
your zope and your plone content should be back in place.
"""
import sys
import transaction
from Testing.makerequest import makerequest
from zope.app import publication
from zope.app.component import site
from Products.CMFPlone.interfaces import IPloneSiteRoot
from raptus.multilanguagefields.interfaces import IMultilanguageField

def setSiteManager(plone):
    ev = publication.interfaces.BeforeTraverseEvent(plone, plone.REQUEST)
    site.threadSiteSubscriber(plone, ev)

def migrate(path):
    print "starting migration of %s" % path
    try:
        parts = path.split('/')
        obj = app
        while len(parts):
            obj = obj._getOb(parts.pop(0))
        if not IPloneSiteRoot.providedBy(obj):
            print "  the object at %s is not a plone site" % path
            raise
        setSiteManager(obj)
        migrate_object(obj)
        print "finished migration of %s" % path
    except:
        print "migrating %s failed" % path
        return

def migrate_object(obj):
    try:
        transaction.begin()
        fields = obj.Schema().fields()
        for field in fields:
            if IMultilanguageField.providedBy(field):
                migrate_field(field, obj)
        transaction.commit()
    except:
        transaction.abort()
        pass
    try:
        for child in obj.objectValues():
            migrate_object(child)
    except:
        pass

def migrate_field(field, obj):
    try:
        field.resetLanguage()
        target = field.getDefaultLang(obj) or field._getCurrentLanguage(obj)
        value = field.get(obj, lang=target)
        if true_value(value, field, obj):
            return
        original = field.get(obj, lang='original')
        if not true_value(original, field, obj) and obj.schema.has_key(field.__name__):
            original_field = obj.schema.get(field.__name__)
            original = original_field.get(obj)
        if true_value(original, field, obj):
            print "  %s migrating field %s storing in %s" % ('/'.join(obj.getPhysicalPath()), field.__name__, target)
            field.set(obj, {target: original})
            obj.reindexObject()
    except:
        pass

def true_value(value, field, obj):
    return value and not value == field.getDefault(obj) and (not hasattr(value, 'get_size') or value.get_size() > 0)

print """
***********************************************************************************
                       raptus.multilanguagefields Migration


"""

app = makerequest(app)
args = sys.argv[1:]
while len(args):
    path = args.pop(0)
    if path == '-h' or path == '--help':
        print __doc__
        break
    migrate(path)

print """


***********************************************************************************
"""
