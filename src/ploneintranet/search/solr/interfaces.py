# -* coding: utf-8 -*-
from zope.interface import Interface
from zope import schema

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa


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
