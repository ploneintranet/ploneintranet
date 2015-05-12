# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import TEST_USER_ID
from ploneintranet.todo.behaviors import ITodo
from ploneintranet.todo.testing import IntegrationTestCase
from zope.lifecycleevent import ObjectModifiedEvent

import zope.event


class TestTodo(IntegrationTestCase):
    """Test Todo content type"""

    def setUp(self):
        self.portal = self.layer['portal']
        obj = api.content.create(
            type='todo',
            title='todo1',
            container=self.portal,
        )
        todo = ITodo(self.portal.todo1)
        todo.assignee = TEST_USER_ID
        event = ObjectModifiedEvent(obj)
        zope.event.notify(event)

    def test_assignee_role(self):
        todo = self.portal.todo1
        self.assertIn(
            'Assignee',
            api.user.get_roles(username=TEST_USER_ID, obj=todo)
        )
