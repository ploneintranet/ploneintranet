# -*- coding: utf-8 -*-
from plone import api

from ploneintranet.async.celerytasks import generate_and_add_preview, app
from . import attachments


def get(obj):
    """Get the preview images for the given object

    If there are currently no previews an empty list will be returned

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: The preview images
    :rtype: list
    """
    return attachments.get_attachments(obj, 'preview')


def get_previews(obj, scale='preview'):
    """Get preview images to the given content object

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :param request: The Plone request object
    :type request: HttpRequest
    :param scale: The ImageScaling scale name
    :type scale: str
    :return: List of `ImageScaling` objects
    :rtype: list
    """
    previews = []
    portal = api.portal.get()
    for image in get(obj):
        previews.append(
            api.content.get_view(
                'images',
                image,
                portal.REQUEST,
            ).scale(fieldname='image', scale=scale)
        )
    return previews


def get_preview_urls(obj, scale='preview'):
    """Convenience method to get URLs of image previews as these are most
    frequently used

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :param scale: The Plone image scale to get preview images at
    :type scale: str
    :return: List of preview image absolute URLs
    :rtype: list
    """
    number_of_previews = len(get(obj))

    # If there aren't any previews, return the placeholder url
    if number_of_previews < 1:
        return [fallback_image_url()]
    return ['{0}/@@preview?page={1}&scale={2}'.format(obj.absolute_url(),
                                                      x,
                                                      scale)
            for x in range(1, number_of_previews + 1)
            ]


def fallback_image_url():
    return '{0}/++theme++ploneintranet.theme/generated/media/logo.svg'.format(
        api.portal.get().absolute_url())


def get_thumbnail(obj):
    """Get the thumnail preview image for the given object

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :return: The preview thumbnail
    :rtype: ImageScaling
    """
    previews = get_previews(obj, scale='thumb')
    if len(previews) < 1:
        return fallback_image_url()
    return previews[0]


def get_thumbnail_url(obj):
    """Convenience method to get the absolute URL of thumbnail image

    :param obj: The Plone content object to get preview URLs for
    :type obj: A Plone content object
    :return: The absolute URL to the thumbnail image
    :rtype: str
    """
    return '{}/@@thumbnail'.format(
        obj.absolute_url(),
    )


def create(obj, request):
    """Generate the preview images and preview thumbnail for the given content
    object

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :param request: The Plone request object
    :type request: HTTPRequest
    """
    if app.conf.get('CELERY_ALWAYS_EAGER', False):
        # If we're running synchronously, call the Plone view directly
        view = api.content.get_view(
            'generate-previews',
            obj,
            request
        )
        view()
    else:
        # Otherwise call the Celery task
        kwargs = dict(
            url=obj.absolute_url(),
            cookies=request.cookies
        )
        generate_and_add_preview.apply_async(
            countdown=10,
            kwargs=kwargs,
        )
