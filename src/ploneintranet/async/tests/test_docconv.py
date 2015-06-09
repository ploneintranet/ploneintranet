from subprocess import CalledProcessError
from zope.component import getMultiAdapter

from ..browser.docconv import _parse_cmd_output
from ..testing import IntegrationTestCase


class TestDocconv(IntegrationTestCase):
    """
    Tests for the docconv browser view
    """

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.view = getMultiAdapter((self.portal, self.request),
                                    name='convert-document')

    def test__parse_cmd_output(self):
        cmd = ['uname', '-a']
        parsed = _parse_cmd_output(cmd)
        self.assertIsInstance(parsed, list)

        cmd = ['not-a-command']
        with self.assertRaises(OSError):
            _parse_cmd_output(cmd)

        cmd = ['ps', '-quux']
        with self.assertRaises(CalledProcessError):
            _parse_cmd_output(cmd)
