# -*- coding: utf-8 -*-
from plone.testing import layered
from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING

import doctest
import unittest


tests = (
    '../../../../README.rst',
)


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
                 layer=PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING)
            for f in tests]
    )
