"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
import sys
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from Products.PloneTestCase.layer import ZCMLLayer


@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    fiveconfigure.debug_mode = True
    # patch to allow demo content types
    from raptus.multilanguagefields import config
    config.REGISTER_DEMO_TYPES = True
    import raptus.multilanguagefields
    zcml.load_config('configure.zcml', raptus.multilanguagefields)
    fiveconfigure.debug_mode = False
    ztc.installPackage('raptus.multilanguagefields')



setup_product()
ptc.setupPloneSite()

class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            # fix doctests in case of using ipython
            try :
                iphook = sys.displayhook
                sys.displayhook = sys.__displayhook__
            except:
                pass   

        @classmethod
        def tearDown(cls):
            pass

    def afterSetUp(self):
        #self.portal.portal_languages.use_cookie_negotiation=1
        self.portal.portal_languages.use_request_negotiation=1
        self.portal.portal_languages.always_show_selector=1
        self.portal.portal_languages.start_neutral=1