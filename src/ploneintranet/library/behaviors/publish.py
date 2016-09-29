# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent

from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


class IPublishWidely(Interface):
    """
    A behavior that allows an object to place a copy
    of itself in the Library.

    Note that not every object with this behavior necessarily
    is published widely. It's just enabled to do so if needed.
    """


@implementer(IPublishWidely)
@adapter(IDexterityContent)
class PublishWidely(object):

    def __init__(self, context):
        self.context = context
