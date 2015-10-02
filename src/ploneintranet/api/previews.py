# -*- coding: utf-8 -*-
''' Methods to generate and access preview images on content '''

from ploneintranet.docconv.client import previews


def get(obj, scale='normal'):
    """Get the preview images for the given object

    If there are currently no previews, an empty list will be returned

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: The preview images
    :rtype: list
    """
    return previews.get(obj, scale)


def has_previews(obj):
    """Test if the object has generated previews.

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: True if there are previews. False otherwise.
    :rtype: boolean
    """
    return previews.has_previews(obj)


def get_preview_urls(obj, scale='normal'):
    """Convenience method to get URLs of image previews as these are most
    frequently used

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :param scale: The Plone image scale to get preview images at
    :type scale: str
    :return: List of preview image absolute URLs
    :rtype: list
    """
    return previews.get_preview_urls(obj, scale)


def fallback_image(obj):
    """DEPRECATED: Return a fallback image for use if there are no previews.

    Prototype does not use fallback image anymore, instead offers css solution.

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: An image object
    :rtype: ZODB.blob.Blob
    """
    return previews.fallback_image(obj)


def fallback_image_url(obj):
    """DEPRECATED: Return a fallback image URL for use if there are no previews.

    Prototype does not use fallback image anymore, instead offers css solution.

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: An image object url
    :rtype: string
    """
    return previews.fallback_image_url(obj)


def get_thumbnail(obj):
    """Get the thumnail preview image for the given object

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: The preview thumbnail
    :rtype: ImageScaling
    """
    return previews.get_thumbnail(obj)


def get_thumbnail_url(obj, relative=False):
    """Convenience method to get the absolute URL of thumbnail image

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: The absolute URL to the thumbnail image
    :rtype: str
    """
    return previews.get_thumbnail_url(obj, relative)


def has_pdf(obj):
    """ NOT IMPLEMENTED. Once we do pdf generation for text content, this will work

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: True if there is a pdf available
    :rtype: boolean
    """
    return False


def get_pdf(obj):
    """ NOT IMPLEMENTED. Once we do pdf generation for text content, this will work

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: The generated pdf preview of the content item
    :rtype: Blob
    """
    return None


def generate_previews(obj, event=None):
    """ Generate the previews for a content type. We need our own subscriber as
    c.dv insists on checking for its custom layout. Also we want our own async
    mechanism, it is using this method.

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: Does not return anything.
    :rtype: None
    """
    previews.generate_previews(obj, event)
