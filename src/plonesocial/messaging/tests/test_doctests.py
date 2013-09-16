import doctest
import unittest

from plone.testing import layered
from plonesocial.messaging.testing import \
    PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING


tests = (
    '../../../../README.rst',
)


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
                 layer=PLONESOCIAL_MESSAGING_FUNCTIONAL_TESTING)
            for f in tests]
    )
