# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.microblog.browser.interfaces import (
    IPloneIntranetMicroblogLayer)
from ploneintranet.activitystream.browser.interfaces import (
    IPloneIntranetActivitystreamLayer
)
import ploneintranet.microblog.statuscontainer
from ploneintranet.microblog.tool import MicroblogTool
from ploneintranet.microblog.testing import (
    PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING
)
from ploneintranet.microblog.statusupdate import StatusUpdate
from zope.interface import alsoProvides
import unittest2 as unittest


class TestSetup(unittest.TestCase):

    layer = PLONEINTRANET_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneIntranetActivitystreamLayer)
        alsoProvides(self.request, IPloneIntranetMicroblogLayer)
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 0

    def tearDown(self):
        ploneintranet.microblog.statuscontainer.MAX_QUEUE_AGE = 1000

    def test_newpostbox_tile_on_portal(self):
        ''' This will test the existence of the newpostbox.tile
        and its functionality
        '''
        tile = api.content.get_view(
            'newpostbox.tile',
            self.portal,
            self.request
        )
        # we have a post container which is the microblog tool
        self.assertIsInstance(tile.post_container, MicroblogTool)
        # we dont' have a post context
        self.assertEqual(tile.post_context, None)
        # we have an attachment form token
        self.assertRegexpMatches(
            tile.attachment_form_token,
            'test-user-([0-9]*)'
        )
        # we are not posting
        self.assertEqual(tile.is_posting, False)
        self.assertEqual(tile.post_text, u'')
        self.assertEqual(tile.post_attachment, None)
        # calling update does not create a post
        tile.update()
        self.assertEqual(tile.post, None)
        # check if we render correctly
        self.assertIn('form id="post-box"', tile())

    def test_newpostbox_tile_submission_on_portal(self):
        ''' This will test the existence of the newpostbox.tile
        and its functionality
        '''
        request = self.request.clone()
        request.form.update({
            'form.widgets.text': u'Testing post',
            # 'form.widgets.attachments': u'No attachments',
            'form.buttons.statusupdate': '1'
        })
        request.other['ACTUAL_URL'] = 'http://nohost'

        tile = api.content.get_view(
            'newpostbox.tile',
            self.portal,
            request
        )
        # we are not posting
        self.assertEqual(tile.is_posting, True)
        self.assertEqual(tile.post_text, u'Testing post')
        # self.assertEqual(tile.post_attachment, u'No attachments')
        # calling update creates a post
        tile.update()
        self.assertIsInstance(tile.post, StatusUpdate)
