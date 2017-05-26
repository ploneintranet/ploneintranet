# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.userprofile.browser.tiles.contacts_search import ContactsSearch  # noqa
from ploneintranet.userprofile.testing import PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING  # noqa
from ploneintranet.userprofile.tests.base import BaseTestCase


TEST_AVATAR_FILENAME = u'test_avatar.jpg'


class TestPersonalTasks(BaseTestCase):

    layer = PLONEINTRANET_USERPROFILE_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestPersonalTasks, self).setUp()
        self.login_as_portal_owner()
        username1 = 'johndoe'
        self.profile1 = api.content.create(
            container=self.profiles,
            type='ploneintranet.userprofile.userprofile',
            id=username1,
            username=username1,
            first_name='John',
            last_name='Doe',
        )
        api.content.transition(self.profile1, 'approve')
        self.profile1.reindexObject()
        pq = api.portal.get_tool('portal_quickinstaller')
        pq.installProducts(['ploneintranet.todo'])
        self.logout()

    def test_personal_task_allowed(self):
        ''' Check that we can create personal tasks
        '''
        self.login('johndoe')
        obj = api.content.create(
            title='Personal task',
            container=self.profile1,
            type='todo',
        )
        view = api.content.get_view('view', obj, self.request)
        self.assertIn('todo_view', repr(view))
