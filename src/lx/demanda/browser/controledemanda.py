# -*- coding: utf-8 -*-

# Zope3 imports
from zope.component import getUtility
from Acquisition import aq_inner
from zope.component import getMultiAdapter

# Product imports
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

#Plone imports
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

#Libs imports
from DateTime import DateTime


# lx.demanda imports
from lx.demanda.interfaces.contents import IDemanda, IAtividade
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
            if self.validateOrdemServico():
                return self.getColaboradores()

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

        if (ordemServico == ' ') and not(projetizada):
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
    def getColaboradores(self):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = '/'.join(self.context.getPhysicalPath())
        ordemServico = self.request.get('ordemServico', None)
        projetizada = self.request.get('projetizada', False)
        if (ordemServico != ' ' and ordemServico != None) or projetizada:
            colabs = catalog(portal_type="colaborador",
                               path=path_demandas,
                               sort_on='getObjPositionInParent',)

            list_colab = []
            if colabs:
                for colab in colabs:
                    dic = {
                        'nome': colab.Title,
                        'url': colab.getURL(),
                        'total': self.getTotalHST(colab),
                    }
                    list_colab.append(dic)

            return list_colab

    @memoize
    def getDemandas(self, colab):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = colab.getPath()
        ordemServico = self.request.get('ordemServico', None)
        projetizada = self.request.get('projetizada', False)
        start = self.request.get('start', None)
        end = self.request.get('end', None)

        dic = {'demanda':[], 'atividades':[]}

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
            if start and end:
                atividades = self.getAtividades(colab)
                if atividades:
                    for i in atividades:
                        dic['atividades'].append(i)

        return dic

    @memoize
    def getAtividades(self, colab):
        """
        """
        catalog = getToolByName(self, 'portal_catalog')
        path_demandas = colab.getPath()
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
    def getTotalHST(self, colab):
        """
        """
        tarefas = self.getDemandas(colab)
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
        #registry = getUtility(IRegistry)
        #settings = registry.forInterface(ICatalogoServicoPrefsForm)
        ordens_servicos = tuple(' ')
        try:
            # ordens_servicos = ordens_servicos + settings.ordem_servico
            ordens_servicos = ordens_servicos + self.context.lista_os

            if ordens_servicos:
                lista_os = []
                for i in ordens_servicos:
                    lista_os.append(i)
                if not self.autenticado():
                    lista_os.remove('---')
            ordens_servicos = lista_os
        except:
            ordens_servicos = ordens_servicos
        return ordens_servicos

    @memoize
    def autenticado(self):
        """Retorna True(verdadeiro) se o usuário estiver autenticado.
        """
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')

        if not portal_state.anonymous():
            return True
        else:
            return False