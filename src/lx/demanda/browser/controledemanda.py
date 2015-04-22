# -*- coding: utf-8 -*-

# Zope3 imports
from zope.component import getUtility
from Acquisition import aq_inner

# Product imports
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

#Plone imports
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

#Libs imports


# lx.demanda imports
from lx.demanda.interfaces.contents import IDemanda
from lx.demanda.interfaces.interfaces import ICatalogoServicoPrefsForm


class ControleDemandaView(BrowserView):
    """ view 
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def settings(self):
        if 'form.action.ordemServico' in self.request.form:
            ordemServico = self.request.get('ordemServico', None)
            if self.validateOrdemServico(ordemServico):
                return self.getColaborador()

    @memoize
    def validateOrdemServico(self, ordemServico):
        """Validação
        """
        context = aq_inner(self.context)
        utils = getToolByName(context, 'plone_utils')
        if (ordemServico == ' '):
            self.errors['ordem_servico'] = "O campo é obrigatório."
        # Check for errors
        if self.errors:
            utils.addPortalMessage("Corrija os erros.", type='error')
            return False
        else:
            return True

    @memoize
    def getColaborador(self):
        """
        """
        ordemServico = self.request.get('ordemServico', None)
        if (ordemServico != None) and (ordemServico != ' '):
            catalog = getToolByName(self, 'portal_catalog')
            path_demandas = '/'.join(self.context.getPhysicalPath())
            demandas = catalog(portal_type="colaborador",
                               path=path_demandas,
                               sort_on='getObjPositionInParent',)
            return demandas



    @memoize
    def getDemandas(self, colab):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = colab.getPath()
        ordemServico = self.request.get('ordemServico', None)
        if (ordemServico != None) and (ordemServico != ' '):
            demandas = catalog(object_provides=IDemanda.__identifier__,
                               path=path_demandas,
                               ordem_servico=ordemServico,
                               sort_on='Date',
                               sort_order='reverse',)
            return demandas
        else:
            demandas = catalog(object_provides=IDemanda.__identifier__,
                               path=path_demandas,
                               sort_on='Date',
                               sort_order='reverse',)
            return demandas

    @memoize
    def getTotalHST(self, colab):
        """
        """
        demandas = self.getDemandas(colab)
        quantidades = []
        for i in demandas:
            totalAt = i.quantHST
            quantidades.append(totalAt)
        total = sum(quantidades)
        return total

    @memoize
    def getOS(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICatalogoServicoPrefsForm)
        ordens_servicos = tuple(' ')
        try:
            ordens_servicos = ordens_servicos + settings.ordem_servico
        except:
            ordens_servicos = ordens_servicos
        return ordens_servicos
