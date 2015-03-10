from datetime import datetime, timedelta
from DateTime import DateTime
import os
import csv
import logging
import json
import time
import mimetypes
from DateTime import DateTime
from zope.component import queryUtility
from collective.workspace.interfaces import IWorkspace
from plone import api
from OFS.Image import Image
from Products.PlonePAS.utils import scale_image
from ploneintranet.todo.behaviors import ITodo
from ploneintranet.attachments.attachments import IAttachmentStorage
from ploneintranet.attachments.utils import create_attachment
from plonesocial.network.interfaces import INetworkGraph
from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.statusupdate import StatusUpdate


def decode(value):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    return value


def create_users(context, users, avatars_dir):
    """Creates user from the given list of dictionaries.

    ``context`` is the step context.

    ``users`` is a list of dictionaries each containing the following keys:

      * userid
      * fullname
      * email
      * location
      * description
      * follows (a list of userids followed)

    ``avatars_dir`` is a directory where for each userid
    there is a ``$userid.jpg`` file.
    """
    logger = logging.getLogger('ploneintranet.suite.create_users')
    for i, user in enumerate(users):
        email = decode(user['email'])
        userid = decode(user['userid'])
        file_name = '{}.jpg'.format(userid)
        properties = {
            'fullname': user.get('fullname', u"Anon Ymous {}".format(i)),
            'location': user.get('location', u"Unknown"),
            'description': user.get('description', u"")
        }
        try:
            api.user.create(
                email=email,
                username=userid,
                password='secret',
                properties=properties
            )
        except ValueError:
            user = api.user.get(username=userid)
            user.setMemberProperties(properties)
        logger.info('Created user {}'.format(userid))
        portrait_filename = os.path.join(avatars_dir, file_name)
        portrait = context.openDataFile(portrait_filename)
        if portrait:
            scaled, mimetype = scale_image(portrait)
            portrait = Image(id=userid, file=scaled, title='')
            memberdata = api.portal.get_tool(name='portal_memberdata')
            memberdata._setPortrait(portrait, userid)
        else:
            logger.warning(
                'Missing portrait file for {}: {}'.format(
                    userid,
                    portrait_filename
                )
            )

    # setup social network
    graph = queryUtility(INetworkGraph)
    graph.clear()
    for user in users:
        for followee in user.get('follows', []):
            graph.set_follow(userid, decode(followee))


def create_groups(groups):
    """Creates groups.

    ``groups`` is a dictionary with the following keys:

      * groupid
      * groupname
      * roles (list)
      * parentgroups
      * members (list)
    """
    group_tool = api.portal.get_tool(name='portal_groups')
    for group in groups:
        groupid = decode(group['groupid'])
        try:
            group_obj = api.group.get(groupname=groupid)
        except ValueError:
            group_obj = None
        if group_obj is None:
            api.group.create(
                groupname=groupid,
                roles=group.get('roles', []),
                title=group.get('title', groupid),
                groups=[decode(g) for g in group.get('parentgroups', [])]
            )
        else:
            group_tool.editGroup(
                groupid,
                roles=group.get('roles', []),
                title=group.get('title', groupid),
                groups=[decode(g) for g in group.get('parentgroups', [])]
            )
        for member in group.get('members', []):
            api.group.add_user(
                groupname=groupid,
                username=decode(member)
            )


def create_as(userid, *args, **kwargs):
    """Call api.content.create as a different user
    """
    obj = None
    with api.env.adopt_user(username=userid):
        try:
            obj = api.content.create(*args, **kwargs)
        except:
            # we still need to know what happend
            raise
    return obj


def create_news_items(newscontent):
    portal = api.portal.get()

    if 'news' not in portal:
        news_folder = api.content.create(
            type='Folder',
            title='News',
            container=portal
        )
    else:
        news_folder = portal['news']

    for newsitem in newscontent:
        # give the users rights to add news
        api.user.grant_roles(
            username=newsitem['creator'],
            roles=['Contributor', 'Reader', 'Editor'],
            obj=news_folder
        )
        # give the users rights to add news
        obj = create_as(
            userid=newsitem['creator'],
            type='News Item',
            title=newsitem['title'],
            description=newsitem['description'],
            container=news_folder
        )
        obj.setSubject(tuple(newsitem['tags']))

        # TODO: there is no workflow at this point
        # api.content.transition(obj=obj, transition='publish')

        obj.setEffectiveDate(newsitem['publication_date'])
        obj.reindexObject(idxs=['effective', ])


def create_tasks(todos):
    portal = api.portal.get()

    if 'todos' not in portal:
        todos_folder = api.content.create(
            type='Folder',
            title='Todos',
            container=portal)
    else:
        todos_folder = portal['todos']

    for data in todos:
        obj = create_as(
            data['creator'],
            type='simpletodo',
            title=data['title'],
            container=todos_folder)
        todo = ITodo(obj)
        todo.assignee = data['assignee']


def create_workspaces(workspaces):
    portal = api.portal.get()
    if 'workspaces' not in portal:
        ws_folder = api.content.create(
            container=portal,
            type='ploneintranet.workspace.workspacecontainer',
            title='Workspaces'
        )
    else:
        ws_folder = portal['workspaces']

    for w in workspaces:
        contents = w.pop('contents', None)
        members = w.pop('members', [])
        workspace = api.content.create(
            container=ws_folder,
            type='ploneintranet.workspace.workspacefolder',
            **w
        )
        api.content.transition(obj=workspace, transition='make_open')
        if contents is not None:
            create_ws_content(workspace, contents)
        for m in members:
            IWorkspace(workspace).add_to_team(user=m, groups=set([u'Members']))


def create_ws_content(parent, contents):
    for content in contents:
        sub_contents = content.pop('contents', None)
        obj = api.content.create(
            container=parent,
            **content
        )
        if sub_contents is not None:
            create_ws_content(obj, sub_contents)


def create_events(events):
    portal = api.portal.get()
    if 'events' not in portal:
        event_folder = api.content.create(
            container=portal,
            type='Folder',
            title='Events'
        )
    else:
        event_folder = portal['events']
    for ev in events:
        create_as(
            ev['creator'],
            type='Event',
            container=event_folder,
            **ev
        )


class FakeFileField(object):
    """A mock so that we can use ``create_attachment``
    """

    def __init__(self, filename, file_object):
        self.filename = filename
        self.file_object = file_object

    @property
    def headers(self):
        ctype, encoding = mimetypes.guess_type(self.filename)
        if ctype is None:
            ctype = 'application/octet-stream'
        return {
            'content-type': ctype
        }

    def read(self):
        return self.file_object.read()


def create_stream(context, stream, files_dir):
    contexts_cache = {}
    microblog = queryUtility(IMicroblogTool)
    microblog.clear()
    for status in stream:
        kwargs = {}
        if status['context']:
            if status['context'] not in contexts_cache:
                contexts_cache[status['context']] = api.content.get(
                    path='/' + decode(status['context']).lstrip('/')
                )
            kwargs['context'] = contexts_cache[status['context']]
        status_obj = StatusUpdate(status['text'], **kwargs)
        status_obj.userid = status['user']
        status_obj.creator = api.user.get(
            username=status['user']
        ).getProperty('fullname')
        offset_time = status['timestamp'] * 60
        status_obj.id -= int(offset_time * 1e6)
        status_obj.date = DateTime(time.time() - offset_time)
        microblog.add(status_obj)
        # THIS BREAKS BECAUSE DOCCONV. FIX DOCCONV, UNCOMMENT
        # if 'attachment' in status:
        #     attachment_definition = status['attachment']
        #     attachment_filename = os.path.join(
        #         files_dir,
        #         attachment_definition['filename']
        #     )
        #     attachment = context.openDataFile(attachment_filename)
        #     fake_field = FakeFileField(
        #         attachment_definition['filename'],
        #         attachment
        #     )
        #     attachment_obj = create_attachment(fake_field)
        #     attachments = IAttachmentStorage(status_obj)
        #     attachments.add(attachment_obj)


def testing(context):
    if context.readDataFile('ploneintranet.suite_testing.txt') is None:
        return

    users_csv_file = os.path.join(context._profile_path, 'users.csv')
    users = []
    with open(users_csv_file, 'rb') as users_csv_data:
        reader = csv.DictReader(users_csv_data)
        for user in reader:
            user = {
                k: v.decode('utf-8') for k, v in user.iteritems()
            }
            user['email'] = '{}@example.com'.format(decode(user['userid']))
            user['follows'] = [
                decode(u) for u in user['follows'].split(' ') if u
            ]
            users.append(user)
    create_users(context, users, 'avatars')

    groups_csv_file = os.path.join(context._profile_path, 'groups.csv')
    groups = []
    with open(groups_csv_file, 'rb') as groups_csv_data:
        reader = csv.DictReader(groups_csv_data)
        for group in reader:
            group = {
                k: v.decode('utf-8') for k, v in group.iteritems()
            }
            group['roles'] = [r for r in group['roles'].split('|') if r]
            group['parentgroups'] = [
                g for g in group['parentgroups'].split(' ') if g
            ]
            group['members'] = [
                u for u in group['members'].split(' ') if u
            ]
            groups.append(group)
    create_groups(groups)

    # We use following fixed tags
    tags = ['Rain', 'Sun', 'Planes', 'ICT', ]

    # We use fixed dates, we need these to be relative
    # publication_date = ['just now', 'next week', 'next year', ]
    publication_date = [DateTime('01/01/2019'),
                        DateTime('03/03/2021'),
                        DateTime('11/11/2023'), ]

    # make newsitems
    news_content = [
        {'title': 'Second Indian Airline to join Global Airline Alliance',
         'description': 'Weak network in growing Indian aviation market',
         'tags': [tags[0]],
         'publication_date': publication_date[0],
         'creator': 'alice_lindstrom'},

        {'title': 'BNB and Randomize to codeshare',
         'description': 'Starting September 10, BNB passengers will be'
                        'able to book connecting flights on Ethiopian '
                        'Airlines.',
         'tags': [tags[1]],
         'publication_date': publication_date[1],
         'creator': 'allan_neece'},

        {'title': 'Alliance Officially Opens New Lounge',
         'description': '',
         'tags': [tags[0], tags[1]],
         'publication_date': publication_date[2],
         'creator': 'christian_stoney'},
    ]
    create_news_items(news_content)

    # Create tasks
    todos_content = [{
        'title': 'Inquire after References',
        'creator': 'alice_lindstrom',
        'assignee': 'employees',
    }, {
        'title': 'Finalize budget',
        'creator': 'christian_stoney',
        'assignee': 'employees',
    }, {
        'title': 'Write SWOT analysis',
        'creator': 'pearlie_whitby',
        'assignee': 'employees',
    }, {
        'title': 'Prepare sales presentation',
        'creator': 'lance_stockstill',
        'assignee': 'lance_stockstill',
    }, {
        'title': 'Talk to HR about vacancy',
        'creator': 'allan_neece',
        'assignee': 'allan_neece',
    }]
    create_tasks(todos_content)

    now = datetime.now()

    # Create workspaces
    workspaces = [
        {'title': 'Open Market Committee',
         'description': 'The OMC holds eight regularly scheduled meetings '
                        'during the year and other meetings as needed.',
         'contents':
             [{'title': 'Manage Information',
               'type': 'Folder',
               'contents':
                   [{'title': 'Preparation of Records',
                     'description': 'How to prepare records',
                     'type': 'File'},
                    {'title': 'Public bodies reform',
                     'description': 'Making arrangements for the transfer of '
                                    'information, records and knowledge is a '
                                    'key part of any Machinery of Government '
                                    'change.',
                     'type': 'Document'}]},
              {'title': 'Projection Materials',
               'type': 'Folder',
               'contents':
                   [{'title': 'Projection Material',
                     'type': 'File'}]},
              {'title': 'Future Event',
               'type': 'Event',
               'start': now + timedelta(days=7),
               'end': now + timedelta(days=14)},
              {'title': 'Past Event',
               'type': 'Event',
               'start': now + timedelta(days=-7),
               'end': now + timedelta(days=-14)},
              ],
         'members': ['christian_stoney', ],
         },
        {'title': 'Parliamentary papers guidance',
         'description': '"Parliamentary paper" is a term used to describe a '
                        'document which is laid before Parliament. Most '
                        'government organisations will produce at least one '
                        'parliamentary paper per year.',
         'contents':
            [{'title': 'Test Document',
              'description': 'A document just for testing',
              'type': 'Document'}]
         }
    ]
    create_workspaces(workspaces)

    # Create some events
    tomorrow = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0,
                                                 microsecond=0)
    next_month = (now + timedelta(days=30)).replace(hour=9, minute=0,
                                                    second=0, microsecond=0)
    events = [
        {'title': 'Open Market Day',
         'creator': 'allan_neece',
         'start': tomorrow,
         'end': tomorrow + timedelta(hours=8)},
        {'title': 'Plone Conf',
         'creator': 'alice_lindstrom',
         'start': next_month,
         'end': next_month + timedelta(days=3, hours=8)}
    ]
    create_events(events)

    stream_json = os.path.join(context._profile_path, 'stream.json')
    with open(stream_json, 'rb') as stream_json_data:
        stream = json.load(stream_json_data)
    create_stream(context, stream, 'files')
