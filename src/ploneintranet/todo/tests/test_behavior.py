# -*- coding: utf-8 -*-

from ploneintranet.todo.testing import IntegrationTestCase
from plone import api

from ploneintranet.todo.behaviors import IMustRead


class TestBehavior(IntegrationTestCase):
    """Test MustRead behavior."""

    def setUp(self):
        self.portal = self.layer['portal']

    def test_set_get(self):
        news = api.content.create(
            type='News Item',
            title='My news',
            container=self.portal)
        behavior = IMustRead(news)
        behavior.mustread = True
        self.assertTrue(behavior.mustread)
