# -*- coding: utf-8 -*-

# Zope3 imports
from zope.interface import implements
from zope.component import getUtility
# Security
from AccessControl import ClassSecurityInfo

# Archetypes & ATCT imports
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

#Libs

# Product imports
from lx.demanda import demandaMessageFactory as _
from lx.demanda.interfaces.contents import ISecao
from lx.demanda import config

# Schema definition
schema = ATFolder.schema.copy() + atapi.Schema((
    atapi.LinesField(
        name='lista_os',
        required=False,
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u"Lista de OS"),
            description=_(u"Lista de OS"),
            size=10,)
    ),
),)

schemata.finalizeATCTSchema(schema)


class Secao(ATFolder, HistoryAwareMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(ISecao)

    meta_type = 'Secao'
    portal_type = 'Secao'

    _at_rename_after_creation = True
    schema = schema

atapi.registerType(Secao, config.PROJECTNAME)
