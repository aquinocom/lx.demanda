# -*- coding: utf-8 -*-

# Product imports
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize
from suds.client import Client
import re


class ListaRAOSV2View(BrowserView):
    """
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        self.props = getToolByName(self.context, 'portal_properties')
        self.utils = getToolByName(self.context, 'plone_utils')
        self.site_properties = self.props['site_properties']

        self.url_solicitacao_pesquisa = self.context.absolute_url()
        self.url_sucess = self.context.absolute_url()

        self.url_servico_ra = self.site_properties.URL_SERVICO_RA

        self.lista = []

        if 'ordemServico' in request.form:
            ordemServico = request.form['ordemServico']
            request.set('ordemServico', ordemServico)
            self.ordemServico = ordemServico
        else:
            self.ordemServico = None

        if 'anoOS' in request.form:
            anoOS = request.form['anoOS']
            request.set('anoOS', anoOS)
            self.anoOS = anoOS
        else:
            self.anoOS = None

    def __call__(self):

        if 'form.enviar' in self.request.form:
            if self.validateForm():
                self.getRAs()

        return self.index()

    @memoize
    def validateForm(self):
        """
        """

        if not self.ordemServico:
            self.errors['ordem_servico'] = "O campo é obrigatório."

        if not self.anoOS:
            self.errors['ano'] = "O campo é obrigatório."

        # Check for errors
        if self.errors:
            self.utils.addPortalMessage("Corrija os erros.", type='error')
            return False
        else:
            return True

    @memoize
    def getRAs(self):
        """
        """
        client = Client(self.url_servico_ra)
        items = client.service.Executar(OrdemDeServicoID=self.ordemServico, AnoOsID=self.anoOS)
        if items:
            try:
                for i in items['RegistrosDeAtividades']['RegistroAtividade']:
                    SessionID = i['SessionID']
                    complexValorAtividade = self.getComplexValorAtividade(items, SessionID)
                    complexidade = complexValorAtividade['complex']
                    valor = float(complexValorAtividade['valor'].replace(',', '.'))
                    #federativo = i['SistemaFederativo']
                    federativo = True
                    try:
                        OrigemDaDemana = i['OrigemDaDemana']
                    except:
                        OrigemDaDemana = ''
                    try:
                        UnidadeClienteSigla = i['UnidadeClienteSigla']
                    except:
                        UnidadeClienteSigla = ''
                    try:
                        UnidadeExecutoraSigla = i['UnidadeExecutoraSigla']
                    except:
                        UnidadeExecutoraSigla = ''
                    try:
                        UsuarioExecutor = i['UsuarioExecutor']
                    except:
                        UsuarioExecutor = ''
                    try:
                        UsuarioSolicitante = i['UsuarioSolicitante']
                    except:
                        UsuarioSolicitante = ''
                    try:
                        SistemaSigla = i['SistemaSigla']
                    except:
                        SistemaSigla = ''
                    try:
                        AtividadeObservacoes = i['AtividadeObservacoes']
                    except:
                        AtividadeObservacoes = ''
                    dic = {
                        'ra':  i['ProcessID'],
                        'Status': i['Status'],
                        'OrdemServico': i['OrdemServico'],
                        'CodigoAtividade': i['CodigoAtividade'],
                        'SistemaSigla': SistemaSigla,
                        'SistemaFederativo': i['SistemaFederativo'],
                        'IncideDeflator': i['IncideDeflator'],
                        'Deflator': i['Deflator'],
                        'Multiplicador': i['Multiplicador'],
                        'EngenhariaReversa': i['EngenhariaReversa'],
                        'OrigemDaDemana': OrigemDaDemana,
                        'UsuarioSolicitante': UsuarioSolicitante,
                        'UsuarioExecutor': UsuarioExecutor,
                        'TaskURL': i['TaskURL'],
                        'UnidadeClienteSigla': UnidadeClienteSigla,
                        'UnidadeExecutoraSigla': UnidadeExecutoraSigla,
                        'complexidade': complexidade,
                        'valor': valor,
                        'AtividadeObservacoes': AtividadeObservacoes
                    }
                    # Calculo da HST
                    complexidade = valor
                    multiplicador = float(i['Multiplicador'])

                    if i['IncideDeflator']:
                        valorDeflator = float(i['Deflator'])
                    else:
                        valorDeflator = 1.0

                    if i['IncideDeflator'] and federativo and i['EngenhariaReversa']:
                        totalHST = ((valor * 1.3) * multiplicador) * valorDeflator

                    if i['IncideDeflator'] and not(federativo) and not(i['EngenhariaReversa']):
                        totalHST = ((valor * multiplicador) * valorDeflator) * 0.6

                    if not(i['IncideDeflator']) and not(federativo) and not(i['EngenhariaReversa']):
                        totalHST = (valor * multiplicador) * 0.6

                    if i['IncideDeflator'] and federativo and not(i['EngenhariaReversa']):
                        totalHST = (valor * multiplicador) * valorDeflator

                    if i['IncideDeflator'] and not(federativo) and i['EngenhariaReversa']:
                        totalHST = (((valor * 1.3) * multiplicador) * 0.6) * valorDeflator

                    if not(i['IncideDeflator']) and not(federativo) and i['EngenhariaReversa']:
                        totalHST = ((valor * 1.3) * multiplicador) * 0.6

                    if not(i['IncideDeflator']) and federativo and not(i['EngenhariaReversa']):
                        totalHST = (valor * multiplicador)

                    if not(i['IncideDeflator']) and federativo and i['EngenhariaReversa']:
                        totalHST = ((valor * 1.3) * multiplicador)
                    dic['totalHST'] = totalHST

                    self.lista.append(dic)
            except:
                import pdb; pdb.set_trace()
                pass
        pass

    def getComplexValorAtividade(self, items, SessionID):
        """
        """
        try:
            for i in items['RegistroAtividadesComplexidade']['RegistroAtividadeComplexidade']:
                if SessionID == i['SessionID']:
                    dic = {
                        'complex': i['Nome'],
                        'valor': i['Valor'],
                    }
        except:
            dic = {
                'complex': None,
                'valor': None,
            }
        return dic

    def getTotalGeralHST(self):
        """
        """
        total = 0
        if self.lista:
            for i in self.lista:
                if i['Status'] != 'Cancelada':
                    total += i['totalHST']
        return total

    def getTotalCancelHST(self):
        """
        """
        total = 0
        if self.lista:
            for i in self.lista:
                if i['Status'] == 'Cancelada':
                    total += i['totalHST']
        return total