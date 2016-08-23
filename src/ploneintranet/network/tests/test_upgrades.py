# -*- coding: utf-8 -*-
from mock import patch
import unittest2 as unittest
from ploneintranet.network.graph import NetworkGraph
from ploneintranet.network.upgrades import upgrade_to_0003


class TestUpgrades(unittest.TestCase):

    def test_to_0003(self):
        ''' Check that the network graph is fixed by this upgrade
        '''
        # Remove from ng tool the attributes added in version 0003
        ng = NetworkGraph()
        delattr(ng, '_bookmarks')
        delattr(ng, '_bookmarked')

        # the storages for bookmarks are no longer there
        # as it was up to version 0002
        with self.assertRaises(AttributeError):
            ng._bookmarks
            ng._bookmarked

        with patch('plone.api.portal.get_tool', return_value=ng):
            upgrade_to_0003(None)

        # the storages for bookmarks are back again
        for item_type in ng.supported_bookmark_types:
            self.assertTupleEqual(tuple(ng._bookmarks[item_type].keys()), ())
            self.assertTupleEqual(tuple(ng._bookmarked[item_type].keys()), ())
