# -*- coding: utf-8 -*-

# Zope3 imports
from zope.interface import implements
from zope.component import getUtility
# Security
from AccessControl import ClassSecurityInfo

# Archetypes & ATCT imports
from Acquisition import aq_inner, aq_parent
from Products.MasterSelectWidget.MasterSelectWidget import MasterSelectWidget
from Products.Archetypes.utils import DisplayList
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry

#Libs
from suds.client import Client

# Product imports
from lx.demanda.interfaces.interfaces import ICatalogoServicoPrefsForm
from lx.demanda import demandaMessageFactory as _
from lx.demanda.interfaces.contents import IDemanda
from lx.demanda import config

# Schema definition
schema = ATCTContent.schema.copy() + atapi.Schema((
    atapi.StringField(
        name='tipo_servico',
        required=True,
        searchable=True,
        #vocabulary=DisplayList(
        #    (('', ''),
        #        ('1', 'Infraestrutura'),
        #        ('2', 'Apoio ao Controle'),
        #        ('3', 'Sustentação'),
        #        ('4', 'Apoio ao Planejamento'),)),
        vocabulary=DisplayList(
            (('', ''),
                ('2', 'Apoio ao Controle'),
                ('3', 'Sustentação'),
                ('4', 'Apoio ao Planejamento'),)),
        widget=MasterSelectWidget(
            label=_(u"Tipo de Serviço"),
            description=_(u"Tipo de Serviço"),
            slave_fields=({'name': 'atividade',
                           'action': 'vocabulary',
                           'vocab_method': 'getAtividades',
                           'control_param': 'id',
                           },),
        )
    ),
    atapi.StringField(
        name='atividade',
        required=True,
        searchable=True,
        vocabulary=[],
        widget=MasterSelectWidget(
            label=_(u"Atividade"),
            description=_(u"Atividade"),
            slave_fields=(
                {'name': 'produto',
                 'action': 'value',
                 'vocab_method': 'getProdutos',
                 'control_param': 'id',
                 },
                {'name': 'complexidade',
                 'action': 'vocabulary',
                 'vocab_method': 'getComplexidades',
                 'control_param': 'id',
                 },
                {'name': 'valor_deflator',
                 'action': 'value',
                 'vocab_method': 'getVlDeflator',
                 'control_param': 'id',
                 },),
        )
    ),
    atapi.StringField(
        name="produto",
        required=False,
        searchable=False,
        widget=atapi.TextAreaWidget(
            label=_(u"Produto"),),
    ),
    atapi.StringField(
        name='complexidade',
        required=True,
        searchable=True,
        vocabulary=[],
        widget=MasterSelectWidget(
            label=_(u"Complexidade"),
            description=_(u"Complexidade"),)
    ),
    atapi.FloatField(
        name='multiplicador',
        required=True,
        searchable=True,
        default=1.0,
        widget=atapi.StringWidget(
            label=_(u"Multiplicador"),
            description=_(u"Multiplicador"),
            size=10,)
    ),
    atapi.BooleanField(
        name='deflator',
        required=False,
        searchable=True,
        widget=atapi.BooleanWidget(
            label=_(u"Deflator"),
            description=_(u"Aplicar deflator"),)
    ),
    atapi.FloatField(
        name='valor_deflator',
        required=False,
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u"Valor do deflator"),
            description=_(u"Valor do deflator"),
            size=10,)
    ),
    atapi.StringField(
        name='chamado',
        required=False,
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u"Chamado"),
            description=_(u"Número do chamado"),
            size=10,)
    ),
    atapi.StringField(
        name='ordem_servico',
        required=False,
        searchable=True,
        widget=atapi.SelectionWidget(
            label=_(u"Ordem de serviço"),
            description=_(u"Número da ordem de serviço"),
            format='select',),
        vocabulary='getOS',
    ),
    atapi.BooleanField(
        name='federativo',
        required=False,
        searchable=True,
        default=True,
        widget=atapi.BooleanWidget(
            label=_(u"Federativo"),
            description=_(u"Federativo quando é utilizado em 15 ou mais tribunais da Justiça Eleitoral."),)
    ),
    atapi.BooleanField(
        name='reversa',
        required=False,
        searchable=True,
        default=False,
        widget=atapi.BooleanWidget(
            label=_(u"Engenharia reversa"),
            description=_(u"Engenharia reversa."),)
    ),
    #atapi.StringField(
    #    name="observacao",
    #    required=False,
    #    searchable=False,
    #    widget=atapi.TextAreaWidget(
    #        label=_(u"Observação"),),
    #),
    atapi.TextField(
        name='observacao',
        required=False,
        searchable=True,
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label='Observação',
            rows=10,
        ),
    ),
    atapi.StringField(
        name='status_ra',
        required=False,
        searchable=True,
        widget=atapi.SelectionWidget(
            label=_(u"Status da RA"),
            description=_(u"Selecione o status da RA"),
            format='select',),
        vocabulary=['', 'Em aprovação', 'Nova', 'Atribuída', 'Executada', 'Aceita'],
    ),
),)

schema['description'].widget.visible['edit'] = 'invisible'
schema['excludeFromNav'].default = True
#schema['valor_deflator'].widget.visible['edit'] = 'invisible'

schemata.finalizeATCTSchema(schema)


class Demanda(ATCTContent, HistoryAwareMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(IDemanda)

    meta_type = 'Demanda'
    portal_type = 'Demanda'

    _at_rename_after_creation = True
    schema = schema

    idTipoServico = ''
    siglaTipoServico = ''
    codigoAtividade = ''
    descricaoAtividade = ''
    multiplicadorAtividade = ''

    @memoize
    def getURLWebservice(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICatalogoServicoPrefsForm)
        url = str(settings.url_webservice)
        return url

    def getAtividades(self, id):
        listAtividade = DisplayList()
        if id != '':
            url = self.getURLWebservice()
            client = Client(url)
            filtro = client.factory.create('wsFiltros')

            if id == '1':
                self.idTipoServico = 1
                self.siglaTipoServico = "INFR"
            if id == '2':
                self.idTipoServico = 2
                self.siglaTipoServico = "CRTL"
            if id == '3':
                self.idTipoServico = 3
                self.siglaTipoServico = "SUST"
            if id == '4':
                self.idTipoServico = 4
                self.siglaTipoServico = "PLAN"

            filtro.tipoServico.id = self.idTipoServico
            filtro.tipoServico.sigla = self.siglaTipoServico
            search = client.service.consultarAtividades(filtro)

            if search:
                item = search.item
                for item in item:
                    listAtividade.add('', '')
                    atividade = item.listAtividade[0]
                    codAtividade = atividade.codigo
                    descAtividade = atividade.codigo + ' - ' + atividade.descricao
                    #self.descricaoAtividade = descAtividade
                    listAtividade.add(codAtividade, descAtividade)
            listAtividade = listAtividade.sortedByValue()
        return listAtividade

    def getComplexidades(self, id):
        listComplexidade = DisplayList()
        if id != '' and id != 'null':
            try:
                url = self.getURLWebservice()
                client = Client(url)
                filtro = client.factory.create('wsFiltros')
                filtro.tipoServico.id = self.idTipoServico
                filtro.tipoServico.sigla = self.siglaTipoServico
                filtro.codigoAtividade = id
                search = client.service.consultarAtividades(filtro)
                complexidades = search.item[0].listAtividade[0].listComplexidade
                if complexidades.__len__() > 0:
                    for complexidade in complexidades:
                        quantidade = str(complexidade.quantidade)
                        descricao = getattr(complexidade, 'descricao', '')
                        nome = complexidade.nome + ' - ' + descricao + ' - ' + quantidade + 'HST'
                        listComplexidade.add(quantidade, nome)
                return listComplexidade
            except:
                return listComplexidade
        return listComplexidade

    def getProdutos(self, id):
        text = ''
        if id != '' and id != 'null':
            try:
                url = self.getURLWebservice()
                client = Client(url)
                filtro = client.factory.create('wsFiltros')
                filtro.tipoServico.id = self.idTipoServico
                filtro.tipoServico.sigla = self.siglaTipoServico
                filtro.codigoAtividade = id
                search = client.service.consultarAtividades(filtro)
                produtos = search.item[0].listAtividade[0].listProduto
                if produtos.__len__() > 0:
                    for produto in produtos:
                        text = text + getattr(produto, 'descricao', '')
                return text
            except:
                return text
        return text

    def getVlDeflator(self, id):
        if id != '' and id != 'null':
            try:
                url = self.getURLWebservice()
                client = Client(url)
                filtro = client.factory.create('wsFiltros')
                filtro.tipoServico.id = self.idTipoServico
                filtro.tipoServico.sigla = self.siglaTipoServico
                filtro.codigoAtividade = id
                search = client.service.consultarAtividades(filtro)
                deflator = search.item[0].listAtividade[0].deflator
                return deflator
            except:
                return 1.0
        return 1.0

    #def quantHST(self):
    #    pass

    def at_post_edit_script(self):
        self.SetQuantHST()

    def at_post_create_script(self):
        self.SetQuantHST()

    def SetQuantHST(self):
        complexidade = float(self.complexidade)
        multiplicador = float(self.multiplicador)
        if self.valor_deflator:
            valorDeflator = float(self.valor_deflator)
        else:
            valorDeflator = 1.0
        if self.deflator and self.federativo and self.reversa:
            totalHST = ((complexidade * 1.3) * multiplicador) * valorDeflator
        if self.deflator and not(self.federativo) and not(self.reversa):
            totalHST = ((complexidade * multiplicador) * valorDeflator) * 0.6
        if not(self.deflator) and not(self.federativo) and not(self.reversa):
            totalHST = (complexidade * multiplicador) * 0.6
        if self.deflator and self.federativo and not(self.reversa):
            totalHST = (complexidade * multiplicador) * valorDeflator
        if self.deflator and not(self.federativo) and self.reversa:
            totalHST = (((complexidade * 1.3) * multiplicador) * 0.6) * valorDeflator
        if not(self.deflator) and not(self.federativo) and self.reversa:
            totalHST = ((complexidade * 1.3) * multiplicador) * 0.6
        if not(self.deflator) and self.federativo and not(self.reversa):
            totalHST = (complexidade * multiplicador)
        if not(self.deflator) and self.federativo and self.reversa:
            totalHST = ((complexidade * 1.3) * multiplicador)
        self.quantHST = totalHST
        self.reindexObject(idxs='quantHST')

    def getOS(self):
        obj = self
        while True:
           obj = obj.aq_parent
           obj_type = obj.portal_type
           if obj.portal_type == 'Secao':
               break
        # import pdb; pdb.set_trace()
        # registry = getUtility(IRegistry)
        # settings = registry.forInterface(ICatalogoServicoPrefsForm)
        try:
            ordens_servicos = obj.lista_os
            #ordens_servicos = settings.ordem_servico
        except:
            ordens_servicos = tuple(' ')
        return ordens_servicos


atapi.registerType(Demanda, config.PROJECTNAME)
