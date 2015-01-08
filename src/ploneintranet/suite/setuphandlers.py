import os
import csv
import logging
import transaction
from zope.component import queryUtility
from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from OFS.Image import Image
from Products.PlonePAS.utils import scale_image
from ploneintranet.todo.behaviors import ITodo
from plonesocial.network.interfaces import INetworkGraph

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
    current = api.user.get_current()
    user = api.user.get(username=userid)
    newSecurityManager(None, user)
    obj = None
    try:
        obj = api.content.create(*args, **kwargs)
    finally:
        # we always restore the previous security context, no matter what
        newSecurityManager(None, current)
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
        obj = create_as(
            'admin',
            type='News Item',
            title=newsitem['title'],
            description=newsitem['description'],
            container=news_folder
        )
        obj.publication_date = newsitem['publication_date']
        obj.Subject = newsitem['tags']


def create_tasks(todos):
    portal = api.portal.get()

    if 'todos' not in portal:
        todos_folder = create_as(
            "admin",
            type='Folder',
            title='Todos',
            container=portal)
        api.content.transition(obj=todos_folder, transition='publish')
    else:
        todos_folder = portal['todos']

    for data in todos:
        obj = create_as(
            'admin',
            type='simpletodo',
            title=data['title'],
            container=todos_folder)
        todo = ITodo(obj)
        todo.assignee = data['assignee']


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

    # make newsitems
    news_content = [
        {'title': 'Second Indian Airline to join Global Airline Alliance',
         'description': 'Weak network in growing Indian aviation market',
         'tags': [tags[0]],
         'publication_date': ''},

        {'title': 'BNB and Randomize to codeshare',
         'description': 'Starting September 10, BNB passengers will be'
                        'able to book connecting flights on Ethiopian '
                        'Airlines.',
         'tags': [tags[1]],
         'publication_date': ''},

        {'title': 'Alliance Officially Opens New Lounge',
         'description': '',
         'tags': [tags[0], tags[1]],
         'publication_date': ''},
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
        'creator': 'kurt_weissman',
        'assignee': 'kurt_weissman',
    }]
    create_tasks(todos_content)
