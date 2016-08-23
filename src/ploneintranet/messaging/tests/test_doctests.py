# -*- coding: utf-8 -*-
from plone.testing import layered
from ploneintranet.messaging.testing import \
    INTEGRATION_TESTING

import doctest
import unittest


tests = (
    'doctests.rst',
)


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
                 layer=INTEGRATION_TESTING)
            for f in tests]
    )
