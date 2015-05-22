# -*- coding: utf-8 -*-

from plone import api
from plone.app.testing import TEST_USER_ID
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.lifecycleevent import ObjectModifiedEvent
import zope.event


class TestTodos(BaseTestCase):
    """Test Todo items in Case Workspaces"""

    def setUp(self):
        self.portal = self.layer['portal']
        obj = api.content.create(
            type='todo',
            title='todo1',
            container=self.portal,
        )
        obj.assignee = TEST_USER_ID
        event = ObjectModifiedEvent(obj)
        zope.event.notify(event)

        workspaces = api.content.create(
            type='ploneintranet.workspace.workspacecontainer',
            title='workspaces',
            container=self.portal,
        )
        self.case = api.content.create(
            type='ploneintranet.workspace.case',
            title='case',
            container=workspaces,
        )
        api.content.transition(self.case, 'transfer_to_department')

    def test_todo_reopen_earlier_milestone(self):
        case_todo = api.content.create(
            type='todo',
            title='case_todo',
            container=self.case,
            milestone='new',
        )
        api.content.transition(case_todo, 'finish')
        case_todo.reopen()
        self.assertEquals(
            self.portal.portal_workflow.getInfoFor(case_todo, 'review_state'),
            'open'
        )

    def test_todo_reopen_current_milestone(self):
        case_todo = api.content.create(
            type='todo',
            title='case_todo',
            container=self.case,
            milestone='in_progress',
        )
        api.content.transition(case_todo, 'finish')
        case_todo.reopen()
        self.assertEquals(
            self.portal.portal_workflow.getInfoFor(case_todo, 'review_state'),
            'open'
        )

    def test_todo_reopen_future_milestone(self):
        case_todo = api.content.create(
            type='todo',
            title='case_todo',
            container=self.case,
            milestone='archived',
        )
        api.content.transition(case_todo, 'finish')
        case_todo.reopen()
        self.assertEquals(
            self.portal.portal_workflow.getInfoFor(case_todo, 'review_state'),
            'planned'
        )
