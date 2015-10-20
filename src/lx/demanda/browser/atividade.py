# -*- coding: utf-8 -*-

# Zope3 imports

# Product imports
from Products.Five.browser import BrowserView


class AtividadeView(BrowserView):
    """ view 
    """

    def getData(self, data):
        """
        """
        if data == 'inicio':
            try:
                date = self.context.data_inicio.strftime('%d/%m/%Y %H:%M')
            except:
                date = ''
        if data == 'fim':
            try:
                date = self.context.data_fim.strftime('%d/%m/%Y %H:%M')
            except:
                date = ''
        return date
