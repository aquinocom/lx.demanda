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


# lx.demanda imports
from lx.demanda.interfaces.contents import IDemanda
from lx.demanda.interfaces.interfaces import ICatalogoServicoPrefsForm


class DemandaView(BrowserView):
    """ view 
    """
