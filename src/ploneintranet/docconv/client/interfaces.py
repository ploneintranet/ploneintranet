# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface


class IPloneintranetDocconvClientLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IDocconv(Interface):
    """ """

    def has_pdf():
        """ """

    def has_previews():
        """ """

    def has_thumbs():
        """ """

    def conversion_message():
        """ """

    def get_pdf():
        """ """

    def get_previews():
        """ """

    def get_thumbs():
        """ """

    def generate_all():
        """ """


class IPreviewFetcher(Interface):
    """ Adapter that fetches preview images and pdf version for an object from
    the docconv service """

    def __call__():
        """ fetches everything and stores it in annotations on the object """
