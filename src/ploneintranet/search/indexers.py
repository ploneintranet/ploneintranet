import logging

from Products.CMFCore.interfaces import IContentish
from Products.MimetypesRegistry import MimeTypeException
from plone import api
from plone.app.contenttypes.interfaces import IFile
from plone.indexer import indexer
from plone.rfc822.interfaces import IPrimaryFieldInfo

from ploneintranet.userprofile.content.userprofile import IUserProfile


logger = logging.getLogger(__name__)


@indexer(IContentish)
def friendly_type_name(obj):
    """Index for the friendly name of any content type.

    :param obj: The Plone content object to index
    :type obj: IContentish
    :return: Friendly content type name
    :rtype: str
    """
    default_name = obj.Type()
    # If the object is a file get the friendly name of the mime type
    if IFile.providedBy(obj):
        mtr = api.portal.get_tool(name='mimetypes_registry')

        primary_field_info = IPrimaryFieldInfo(obj)
        if not primary_field_info.value:
            return default_name

        if hasattr(primary_field_info.value, 'contentType'):
            contenttype = primary_field_info.value.contentType
            try:
                mimetypeitem = mtr.lookup(contenttype)
            except MimeTypeException as msg:
                logger.warn(
                    'mimetype lookup failed for %s. Error: %s',
                    obj.absolute_url(),
                    str(msg)
                )
                return default_name

            mimetype_name = mimetypeitem[0].name()
            if mimetype_name != contenttype:
                return mimetype_name
    elif IUserProfile.providedBy(obj):
        return 'Person'

    return default_name
