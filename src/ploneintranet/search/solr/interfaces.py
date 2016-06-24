# -* coding: utf-8 -*-
from zope.interface import Interface
from zope import schema

from ploneintranet.core import ploneintranetCoreMessageFactory as _


class IConnectionConfig(Interface):
    """Represents details of a Solr connection."""

    host = schema.ASCIILine()
    port = schema.Int()
    basepath = schema.ASCIILine()
    core = schema.ASCIILine()
    url = schema.ASCIILine(
        description=_(u'The URL that will resolve to a SOLR core.')
    )


class IMaintenance(Interface):
    """Perform maintenance on the Solr server.

    Each method implemented here should communicate with
    the remote Solr instance, and perform some operation.

    All operations should be synchronous.
    """

    def build_spellchcker():
        """Build the Solr spell-checker."""

    def reindex_all():
        """Re-index all objects."""

    def sync():
        """Synchronize with portal_catalog."""


# Marker interfaces used to hook up scorched to the ZCA.

class IConnection(Interface):
    """Marker."""


class IQuery(Interface):
    """Marker."""


class IResponse(Interface):
    """Marker."""

    query_params = schema.Dict(
        description=u'Used to normalize spelling sugestions.',
        required=True)


class IContentAdder(Interface):
    """Marker."""


class ICheckIndexable(Interface):
    """ Check if an object is indexable """

    def __call__():
        """ Return `True`, if context is indexable and `False`otherwise
        """


class ISolrMaintenanceView(Interface):
    """ solr maintenance view for clearing, re-indexing content etc """

    def optimize():
        """ optimize solr indexes """

    def clear():
        """ clear all data from solr, i.e. delete all indexed objects """

    def reindex(batch=1000, skip=0):
        """ find all contentish objects (meaning all objects derived from one
            of the catalog mixin classes) and (re)indexes them """

    def sync(batch=1000):
        """ sync the solr index with the portal catalog;  records contained
            in the catalog but not in solr will be indexed and records not
            contained in the catalog can be optionally removed;  this can
            be used to ensure consistency between zope and solr after the
            solr server has been unavailable etc """

    def cleanup(batch=1000):
        """ remove entries from solr that don't have a corresponding Zope
            object  or have a different UID than the real object"""
