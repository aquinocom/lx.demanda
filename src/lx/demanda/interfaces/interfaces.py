# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema

# Product imports
from lx.demanda import demandaMessageFactory as _


class ICatalogoServicoPrefsForm(Interface):
    """ A view para o formulário de preferências do webservice. """

    url_webservice = schema.TextLine(title=_(u'URL do webservice'),
                                    description=_(u"URL do WSDL."),
                                    required=True)

    ordem_servico = schema.Tuple(
        title=_(u'Ordens de Serviço'),
        description=_(u"Insira uma ordem de serviço por linha"),
        required=False,
        missing_value=None,
        default=(),
        value_type=schema.TextLine()
    )
