# -*- coding: utf-8 -*-

# Zope3 imports
from zope.interface import implements
# Security
from AccessControl import ClassSecurityInfo

# Archetypes & ATCT imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

# Product imports
from lx.demanda import demandaMessageFactory as _
from lx.demanda.interfaces.contents import IAtividade
from lx.demanda import config

# Schema definition
schema = ATCTContent.schema.copy() + atapi.Schema((
    atapi.StringField(
        name='projeto',
        required=False,
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u"Projeto"),
            description=_(u"Nome do projeto"),
            size=30,)
    ),

    atapi.DateTimeField(
        name='data_inicio',
        required=False,
        searchable=True,
        widget=atapi.CalendarWidget(
            label=_(u'Data de início'),
        ),
    ),

    atapi.DateTimeField(
        name='data_fim',
        required=False,
        searchable=True,
        widget=atapi.CalendarWidget(
            label=_(u'Data de conclusão'),
        ),
    ),

    atapi.FloatField(
        name='duracao',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u"Duração"),
            description=_(u"Duração em horas da atividade."),
            size=10,)
    ),

    atapi.FloatField(
        name='quantHST',
        required=True,
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u"QTDE de HST"),
            size=10,)
    ),

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

),)

schema['description'].widget.visible['edit'] = 'invisible'
schema['excludeFromNav'].default = True

schemata.finalizeATCTSchema(schema)


class Atividade(ATCTContent, HistoryAwareMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(IAtividade)

    meta_type = 'Atividade'
    portal_type = 'Atividade'

    _at_rename_after_creation = True
    schema = schema

atapi.registerType(Atividade, config.PROJECTNAME)
