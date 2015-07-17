# -*- coding: utf-8 -*-
"""Init and utils."""
from zope.i18nmessageid import MessageFactory

# Set up the i18n message factory for our package
_ = MessageFactory('ploneintranet')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
