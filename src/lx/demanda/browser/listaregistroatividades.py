# -*- coding: utf-8 -*-

# Product imports
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize
from suds.client import Client
import re


class ListaRegistroAtividadesView(BrowserView):
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
                    if self.context.email == i['UsuarioSolicitante']:
                        try:
                            OrigemDaDemana = i['OrigemDaDemana']
                        except:
                            OrigemDaDemana = ''
                        dic = {
                            'ra':  i['ProcessID'],
                            'Status': i['Status'],
                            'OrdemServico': i['OrdemServico'],
                            'CodigoAtividade': i['CodigoAtividade'],
                            'SistemaSigla': i['SistemaSigla'],
                            'SistemaFederativo': i['SistemaFederativo'],
                            'IncideDeflator': i['IncideDeflator'],
                            'Deflator': i['Deflator'],
                            'Multiplicador': i['Multiplicador'],
                            'EngenhariaReversa': i['EngenhariaReversa'],
                            'OrigemDaDemana': OrigemDaDemana,
                            'TaskURL': i['TaskURL'],
                            'UnidadeClienteSigla': i['UnidadeClienteSigla'],
                            'UnidadeExecutoraSigla': i['UnidadeExecutoraSigla'],
                        }
                        self.lista.append(dic)
            except:
                pass
        pass

