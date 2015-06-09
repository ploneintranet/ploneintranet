# -*- coding: utf-8 -*-
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
    """Generate the preview images for the given content object

    :param obj: The Plone object to get previews for
    :type obj: A Plone content object
    :param request: The Plone request object
    :type request: HTTPRequest
    """
    pass
