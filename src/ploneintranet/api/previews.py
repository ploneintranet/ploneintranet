# -*- coding: utf-8 -*-
from plone import api

from ploneintranet.async.celerytasks import generate_and_add_preview


def get(obj):
    """Get the preview images for the given object

    If there are currently no previews an empty list will be returned

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: The preview images
    :rtype: list
    """
    return []


def create(obj, request):
    """Generate the preview images and preview thumbnail for the given content
    object

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :param request: The Plone request object
    :type request: HTTPRequest
    """
    kwargs = dict(
        url=obj.absolute_url(),
        cookies=request.cookies
    )

    generate_and_add_preview.apply_async(
        countdown=10,
        kwargs=kwargs,
    )


def get_thumb(obj):
    """Get the thumnail preview image for the given object

    If there is no thumbnail None will be returned

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: The preview thumbnail
    :rtype: NamedBlobFile ??
    """
    return None


def has_thumb(obj):
    """Does this item have a preview thumbnail

    :return: Whether or not the given content object has a preview thumbnail
    :rtype: bool
    """
    return bool(get_thumb(obj))


def has_previews(obj):
    """Does this item have preview images

    :return: Whether or not the given content object has preview thumbnails
    :rtype: bool
    """
    return bool(get(obj))


def get_preview_urls(obj):
    """Get URLs to the preview images to the given content object

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: List of URLs to the preview images
    :rtype: list
    """
    previews = get(obj)
    images = api.content.get_view(
        'images',
        previews[0],
        obj.request,
    )
    urls = [images.scale(scale='preview').absolute_url()]
    return urls
