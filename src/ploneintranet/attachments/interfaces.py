# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface


class IPloneintranetAttachmentsLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IAttachmentInfo(Interface):
    """Interface for helper view to get attachment information"""

    def get_attachment_ids():
        """Get the list of ids of all attachments of the context"""
        pass
