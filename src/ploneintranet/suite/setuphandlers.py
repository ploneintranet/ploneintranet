from AccessControl.SecurityManagement import newSecurityManager
from plone import api

def create_as(userid, *args, **kwargs):
    current = api.user.get_current()
    user = api.user.get(username=userid)
    newSecurityManager(None, user)
    try:
        api.content.create(*args, **kwargs)
    finally:
        # we always restore the previous security context, no matter what
        newSecurityManager(None, current)

def testing(context):

    if context.readDataFile('ploneintranet.suite_testing.txt') is None:
        return

    portal = api.portal.get()

    # see: https://github.com/cosent/plonesocial.suite/
    #       blob/master/src/plonesocial/suite/setuphandlers.py

    # for creating users and network

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
            create_as(
                "admin",
                type='News Item',
                title=newsitem['title'],
                description=newsitem['description'],
                container=portal['news'])
