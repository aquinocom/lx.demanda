from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class LxdemandaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import lx.demanda
        xmlconfig.file(
            'configure.zcml',
            lx.demanda,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'lx.demanda:default')

LX_DEMANDA_FIXTURE = LxdemandaLayer()
LX_DEMANDA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(LX_DEMANDA_FIXTURE,),
    name="LxdemandaLayer:Integration"
)
LX_DEMANDA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(LX_DEMANDA_FIXTURE, z2.ZSERVER_FIXTURE),
    name="LxdemandaLayer:Functional"
)
