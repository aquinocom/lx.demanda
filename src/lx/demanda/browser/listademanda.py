# -*- coding: utf-8 -*-

# Zope3 imports
from zope.component import getUtility
from Acquisition import aq_inner

# Product imports
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

#Plone imports
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry


#Libs imports
from DateTime import DateTime

# lx.demanda imports
from lx.demanda.interfaces.contents import IDemanda, IAtividade
from lx.demanda.interfaces.interfaces import ICatalogoServicoPrefsForm


class ListaDemandaView(BrowserView):
    """ view 
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def settings(self):
        if 'form.action.ordemServico' in self.request.form:
            if self.validateOrdemServico():
                return self.getDemandas()

    @memoize
    def validateOrdemServico(self):
        """Validação
        """
        context = aq_inner(self.context)
        utils = getToolByName(context, 'plone_utils')
        ordemServico = self.request.get('ordemServico', None)
        projetizada = self.request.get('projetizada', False)
        start = self.request.get('start', None)
        end = self.request.get('end', None)

        if (ordemServico == ' '):
            self.errors['ordem_servico'] = "O campo é obrigatório."

        if projetizada == 'True':
            if (start == '') or (end == ''):
                self.errors['projetizada'] = "Preencher as datas"
        # Check for errors
        if self.errors:
            utils.addPortalMessage("Corrija os erros.", type='error')
            return False
        else:
            return True


    @memoize
    def getDemandas(self):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = '/'.join(self.context.getPhysicalPath())
        ordemServico = self.request.get('ordemServico', None)
        projetizada = self.request.get('projetizada', False)
        start = self.request.get('start', None)
        end = self.request.get('end', None)

        dic = {'demanda':[], 'atividades':[]}
        if (ordemServico == None):
            os = self.getOS()
            if os:
                ordemServico = os[0]
        if (ordemServico != None) and (ordemServico != ' '):
            demandas = catalog(object_provides=IDemanda.__identifier__,
                               path=path_demandas,
                               ordem_servico=ordemServico,
                               sort_on='chamado',
                               sort_order='reverse',)

            if demandas:
                for i in demandas:
                    dic['demanda'].append(i)

        if projetizada == 'True':
            if start or end:
                atividades = self.getAtividades()
                if atividades:
                    for i in atividades:
                        dic['atividades'].append(i)

        return dic

    @memoize
    def getAtividades(self):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = '/'.join(self.context.getPhysicalPath())
        start = self.request.get('start', None)
        end = self.request.get('end', None)

        first_date = DateTime(start, datefmt='international')
        last_date = DateTime(end + ' 23:59:59', datefmt='international')
        atividades = catalog(object_provides=IAtividade.__identifier__,
                           path=path_demandas,
                           data_inicio={'query': first_date, 'range': 'min'},
                           data_fim={'query': last_date, 'range': 'max'},
                           sort_on='data_inicio')

        return atividades


    @memoize
    def getTotalHST(self):
        """
        """
        tarefas = self.getDemandas()

        atividades = tarefas['atividades']
        demandas = tarefas['demanda']

        if not atividades and not demandas:
            return '0'

        if atividades and demandas:
            lista_tarefas = atividades + demandas
        if atividades and not demandas:
            lista_tarefas = atividades
        if not atividades and demandas:
            lista_tarefas = demandas

        quantidades = []
        for i in lista_tarefas:
            totalAt = i.quantHST
            quantidades.append(totalAt)
        total = sum(quantidades)
        return total

    @memoize
    def getOS(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICatalogoServicoPrefsForm)
        ordens_servicos = tuple()
        try:
            ordens_servicos = ordens_servicos + settings.ordem_servico
        except:
            ordens_servicos = ordens_servicos
        return ordens_servicos

    @memoize
    def requestOS(self):
        ordemServico = self.request.get('ordemServico', None)
        projetizada = self.request.get('projetizada', False)
        start = self.request.get('start', None)
        end = self.request.get('end', None)

        if (ordemServico == None):
            os = self.getOS()
            if os:
                ordemServico = os[0]

        if not projetizada:
            args = "ordemServico=%s" % ordemServico

        if projetizada == 'True':
            if start or end:
                args = "ordemServico=%s&start=%s&end=%s" % (ordemServico, start, end)

        return args
