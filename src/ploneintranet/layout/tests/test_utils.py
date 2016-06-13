# -*- coding: utf-8 -*-
import unittest2 as unittest
from ploneintranet.layout import utils


string_with_unicode = "This is a ∞ string that contains non-ascii"
string_with_unicode_shortened = u"This is a ∞ string …"
unicode_string = u"I ♡ unicode with all my heart "
unicode_string_shortened = u"I ♡ unicode with …"


class TestUtilityMethods(unittest.TestCase):
    """
    We define utility methods in various places in our code suite. Add tests
    for their basic functionality.

    See also activitystream/tests/test_utils
    """

    def test_text_shortener(self):
        text = utils.shorten(string_with_unicode, 20)
        self.assertEquals(text, string_with_unicode_shortened)
        text = utils.shorten(unicode_string, 20)
        self.assertEquals(text, unicode_string_shortened)
