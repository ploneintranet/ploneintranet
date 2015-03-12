# -*- coding: utf-8 -*-
import unittest
from ploneintranet.documentviewer.testing import \
    PLONEINTRANET_documentviewer_INTEGRATION_TESTING
from ..decorators import maybe_async


@maybe_async
def myTask(log, a, b):
    log.append(a / b)


class TestSync(unittest.TestCase):

    layer = PLONEINTRANET_documentviewer_INTEGRATION_TESTING

    def setUp(self):
        self.log = []

    def testSync(self):
        myTask(self.log, 10, 2)
        self.assertEqual(len(self.log), 1)
