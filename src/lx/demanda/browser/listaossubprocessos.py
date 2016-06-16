# -*- coding: utf-8 -*-

# Product imports
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize
from suds.client import Client
import re


class ListaOSSubprocessosView(BrowserView):
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

        self.lista_1_1 = []
        self.lista_1_2 = []
        self.lista_1_3 = []
        self.lista_1_4 = []
        self.lista_1_5 = []
        self.lista_1_6 = []
        self.lista_1_7 = []
        self.lista_1_8 = []
        self.lista_2_1 = []
        self.lista_2_2 = []
        self.lista_2_3 = []
        self.lista_2_4 = []
        self.lista_2_5 = []
        self.lista_3_1 = []
        self.lista_3_2 = []

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

                    if i['CodigoAtividade'][:3] == '1.1':
                        self.lista_1_1.append(dic)
                    if i['CodigoAtividade'][:3] == '1.2':
                        self.lista_1_2.append(dic)
                    if i['CodigoAtividade'][:3] == '1.3':
                        self.lista_1_3.append(dic)
                    if i['CodigoAtividade'][:3] == '1.4':
                        self.lista_1_4.append(dic)
                    if i['CodigoAtividade'][:3] == '1.5':
                        self.lista_1_5.append(dic)
                    if i['CodigoAtividade'][:3] == '1.6':
                        self.lista_1_6.append(dic)
                    if i['CodigoAtividade'][:3] == '1.7':
                        self.lista_1_7.append(dic)
                    if i['CodigoAtividade'][:3] == '1.8':
                        self.lista_1_8.append(dic)
                    if i['CodigoAtividade'][:3] == '2.1':
                        self.lista_2_1.append(dic)
                    if i['CodigoAtividade'][:3] == '2.2':
                        self.lista_2_2.append(dic)
                    if i['CodigoAtividade'][:3] == '2.3':
                        self.lista_2_3.append(dic)
                    if i['CodigoAtividade'][:3] == '2.4':
                        self.lista_2_4.append(dic)
                    if i['CodigoAtividade'][:3] == '2.5':
                        self.lista_2_5.append(dic)
                    if i['CodigoAtividade'][:3] == '3.1':
                        self.lista_3_1.append(dic)
                    if i['CodigoAtividade'][:3] == '3.2':
                        self.lista_3_2.append(dic)
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

    def getTotalSubprocessoHST(self, subprocesso):
        """
        """
        total = 0
        if subprocesso == '1.1':
            if self.lista_1_1:
                for i in self.lista_1_1:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.2':
            if self.lista_1_2:
                for i in self.lista_1_2:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.3':
            if self.lista_1_3:
                for i in self.lista_1_3:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.4':
            if self.lista_1_4:
                for i in self.lista_1_4:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.5':
            if self.lista_1_5:
                for i in self.lista_1_5:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.6':
            if self.lista_1_6:
                for i in self.lista_1_6:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.7':
            if self.lista_1_7:
                for i in self.lista_1_7:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.8':
            if self.lista_1_8:
                for i in self.lista_1_8:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.1':
            if self.lista_2_1:
                for i in self.lista_2_1:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.2':
            if self.lista_2_2:
                for i in self.lista_2_2:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.3':
            if self.lista_2_3:
                for i in self.lista_2_3:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.4':
            if self.lista_2_4:
                for i in self.lista_2_4:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.5':
            if self.lista_2_5:
                for i in self.lista_2_5:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '3.1':
            if self.lista_3_1:
                for i in self.lista_3_1:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '3.2':
            if self.lista_3_2:
                for i in self.lista_3_2:
                    if i['Status'] != 'Cancelada':
                        total += i['totalHST']
        return total

    def getTotalSubprocessoCancelHST(self, subprocesso):
        """
        """
        total = 0
        if subprocesso == '1.1':
            if self.lista_1_1:
                for i in self.lista_1_1:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.2':
            if self.lista_1_2:
                for i in self.lista_1_2:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.3':
            if self.lista_1_3:
                for i in self.lista_1_3:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.4':
            if self.lista_1_4:
                for i in self.lista_1_4:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.5':
            if self.lista_1_5:
                for i in self.lista_1_5:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.6':
            if self.lista_1_6:
                for i in self.lista_1_6:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.7':
            if self.lista_1_7:
                for i in self.lista_1_7:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '1.8':
            if self.lista_1_8:
                for i in self.lista_1_8:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.1':
            if self.lista_2_1:
                for i in self.lista_2_1:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.2':
            if self.lista_2_2:
                for i in self.lista_2_2:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.3':
            if self.lista_2_3:
                for i in self.lista_2_3:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.4':
            if self.lista_2_4:
                for i in self.lista_2_4:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '2.5':
            if self.lista_2_5:
                for i in self.lista_2_5:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '3.1':
            if self.lista_3_1:
                for i in self.lista_3_1:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        if subprocesso == '3.2':
            if self.lista_3_2:
                for i in self.lista_3_2:
                    if i['Status'] == 'Cancelada':
                        total += i['totalHST']
        return total

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