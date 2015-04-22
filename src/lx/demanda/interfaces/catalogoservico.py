# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from zope.component import getUtility
from persistent import Persistent
from zope.interface import implements

# Product imports
from lx.demanda.interfaces.interfaces import ICatalogoServicoPrefsForm
from lx.demanda import demandaMessageFactory as _


class CatalogoServicoSettings(Persistent):

    implements(ICatalogoServicoPrefsForm)

    url_webservice = ''


class CatalogoServicoSettingsPanel(controlpanel.RegistryEditForm):
    """Configuração dos campos do formulario.
    """
    schema = ICatalogoServicoPrefsForm
    label = _(u'Formulário de onfiguração do webservice')
    description = _(u'Configuração do webservice')
    form_name = _(u'Formulário de configuração do webservice')

    def updateFields(self):
        super(CatalogoServicoSettingsPanel, self).updateFields()

    def updateWidgets(self):
        super(CatalogoServicoSettingsPanel, self).updateWidgets()


class JEMultimidiaPrefsForm(controlpanel.ControlPanelFormWrapper):
    """ Classe para o formulário de preferência do webservice.
    """
    form = CatalogoServicoSettingsPanel


def webservice_settings(context):
    return getUtility(ICatalogoServicoPrefsForm)
