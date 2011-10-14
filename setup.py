import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

from xml.dom import minidom

metadata_file = os.path.join(os.path.dirname(__file__),
                             'raptus', 'multilanguagefields',
                             'profiles', 'default', 'metadata.xml')

metadata = minidom.parse(metadata_file)
version = metadata.getElementsByTagName("version")[0].childNodes[0].nodeValue
version = str(version).strip()

if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    requires = ['simplejson']
else:
    requires = []

setup(name='raptus.multilanguagefields',
      version=version,
      description="Providing multi language fields and widgets",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone archetypes widgets fields',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='http://plone.org/products/raptus.multilanguagefields',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ] + requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
