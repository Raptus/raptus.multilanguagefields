Introduction
============

raptus.multilanguagefields provides Archetypes fields and catalog indexes which 
are able to store multiple languages.

Migrating
---------

Migration of already populated plone sites which where previously not
running raptus.multilanguagefields is done by using the script **migrate.py**
in the **scripts** folder of this package.

::

    migrate -- migrate an existing single language site to a multilingual
               site using raptus.multilanguagefields
    
    Usage: bin/instance run path_to_this_script path_to_the_desired_plone_instance_in_zope [path_to_the_desired_plone_instance_in_zope] ..
    
    Options:
    -h/--help -- print usage message and exit

The script will iterate over all objects in your plone instance and replace
the value of the default language, if non is available, by the one set before
using raptus.multilanguagefields.

Example
```````

Say you have a plone instance with the ID "Plone" in your zope root folder which
has it's content already populated in english and you need another language, say
german, which you would like to provide using raptus.multilanguagefields and the
additional package raptus.multilanguageplone.

Now if you just install raptus.multilanguageplone your already populated english
content will no longer be visible and that is when you have to run this script.

Shut down your zope and make sure you have a backup of your database and your
third-party storages like blob or sql.

Now run the script as followed::

    bin/instance run [path_to_this_script] Plone

This will copy the already populated english content into the default language set
in the portal_languages tool, which in your case should be english. Now start up
your zope and your plone content should be back in place.
