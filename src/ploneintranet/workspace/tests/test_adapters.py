# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.workspace.browser.status import WSStatusProvider
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from plonesocial.microblog.browser.interfaces import IPlonesocialMicroblogLayer


class TestAdapters(BaseTestCase):

    def test_status_update(self):
        """
        We need a workspace folder
        We want to make sure the adapter registered for it
        is correctly picked up
        """
        workspace_folder = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )

        request = self.request.clone()
        alsoProvides(request, IPlonesocialMicroblogLayer)
        provider = getMultiAdapter(
            (workspace_folder, request, self),
            name='plonesocial.microblog.status_provider'
        )
        self.assertIsInstance(provider, WSStatusProvider)
