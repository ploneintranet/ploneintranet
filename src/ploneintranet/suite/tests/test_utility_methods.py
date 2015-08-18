# -*- coding: utf-8 -*-
import unittest2 as unittest
from ploneintranet.core.browser import utils as core_utils
from ploneintranet.layout import utils as layout_utils


text_with_links = "I want to link to http://ploneintranet.org or " \
    "https://plone.org in my text."  # noqa
text_with_links_replaced = "I want to link to " \
    """<a href="http://ploneintranet.org">"""\
    """http://ploneintranet.org</a> or <a href="https://plone.org">"""\
    """https://plone.org</a> in my text."""

string_with_unicode = "This is a ∞ string that contains non-ascii"
string_with_unicode_shortened = u"This is a ∞ string …"
unicode_string = u"I ♡ unicode with all my heart "
unicode_string_shortened = u"I ♡ unicode with …"


class TestUtilityMethods(unittest.TestCase):
    """
    We define utility methods in various places in our code suite. Add tests
    for their basic functionality.
    """

    def test_link_urls(self):
        text = core_utils.link_urls(text_with_links)
        self.assertEquals(text, text_with_links_replaced)

    def test_text_shortener(self):
        text = layout_utils.shorten(string_with_unicode, 20)
        self.assertEquals(text, string_with_unicode_shortened)
        text = layout_utils.shorten(unicode_string, 20)
        self.assertEquals(text, unicode_string_shortened)
