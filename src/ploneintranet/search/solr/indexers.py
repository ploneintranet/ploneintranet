# -*- coding: utf-8 -*-
"""Index Plone contnet in Solr."""
import logging
from urllib import urlencode

from collective.indexing.interfaces import IIndexQueueProcessor
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer import indexer
from plone.indexer.interfaces import IIndexableObject
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.component import adapter, queryMultiAdapter, queryUtility
from zope.interface import implementer, Interface
import lxml.etree as etree
import requests

from .interfaces import IContentAdder, IConnectionConfig, IConnection
from .utilities import prepare_data


logger = logging.getLogger(__name__)


@implementer(IContentAdder)
@adapter(IDexterityContent, IConnection)
class ContentAdder(object):

    def __init__(self, context, solr):
        self.context = context
        self.solr = solr

    def add(self, data):
        self.solr.add(data)


@implementer(IContentAdder)
@adapter(IDexterityContent, IConnection)
class BinaryAdder(ContentAdder):

    @property
    def blob_data(self):
        pfi = IPrimaryFieldInfo(self.context, None)
        if pfi is not None:
            named_blob = pfi.field.get(self.context)
            if named_blob is not None:
                return named_blob.data
        return None

    def add(self, data):
        """Add documents to be indexed containing binary data.

        This uses Apache Tika `ExtractingRequestHandler` to upload
        binary data, and extract the textual representation of the
        binary data for indexing.

        :seealso:
          https://cwiki.apache.org/confluence/display/solr\
        /Uploading+Data+with+Solr+Cell+using+Apache+Tika

        :param data: The key/value data to index in Solr
        :type data: collections.Mapping
        :returns:
        """
        blob_data = self.blob_data
        if blob_data is not None:
            params = {}
            headers = {'Content-type': data.get('content_type', 'text/plain')}
            params['extractFormat'] = 'text'
            params['extractOnly'] = 'true'
            sparams = urlencode(params)
            url = '{}update/extract?{}'.format(self.solr.conn.url, sparams)
            try:
                response = requests.post(url, data=blob_data, headers=headers)
            except requests.ConnectionError as conn_err:
                logger.exception(conn_err)
            else:
                tree = etree.fromstring(response.text.encode('utf-8'))
                elems = tree.xpath('//response/str')
                if elems:
                    data['SearchableText'] = elems[0].text
                else:
                    logger.error(u'Failed to extract text from binary data '
                                 u'for file upload: %r', data)
        super(BinaryAdder, self).add(data)


@implementer(IIndexQueueProcessor)
class ContentIndexer(object):
    """Content indexing for Plone > SOLR."""

    _connection = None

    _solr_to_plone_field_mapping = {
        'tags': 'Subject'
    }

    _solr_only_attrs = frozenset({
        'default',
        '_version_'
    })

    def _encode_unicode(self, val):
        return val.encode('utf-8')

    def _encode_DateTime(self, val):
        return val.asdatetime()

    def _decode_object_value(self, val):
        """Dispatcher that will call any internal decoding routines."""
        val_type = type(val).__name__
        decode = getattr(self, '_encode_{}'.format(val_type), None)
        if decode is not None and callable(decode):
            return decode(val)
        return val

    def _add_mandatory_data(self, data):
        """Add `mandatory` data to the `data` to indexed by SOLR.

        Modifies `data` in place, in particular,
        to  ensure the `allowedRolesAndUsers` value is indexed.

        :param data: The data to be indexed.
        :type data: collections.MutableMapping
        """
        prepare_data(data)

    def _required_fields(self, schema):
        """Return a mapping of required field from the SOLR schema.

        :param schema: The SOLR schema mapping.
        :type schema: collections.MutableMapping
        """
        schema_fields = schema.get('fields', ())
        return {f['name'] for f in schema_fields if f.get('required')}

    def _data_attributes(self, schema, attributes):
        """Retrive the set of attribute names that should be index.

        The attributes returned will be used to get values from
        the (indexble-wrapped) Plone content object.

        :param schema: The SOLR schema mapping.
        :type schema: collections.MutableMapping
        :param attributes: Optional sequence of SOLR attributes names.
        :type attributes: collections.Sequence
        """
        schema_fields = schema.get('fields', [])
        fielddef_map = {fdef['name']: fdef for fdef in schema_fields}

        # SOLR now supports partial updates.
        # If we are asked to index only a single attribute, that's fine.
        attr_names = set(fielddef_map)
        if attributes is None:
            attributes = attr_names
        else:
            attr_names &= set(attributes)

        # If no matching attributes found, bail out here
        # (nothing to update in solr)
        if not attr_names:
            return []

        # The uniqueKey must be present in the payload sent to SOLR
        # Ensure the unique key is always supplied.
        unique_key = schema.get('uniqueKey')
        if unique_key is None:
            raise EnvironmentError(
                'Solr schema missing required `uniqueKey`'
            )
        attr_names.add(unique_key)

        # Remove attributes that should never exist on a Plone object.
        attr_names -= self._solr_only_attrs
        return attr_names

    def _indexable_wrapper(self, obj):
        """Adapt the content object in the usual Plone way to access indexable values.

        :param obj: The content object.
        :type obj: Products.CMFPlone.interfaces.ICatalogAware
        :returns: The adapted object.
        :rtype: plone.indexer.interfaces.IIndexableObject
        """
        # We use getToolByName here rather than plone.api
        # so that we rely on the explicit context of the obj we are
        # indexing, rather than plone.api's magic context
        portal_catalog = getToolByName(obj, 'portal_catalog')
        return queryMultiAdapter((obj, portal_catalog), IIndexableObject)

    def _get_value_for_indexable_object(self, iobj, attr_name):
        """Attempt to get the value for SOLR attribute name  the content object.

        If any mapping from SOLR name to Plone name is required,
        this should be done here.

            1. Normal attribute lookup
            2. Calling any accessors as are necsesary.

        Finally, we decode retrieved value from content object,
        suitable for the type configured for the attribute in the SOLR
        schema.

        :param iobj: The indexable content object.
        :type iobj: plone.indexer.interfaces.IIndexableObject
        :param attr_name: The name of the attribute.
        :type attr_name: str
        :returns: The attribute value.
        :rtype: object
        """
        if attr_name in self._solr_to_plone_field_mapping:
            iobj_attr_name = self._solr_to_plone_field_mapping[attr_name]
        else:
            iobj_attr_name = attr_name
        val = getattr(iobj, iobj_attr_name, None)
        if callable(val):
            val = val()
        return self._decode_object_value(val)

    def _get_data(self, obj, attributes=None):
        """Get the data to index into SOLR.

        :obj: The Plone content object.
        :type obj: Products.CMFPlone.interfaces.IContentish
        :returns: A data mapping suitable for sending to SORL.
        :rtype data: collections.MutableMapping
        """
        data = {}
        iobj = self._indexable_wrapper(obj)
        schema = self._solr.schema
        attr_names = self._data_attributes(schema, attributes)
        if not attr_names:
            # No attributes matched - nothing to do
            logger.warn('No solr fields to update')
            return None

        for attr_name in attr_names:
            val = self._get_value_for_indexable_object(iobj, attr_name)
            data[attr_name] = val
            logger.debug(
                'Decoded %r from original value %r to  %r',
                attr_name, val, data[attr_name]
            )
        self._add_mandatory_data(data)
        required_fields = self._required_fields(schema)
        missing = required_fields - set(data)
        if missing:
            logger.warn('Missing required fields: %r', missing)
            return None
        return data

    @property
    def _solr_conf(self):
        return queryUtility(IConnectionConfig)

    @property
    def _solr(self):
        if self._connection is None:
            self._connection = IConnection(self._solr_conf)
        return self._connection

    def abort(self):
        self._solr.rollback()

    def begin(self):
        pass

    def commit(self):
        self._solr.commit(waitSearcher=None, expungeDeletes=True)
        # TODO: Too expensive to do this every time?
        # when do we optimize (and re-build the spellcheker) ?
        self._solr.optimize(waitSearcher=None)

    def index(self, obj, attributes=None):
        """Index the object.

        """
        data = self._get_data(obj, attributes=attributes)
        if data is not None:
            portal_type = data.get('portal_type', 'default')
            adder = queryMultiAdapter((obj, self._solr), name=portal_type)
            if adder is None:
                adder = ContentAdder(obj, self._solr)
            adder.add(data)

    def reindex(self, obj, attributes=None):
        self.index(obj, attributes)

    def unindex(self, obj):
        if hasattr(obj, 'context'):
            obj = obj.context
        schema = self._solr.schema
        unique_key = schema['uniqueKey']
        data = self._get_data(obj, attributes=[unique_key])
        if data is None:
            return None
        if unique_key not in data:
            raise EnvironmentError('Missing unique key in schema/data')
        self._solr.delete_by_ids(data[unique_key])


@indexer(Interface)
def path_string(obj, **kwargs):
    """Return the physical path as a string."""
    return '/'.join(obj.getPhysicalPath())


@indexer(Interface)
def path_depth(obj, **kwargs):
    """Return the depth of the physical path to the object."""
    return len('/'.join(obj.getPhysicalPath()))


@indexer(Interface)
def path_parents(obj, **kwargs):
    """Return all parent paths leading up to the object."""
    elements = obj.getPhysicalPath()
    return ['/'.join(elements[:n + 1]) for n in xrange(1, len(elements))]
