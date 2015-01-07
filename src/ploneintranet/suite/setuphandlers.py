import os
import csv
import logging
from zope.component import queryUtility
from plone import api
from OFS.Image import Image
from Products.PlonePAS.utils import scale_image
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


def testing(context):

    if context.readDataFile('ploneintranet.suite_testing.txt') is None:
        return

    portal = api.portal.get()
    csv_file = os.path.join(context._profile_path, 'users.csv')
    users = []
    with open(csv_file, 'rb') as csv_data:
        reader = csv.DictReader(csv_data)
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

    # news item
    if 'news' in portal.keys():

        newscontent = [
            {'title': 'Second Indian Airline to join Global Airline Alliance',
             'description': 'Weak network in growing Indian aviation market'},

            {'title': 'BNB and Randomize to codeshare',
             'description': 'Starting September 10, BNB passengers will be' +
             'able to book connecting flights on Ethiopian Airlines.'},

            {'title': 'Alliance Officially Opens New Lounge',
             'description': ''},
        ]
        for newsitem in newscontent:
            api.content.create(
                type='News Item',
                title=newsitem['title'],
                description=newsitem['description'],
                container=portal['news'])
