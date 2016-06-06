# -*- coding: utf-8 -*-
import unittest2 as unittest
from ploneintranet.activitystream.browser import utils


text_with_links = "I want to link to http://ploneintranet.org or " \
    "https://plone.org in my text."  # noqa
text_with_links_replaced = "I want to link to " \
    """<a href="http://ploneintranet.org">"""\
    """http://ploneintranet.org</a> or <a href="https://plone.org">"""\
    """https://plone.org</a> in my text."""


class TestUtilityMethods(unittest.TestCase):
    """
    We define utility methods in various places in our code suite. Add tests
    for their basic functionality.

    See also layout/tests/test_utils
    """

    def test_link_urls(self):
        text = utils.link_urls(text_with_links)
        self.assertEquals(text, text_with_links_replaced)
