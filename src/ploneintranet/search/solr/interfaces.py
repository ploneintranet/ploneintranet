from zope.interface import implementer, Interface
from zope import schema

from .. import _


class IBoostField(Interface):

    boost = schema.Int()


@implementer(IBoostField)
class BoostField(schema.Field):

    def __init__(self, boost=0, **kw):
        super(BoostField, self).__init__(**kw)
        self.boost = boost


def boost_field(schema_field_cls, boost=0):
    field_cls = type('BoostField', (BoostField, schema_field_cls), {})
    return field_cls(boost=boost)


class IConnectionConfig(Interface):
    """Represents a SOLR connection."""

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

    All operations should be synchronus.
    """

    def build_spellchcker():
        """Build the Solr spellchecker."""

    def reindex_all():
        """Re-index all objects."""

    def sync():
        """Synchronize with portal_catalog."""


class IQueryFields(Interface):

    Title = boost_field(schema.TextLine, boost=5)
    Description = boost_field(schema.TextLine, boost=3)
    SearchableText = boost_field(schema.Text, boost=2)


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
