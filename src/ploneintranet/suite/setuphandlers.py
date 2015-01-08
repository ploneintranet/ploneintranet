from AccessControl.SecurityManagement import newSecurityManager
from plone import api


def create_as(userid, *args, **kwargs):
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


def testing(context):

    if context.readDataFile('ploneintranet.suite_testing.txt') is None:
        return

    # see: https://github.com/cosent/plonesocial.suite/
    #       blob/master/src/plonesocial/suite/setuphandlers.py
    # for creating users and network

    # We use following fixed tags
    tags = ['Rain', 'Sun', 'Planes', 'ICT', ]

    # We use fixed dates, we need thes to be relative
    #publication_date = ['just now', 'next week', 'next year', ]

    # make newsitems
    news_content = [
        {'title': 'Second Indian Airline to join Global Airline Alliance',
         'description': 'Weak network in growing Indian aviation market',
         'tags': [tags[0]],
         'publication_date': ''},

        {'title': 'BNB and Randomize to codeshare',
         'description': 'Starting September 10, BNB passengers will be' +
         'able to book connecting flights on Ethiopian Airlines.',
         'tags': [tags[1]],
         'publication_date': ''},

        {'title': 'Alliance Officially Opens New Lounge',
         'description': '',
         'tags': [tags[0], tags[1]],
         'publication_date': ''},
    ]
    create_news_items(news_content)


def create_news_items(context, newscontent):
    # news item
    portal = api.portal.get()

    if not 'news' in portal.keys():
        # do we creat it?
        pass

    if 'news' in portal.keys():
        for newsitem in newscontent:
            obj = create_as("admin",
                            type='News Item',
                            title=newsitem['title'],
                            description=newsitem['description'],
                            container=portal['news'])
            obj.publication_date = newsitem['publication_date']
            obj.Subject = newsitem['tags']
