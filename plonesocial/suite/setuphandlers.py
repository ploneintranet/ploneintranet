import os
import random
from DateTime import DateTime
import time
import loremipsum

from zope.component import queryUtility
from OFS.Image import Image
from Products.PlonePAS.utils import scale_image
from Products.CMFCore.utils import getToolByName
from plone import api


from plonesocial.network.interfaces import INetworkGraph
from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.statusupdate import StatusUpdate


def importVarious(context):

    if context.readDataFile('plonesocial.suite_various.txt') is None:
        return

    site = context.getSite()
    site.layout = "activitystream_portal"
    site.default_page = "activitystream_portal"


def demo(context):

    if context.readDataFile('plonesocial.suite_demo.txt') is None:
        return

    site = context.getSite()
    avatar_path = os.path.join(context._profile_path, 'avatars')

    # create users
    users = []
    for file_name in os.listdir(avatar_path):
        userid = str(file_name.split('.')[0])
        users.append(userid)
        properties = dict(
            fullname=" ".join([x.capitalize() for x in userid.split("_")]),
            location=random.choice(
                ("New York", "Chicago", "San Francisco",
                 "Paris", "Amsterdam", "Zurich")),
            description=" ".join(loremipsum.get_sentences(2)))
        try:
            api.user.create(email='%s@demo.com' % userid,
                            username=userid,
                            password='secret',
                            properties=properties)
        except ValueError:
            user = api.user.get(username=userid)
            user.setMemberProperties(properties)

        portrait = context.openDataFile(file_name, 'avatars')
        scaled, mimetype = scale_image(portrait)
        portrait = Image(id=userid, file=scaled, title='')
        memberdata = getToolByName(site, 'portal_memberdata')
        memberdata._setPortrait(portrait, userid)

    # setup social network
    graph = queryUtility(INetworkGraph)
    graph.clear()
    for i in xrange(25):
        followee = random.choice(users)
        follower = random.choice(users)
        if followee != follower:
            graph.set_follow(follower, followee)

    # microblog
    microblog = queryUtility(IMicroblogTool)
    microblog.clear()  # wipe all
    tags = ("hr", "marketing", "fail", "innovation", "learning", "easy",
            "newbiz", "conference", "help", "checkthisout")
    for i in xrange(100):
        text = " ".join(loremipsum.get_sentences(3))
        if random.choice((True, False)):
            text += " #%s" % random.choice(tags)
        status = StatusUpdate(text)
        # assign to random user
        userid = random.choice(users)
        status.userid = userid
        status.creator = " ".join([x.capitalize() for x in userid.split("_")])
        # distribute over last week
        offset_time = random.random() * 3600 * 24 * 7
        status.id -= int(offset_time * 1e6)
        status.date = DateTime(time.time() - offset_time)
        microblog.add(status)
    microblog.flush_queue()
