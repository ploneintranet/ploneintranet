import unittest

from ploneintranet.search.base import FEATURE_NOT_IMPLEMENTED


class FeatureTests(unittest.TestCase):

    def test_feature_not_implemented(self):
        self.assertFalse(FEATURE_NOT_IMPLEMENTED)
