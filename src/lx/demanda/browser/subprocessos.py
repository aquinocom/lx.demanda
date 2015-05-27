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
from Acquisition import aq_base, aq_inner, aq_parent
#Libs python
from lx.demanda.interfaces.contents import IDemanda


class SubProcessosView(BrowserView):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def settings(self):
        if 'form.action.ordemServico' in self.request.form:
            ordemServico = self.request.get('ordemServico', None)
            subProcesso = self.request.get('subProcesso', None)
            if self.validateOrdemServico(ordemServico, subProcesso):
                return self.getAtividades()

    @memoize
    def validateOrdemServico(self, ordemServico, subProcesso):
        """Validação
        """
        context = aq_inner(self.context)
        utils = getToolByName(context, 'plone_utils')
        if (ordemServico == ''):
            self.errors['ordem_servico'] = "O campo é obrigatório."
        if (subProcesso == ''):
            self.errors['sub_processos'] = "O campo é obrigatório."
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
        subProcesso = self.request.get('subProcesso', None)
        if (ordemServico != '' and subProcesso != ''):
            catalog = getToolByName(self, 'portal_catalog')
            path_demandas = '/'.join(self.context.getPhysicalPath())
            atividades = catalog(object_provides=IDemanda.__identifier__,
                               path=path_demandas,
                               sort_on='chamado',
                               sort_order='reverse',
                               ordem_servico=ordemServico,
                               )
            results = []
            for i in atividades:
                if i.atividade[:3] == subProcesso:
                    results.append(i)
            return results

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

    @memoize
    def getColaborador(self, item):
        obj = item.getObject()
        colab = aq_parent(aq_inner(obj)).Title()
        return colab
