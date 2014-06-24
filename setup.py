import os
import sys
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1b10.dev0'

if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    requires = ['simplejson']
else:
    requires = []

setup(name='raptus.multilanguagefields',
      version=version,
      description="Providing multi language fields and widgets",
      long_description=open("README.rst").read() + "\n" +
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
      url='https://github.com/Raptus/raptus.multilanguagefields',
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
