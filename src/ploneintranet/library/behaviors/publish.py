# -*- coding: utf-8 -*-
from plone.dexterity.interfaces import IDexterityContent
from Products.Five import BrowserView

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

    def can_publish_widely(self):
        return True


class PublishActionView(BrowserView):

    def __call__(self):
        self.update()
        return self.index()

    def update(self):
        pass

    def library_url(self):
        return 'FIXME'

    def copied_to_url(self):
        return 'FIXME'
