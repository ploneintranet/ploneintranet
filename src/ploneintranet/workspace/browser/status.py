# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ploneintranet.workspace.workspacefolder import IWorkspaceFolder
from plonesocial.microblog.browser.interfaces import IPlonesocialMicroblogLayer
from plonesocial.microblog.browser.interfaces import IStatusProvider
from plonesocial.microblog.browser.status import StatusProvider
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IStatusProvider)
@adapter(IWorkspaceFolder, IPlonesocialMicroblogLayer, Interface)
class WSStatusProvider(StatusProvider):
    '''
    status form provider to be used on a statusupdate for a workspace
    '''
    index = ViewPageTemplateFile('templates/status.pt')
