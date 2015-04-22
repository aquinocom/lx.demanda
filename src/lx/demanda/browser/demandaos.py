# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from plone.memoize.instance import memoize
from lxml import etree
import re
import logging
from zope.site.hooks import getSite
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from xml.etree.ElementTree import iterparse
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
#Libs python
from lx.demanda.interfaces.contents import IDemanda


class DemandaOSView(BrowserView):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def settings(self):
        if 'form.action.ordemServico' in self.request.form:
            ordemServico = self.request.get('ordemServico', None)
            if self.validateOrdemServico(ordemServico):
                return self.getAtividades()

    @memoize
    def validateOrdemServico(self, ordemServico):
        """Validação
        """
        context = aq_inner(self.context)
        utils = getToolByName(context, 'plone_utils')
        if (ordemServico == ''):
            self.errors['ordem_servico'] = "O campo é obrigatório."
        # Check for errors
        if self.errors:
            utils.addPortalMessage("Corrija os erros.", type='error')
            return False
        else:
            return True

    def getAtividades(self):
        """
        """
        ordemServico = self.request.get('ordemServico', None)
        if (ordemServico != ''):
            catalog = getToolByName(self, 'portal_catalog')
            path_demandas = '/'.join(self.context.getPhysicalPath())
            atividades = catalog(object_provides=IDemanda.__identifier__,
                               path=path_demandas,
                               sort_on='chamado',
                               sort_order='reverse',
                               ordem_servico=ordemServico,
                               )
            return atividades

    @memoize
    def getOrdemServico(self):
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = '/'.join(self.context.getPhysicalPath())
        demandas = catalog(object_provides=IDemanda.__identifier__,
                           path=path_demandas,
                           sort_on='Date',
                           sort_order='reverse',)
        listOS = []
        for i in demandas:
            if i.ordem_servico:
                if not(i.ordem_servico in listOS):
                    listOS.append(i.ordem_servico)
        return listOS

    @memoize
    def getTotalHST(self):
        """
        """
        demandas = self.getAtividades()
        quantidades = []
        for i in demandas:
            totalAt = i.quantHST
            quantidades.append(totalAt)
        total = sum(quantidades)
        return total

