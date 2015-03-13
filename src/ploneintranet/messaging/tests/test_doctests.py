# -*- coding: utf-8 -*-
from plone.testing import layered
from ploneintranet.messaging.testing import \
    PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING

import doctest
import unittest


tests = (
    'doctests.rst',
)


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
                 layer=PLONEINTRANET_MESSAGING_FUNCTIONAL_TESTING)
            for f in tests]
    )
