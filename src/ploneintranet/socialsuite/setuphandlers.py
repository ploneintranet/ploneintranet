import os
import random
from DateTime import DateTime
import time
import loremipsum
import transaction

from zope.component import queryUtility
from zope.interface import alsoProvides
from OFS.Image import Image
from Products.PlonePAS.utils import scale_image
from Products.CMFCore.utils import getToolByName
from plone import api

from ploneintranet.network.interfaces import INetworkGraph
from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate


def demo(context):

    if context.readDataFile('ploneintranet.socialsuite_demo.txt') is None:
        return

    portal = site = context.getSite()
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
    testusers = ['clare_presler', 'kurt_silvio']
    graph.follow("user", testusers[0], testusers[1])
    # give clare som extra followers
    for fan in ['christian_stoner', 'guy_hachey', 'jamie_jacko']:
        graph.follow("user", testusers[0], fan)
    # fully random followers
    for i in xrange(100):
        followee = random.choice(users)
        follower = random.choice(users)
        if followee in testusers or follower in testusers \
                or followee == follower:
            continue
        else:
            graph.follow("user", followee, follower)

    # setup publicly accessible folder and document
    portal.invokeFactory('Folder', 'public', title=u"Public Folder")
    public = portal['public']
    public.invokeFactory('Document', 'd1', title=u"Public Document")

    # create and fill a local IMicroblogContext workspace
    workspace_users = ['clare_presler',
                       'dollie_nocera',
                       'esmeralda_claassen',
                       'pearlie_whitby']
    if 'workspace' not in portal:
        portal.invokeFactory('Folder', 'workspace',
                             title=u"Secure Workspace")
        # enable local microblog
        alsoProvides(portal.workspace, IMicroblogContext)
        # in testing we don't have the 'normal' default workflow
        workflowTool = getToolByName(portal, 'portal_workflow')
        if workflowTool.getInfoFor(portal.workspace,
                                   'review_state') != 'private':
            workflowTool.doActionFor(portal.workspace, 'hide')
        # share workspace with some users
        for userid in workspace_users:
            api.user.grant_roles(username=userid,
                                 obj=portal.workspace,
                                 roles=['Contributor', 'Reader', 'Editor'])
        # update object_provides + workflow state + sharing indexes
        portal.workspace.reindexObject()

    # microblog random loremipsum
    # prepare microblog
    microblog = queryUtility(IMicroblogTool)
    microblog.clear()  # wipe all
    tags = ("hr", "marketing", "fail", "innovation", "learning", "easy",
            "newbiz", "conference", "help", "checkthisout")
    for i in xrange(100):
        # select random user
        userid = random.choice(users)
        # generate text
        text = " ".join(loremipsum.get_sentences(3))
        if random.choice((True, False)):
            text += " #%s" % random.choice(tags)
        if userid in workspace_users:
            # workspace
            status = StatusUpdate(
                text,
                microblog_context=portal.workspace,
                tags=['girlspace']
            )
        else:
            # global
            status = StatusUpdate(text)
        status.userid = userid
        status.creator = " ".join([x.capitalize() for x in userid.split("_")])
        # distribute most over last week
        if i < 90:
            offset_time = random.random() * 3600 * 24 * 7
            status.id -= int(offset_time * 1e6)
            status.date = DateTime(time.time() - offset_time)
        microblog.add(status)

    # microblog deterministic test content most recent
    # workspace
    t0 = ('Workspaces can have local microblogs and activitystreams. '
          'Local activitystreams show only local status updates. '
          'Microblog updates will show globally only for users who '
          'have the right permissions. This demo has a #girlspace workspace.')
    s0 = StatusUpdate(
        t0,
        microblog_context=portal.workspace,
        tags=['girlspace']
    )
    s0.userid = workspace_users[0]  # clare
    s0.creator = " ".join([x.capitalize() for x in s0.userid.split("_")])
    microblog.add(s0)
    # global
    t1 = ('The "My Network" section only shows updates '
          'of people you are following.')
    s1 = StatusUpdate(t1)
    s1.userid = testusers[0]  # clare
    s1.creator = " ".join([x.capitalize() for x in s1.userid.split("_")])
    microblog.add(s1)
    t2 = 'The "Explore" section shows all updates of all people.'
    s2 = StatusUpdate(t2)
    s2.userid = testusers[1]  # kurt
    s2.creator = " ".join([x.capitalize() for x in s2.userid.split("_")])
    microblog.add(s2)
    t3 = 'The #demo hashtag demonstrates that you can filter on topic'
    s3 = StatusUpdate(t3, tags=['demo'])
    s3.userid = s2.userid  # kurt
    s3.creator = s2.creator
    microblog.add(s3)

    # commit
    microblog.flush_queue()
    transaction.commit()

    # testing.py provides additional content
