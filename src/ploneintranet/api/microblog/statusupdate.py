# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import datetime
from plone import api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate
from zope.component import queryUtility


def get(status_id):
    """Get a status update by id.

    :param status_id: The id of the status update
    :type status_id: int
    :returns: The matching StatusUpdate
    :rtype: StatusUpdate
    """
    microblog = queryUtility(IMicroblogTool)
    return microblog.get(status_id)


def create(
    text,
    microblog_context=None,
    thread_id=None,
    mention_ids=None,
    tags=None,
    user=None,
    userid=None,
    time=None,
    content_context=None,
):
    """Create a status update (post).

    :param text: [required] text of the post
    :type text: Unicode object

    :param microblog_context: Container of the post
    :type microblog_context: Content object

    :param user: User who should post. By default the current user posts.
    :type user: user object

    :param userid: userid of the user who should post.
    :type userid: string

    :param time: time when the post should happen. By default the current time.
    :type time: datetime object

    :param content_context: a content referenced we are talking about
    :type content_context: content object

    :returns: Newly created statusupdate
    :rtype: StatusUpdate object
    """
    status_obj = StatusUpdate(
        text=text,
        microblog_context=microblog_context,
        thread_id=thread_id,
        mention_ids=mention_ids,
        tags=tags,
        content_context=content_context,
    )
    # By default the post is done by the current user
    # Passing a userid or user allows to post as a different user
    if user is None and userid is not None:
        user = api.user.get(userid=userid)
    if user is not None:
        status_obj.userid = user.getId()
        status_obj.creator = user.getUserName()

    # By default the post happens now
    # Passing a time (as a datetime-object) the id and the date can be set
    if time is not None:
        assert(isinstance(time, datetime))
        delta = time - datetime.utcfromtimestamp(0)
        status_obj.id = long(delta.total_seconds() * 1e6)
        status_obj.date = DateTime(time)

    microblog = queryUtility(IMicroblogTool)
    microblog.add(status_obj)
    # take care - statusupdate may still be queued for storage
    # and not actually written into the container yet
    # this may change the status_obj.id
    return status_obj
