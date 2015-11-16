from zope import schema
from zope.component.zcml import utility
from zope.interface import Interface

from .interfaces import IConnectionConfig
from .utilities import ConnectionConfig


class IConnectionConfigDirective(Interface):
    """Directive which registers a SOLR connection config"""

    host = schema.ASCIILine(
        title=u'Host',
        description=u'The host name of the SOLR instance to be used.',
        required=True,
    )

    port = schema.Int(
        title=u'Port',
        description=u'The port of the SOLR instance to be used.',
        required=True,
    )

    basepath = schema.ASCIILine(
        title=u'Base path',
        description=(
            u'The base prefix of the SOLR instance to be used -'
            u' this should start with a forward-slash'),
        required=True,
    )

    core = schema.ASCIILine(
        title=u'Core name',
        description=u'The name of the SOLR core to be used.',
        required=True,
    )


def configure_connection(_context, host, port, basepath, core):
    return utility(
        _context,
        provides=IConnectionConfig,
        component=ConnectionConfig(host, port, basepath, core))
